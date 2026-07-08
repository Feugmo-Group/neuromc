"""
widom.py
========
Widom test-particle insertion for the dft subpackage.

Provides μ_ex (excess chemical potential) and the Henry coefficient via:

    exp(-β·μ_ex) = <exp(-β·ΔU)>_N

for two model systems:

- **1D hard rods** (``WidomHardRod``): ghost insertion into a ``HardRodSystem``
  or a positions array. For hard rods, ΔU = 0 if no overlap, +∞ otherwise,
  so <exp(-β·ΔU)> = P(no overlap) = free-volume fraction.

- **3D RPM mimic** (``WidomRPM``): ghost insertion of a test cation and a test
  anion into an ``RPMSystem``. Returns μ_ex for each species.

Both classes expose a ``run()`` method that returns a dict with
``mu_ex``, ``henry``, ``free_volume_fraction`` (hard rods), etc.

References
----------
Frenkel & Smit, Understanding Molecular Simulation, Ch. 7 (2002)
Sammüller et al., J. Phys.: Condens. Matter 36, 243002 (2024)
Bui & Cox, Phys. Rev. Lett. 134, 148001 (2025)
"""

from __future__ import annotations

import math
import numpy as np

from .hard_rod_sim import HardRodSystem
from .rpm_sim import RPMSystem


# ---------------------------------------------------------------------------
# 1D Hard-rod Widom insertion
# ---------------------------------------------------------------------------

class WidomHardRod:
    """
    Widom test-particle insertion for the 1-D hard-rod fluid.

    For hard rods ΔU ∈ {0, +∞}, so:
        exp(-β·μ_ex) = P(no overlap) = free-volume fraction

    Insertions are spatially resolved to give ρ_ex(x) = exp(β·μ_loc(x)) / ξ,
    where ξ is the thermal de Broglie wavelength (set to 1 here).

    Parameters
    ----------
    system : HardRodSystem
        A pre-equilibrated system to sample from.
    n_bins : int
        Number of spatial bins for the resolved insertion profile.
    """

    def __init__(self, system: HardRodSystem, n_bins: int = 200):
        self.system = system
        self.n_bins = n_bins

    def run(
        self,
        n_insertions: int = 10_000,
        rng=None,
    ) -> dict:
        """
        Perform Widom insertions on the *current* configuration of ``system``.

        Parameters
        ----------
        n_insertions : int
            Number of ghost insertions.
        rng : np.random.Generator, optional
            Uses ``system.rng`` if None.

        Returns
        -------
        dict with keys:
            'mu_ex'                : float  — excess chemical potential (β units)
            'henry'                : float  — Henry coefficient exp(-β·μ_ex)
            'free_volume_fraction' : float  — fraction of insertions with no overlap
            'x_centers'            : ndarray (n_bins,)
            'insertion_profile'    : ndarray (n_bins,)
                                    Local success rate ρ(x) / (total insertions)
        """
        rng = rng if rng is not None else self.system.rng
        L = self.system.L
        sigma = self.system.sigma

        dx = L / self.n_bins
        x_edges = np.linspace(0.0, L, self.n_bins + 1)
        x_centers = 0.5 * (x_edges[:-1] + x_edges[1:])
        hist_accept = np.zeros(self.n_bins, dtype=np.float64)

        n_accept = 0
        for _ in range(n_insertions):
            x_ghost = rng.uniform(0.0, L)
            overlap = self.system._overlaps_any(x_ghost)
            if not overlap:
                n_accept += 1
                bin_idx = min(int(x_ghost / dx), self.n_bins - 1)
                hist_accept[bin_idx] += 1

        free_vol = n_accept / n_insertions if n_insertions > 0 else 0.0
        # <exp(-β·ΔU)> = P(no overlap) for hard rods
        henry = free_vol
        mu_ex = -math.log(henry) if henry > 0.0 else math.inf

        return {
            "mu_ex": mu_ex,
            "henry": henry,
            "free_volume_fraction": free_vol,
            "x_centers": x_centers,
            "insertion_profile": hist_accept / (n_insertions * dx),
        }


