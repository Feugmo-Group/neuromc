"""
rpm_sim.py
==========
Grand-canonical MC for the Restricted Primitive Model (RPM) mimic system.

The mimic system uses the short-range electrostatic potential:
    v₀(r) = Z⁺Z⁻ · erfc(κ·r) / r   (for ions ±)

with κ⁻¹ = 1.8σ (default) as the cutoff length scale.

The density profiles ρ₊(z) and ρ₋(z) are accumulated as histograms.

References
----------
Bui & Cox, Phys. Rev. Lett. 134, 148001 (2025)
"""

from __future__ import annotations

import math
import numpy as np


# ---------------------------------------------------------------------------
# Default parameters
# ---------------------------------------------------------------------------

_DEFAULT_KAPPA_INV = 1.8   # κ⁻¹ in units of σ (Bui & Cox default)


# ---------------------------------------------------------------------------
# Helper: erfc (lazy import scipy, fallback to math)
# ---------------------------------------------------------------------------

def _erfc(x):
    """Element-wise erfc; uses scipy if available, else math.erfc."""
    x = np.asarray(x, dtype=float)
    try:
        from scipy.special import erfc as _sp_erfc
        return _sp_erfc(x)
    except ImportError:
        vec = np.vectorize(math.erfc)
        return vec(x)


# ---------------------------------------------------------------------------
# Core simulation class
# ---------------------------------------------------------------------------

