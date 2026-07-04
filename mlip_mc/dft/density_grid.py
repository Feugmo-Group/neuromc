"""
On-grid density accumulators and c⁽¹⁾ estimators for GCMC runs.

DensityGrid1D: planar projection ρ(z) — matches both papers' primary geometry.
DensityGrid3D: full volumetric ρ(x,y,z).

The one-body direct correlation is computed from the exact DFT identity
(Sammüller 2024 Eq. 6 / PRL 134 Eq. 3):

    c⁽¹⁾(r) = ln ρ(r) − β μ + β V_ext(r)

c⁽²⁾(r, r') is NOT estimated here; it is derived post-hoc from the
Ornstein-Zernike equation in Fourier space (see mlip_mc/dft/oz.py, planned).
"""

from __future__ import annotations

from typing import Optional
import numpy as np


class DensityGrid1D:
    """
    Planar density accumulator: bins particle z-coordinates into ρ(z).

    Supports block averaging for uncertainty quantification.

    Parameters
    ----------
    box_z : float
        Box length along z in Å.
    n_bins : int
        Number of histogram bins.
    n_blocks : int
        Number of production blocks for block averaging.
    xy_area : float
        Cross-sectional area A = Lx·Ly in Å².  Used to convert counts → ρ [Å⁻³].
    """

    def __init__(
        self,
        box_z: float,
        n_bins: int = 200,
        n_blocks: int = 10,
        xy_area: float = 1.0,
    ) -> None:
        self.box_z = box_z
        self.n_bins = n_bins
        self.n_blocks = n_blocks
        self.xy_area = xy_area

        self.dz = box_z / n_bins
        self.z_centers = (np.arange(n_bins) + 0.5) * self.dz

        # Accumulator: shape (n_blocks, n_bins)
        self._block_counts = np.zeros((n_blocks, n_bins), dtype=np.float64)
        self._block_steps = np.zeros(n_blocks, dtype=np.int64)
        self._current_block = 0
        self._total_steps = 0

    def reset(self) -> None:
        self._block_counts[:] = 0
        self._block_steps[:] = 0
        self._current_block = 0
        self._total_steps = 0

    def accumulate(self, positions: np.ndarray, steps_per_block: int) -> None:
        """
        Add adsorbate positions for one MC step.

        Parameters
        ----------
        positions : np.ndarray, shape (N_ads_atoms, 3)
            Positions of ALL adsorbate atoms (molecules × atoms_per_molecule).
        steps_per_block : int
            Number of production steps per block (for block assignment).
        """
        z = positions[:, 2] % self.box_z          # PBC wrap
        idx = np.floor(z / self.dz).astype(int)
        idx = np.clip(idx, 0, self.n_bins - 1)
        np.add.at(self._block_counts[self._current_block], idx, 1)
        self._block_steps[self._current_block] += 1
        self._total_steps += 1

        if self._block_steps[self._current_block] >= steps_per_block:
            self._current_block = min(self._current_block + 1, self.n_blocks - 1)

    def density(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Block-averaged ρ(z) [Å⁻³] and its standard error.

        Returns
        -------
        rho_mean : np.ndarray, shape (n_bins,)
        rho_stderr : np.ndarray, shape (n_bins,)
        """
        bin_vol = self.xy_area * self.dz
        block_densities = np.zeros((self.n_blocks, self.n_bins))
        for b in range(self.n_blocks):
            n_steps = max(self._block_steps[b], 1)
            block_densities[b] = self._block_counts[b] / (n_steps * bin_vol)

        rho_mean = block_densities.mean(axis=0)
        rho_stderr = block_densities.std(axis=0) / np.sqrt(self.n_blocks)
        return rho_mean, rho_stderr

    def c1(
        self,
        mu: float,
        beta: float,
        v_ext_grid: np.ndarray,
        rho_min: float = 1e-10,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Block-averaged c⁽¹⁾(z) and standard error.

        c⁽¹⁾(z) = ln ρ(z) − β μ + β V_ext(z)    [Sammüller 2024 Eq. 6]

        Parameters
        ----------
        mu : float
            Chemical potential in eV.
        beta : float
            1 / (kB T) in eV⁻¹.
        v_ext_grid : np.ndarray, shape (n_bins,)
            External potential sampled at bin centres (eV).
        rho_min : float
            Floor for ρ before taking log (avoids −∞ in empty bins).
        """
        bin_vol = self.xy_area * self.dz
        block_densities = np.zeros((self.n_blocks, self.n_bins))
        for b in range(self.n_blocks):
            n_steps = max(self._block_steps[b], 1)
            block_densities[b] = self._block_counts[b] / (n_steps * bin_vol)

        block_c1 = (
            np.log(np.maximum(block_densities, rho_min))
            - beta * mu
            + beta * v_ext_grid[None, :]
        )
        c1_mean = block_c1.mean(axis=0)
        c1_stderr = block_c1.std(axis=0) / np.sqrt(self.n_blocks)
        return c1_mean, c1_stderr

    def v_ext_on_grid(self, external_field) -> np.ndarray:
        """
        Evaluate an ExternalField on grid z-centres (returns shape (n_bins,)).

        The field is queried with dummy x=0, y=0 positions.
        """
        dummy_pos = np.zeros((self.n_bins, 3))
        dummy_pos[:, 2] = self.z_centers
        return external_field(dummy_pos)

    def results(
        self,
        mu: float,
        beta: float,
        external_field=None,
    ) -> dict:
        """Return a dict with all arrays needed by SampleWriter."""
        v_ext_grid = (
            self.v_ext_on_grid(external_field)
            if external_field is not None
            else np.zeros(self.n_bins)
        )
        rho_mean, rho_stderr = self.density()
        c1_mean, c1_stderr = self.c1(mu, beta, v_ext_grid)
        return {
            "z": self.z_centers,
            "rho": rho_mean,
            "rho_stderr": rho_stderr,
            "c1": c1_mean,
            "c1_stderr": c1_stderr,
            "v_ext": v_ext_grid,
            "n_bins": self.n_bins,
            "dz": self.dz,
            "box_z": self.box_z,
            "xy_area": self.xy_area,
            "n_blocks": self.n_blocks,
            "total_steps": self._total_steps,
        }


class DensityGrid3D:
    """
    Full volumetric ρ(x,y,z) accumulator.

    Parameters
    ----------
    box : np.ndarray, shape (3,)
        Box lengths [Lx, Ly, Lz] in Å.
    n_bins : tuple[int, int, int]
        Number of bins per axis.
    n_blocks : int
    """

    def __init__(
        self,
        box: np.ndarray,
        n_bins: tuple[int, int, int] = (32, 32, 32),
        n_blocks: int = 10,
    ) -> None:
        self.box = np.asarray(box, dtype=float)
        self.n_bins = tuple(n_bins)
        self.n_blocks = n_blocks
        self.dr = self.box / np.array(self.n_bins)

        nx, ny, nz = self.n_bins
        self._block_counts = np.zeros((n_blocks, nx, ny, nz), dtype=np.float64)
        self._block_steps = np.zeros(n_blocks, dtype=np.int64)
        self._current_block = 0
        self._total_steps = 0

    def accumulate(self, positions: np.ndarray, steps_per_block: int) -> None:
        pos_pbc = positions % self.box[None, :]
        idx = (pos_pbc / self.dr[None, :]).astype(int)
        idx = np.clip(idx, 0, np.array(self.n_bins) - 1)
        for ix, iy, iz in idx:
            self._block_counts[self._current_block, ix, iy, iz] += 1
        self._block_steps[self._current_block] += 1
        self._total_steps += 1
        if self._block_steps[self._current_block] >= steps_per_block:
            self._current_block = min(self._current_block + 1, self.n_blocks - 1)

    def density(self) -> tuple[np.ndarray, np.ndarray]:
        bin_vol = float(np.prod(self.dr))
        block_densities = np.zeros((self.n_blocks, *self.n_bins))
        for b in range(self.n_blocks):
            n_steps = max(self._block_steps[b], 1)
            block_densities[b] = self._block_counts[b] / (n_steps * bin_vol)
        rho_mean = block_densities.mean(axis=0)
        rho_stderr = block_densities.std(axis=0) / np.sqrt(self.n_blocks)
        return rho_mean, rho_stderr

    def grid_centers(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return (x, y, z) 1D arrays of bin centres."""
        return tuple(
            (np.arange(n) + 0.5) * d
            for n, d in zip(self.n_bins, self.dr)
        )