def widom_hard_rod(
    L: float,
    mu: float,
    T: float = 1.0,
    sigma: float = 1.0,
    vext_fn=None,
    n_equil: int = 5_000,
    n_prod: int = 20_000,
    n_insertions_per_step: int = 10,
    n_bins: int = 200,
    rng=None,
) -> dict:
    """
    Convenience driver: equilibrate a ``HardRodSystem`` then perform Widom
    insertion every production step, accumulating spatial insertion profiles.

    Returns
    -------
    dict with keys:
        'mu_ex'                : float
        'henry'                : float
        'free_volume_fraction' : float
        'x_centers'            : ndarray (n_bins,)
        'insertion_profile'    : ndarray (n_bins,) — time-averaged
        'rho'                  : ndarray (n_bins,) — density from GCMC
    """
    if rng is None:
        rng = np.random.default_rng()

    system = HardRodSystem(L=L, mu=mu, T=T, sigma=sigma, vext_fn=vext_fn, rng=rng)

    for _ in range(n_equil):
        system.sweep(n_gc=1)

    dx = L / n_bins
    x_edges = np.linspace(0.0, L, n_bins + 1)
    x_centers = 0.5 * (x_edges[:-1] + x_edges[1:])
    hist_rho = np.zeros(n_bins, dtype=np.float64)
    hist_accept = np.zeros(n_bins, dtype=np.float64)
    total_insert = 0
    total_accept = 0

    widom = WidomHardRod(system, n_bins=n_bins)

    for _ in range(n_prod):
        system.sweep(n_gc=1)
        pos = system.positions
        if len(pos) > 0:
            counts, _ = np.histogram(pos, bins=x_edges)
            hist_rho += counts.astype(np.float64)

        result = widom.run(n_insertions=n_insertions_per_step, rng=rng)
        n_acc = int(round(result["free_volume_fraction"] * n_insertions_per_step))
        total_insert += n_insertions_per_step
        total_accept += n_acc
        hist_accept += result["insertion_profile"] * n_insertions_per_step * dx

    rho = hist_rho / (n_prod * dx)
    free_vol = total_accept / total_insert if total_insert > 0 else 0.0
    henry = free_vol
    mu_ex = -math.log(henry) if henry > 0.0 else math.inf

    return {
        "mu_ex": mu_ex,
        "henry": henry,
        "free_volume_fraction": free_vol,
        "x_centers": x_centers,
        "insertion_profile": hist_accept / (n_prod * n_insertions_per_step * dx),
        "rho": rho,
    }


# ---------------------------------------------------------------------------
# 3D RPM Widom insertion
# ---------------------------------------------------------------------------

class WidomRPM:
    """
    Widom test-particle insertion for the 3D RPM mimic system.

    Inserts a ghost cation (+1) and a ghost anion (-1) independently.
    The excess chemical potential for each species is:

        exp(-β·μ_ex±) = <exp(-β·ΔU±)>_N

    where ΔU± is the pair energy of the ghost ion with all real particles.

    Spatially resolved insertion profiles are accumulated along z.

    Parameters
    ----------
    system : RPMSystem
        A pre-equilibrated system.
    n_bins_z : int
        Number of z-bins for the resolved profile.
    """

    def __init__(self, system: RPMSystem, n_bins_z: int = 100):
        self.system = system
        self.n_bins_z = n_bins_z

    def run(
        self,
        n_insertions: int = 500,
        rng=None,
        vext_plus_fn=None,
        vext_minus_fn=None,
        phi_fn=None,
    ) -> dict:
        """
        Perform n_insertions ghost insertions for each species independently.

        Returns
        -------
        dict with keys:
            'mu_ex_plus'         : float  — β·μ_ex for cation
            'mu_ex_minus'        : float  — β·μ_ex for anion
            'henry_plus'         : float  — <exp(-β·ΔU)> for cation
            'henry_minus'        : float  — <exp(-β·ΔU)> for anion
            'z_centers'          : ndarray (n_bins_z,)
            'profile_plus'       : ndarray (n_bins_z,) — Boltzmann-weighted z-profile (cation)
            'profile_minus'      : ndarray (n_bins_z,) — Boltzmann-weighted z-profile (anion)
        """
        rng = rng if rng is not None else self.system.rng
        sys = self.system
        beta = sys.beta
        z_min = sys.z_wall
        z_max = sys.Lz - sys.z_wall
        z_range = z_max - z_min

        z_edges = np.linspace(z_min, z_max, self.n_bins_z + 1)
        z_centers = 0.5 * (z_edges[:-1] + z_edges[1:])
        dz = z_edges[1] - z_edges[0]

        profile_plus  = np.zeros(self.n_bins_z, dtype=np.float64)
        profile_minus = np.zeros(self.n_bins_z, dtype=np.float64)
        sum_boltz_plus  = 0.0
        sum_boltz_minus = 0.0

        for _ in range(n_insertions):
            # --- ghost cation ---
            pos_g = sys._random_position()
            dU = sys._all_pair_energies(pos_g, +1.0)
            if not math.isinf(dU):
                vext = sys._vext_energy(pos_g, +1.0, vext_plus_fn, vext_minus_fn, phi_fn)
                boltz = math.exp(-beta * dU - vext)
                sum_boltz_plus += boltz
                z_g = pos_g[2]
                if z_min <= z_g <= z_max:
                    b_idx = min(int((z_g - z_min) / dz), self.n_bins_z - 1)
                    profile_plus[b_idx] += boltz

            # --- ghost anion ---
            pos_g = sys._random_position()
            dU = sys._all_pair_energies(pos_g, -1.0)
            if not math.isinf(dU):
                vext = sys._vext_energy(pos_g, -1.0, vext_plus_fn, vext_minus_fn, phi_fn)
                boltz = math.exp(-beta * dU - vext)
                sum_boltz_minus += boltz
                z_g = pos_g[2]
                if z_min <= z_g <= z_max:
                    b_idx = min(int((z_g - z_min) / dz), self.n_bins_z - 1)
                    profile_minus[b_idx] += boltz

        henry_plus  = sum_boltz_plus  / n_insertions
        henry_minus = sum_boltz_minus / n_insertions
        mu_ex_plus  = -math.log(henry_plus)  if henry_plus  > 0.0 else math.inf
        mu_ex_minus = -math.log(henry_minus) if henry_minus > 0.0 else math.inf

        norm = n_insertions * dz
        return {
            "mu_ex_plus":    mu_ex_plus,
            "mu_ex_minus":   mu_ex_minus,
            "henry_plus":    henry_plus,
            "henry_minus":   henry_minus,
            "z_centers":     z_centers,
            "profile_plus":  profile_plus / norm,
            "profile_minus": profile_minus / norm,
        }