class RPMSystem:
    """
    3D GCMC for a symmetric RPM mimic system (cations + anions).

    Parameters
    ----------
    Lx, Ly, Lz : float
        Box dimensions in σ units.
    mu_plus, mu_minus : float
        β·μ for cations (+) and anions (-).
    kappa : float, optional
        Screening parameter κ (in units of 1/σ). Default 1/1.8.
    sigma : float
        Hard-sphere diameter, default 1.0.
    beta : float
        Inverse temperature, default 1.0.
    z_wall : float, optional
        Exclusion zone from walls; particles must have z ∈ [z_wall, Lz - z_wall].
        Default 0.5*sigma.
    rng : np.random.Generator, optional
        Random number generator for reproducibility.
    """

    def __init__(
        self,
        Lx: float,
        Ly: float,
        Lz: float,
        mu_plus: float,
        mu_minus: float,
        kappa: float | None = None,
        sigma: float = 1.0,
        beta: float = 1.0,
        z_wall: float | None = None,
        rng=None,
    ):
        self.Lx = float(Lx)
        self.Ly = float(Ly)
        self.Lz = float(Lz)
        self.mu_plus = float(mu_plus)
        self.mu_minus = float(mu_minus)
        self.sigma = float(sigma)
        self.beta = float(beta)

        if kappa is None:
            self.kappa = 1.0 / _DEFAULT_KAPPA_INV
        else:
            self.kappa = float(kappa)

        if z_wall is None:
            self.z_wall = 0.5 * self.sigma
        else:
            self.z_wall = float(z_wall)

        self.rng = rng if rng is not None else np.random.default_rng()

        # Particle positions: (N, 3) arrays for each species
        # _pos_plus[i] = [x, y, z] of i-th cation
        self._pos_plus: list[np.ndarray] = []   # cations  (+1)
        self._pos_minus: list[np.ndarray] = []  # anions   (-1)

        # Move acceptance counters
        self.n_insert_accept = {"plus": 0, "minus": 0}
        self.n_insert_trial  = {"plus": 0, "minus": 0}
        self.n_delete_accept = {"plus": 0, "minus": 0}
        self.n_delete_trial  = {"plus": 0, "minus": 0}
        self.n_move_accept   = 0
        self.n_move_trial    = 0
        self.n_swap_accept   = 0
        self.n_swap_trial    = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def n_plus(self) -> int:
        return len(self._pos_plus)

    @property
    def n_minus(self) -> int:
        return len(self._pos_minus)

    @property
    def V_accessible(self) -> float:
        """Accessible volume (excluding wall exclusion zones)."""
        return self.Lx * self.Ly * max(0.0, self.Lz - 2.0 * self.z_wall)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _random_position(self) -> np.ndarray:
        """Draw a uniformly random position in the accessible volume."""
        x = self.rng.uniform(0.0, self.Lx)
        y = self.rng.uniform(0.0, self.Ly)
        z = self.rng.uniform(self.z_wall, self.Lz - self.z_wall)
        return np.array([x, y, z], dtype=float)

    def _min_image_xy(self, dr: np.ndarray) -> np.ndarray:
        """Apply minimum-image convention in x and y (PBC); z is left as-is."""
        dr = dr.copy()
        dr[0] -= self.Lx * round(dr[0] / self.Lx)
        dr[1] -= self.Ly * round(dr[1] / self.Ly)
        return dr

    def _dist(self, pos_a: np.ndarray, pos_b: np.ndarray) -> float:
        """Minimum-image distance (PBC in x,y only; hard walls in z)."""
        dr = self._min_image_xy(pos_a - pos_b)
        return float(np.sqrt(np.dot(dr, dr)))

    def _pair_energy_mimic(
        self,
        pos_new: np.ndarray,
        charge_new: float,
        species_positions: list[np.ndarray],
        species_charges: list[float],
    ) -> float:
        """
        Electrostatic energy of a new particle with all existing particles.

        Hard core: returns +inf if any r < sigma.
        Electrostatic mimic: sums charge_new * charge_j * erfc(kappa*r)/r
        over all existing particles.

        Parameters
        ----------
        pos_new : (3,) array — position of the new particle
        charge_new : float — charge of the new particle (+1 or -1)
        species_positions : list of (3,) arrays
        species_charges : list of floats (matching species_positions)

        Returns
        -------
        float — pair energy in units of kT (i.e. beta*U already divided out,
                 the caller scales by beta if needed; here we return beta*U).
        """
        if not species_positions:
            return 0.0

        total = 0.0
        kappa = self.kappa
        sigma = self.sigma

        for pos_j, charge_j in zip(species_positions, species_charges):
            dr = self._min_image_xy(pos_new - pos_j)
            r2 = float(np.dot(dr, dr))
            if r2 < sigma * sigma:
                return math.inf
            r = math.sqrt(r2)
            total += charge_new * charge_j * math.erfc(kappa * r) / r

        return total  # in units of (charge²/σ); caller handles prefactor

    def _all_pair_energies(self, pos_new: np.ndarray, charge_new: float) -> float:
        """
        Total mimic pair energy of pos_new with ALL existing particles.

        Returns +inf on hard-core overlap, else float (in kT = 1/beta units).
        The Bui & Cox interaction energy for the RPM mimic is:
            U_pair(i,j) = q_i * q_j * erfc(kappa * r_ij) / r_ij
        (In reduced units where q² / (epsilon * kT) is absorbed into beta.)
        """
        # Gather all positions and charges
        all_pos = self._pos_plus + self._pos_minus
        all_q   = [+1.0] * self.n_plus + [-1.0] * self.n_minus

        return self._pair_energy_mimic(pos_new, charge_new, all_pos, all_q)

    def _vext_energy(
        self,
        pos: np.ndarray,
        charge: float,
        vext_plus_fn=None,
        vext_minus_fn=None,
        phi_fn=None,
    ) -> float:
        """
        External potential energy (in β units) for a particle at pos.

        Parameters
        ----------
        pos : (3,) array
        charge : float  — +1 (cation) or -1 (anion)
        vext_plus_fn : callable(z) -> β*V_ext for cations, or None
        vext_minus_fn : callable(z) -> β*V_ext for anions, or None
        phi_fn : callable(z) -> β*ϕ_R(z) external electrostatic potential, or None

        Returns
        -------
        float — β * V_ext_total
        """
        z = pos[2]
        v = 0.0

        if charge > 0 and vext_plus_fn is not None:
            v += float(vext_plus_fn(z))
        elif charge < 0 and vext_minus_fn is not None:
            v += float(vext_minus_fn(z))

        if phi_fn is not None:
            # electrostatic: β*q*ϕ_R(z) — phi_fn returns β*ϕ_R
            v += charge * float(phi_fn(z))

        return v

    # ------------------------------------------------------------------
    # Grand-canonical moves
    # ------------------------------------------------------------------

    def trial_insert(
        self,
        charge: float,
        vext_plus_fn=None,
        vext_minus_fn=None,
        phi_fn=None,
    ) -> bool:
        """
        Attempt a grand-canonical insertion of a particle with given charge.

        charge = +1 for cation, -1 for anion.

        Acceptance probability (Adams convention):
            acc = min(1, V/(N+1) * exp(β·μ - β·ΔU_pair - β·Vext))
        where β·ΔU_pair is the pair energy with existing particles (in kT).
        """
        label = "plus" if charge > 0 else "minus"
        mu = self.mu_plus if charge > 0 else self.mu_minus
        self.n_insert_trial[label] += 1

        pos_new = self._random_position()

        # Pair energy (already in kT if Coulomb prefactor is in kT units)
        dU_pair = self._all_pair_energies(pos_new, charge)
        if math.isinf(dU_pair):
            return False  # hard-core overlap

        # External potential (in β units)
        beta_vext = self._vext_energy(pos_new, charge, vext_plus_fn, vext_minus_fn, phi_fn)

        N_new = (self.n_plus if charge > 0 else self.n_minus) + 1
        V = self.V_accessible

        # log acceptance: log(V/N_new) + βμ - β*dU_pair - β*Vext
        # Note: dU_pair is already in β units (kT), beta_vext is in β units
        log_acc = math.log(V / N_new) + mu - self.beta * dU_pair - beta_vext
        if log_acc >= 0.0 or self.rng.random() < math.exp(log_acc):
            if charge > 0:
                self._pos_plus.append(pos_new)
            else:
                self._pos_minus.append(pos_new)
            self.n_insert_accept[label] += 1
            return True
        return False

    def trial_delete(
        self,
        charge: float,
        vext_plus_fn=None,
        vext_minus_fn=None,
        phi_fn=None,
    ) -> bool:
        """
        Attempt a grand-canonical deletion of a random particle with given charge.

        Acceptance probability:
            acc = min(1, N/V * exp(-β·μ + β·ΔU_pair + β·Vext))
        """
        label = "plus" if charge > 0 else "minus"
        mu = self.mu_plus if charge > 0 else self.mu_minus
        self.n_delete_trial[label] += 1

        pool = self._pos_plus if charge > 0 else self._pos_minus
        N_old = len(pool)
        if N_old == 0:
            return False

        idx = int(self.rng.integers(0, N_old))
        pos_del = pool[idx]

        # Build list of all other particles
        if charge > 0:
            others_pos = [p for i, p in enumerate(self._pos_plus) if i != idx] + self._pos_minus
            others_q   = [+1.0] * (self.n_plus - 1) + [-1.0] * self.n_minus
        else:
            others_pos = self._pos_plus + [p for i, p in enumerate(self._pos_minus) if i != idx]
            others_q   = [+1.0] * self.n_plus + [-1.0] * (self.n_minus - 1)

        dU_pair = self._pair_energy_mimic(pos_del, charge, others_pos, others_q)
        # dU_pair is energy particle_del has with all others (never inf here)

        beta_vext = self._vext_energy(pos_del, charge, vext_plus_fn, vext_minus_fn, phi_fn)

        V = self.V_accessible
        # log acc = log(N_old/V) - βμ + β*dU_pair + β*Vext
        log_acc = math.log(N_old / V) - mu + self.beta * dU_pair + beta_vext
        if log_acc >= 0.0 or self.rng.random() < math.exp(log_acc):
            pool.pop(idx)
            self.n_delete_accept[label] += 1
            return True
        return False

    def trial_move(
        self,
        dx_max: float = 0.1,
        vext_plus_fn=None,
        vext_minus_fn=None,
        phi_fn=None,
    ) -> bool:
        """
        Attempt a displacement of a randomly chosen particle (any species).

        Acceptance: Metropolis criterion on ΔU_pair + ΔVext.
        """
        self.n_move_trial += 1
        N_total = self.n_plus + self.n_minus
        if N_total == 0:
            return False

        # Pick a random particle from the combined pool
        flat_idx = int(self.rng.integers(0, N_total))
        if flat_idx < self.n_plus:
            species = "plus"
            charge = +1.0
            pool = self._pos_plus
            idx = flat_idx
        else:
            species = "minus"
            charge = -1.0
            pool = self._pos_minus
            idx = flat_idx - self.n_plus

        pos_old = pool[idx]

        # Propose new position
        displacement = self.rng.uniform(-dx_max, dx_max, size=3)
        pos_new = pos_old + displacement
        # PBC in x, y
        pos_new[0] %= self.Lx
        pos_new[1] %= self.Ly
        # Hard wall in z
        if pos_new[2] < self.z_wall or pos_new[2] > self.Lz - self.z_wall:
            return False

        # Energy of old position with all OTHER particles
        if species == "plus":
            others_pos = [p for i, p in enumerate(self._pos_plus) if i != idx] + self._pos_minus
            others_q   = [+1.0] * (self.n_plus - 1) + [-1.0] * self.n_minus
        else:
            others_pos = self._pos_plus + [p for i, p in enumerate(self._pos_minus) if i != idx]
            others_q   = [+1.0] * self.n_plus + [-1.0] * (self.n_minus - 1)

        U_old = self._pair_energy_mimic(pos_old, charge, others_pos, others_q)
        U_new = self._pair_energy_mimic(pos_new, charge, others_pos, others_q)

        if math.isinf(U_new):
            return False

        dVext = (
            self._vext_energy(pos_new, charge, vext_plus_fn, vext_minus_fn, phi_fn)
            - self._vext_energy(pos_old, charge, vext_plus_fn, vext_minus_fn, phi_fn)
        )

        log_acc = -self.beta * (U_new - U_old) - dVext
        if log_acc >= 0.0 or self.rng.random() < math.exp(log_acc):
            pool[idx] = pos_new
            self.n_move_accept += 1
            return True
        return False

    def trial_swap(
        self,
        vext_plus_fn=None,
        vext_minus_fn=None,
        phi_fn=None,
    ) -> bool:
        """
        Semi-GC swap: convert a random particle from + to - (or vice versa).

        This maintains electroneutrality while allowing composition fluctuations.
        Acceptance: Metropolis on ΔU + Δ(β·μ) + ΔVext.
        """
        self.n_swap_trial += 1
        N_total = self.n_plus + self.n_minus
        if N_total == 0:
            return False

        flat_idx = int(self.rng.integers(0, N_total))
        if flat_idx < self.n_plus:
            old_charge = +1.0
            new_charge = -1.0
            pool_old   = self._pos_plus
            pool_new   = self._pos_minus
            idx        = flat_idx
            delta_mu   = self.mu_minus - self.mu_plus
        else:
            old_charge = -1.0
            new_charge = +1.0
            pool_old   = self._pos_minus
            pool_new   = self._pos_plus
            idx        = flat_idx - self.n_plus
            delta_mu   = self.mu_plus - self.mu_minus

        pos = pool_old[idx]

        # Energy with all OTHER particles for old charge vs new charge
        if old_charge > 0:
            others_pos = [p for i, p in enumerate(self._pos_plus) if i != idx] + self._pos_minus
            others_q   = [+1.0] * (self.n_plus - 1) + [-1.0] * self.n_minus
        else:
            others_pos = self._pos_plus + [p for i, p in enumerate(self._pos_minus) if i != idx]
            others_q   = [+1.0] * self.n_plus + [-1.0] * (self.n_minus - 1)

        U_old = self._pair_energy_mimic(pos, old_charge, others_pos, others_q)
        U_new = self._pair_energy_mimic(pos, new_charge, others_pos, others_q)

        # Vext change
        dVext = (
            self._vext_energy(pos, new_charge, vext_plus_fn, vext_minus_fn, phi_fn)
            - self._vext_energy(pos, old_charge, vext_plus_fn, vext_minus_fn, phi_fn)
        )

        log_acc = delta_mu - self.beta * (U_new - U_old) - dVext
        if log_acc >= 0.0 or self.rng.random() < math.exp(log_acc):
            pool_old.pop(idx)
            pool_new.append(pos.copy())
            self.n_swap_accept += 1
            return True
        return False

    # ------------------------------------------------------------------
    # Sweep
    # ------------------------------------------------------------------

    def sweep(
        self,
        n_transitions: int = 100,
        insert_delete_prob: float = 0.3,
        swap_prob: float = 0.1,
        vext_plus_fn=None,
        vext_minus_fn=None,
        phi_fn=None,
    ) -> None:
        """
        Perform n_transitions MC attempts.

        Move fractions (approximate):
            - insert_delete_prob: split evenly among insert-+, del-+, insert--, del--
            - swap_prob: identity-swap moves
            - remaining: translation moves
        """
        move_prob   = max(0.0, 1.0 - insert_delete_prob - swap_prob)
        cum_ins_del = insert_delete_prob
        cum_swap    = cum_ins_del + swap_prob

        for _ in range(n_transitions):
            r = self.rng.random()
            if r < cum_ins_del:
                # Split among insert/delete and +/-
                r2 = self.rng.random()
                if r2 < 0.25:
                    self.trial_insert(+1.0, vext_plus_fn, vext_minus_fn, phi_fn)
                elif r2 < 0.50:
                    self.trial_delete(+1.0, vext_plus_fn, vext_minus_fn, phi_fn)
                elif r2 < 0.75:
                    self.trial_insert(-1.0, vext_plus_fn, vext_minus_fn, phi_fn)
                else:
                    self.trial_delete(-1.0, vext_plus_fn, vext_minus_fn, phi_fn)
            elif r < cum_swap:
                self.trial_swap(vext_plus_fn, vext_minus_fn, phi_fn)
            else:
                self.trial_move(
                    dx_max=0.1 * self.sigma,
                    vext_plus_fn=vext_plus_fn,
                    vext_minus_fn=vext_minus_fn,
                    phi_fn=phi_fn,
                )


