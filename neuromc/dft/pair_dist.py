"""
Pair distribution function g(r) accumulator for GCMC trajectories.

g(r) is needed to compute c⁽²⁾(r) via the Ornstein-Zernike equation (see oz.py).

For a homogeneous (bulk) fluid:
    g(r) = <ρ(r|0)> / ρ_bulk
         = histogram of inter-particle distances, normalised by ideal gas

For a planar inhomogeneous fluid (what we generate with DensityGrid1D):
    g(z₁, z₂) ≈ g(|z₁ - z₂|)  in the bulk-like interior
    Full 2D g(z₁, z₂) is needed near walls (large memory, deferred).

We implement:
  PairDistBulk  — radial g(r) from 3D positions (isotropic, bulk reference)
  PairDistPlanar — g(z₁, z₂) for the planar geometry
"""

from __future__ import annotations

import numpy as np


class PairDistBulk:
    """
    Accumulate the radial pair distribution function g(r) for a bulk fluid.

    Parameters
    ----------
    r_max : float
        Maximum separation to histogram [Å].
    n_bins : int
        Number of radial bins.
    n_atoms_reference : int
        Number of framework atoms (excluded from adsorbate–adsorbate pairs).
    """

    def __init__(self, r_max: float = 10.0, n_bins: int = 500, n_frame: int = 0) -> None:
        self.r_max = r_max
        self.n_bins = n_bins
        self.n_frame = n_frame
        self.dr = r_max / n_bins
        self.r_centers = (np.arange(n_bins) + 0.5) * self.dr

        self._counts = np.zeros(n_bins, dtype=np.float64)
        self._n_frames = 0
        self._n_particles_sum = 0.0   # running sum of N_ads for normalisation

    def accumulate(self, atoms) -> None:
        """
        Add one snapshot to the g(r) histogram.

        Parameters
        ----------
        atoms : ase.Atoms
            Full system (framework + adsorbates).
        """
        n_ads = len(atoms) - self.n_frame
        if n_ads < 2:
            return

        pos_ads = atoms.get_positions()[self.n_frame:]
        cell = np.array(atoms.get_cell())

        # All unique adsorbate–adsorbate pairs
        for i in range(n_ads - 1):
            dr = pos_ads[i + 1:] - pos_ads[i]
            # Minimum image convention
            dr -= np.round(dr @ np.linalg.inv(cell)) @ cell
            r = np.linalg.norm(dr, axis=1)
            mask = r < self.r_max
            idx = np.floor(r[mask] / self.dr).astype(int)
            idx = np.clip(idx, 0, self.n_bins - 1)
            np.add.at(self._counts, idx, 1)

        self._n_frames += 1
        self._n_particles_sum += n_ads

    def gr(self, rho_bulk: float) -> tuple[np.ndarray, np.ndarray]:
        """
        Normalise accumulated counts to g(r).

        Parameters
        ----------
        rho_bulk : float
            Bulk number density [Å⁻³].

        Returns
        -------
        r : np.ndarray, shape (n_bins,)
        g : np.ndarray, shape (n_bins,)
        """
        if self._n_frames == 0:
            return self.r_centers, np.zeros(self.n_bins)

        n_avg = self._n_particles_sum / self._n_frames
        # Shell volume
        shell_vol = (4.0 / 3.0 * np.pi *
                     ((self.r_centers + self.dr / 2) ** 3 -
                      (self.r_centers - self.dr / 2) ** 3))
        # Ideal-gas count per frame (unique pairs i<j → divide by 2)
        ideal = rho_bulk * shell_vol * n_avg / 2.0

        g = self._counts / (self._n_frames * np.maximum(ideal, 1e-30))
        return self.r_centers, g

    def structure_factor(self, rho_bulk: float, k_max: float = 20.0, n_k: int = 500
                         ) -> tuple[np.ndarray, np.ndarray]:
        """
        Fourier transform of (g(r) - 1) to get S(k) - 1 = ρ·ĥ(k).

        Returns
        -------
        k : np.ndarray
        Sk : np.ndarray  (S(k) = 1 + ρ·ĥ(k))
        """
        r, g = self.gr(rho_bulk)
        h = g - 1.0
        k = np.linspace(1e-6, k_max, n_k)
        # Isotropic 3D FT: ĥ(k) = 4π ∫ r·h(r) sin(kr)/k dr
        hk = np.array([
            4.0 * np.pi * np.trapezoid(r ** 2 * h * np.sinc(ki * r / np.pi), r)
            for ki in k
        ])
        Sk = 1.0 + rho_bulk * hk
        return k, Sk


class PairDistPlanar:
    """
    Planar pair distribution function g(z₁, z₂) for inhomogeneous 1D systems.

    Only the adsorbate–adsorbate pairs are counted.
    The cross-sectional xy-averaging is done implicitly.

    Parameters
    ----------
    box_z : float
        Box length along z [Å].
    n_bins : int
        Number of bins per axis (result is n_bins × n_bins).
    n_frame : int
        Number of framework atoms to skip.
    """

    def __init__(self, box_z: float, n_bins: int = 100, n_frame: int = 0) -> None:
        self.box_z = box_z
        self.n_bins = n_bins
        self.n_frame = n_frame
        self.dz = box_z / n_bins
        self.z_centers = (np.arange(n_bins) + 0.5) * self.dz

        self._counts = np.zeros((n_bins, n_bins), dtype=np.float64)
        self._n_frames = 0

    def accumulate(self, atoms) -> None:
        pos_ads = atoms.get_positions()[self.n_frame:]
        n_ads = len(pos_ads)
        if n_ads < 2:
            return

        z = pos_ads[:, 2] % self.box_z
        iz = np.floor(z / self.dz).astype(int)
        iz = np.clip(iz, 0, self.n_bins - 1)

        for i in range(n_ads):
            for j in range(n_ads):
                if i != j:
                    self._counts[iz[i], iz[j]] += 1

        self._n_frames += 1

    def g_zz(self, rho_z: np.ndarray) -> np.ndarray:
        """
        Normalise to g(z₁, z₂).

        Parameters
        ----------
        rho_z : np.ndarray, shape (n_bins,)
            1D density profile ρ(z) [Å⁻³].

        Returns
        -------
        g : np.ndarray, shape (n_bins, n_bins)
        """
        if self._n_frames == 0:
            return np.zeros((self.n_bins, self.n_bins))
        denom = np.outer(rho_z, rho_z) * self.dz ** 2
        g = self._counts / (self._n_frames * np.maximum(denom, 1e-30))
        return g
