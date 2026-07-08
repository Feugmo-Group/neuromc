"""
Ornstein-Zernike inversion and excess free-energy utilities for 1D/3D fluids.

Provides:
  oz_inversion_1d  — c(z1,z2) from g(z1,z2) via planar OZ in k-space
  oz_inversion_3d  — c(r) from g(r) via isotropic OZ: ĉ(k) = ĥ(k)/(1+ρ·ĥ(k))
  free_energy_excess_ti — F_exc via coupling-constant integration over c⁽²⁾

References
----------
Sammüller et al., J. Phys.: Condens. Matter 36, 243002 (2024)  [Eq. 2–5]
Evans et al., Phys. Rev. Lett. 134, 148001 (2025)
"""

from __future__ import annotations

import numpy as np


def oz_inversion_3d(
    r: np.ndarray,
    gr: np.ndarray,
    rho_bulk: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute the direct correlation function c(r) from g(r) for a bulk fluid.

    Uses the isotropic Ornstein-Zernike relation in k-space:
        ĉ(k) = ĥ(k) / (1 + ρ·ĥ(k))
    then inverse-FT back to real space.

    Parameters
    ----------
    r : np.ndarray, shape (N,)
        Bin centres [Å] (uniform spacing assumed).
    gr : np.ndarray, shape (N,)
        Pair distribution function g(r).
    rho_bulk : float
        Number density [Å⁻³].

    Returns
    -------
    r : np.ndarray, shape (N,)
    cr : np.ndarray, shape (N,)
        Direct correlation function c(r).
    """
    dr = r[1] - r[0]
    h = gr - 1.0

    # Forward FT: ĥ(k) = 4π ∫ r² h(r) sin(kr)/(kr) dr
    k_max = np.pi / dr               # Nyquist
    n_k = len(r)
    k = np.linspace(1e-8, k_max, n_k)

    hk = np.array([
        4.0 * np.pi * np.trapezoid(r ** 2 * h * np.sinc(ki * r / np.pi), r)
        for ki in k
    ])

    # OZ in k-space
    ck = hk / (1.0 + rho_bulk * hk + 1e-300)

    # Inverse FT: c(r) = 1/(2π²) ∫ k² ĉ(k) sin(kr)/(kr) dk
    cr = np.array([
        1.0 / (2.0 * np.pi ** 2) *
        np.trapezoid(k ** 2 * ck * np.sinc(ki2 * k / np.pi), k)
        for ki2 in r
    ])

    return r, cr


def oz_inversion_1d(
    g_zz: np.ndarray,
    rho_z: np.ndarray,
    box_z: float,
) -> np.ndarray:
    """
    Invert the planar OZ equation to obtain c(z1, z2).

    The planar OZ relation in Fourier space (kz):
        Ĥ(kz) = Ĝ(kz) - I    (matrix in z-grid space)
        Ĉ(kz)[I + ρ̄·Ĥ(kz)] = Ĥ(kz)

    where ρ̄ is the diagonal matrix of ρ(z)·dz.

    Parameters
    ----------
    g_zz : np.ndarray, shape (N, N)
        Planar pair distribution g(z1, z2).
    rho_z : np.ndarray, shape (N,)
        1D density profile ρ(z) [Å⁻³].
    box_z : float
        Box length along z [Å].

    Returns
    -------
    c_zz : np.ndarray, shape (N, N)
        Direct correlation function c(z1, z2).
    """
    n = len(rho_z)
    dz = box_z / n

    # h(z1,z2) = g(z1,z2) - 1, symmetrised
    h_zz = g_zz - 1.0
    h_zz = 0.5 * (h_zz + h_zz.T)

    # Weighted by dz: H_ij ≡ h(zi,zj)·dz
    H = h_zz * dz

    # Solve c + c·ρ·h = h row-by-row via OZ: (I + ρ·H)·c^T = H^T
    # Equivalently: c^T (z2 for each z1) from c(I + ρH) = H → c = H(I+ρH)⁻¹
    rho_diag = np.diag(rho_z)
    A = np.eye(n) + rho_diag @ H     # (I + ρ·H)
    # c·A = H  →  c = H·A⁻¹
    try:
        c_zz = np.linalg.solve(A.T, H.T).T / dz
    except np.linalg.LinAlgError:
        c_zz = np.linalg.lstsq(A.T, H.T, rcond=None)[0].T / dz

    return c_zz


def free_energy_excess_ti(
    r: np.ndarray,
    cr_lambda: list[np.ndarray],
    gr_lambda: list[np.ndarray],
    rho_bulk: float,
    lambdas: np.ndarray | None = None,
) -> float:
    """
    Excess free energy via thermodynamic integration over coupling constant λ.

    F_exc = -ρ²/2 ∫₀¹ dλ ∫ dr c(r;λ) h(r;λ)  4πr²

    Parameters
    ----------
    r : np.ndarray, shape (N,)
        Radial bin centres [Å].
    cr_lambda : list of np.ndarray
        c(r) at each λ value.
    gr_lambda : list of np.ndarray
        g(r) at each λ value.
    rho_bulk : float
        Number density [Å⁻³].
    lambdas : np.ndarray, optional
        Coupling constants; defaults to linspace(0,1,len(cr_lambda)).

    Returns
    -------
    f_exc : float
        Excess free energy per particle [eV or same units as c(r)·h(r)·r²].
    """
    n_lam = len(cr_lambda)
    if lambdas is None:
        lambdas = np.linspace(0.0, 1.0, n_lam)

    integrand_lam = np.zeros(n_lam)
    for i, (cr, gr) in enumerate(zip(cr_lambda, gr_lambda)):
        h = gr - 1.0
        integrand_lam[i] = np.trapezoid(4.0 * np.pi * r ** 2 * cr * h, r)

    f_exc = -0.5 * rho_bulk ** 2 * np.trapezoid(integrand_lam, lambdas)
    return float(f_exc)