# ---------------------------------------------------------------------------
# Convenience simulation driver
# ---------------------------------------------------------------------------

def simulate_rpm(
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
    n_equil: int = 5000,
    n_prod: int = 50000,
    rng=None,
) -> dict:
    """
    Run GCMC for the RPM mimic system and return z-resolved density profiles.

    Parameters
    ----------
    Lx, Ly, Lz : float
        Box dimensions in σ units.
    mu_plus, mu_minus : float
        β·μ for cations and anions.
    kappa : float, optional
        Screening parameter κ (1/σ). Default 1/1.8.
    sigma : float
        Hard-sphere diameter.
    beta : float
        Inverse temperature.
    vext_plus_fn : callable(z) -> β*V_ext for cations, optional
    vext_minus_fn : callable(z) -> β*V_ext for anions, optional
    phi_fn : callable(z) -> β*ϕ_R(z) external electrostatic, optional
    n_bins_z : int
        Number of z-histogram bins.
    n_equil : int
        Number of equilibration sweeps.
    n_prod : int
        Number of production sweeps.
    rng : np.random.Generator, optional

    Returns
    -------
    dict with keys:
        'z'         : np.ndarray (n_bins_z,)  — bin centres
        'rho_plus'  : np.ndarray (n_bins_z,)  — ρ₊(z)
        'rho_minus' : np.ndarray (n_bins_z,)  — ρ₋(z)
        'mu_plus'   : float  — β·μ₊ used
        'mu_minus'  : float  — β·μ₋ used
        'phi'       : np.ndarray (n_bins_z,)  — β·ϕ_R evaluated on z-grid (or zeros)
    """
    if rng is None:
        rng = np.random.default_rng()

    system = RPMSystem(
        Lx=Lx, Ly=Ly, Lz=Lz,
        mu_plus=mu_plus, mu_minus=mu_minus,
        kappa=kappa, sigma=sigma, beta=beta,
        rng=rng,
    )

    kwargs = dict(
        vext_plus_fn=vext_plus_fn,
        vext_minus_fn=vext_minus_fn,
        phi_fn=phi_fn,
    )

    # --- Equilibration ---
    for _ in range(n_equil):
        system.sweep(n_transitions=100, **kwargs)

    # --- Production with histogram accumulation ---
    z_min = system.z_wall
    z_max = Lz - system.z_wall
    z_edges = np.linspace(z_min, z_max, n_bins_z + 1)
    z_centers = 0.5 * (z_edges[:-1] + z_edges[1:])
    dz = z_edges[1] - z_edges[0]
    bin_vol = Lx * Ly * dz  # volume of each slab

    hist_plus  = np.zeros(n_bins_z, dtype=float)
    hist_minus = np.zeros(n_bins_z, dtype=float)

    for _ in range(n_prod):
        system.sweep(n_transitions=100, **kwargs)
        # Accumulate cations
        if system.n_plus > 0:
            pos_p = np.array(system._pos_plus)
            counts, _ = np.histogram(pos_p[:, 2], bins=z_edges)
            hist_plus += counts.astype(float)
        # Accumulate anions
        if system.n_minus > 0:
            pos_m = np.array(system._pos_minus)
            counts, _ = np.histogram(pos_m[:, 2], bins=z_edges)
            hist_minus += counts.astype(float)

    # Normalise: ρ(z) = <N_bin> / (bin_vol * n_prod)
    rho_plus  = hist_plus  / (n_prod * bin_vol)
    rho_minus = hist_minus / (n_prod * bin_vol)

    # Evaluate phi_fn on grid (for c₁ calculation)
    if phi_fn is not None:
        phi_vals = np.array([float(phi_fn(z)) for z in z_centers])
    else:
        phi_vals = np.zeros(n_bins_z)

    return {
        "z":         z_centers,
        "rho_plus":  rho_plus,
        "rho_minus": rho_minus,
        "mu_plus":   mu_plus,
        "mu_minus":  mu_minus,
        "phi":       phi_vals,
    }


