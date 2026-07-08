"""
hard_rod_sim.py
===============
Vectorised NumPy 1-D grand-canonical Monte Carlo for hard rods.

References
----------
Sammüller et al., J. Phys.: Condens. Matter 36, 243002 (2024)
https://github.com/sfalmo/NeuralDFT-Tutorial  (Julia reference)
"""

from __future__ import annotations

import math
import numpy as np


# ---------------------------------------------------------------------------
# Core simulation class
# ---------------------------------------------------------------------------

class HardRodSystem:
    """
    1D grand-canonical hard-rod fluid.

    Parameters
    ----------
    L : float
        Box length in units of σ.
    mu : float
        Chemical potential in β-units (i.e. β·μ, kB = 1).
    T : float
        Temperature (kB = 1). For pure hard rods T is irrelevant because
        hard-core energies are 0 or +∞, but it scales any soft Vext.
    sigma : float
        Rod diameter (default 1.0).
    vext_fn : callable(x) -> float | array, optional
        External potential in β-units.  Defaults to zero everywhere.
    rng : np.random.Generator, optional
        Random number generator (for reproducibility).
    """

    def __init__(
        self,
        L: float,
        mu: float,
        T: float = 1.0,
        sigma: float = 1.0,
        vext_fn=None,
        rng=None,
    ):
        self.L = float(L)
        self.mu = float(mu)
        self.T = float(T)
        self.beta = 1.0 / self.T
        self.sigma = float(sigma)
        self.vext_fn = vext_fn if vext_fn is not None else lambda x: 0.0
        self.rng = rng if rng is not None else np.random.default_rng()

        # Particle positions; start empty
        self._positions: list[float] = []

        # Move counters (for diagnostics)
        self.n_insert_accept = 0
        self.n_insert_trial = 0
        self.n_delete_accept = 0
        self.n_delete_trial = 0
        self.n_move_accept = 0
        self.n_move_trial = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def n_particles(self) -> int:
        return len(self._positions)

    @property
    def positions(self) -> np.ndarray:
        return np.asarray(self._positions)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _min_image(self, dx: float) -> float:
        """Minimum-image distance for 1-D PBC."""
        dx -= self.L * round(dx / self.L)
        return dx

    def _overlaps_any(self, x_new: float) -> bool:
        """Return True if x_new overlaps any existing particle (PBC)."""
        if self.n_particles == 0:
            return False
        pos = self.positions
        dists = np.abs(pos - x_new)
        dists = np.minimum(dists, self.L - dists)  # min-image
        return bool(np.any(dists < self.sigma))

    def _overlaps_any_except(self, x_new: float, exclude_idx: int) -> bool:
        """Return True if x_new overlaps any particle except exclude_idx (PBC)."""
        N = self.n_particles
        if N <= 1:
            return False
        pos = np.delete(self.positions, exclude_idx)
        dists = np.abs(pos - x_new)
        dists = np.minimum(dists, self.L - dists)
        return bool(np.any(dists < self.sigma))

    # ------------------------------------------------------------------
    # Grand-canonical moves
    # ------------------------------------------------------------------

    def trial_insert(self) -> bool:
        """
        Attempt a grand-canonical insertion.

        Acceptance probability (hard rods, β·Vext already absorbed in mu):
            acc = min(1, L / N_new · exp(β·μ - β·Vext(x)))
        """
        self.n_insert_trial += 1
        x_new = self.rng.uniform(0.0, self.L)

        if self._overlaps_any(x_new):
            return False  # instant reject (hard core)

        N_new = self.n_particles + 1
        beta_mu_loc = self.mu - self.beta * float(self.vext_fn(x_new))
        log_acc = beta_mu_loc - math.log(N_new / self.L)
        if log_acc >= 0.0 or self.rng.random() < math.exp(log_acc):
            self._positions.append(x_new)
            self.n_insert_accept += 1
            return True
        return False

    def trial_delete(self) -> bool:
        """
        Attempt a grand-canonical deletion.

        Acceptance probability:
            acc = min(1, N_old / L · exp(-β·μ + β·Vext(x)))
        """
        self.n_delete_trial += 1
        N_old = self.n_particles
        if N_old == 0:
            return False

        idx = int(self.rng.integers(0, N_old))
        x_del = self._positions[idx]
        beta_mu_loc = self.mu - self.beta * float(self.vext_fn(x_del))
        log_acc = math.log(N_old / self.L) - beta_mu_loc
        if log_acc >= 0.0 or self.rng.random() < math.exp(log_acc):
            self._positions.pop(idx)
            self.n_delete_accept += 1
            return True
        return False

    def trial_move(self, dx_max: float = 0.1) -> bool:
        """
        Attempt a displacement of a randomly chosen particle.

        For pure hard rods the energy change is 0 (no overlap) or +∞
        (overlap), so acceptance = 1 if no overlap else 0.
        """
        self.n_move_trial += 1
        N = self.n_particles
        if N == 0:
            return False

        idx = int(self.rng.integers(0, N))
        x_old = self._positions[idx]
        dx = self.rng.uniform(-dx_max, dx_max)
        x_new = (x_old + dx) % self.L

        if self._overlaps_any_except(x_new, idx):
            return False

        # Accept (hard-core only, ΔE = 0 for no-overlap case)
        self._positions[idx] = x_new
        self.n_move_accept += 1
        return True

    def sweep(self, n_gc: int = 1, n_trans: int = None) -> None:
        """
        Standard GCMC sweep with correct detailed balance.

        Grand-canonical moves (insertion + deletion) have a FIXED rate per
        sweep, independent of N.  Translation moves scale with N (canonical).

        Parameters
        ----------
        n_gc : int
            Number of insertion attempts AND deletion attempts (each) per sweep.
        n_trans : int, optional
            Number of translation attempts.  Defaults to max(1, N).
        """
        # Grand-canonical moves: fixed rate (detailed-balance correct)
        for _ in range(n_gc):
            self.trial_insert()
        for _ in range(n_gc):
            self.trial_delete()
        # Canonical translations: O(N) per sweep
        n_t = max(1, self.n_particles) if n_trans is None else n_trans
        for _ in range(n_t):
            self.trial_move()


