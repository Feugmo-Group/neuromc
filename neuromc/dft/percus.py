"""
percus.py
=========
Percus' exact density-functional theory for 1-D hard rods.

The exact free-energy functional gives:
    c₁(x) = -ln(1 - n₁(x))

where
    n₁(x) = ∫_{x-R}^{x+R} ρ(x') dx'   (weighted density, R = σ/2)

computed via FFT convolution on a periodic grid.

References
----------
Percus, J. K. (1976).  Equilibrium state of a classical fluid of hard rods
in an external field.  J. Stat. Phys., 15, 505–511.

Sammüller et al., J. Phys.: Condens. Matter 36, 243002 (2024)
https://github.com/sfalmo/NeuralDFT-Tutorial  (Julia reference)
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Weight functions
# ---------------------------------------------------------------------------

def percus_weights(xs: np.ndarray, sigma: float = 1.0):
    """
    Compute Percus weight functions ω₀ and ω₁ on the grid *xs*.

    ω₀(x) = (δ(x − R) + δ(x + R)) / 2   — surface weight (contact)
    ω₁(x) = Θ(R − |x|)                   — volume weight (step function)

    R = sigma / 2.

    The grid *xs* is assumed to cover [0, L) with uniform spacing dx.
    Periodicity is handled by folding the mirror image back onto [0, N).

    Parameters
    ----------
    xs : np.ndarray
        Bin-centre positions.  Must be uniformly spaced starting near 0.
    sigma : float
        Hard-rod diameter.

    Returns
    -------
    omega0, omega1 : np.ndarray — each of shape (len(xs),)
    """
    N = len(xs)
    dx = xs[1] - xs[0]
    L = N * dx            # box length
    R = 0.5 * sigma

    omega0 = np.zeros(N)
    omega1 = np.zeros(N)

    # The convolution kernel is ω(r) for r in [0, L) with periodic wrapping.
    # r=0 maps to index 0; r=L-dx maps to index N-1.
    # Min-image distance from 0: min(r, L-r).
    # ω₁: step function Θ(R - min_image_dist)
    # ω₀: delta function at min_image_dist = R (approx as 0.5/dx spike)
    for i in range(N):
        r = xs[i]                       # position in [dx/2, L-dx/2]
        # shift so kernel is centred at 0: r is in [0, L)
        # min-image distance
        r0 = r if r <= L / 2 else L - r   # distance from 0 on periodic domain
        if r0 < R - 0.5 * dx:
            omega1[i] = 1.0
        elif abs(r0 - R) <= 0.5 * dx:
            omega1[i] = 0.5
            omega0[i] = 0.5 / dx

    return omega0, omega1


# ---------------------------------------------------------------------------
# FFT convolution helper
# ---------------------------------------------------------------------------

def _fft_conv(f: np.ndarray, g: np.ndarray, dx: float) -> np.ndarray:
    """
    Periodic FFT convolution: (f * g)(x) = ∫ f(x') g(x - x') dx'

    Uses np.fft.rfft / irfft, multiplies spectra, scales by dx.
    Output has same length as inputs.
    """
    N = len(f)
    F = np.fft.rfft(f)
    G = np.fft.rfft(g)
    conv = np.fft.irfft(F * G, n=N)
    return conv * dx


# ---------------------------------------------------------------------------
# Percus c₁
# ---------------------------------------------------------------------------

def c1_percus(rho: np.ndarray, xs: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """
    Compute c₁(x) from Percus' exact 1D hard-rod FMT functional.

    The excess free energy density is Φ(n₀, n₁) = −n₀ ln(1−n₁), so:

        c₁(r) = −δF_ex/δρ(r)
               = [(ln(1−n₁)) ⊛ ω₀](r) − [(n₀/(1−n₁)) ⊛ ω₁](r)

    This reproduces the exact Tonks bulk EOS:
        βμ = ln(ρ/(1−ρ)) + ρ/(1−ρ)
        c₁_bulk = ln(1−ρ) − ρ/(1−ρ) < 0

    Convention: c₁(x) = ln(ρ(x)) − β·μ_loc(x) (Sammüller 2024, eq. 6).

    Parameters
    ----------
    rho : np.ndarray (N,)
    xs  : np.ndarray (N,)
    sigma : float

    Returns
    -------
    c1 : np.ndarray (N,)
    """
    dx = xs[1] - xs[0]
    omega0, omega1 = percus_weights(xs, sigma=sigma)

    n1 = _fft_conv(omega1, rho, dx)
    n0 = _fft_conv(omega0, rho, dx)

    n1 = np.clip(n1, 0.0, 1.0 - 1e-12)
    n0 = np.clip(n0, 0.0, None)

    # Full Percus FMT: c₁ = (ln(1-n₁)) ⊛ ω₀  −  (n₀/(1-n₁)) ⊛ ω₁
    ln_term = np.log(1.0 - n1)
    contact_term = n0 / (1.0 - n1)

    c1 = _fft_conv(omega0, ln_term, dx) - _fft_conv(omega1, contact_term, dx)
    return c1


# ---------------------------------------------------------------------------
# DFT self-consistency (Picard iteration)
# ---------------------------------------------------------------------------

def dft_minimize(
    L: float,
    mu: float,
    T: float,
    vext_fn,
    c1_fn,
    n_bins: int = 1000,
    alpha: float = 0.03,
    max_iter: int = 10_000,
    tol: float = 1e-6,
    sigma: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Picard iteration for the DFT self-consistency equation:

        ρ_new(x) = exp(β·μ_loc(x) + c₁(x; [ρ]))
        ρ ← (1 − α)·ρ + α·ρ_new

    Parameters
    ----------
    L : float
        Box length.
    mu : float
        Chemical potential in β-units (β·μ).
    T : float
        Temperature (kB = 1).
    vext_fn : callable(x) -> β·Vext(x)
        External potential in β-units.
    c1_fn : callable(rho, xs) -> c1
        One-body direct correlation functional.  Must accept (rho, xs) and
        return an array of the same shape.
    n_bins : int
        Number of grid bins.
    alpha : float
        Picard mixing parameter (0 < α ≤ 1).
    max_iter : int
        Maximum number of iterations.
    tol : float
        Convergence tolerance on max |ρ_new − ρ|.
    sigma : float
        Hard-rod diameter.

    Returns
    -------
    x_centers : np.ndarray (n_bins,)
    rho : np.ndarray (n_bins,) — converged density profile.

    Raises
    ------
    RuntimeError
        If convergence is not achieved within max_iter iterations.
    """
    beta = 1.0 / T
    dx = L / n_bins
    x_centers = np.linspace(dx / 2, L - dx / 2, n_bins)

    # β·μ_loc(x) = β·μ - β·Vext(x) = mu - vext_fn(x)
    # (vext_fn already returns β·Vext)
    vext_vals = np.asarray([vext_fn(x) for x in x_centers], dtype=np.float64)
    beta_mu_loc = mu - vext_vals

    # Initialise ρ with uniform ideal-gas guess
    rho_init = np.exp(mu) * np.ones(n_bins)
    rho = rho_init.copy()

    for iteration in range(max_iter):
        c1 = c1_fn(rho, x_centers)
        rho_new = np.exp(beta_mu_loc + c1)

        # Damp any divergences
        rho_new = np.clip(rho_new, 0.0, 1.0 / sigma + 1e-6)

        err = np.max(np.abs(rho_new - rho))
        rho = (1.0 - alpha) * rho + alpha * rho_new

        if err < tol:
            return x_centers, rho

    raise RuntimeError(
        f"DFT Picard iteration did not converge after {max_iter} iterations "
        f"(last error = {err:.3e}, tol = {tol:.3e}).  "
        "Try increasing max_iter or decreasing alpha."
    )