# ---------------------------------------------------------------------------
# LMFT mean-field electrostatic potential
# ---------------------------------------------------------------------------

def lmft_potential(
    rho_charge_z: np.ndarray,
    z_centers: np.ndarray,
    kappa: float,
    Lz: float,
) -> np.ndarray:
    """
    Compute the LMFT mean-field electrostatic potential ϕ_MF(z).

    ϕ_MF(z) = ∫ ρ_charge(z') · v₁_planar(|z - z'|) dz'

    where ρ_charge(z) = ρ₊(z) - ρ₋(z) is the charge density profile, and
    v₁_planar is the planar projection of v₁(r) = erf(κr)/r:

        v₁_planar(Δz) ≈ (2π/κ²) · exp(-κ²·Δz²)

    (Gaussian approximation; exact result involves Dawson function.)

    Uses FFT convolution for efficiency.  The grid is assumed uniformly spaced.

    Parameters
    ----------
    rho_charge_z : np.ndarray (N,)
        Charge density profile ρ₊(z) - ρ₋(z).
    z_centers : np.ndarray (N,)
        z-bin centres (uniform spacing assumed).
    kappa : float
        Screening parameter κ (1/σ).
    Lz : float
        Box length in z (used for normalisation).

    Returns
    -------
    phi_mf : np.ndarray (N,)
        Mean-field electrostatic potential on the z-grid.
    """
    rho_charge_z = np.asarray(rho_charge_z, dtype=float)
    z_centers    = np.asarray(z_centers, dtype=float)
    N = len(z_centers)

    if N == 0:
        return np.zeros(0)

    dz = (z_centers[-1] - z_centers[0]) / max(N - 1, 1)

    # Build the kernel v₁_planar on a symmetric grid of length N
    # Use a distance grid centred at 0: delta_z in [-(N//2)*dz, (N//2)*dz]
    delta_z = np.fft.fftfreq(N, d=1.0 / N) * dz   # wraps correctly for FFT
    kernel = (2.0 * math.pi / kappa ** 2) * np.exp(-kappa ** 2 * delta_z ** 2)

    # FFT convolution (linear, not circular — zero-pad to avoid wrap-around)
    N2 = 2 * N
    phi_mf = np.real(
        np.fft.ifft(
            np.fft.fft(rho_charge_z, n=N2) * np.fft.fft(kernel, n=N2)
        )
    )[:N] * dz

    return phi_mf