def widom_rpm(
    Lx: float,
    Ly: float,
    Lz: float,
    mu_plus: float,
    mu_minus: float,
    kappa: float | None = None,
    sigma: float = 1.0,
    beta: float = 1.0,
    vext_plus_fn=None,
    vext_minus_fn=None,
    phi_fn=None,
    n_bins_z: int = 100,
    n_equil: int = 2_000,
    n_prod: int = 10_000,
    n_insertions_per_step: int = 20,
    rng=None,
) -> dict:
    """
    Convenience driver: equilibrate an ``RPMSystem`` then accumulate Widom
    insertion averages over n_prod production sweeps.

    Returns
    -------
    dict with keys:
        'mu_ex_plus'    : float
        'mu_ex_minus'   : float
        'henry_plus'    : float
        'henry_minus'   : float
        'z_centers'     : ndarray (n_bins_z,)
        'profile_plus'  : ndarray (n_bins_z,) — time-averaged Boltzmann profile
        'profile_minus' : ndarray (n_bins_z,)
        'rho_plus'      : ndarray (n_bins_z,) — density from GCMC
        'rho_minus'     : ndarray (n_bins_z,)
    """
    if rng is None:
        rng = np.random.default_rng()

    system = RPMSystem(
        Lx=Lx, Ly=Ly, Lz=Lz,
        mu_plus=mu_plus, mu_minus=mu_minus,
        kappa=kappa, sigma=sigma, beta=beta,
        rng=rng,
    )

    sweep_kwargs = dict(
        vext_plus_fn=vext_plus_fn,
        vext_minus_fn=vext_minus_fn,
        phi_fn=phi_fn,
    )

    for _ in range(n_equil):
        system.sweep(n_transitions=100, **sweep_kwargs)

    z_min = system.z_wall
    z_max = Lz - system.z_wall
    z_edges = np.linspace(z_min, z_max, n_bins_z + 1)
    z_centers = 0.5 * (z_edges[:-1] + z_edges[1:])
    dz = z_edges[1] - z_edges[0]
    bin_vol = Lx * Ly * dz

    hist_plus  = np.zeros(n_bins_z, dtype=np.float64)
    hist_minus = np.zeros(n_bins_z, dtype=np.float64)
    acc_profile_plus  = np.zeros(n_bins_z, dtype=np.float64)
    acc_profile_minus = np.zeros(n_bins_z, dtype=np.float64)
    sum_henry_plus  = 0.0
    sum_henry_minus = 0.0

    widom = WidomRPM(system, n_bins_z=n_bins_z)

    for _ in range(n_prod):
        system.sweep(n_transitions=100, **sweep_kwargs)

        if system.n_plus > 0:
            pos_p = np.array(system._pos_plus)
            counts, _ = np.histogram(pos_p[:, 2], bins=z_edges)
            hist_plus += counts.astype(float)
        if system.n_minus > 0:
            pos_m = np.array(system._pos_minus)
            counts, _ = np.histogram(pos_m[:, 2], bins=z_edges)
            hist_minus += counts.astype(float)

        res = widom.run(n_insertions=n_insertions_per_step, rng=rng, **sweep_kwargs)
        sum_henry_plus  += res["henry_plus"]
        sum_henry_minus += res["henry_minus"]
        acc_profile_plus  += res["profile_plus"]
        acc_profile_minus += res["profile_minus"]

    rho_plus  = hist_plus  / (n_prod * bin_vol)
    rho_minus = hist_minus / (n_prod * bin_vol)

    henry_plus  = sum_henry_plus  / n_prod
    henry_minus = sum_henry_minus / n_prod
    mu_ex_plus  = -math.log(henry_plus)  if henry_plus  > 0.0 else math.inf
    mu_ex_minus = -math.log(henry_minus) if henry_minus > 0.0 else math.inf

    return {
        "mu_ex_plus":    mu_ex_plus,
        "mu_ex_minus":   mu_ex_minus,
        "henry_plus":    henry_plus,
        "henry_minus":   henry_minus,
        "z_centers":     z_centers,
        "profile_plus":  acc_profile_plus  / n_prod,
        "profile_minus": acc_profile_minus / n_prod,
        "rho_plus":      rho_plus,
        "rho_minus":     rho_minus,
    }