# ---------------------------------------------------------------------------
# Convenience simulation driver
# ---------------------------------------------------------------------------

def simulate(
    L: float,
    mu: float,
    T: float,
    vext_fn,
    n_bins: int = 1000,
    n_equil: int = 10_000,
    n_prod: int = 100_000,
    sigma: float = 1.0,
    rng=None,
    vext_beta_scale: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Run GCMC for a 1-D hard-rod system and return the density profile.

    Parameters
    ----------
    L : float
        Box length in σ units.
    mu : float
        Chemical potential in β-units (β·μ).
    T : float
        Temperature (kB = 1).
    vext_fn : callable(x) -> float | array
        External potential in β-units (β·Vext) if vext_beta_scale=True,
        otherwise in energy units and will be multiplied by β internally.
    n_bins : int
        Number of histogram bins for ρ(x).
    n_equil : int
        Number of equilibration sweeps (not accumulated).
    n_prod : int
        Number of production sweeps (accumulated).
    sigma : float
        Rod diameter.
    rng : np.random.Generator, optional
    vext_beta_scale : bool
        If True (default), vext_fn already returns β·Vext.

    Returns
    -------
    x_centers : np.ndarray (n_bins,)
    rho       : np.ndarray (n_bins,) — density profile [particles / σ]
    mu_loc    : np.ndarray (n_bins,) — β·(μ - Vext(x)) at each bin center
    """
    if rng is None:
        rng = np.random.default_rng()

    # Wrap vext_fn so it always returns β·Vext
    if vext_beta_scale:
        _vext = vext_fn
    else:
        beta = 1.0 / T
        _vext = lambda x: beta * vext_fn(x)  # noqa: E731

    system = HardRodSystem(L=L, mu=mu, T=T, sigma=sigma, vext_fn=_vext, rng=rng)

    # --- Equilibration ---
    for _ in range(n_equil):
        system.sweep(n_gc=1)

    # --- Production with histogram accumulation ---
    dx = L / n_bins
    x_edges = np.linspace(0.0, L, n_bins + 1)
    x_centers = 0.5 * (x_edges[:-1] + x_edges[1:])
    hist = np.zeros(n_bins, dtype=np.float64)

    for _ in range(n_prod):
        system.sweep(n_gc=1)
        pos = system.positions
        if len(pos) > 0:
            counts, _ = np.histogram(pos, bins=x_edges)
            hist += counts.astype(np.float64)

    # Normalise: ρ(x) = counts / (n_prod * dx)
    rho = hist / (n_prod * dx)

    # Local chemical potential (β-units)
    vext_vals = np.asarray([_vext(x) for x in x_centers], dtype=np.float64)
    mu_loc = mu - vext_vals

    return x_centers, rho, mu_loc


# ---------------------------------------------------------------------------
# Random external potential generator
# ---------------------------------------------------------------------------

def generate_random_vext(
    L: float,
    rng=None,
    n_sin: int = 3,
    amplitude: float = 2.0,
    n_lin: int = 2,
    n_wall: int = 1,
):
    """
    Generate a random external potential V_ext(x) as a combination of
    sinusoids, linear ramps, and optional soft wall contributions.

    Returns a callable vext_fn(x) -> β·Vext(x).
    Used to generate diverse training data.

    Parameters
    ----------
    L : float
        Box length.
    rng : np.random.Generator, optional
    n_sin : int
        Number of sinusoidal components.
    amplitude : float
        Overall amplitude scale (in β units).
    n_lin : int
        Number of linear-ramp components (compatible with PBC: sine with very
        long period so effectively linear over [0, L]).
    n_wall : int
        Number of soft-wall (Gaussian) contributions.
    """
    if rng is None:
        rng = np.random.default_rng()

    # Sinusoidal terms: V(x) = A * sin(2π k x / L + φ)
    sin_ks = rng.integers(1, 5, size=n_sin)
    sin_As = rng.uniform(-amplitude, amplitude, size=n_sin)
    sin_phis = rng.uniform(0, 2 * math.pi, size=n_sin)

    # Linear-ramp-like: long-period sine with k=0.5 effectively linear
    lin_ks = rng.uniform(0.3, 0.8, size=n_lin)
    lin_As = rng.uniform(-amplitude * 0.5, amplitude * 0.5, size=n_lin)
    lin_phis = rng.uniform(0, 2 * math.pi, size=n_lin)

    # Soft walls: Gaussian bumps
    wall_centers = rng.uniform(0.1 * L, 0.9 * L, size=n_wall)
    wall_As = rng.uniform(0.5, amplitude, size=n_wall)
    wall_widths = rng.uniform(0.1, 0.5, size=n_wall)

    def vext_fn(x: float | np.ndarray) -> float | np.ndarray:
        x = np.asarray(x, dtype=float)
        v = np.zeros_like(x)
        for k, A, phi in zip(sin_ks, sin_As, sin_phis):
            v += A * np.sin(2 * math.pi * k * x / L + phi)
        for k, A, phi in zip(lin_ks, lin_As, lin_phis):
            v += A * np.sin(2 * math.pi * k * x / L + phi)
        for xc, A, w in zip(wall_centers, wall_As, wall_widths):
            v += A * np.exp(-0.5 * ((x - xc) / w) ** 2)
        return v

    return vext_fn
