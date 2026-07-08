"""
particle_gcmc.py
================
General-purpose GCMC for any insertable particle: atom, molecule, or ion.

Works with an ASE MLIP calculator (fairchem, mace-torch, orb-models) and a
rigid host framework (or None for a pure fluid in a periodic box).

Particle type is inferred from the ASE Atoms object:
- 1 atom  → atom / ion mode: insertion + deletion + translation only
- N atoms → molecule mode: insertion + deletion + translation + rotation

Generates (ρ, c₁, V_ext) training triples in ionax-compatible units
(nanometres, dimensionless kT) via ``generate_cdft_training_data``.

References
----------
Sammüller et al., J. Phys.: Condens. Matter 36, 243002 (2024)
Bui & Cox, Phys. Rev. Lett. 134, 148001 (2025)
ionax — Poisson-Nernst-Planck + cDFT solver (Feugmo-Group/ionax)
"""

from __future__ import annotations

import math
import numpy as np
from typing import Optional, Callable, Sequence

# ASE imported lazily — this module can be *imported* without ASE installed,
# but calling any MLIP-backed method will raise ImportError at call time.
_KB_EV = 8.617333262e-5    # eV / K
_ANG_TO_NM = 0.1           # 1 Å = 0.1 nm
_EXP_CAP = 100.0           # overflow guard for log-domain acceptance


# ---------------------------------------------------------------------------
# Rotation helper
# ---------------------------------------------------------------------------

def _random_rotation_matrix(rng: np.random.Generator) -> np.ndarray:
    """Uniformly random 3×3 rotation matrix (Shoemake 1992)."""
    u1, u2, u3 = rng.uniform(0.0, 1.0, 3)
    q = np.array([
        math.sqrt(1 - u1) * math.sin(2 * math.pi * u2),
        math.sqrt(1 - u1) * math.cos(2 * math.pi * u2),
        math.sqrt(u1)     * math.sin(2 * math.pi * u3),
        math.sqrt(u1)     * math.cos(2 * math.pi * u3),
    ])
    w, x, y, z = q
    R = np.array([
        [1 - 2*(y*y + z*z),   2*(x*y - z*w),     2*(x*z + y*w)],
        [2*(x*y + z*w),       1 - 2*(x*x + z*z), 2*(y*z - x*w)],
        [2*(x*z - y*w),       2*(y*z + x*w),     1 - 2*(x*x + y*y)],
    ])
    return R


# ---------------------------------------------------------------------------
# Core simulation class
# ---------------------------------------------------------------------------

class ParticleGCMC:
    """
    Grand-canonical MC for an arbitrary insertable particle in a rigid host.

    Parameters
    ----------
    framework : ase.Atoms or None
        Rigid host structure (crystal, slab, …). Pass None for a pure fluid
        in a periodic box (cell must be set on `particle`).
    particle : ase.Atoms
        Prototype of the insertable particle. For atoms/ions use a single-atom
        Atoms; for molecules use a multi-atom Atoms centred at the origin.
    calculator
        ASE-compatible calculator (MACE, fairchem, orb-models, …).
    mu : float
        β·μ — chemical potential in kT units (dimensionless).
    T : float
        Temperature in Kelvin.
    sigma : float
        Hard-core radius in Å. Particle–particle contacts are rejected when
        the centre-of-mass distance < sigma. Particle–framework contacts use
        covalent radii from ASE.
    charge : float
        Net charge of the insertable particle (unused for energy — handled by
        the MLIP — but stored for bookkeeping and cross-validation with ionax).
    vext_fn : callable(positions: ndarray(N,3)) -> ndarray(N,) [eV], optional
        External potential evaluated on particle centres of mass (Å). Return
        value is in eV; internally multiplied by β.
    rng : np.random.Generator, optional
    """

    def __init__(
        self,
        framework,          # ase.Atoms or None
        particle,           # ase.Atoms
        calculator,
        mu: float,
        T: float,
        sigma: float = 1.4,
        charge: float = 0.0,
        vext_fn: Optional[Callable] = None,
        rng: Optional[np.random.Generator] = None,
    ):
        self._calc = calculator
        self._mu = float(mu)
        self._T = float(T)
        self._beta = 1.0 / (_KB_EV * self._T)
        self._sigma = float(sigma)
        self._charge = float(charge)
        self._vext_fn = vext_fn
        self._rng = rng if rng is not None else np.random.default_rng()

        # Lazy ASE import
        from ase.data import covalent_radii

        if framework is not None:
            self._framework = framework.copy()
            self._cell = np.array(framework.get_cell())
            self._frame_pos = framework.get_positions().copy()
            self._frame_radii = covalent_radii[framework.get_atomic_numbers()]
        else:
            # Pure fluid: cell comes from particle's cell
            self._framework = None
            self._cell = np.array(particle.get_cell())
            self._frame_pos = np.empty((0, 3))
            self._frame_radii = np.empty(0)

        self._cell_inv = np.linalg.inv(self._cell)
        self._V = abs(float(np.linalg.det(self._cell)))  # Å³

        # Prototype particle (centred at origin for molecules)
        self._particle = particle.copy()
        self._n_particle_atoms = len(particle)
        self._is_molecule = self._n_particle_atoms > 1
        if self._is_molecule:
            # Centre at origin
            com = particle.get_positions().mean(axis=0)
            self._particle_rel = particle.get_positions() - com  # (M, 3) relative
        else:
            self._particle_rel = np.zeros((1, 3))

        # Current particle centres-of-mass: list of (3,) arrays
        self._com_positions: list[np.ndarray] = []
        # Current particle orientations (rotation matrices): list of (3,3) for molecules
        self._orientations: list[np.ndarray] = []

        # Move acceptance counters
        self.n_insert_trial = 0
        self.n_insert_accept = 0
        self.n_delete_trial = 0
        self.n_delete_accept = 0
        self.n_translate_trial = 0
        self.n_translate_accept = 0
        self.n_rotate_trial = 0
        self.n_rotate_accept = 0

        # Compute initial energy (bare framework, zero particles)
        self._cached_energy: float = self._compute_energy()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def n_particles(self) -> int:
        return len(self._com_positions)

    @property
    def com_positions(self) -> np.ndarray:
        """Centre-of-mass positions, shape (N, 3) in Å."""
        if self._com_positions:
            return np.array(self._com_positions)
        return np.empty((0, 3))

    @property
    def V(self) -> float:
        """Accessible volume in Å³ (full cell)."""
        return self._V

    def acceptance_rates(self) -> dict:
        def _rate(acc, trial):
            return acc / trial if trial > 0 else float("nan")
        return {
            "insert":    _rate(self.n_insert_accept,    self.n_insert_trial),
            "delete":    _rate(self.n_delete_accept,    self.n_delete_trial),
            "translate": _rate(self.n_translate_accept, self.n_translate_trial),
            "rotate":    _rate(self.n_rotate_accept,    self.n_rotate_trial),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_pbc(self, pos: np.ndarray) -> np.ndarray:
        """Wrap a Cartesian position into the unit cell via fractional coords."""
        s = self._cell_inv @ pos
        s = s - np.floor(s)
        return self._cell @ s

    def _mic_dist(self, pos_a: np.ndarray, pos_b: np.ndarray) -> float:
        """Minimum-image Cartesian distance."""
        dr = pos_a - pos_b
        s = self._cell_inv @ dr
        s = s - np.round(s)
        return float(np.linalg.norm(self._cell @ s))

    def _hard_core_overlap(
        self,
        com_new: np.ndarray,
        exclude_idx: Optional[int] = None,
    ) -> bool:
        """Check hard-core overlap of a trial COM against existing particles and framework."""
        # Particle–particle
        for i, com_i in enumerate(self._com_positions):
            if i == exclude_idx:
                continue
            if self._mic_dist(com_new, com_i) < self._sigma:
                return True
        # Particle–framework (vectorised MIC)
        if len(self._frame_pos) > 0:
            dr = com_new[None, :] - self._frame_pos          # (n_frame, 3)
            s = (self._cell_inv @ dr.T).T
            s = s - np.round(s)
            dists = np.linalg.norm((self._cell @ s.T).T, axis=1)
            cutoffs = self._sigma + self._frame_radii
            if np.any(dists < cutoffs):
                return True
        return False

    def _particle_positions(
        self,
        com: np.ndarray,
        orientation: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Cartesian positions of all atoms in the particle given a COM and orientation."""
        if self._is_molecule:
            R = orientation if orientation is not None else np.eye(3)
            return com[None, :] + (R @ self._particle_rel.T).T
        return com[None, :]

    def _build_atoms(
        self,
        extra_com: Optional[np.ndarray] = None,
        extra_orient: Optional[np.ndarray] = None,
        exclude_idx: Optional[int] = None,
    ):
        """Build a combined ASE Atoms object (framework + current particles + optional extra)."""
        from ase import Atoms

        # Collect all particle positions
        all_pos = []
        all_num = []
        part_nums = list(self._particle.get_atomic_numbers())

        for i, (com_i, orient_i) in enumerate(
            zip(self._com_positions, self._orientations)
        ):
            if i == exclude_idx:
                continue
            pos_i = self._particle_positions(com_i, orient_i)
            all_pos.append(pos_i)
            all_num.extend(part_nums)

        if extra_com is not None:
            pos_extra = self._particle_positions(extra_com, extra_orient)
            all_pos.append(pos_extra)
            all_num.extend(part_nums)

        if self._framework is not None:
            base = self._framework.copy()
            if all_pos:
                guest_pos = np.vstack(all_pos)
                guest = Atoms(
                    numbers=all_num,
                    positions=guest_pos,
                    cell=base.get_cell(),
                    pbc=base.get_pbc(),
                )
                combined = base + guest
            else:
                combined = base
        else:
            if all_pos:
                guest_pos = np.vstack(all_pos)
                combined = Atoms(
                    numbers=all_num,
                    positions=guest_pos,
                    cell=self._cell,
                    pbc=True,
                )
            else:
                # Empty box — return a dummy with just the cell
                combined = Atoms(cell=self._cell, pbc=True)

        combined.calc = self._calc
        return combined

    def _compute_energy(
        self,
        extra_com: Optional[np.ndarray] = None,
        extra_orient: Optional[np.ndarray] = None,
        exclude_idx: Optional[int] = None,
    ) -> float:
        atoms = self._build_atoms(extra_com, extra_orient, exclude_idx)
        return float(atoms.get_potential_energy())

    def _vext_energy(self, com: np.ndarray) -> float:
        """External potential energy at COM in eV (returns 0 if no vext_fn)."""
        if self._vext_fn is None:
            return 0.0
        return float(self._vext_fn(com[None, :])[0])

    def _accept(self, log_acc: float) -> bool:
        if log_acc >= _EXP_CAP:
            return True
        if log_acc < -_EXP_CAP:
            return False
        return self._rng.random() < math.exp(log_acc)

    # ------------------------------------------------------------------
    # Grand-canonical moves
    # ------------------------------------------------------------------

    def trial_insert(self) -> bool:
        """Attempt a grand-canonical insertion at a uniformly random position."""
        self.n_insert_trial += 1

        # Random COM in the unit cell
        s = self._rng.uniform(0.0, 1.0, 3)
        com_new = self._cell @ s

        if self._hard_core_overlap(com_new):
            return False

        orient_new = _random_rotation_matrix(self._rng) if self._is_molecule else None

        vext = self._vext_energy(com_new)
        U_old = self._cached_energy
        U_new = self._compute_energy(extra_com=com_new, extra_orient=orient_new)

        N_new = self.n_particles + 1
        # log acc = log(V / N_new) + β·μ − β·ΔU − β·V_ext
        log_acc = (
            math.log(self._V / N_new)
            + self._mu
            - self._beta * (U_new - U_old)
            - self._beta * vext
        )

        if self._accept(log_acc):
            self._com_positions.append(com_new)
            self._orientations.append(orient_new)
            self._cached_energy = U_new
            self.n_insert_accept += 1
            return True
        return False

    def trial_delete(self) -> bool:
        """Attempt a grand-canonical deletion of a randomly chosen particle."""
        self.n_delete_trial += 1
        N_old = self.n_particles
        if N_old == 0:
            return False

        idx = int(self._rng.integers(0, N_old))
        com_del = self._com_positions[idx]
        orient_del = self._orientations[idx]

        vext = self._vext_energy(com_del)
        U_old = self._cached_energy
        U_new = self._compute_energy(exclude_idx=idx)

        # log acc = log(N_old / V) − β·μ + β·ΔU_del + β·V_ext
        # ΔU_del = U(N-1) - U(N) = U_new - U_old  (negative = energetically favourable)
        log_acc = (
            math.log(N_old / self._V)
            - self._mu
            - self._beta * (U_new - U_old)
            + self._beta * vext
        )

        if self._accept(log_acc):
            self._com_positions.pop(idx)
            self._orientations.pop(idx)
            self._cached_energy = U_new
            self.n_delete_accept += 1
            return True
        return False

    def trial_translate(self, dx_max: float = 0.5) -> bool:
        """Attempt a random displacement of a randomly chosen particle."""
        self.n_translate_trial += 1
        if self.n_particles == 0:
            return False

        idx = int(self._rng.integers(0, self.n_particles))
        com_old = self._com_positions[idx].copy()
        orient = self._orientations[idx]

        disp = self._rng.uniform(-dx_max, dx_max, 3)
        com_new = self._apply_pbc(com_old + disp)

        if self._hard_core_overlap(com_new, exclude_idx=idx):
            return False

        vext_old = self._vext_energy(com_old)
        vext_new = self._vext_energy(com_new)

        # Build trial atoms with particle idx moved to com_new
        # Strategy: exclude idx, add com_new as extra
        U_old = self._cached_energy
        U_new = self._compute_energy(
            extra_com=com_new, extra_orient=orient, exclude_idx=idx
        )

        log_acc = (
            -self._beta * (U_new - U_old)
            - self._beta * (vext_new - vext_old)
        )

        if self._accept(log_acc):
            self._com_positions[idx] = com_new
            self._cached_energy = U_new
            self.n_translate_accept += 1
            return True
        return False

    def trial_rotate(self) -> bool:
        """Attempt a random rotation of a randomly chosen molecule (no-op for atoms)."""
        if not self._is_molecule:
            return False
        self.n_rotate_trial += 1
        if self.n_particles == 0:
            return False

        idx = int(self._rng.integers(0, self.n_particles))
        com = self._com_positions[idx]
        orient_old = self._orientations[idx]
        orient_new = _random_rotation_matrix(self._rng)

        # Hard-core: rotation changes atom positions, check overlap
        # (COM unchanged, so particle–particle centre-of-mass check is same;
        #  we skip the hard-core check here — atom-level overlap is handled by MLIP)

        U_old = self._cached_energy
        U_new = self._compute_energy(
            extra_com=com, extra_orient=orient_new, exclude_idx=idx
        )

        log_acc = -self._beta * (U_new - U_old)

        if self._accept(log_acc):
            self._orientations[idx] = orient_new
            self._cached_energy = U_new
            self.n_rotate_accept += 1
            return True
        return False

    # ------------------------------------------------------------------
    # Sweep
    # ------------------------------------------------------------------

    def sweep(
        self,
        n_transitions: int = 100,
        insert_delete_prob: float = 0.4,
        rotate_prob: float = 0.1,
        dx_max: float = 0.5,
    ) -> None:
        """
        Perform n_transitions MC attempts.

        Move fractions (approximate):
            insert_delete_prob : split evenly insert/delete
            rotate_prob        : rotation (molecules only; skipped for atoms)
            remaining          : translation
        """
        for _ in range(n_transitions):
            r = self._rng.random()
            if r < insert_delete_prob / 2:
                self.trial_insert()
            elif r < insert_delete_prob:
                self.trial_delete()
            elif self._is_molecule and r < insert_delete_prob + rotate_prob:
                self.trial_rotate()
            else:
                self.trial_translate(dx_max=dx_max)


# ---------------------------------------------------------------------------
# Convenience simulation driver
# ---------------------------------------------------------------------------

def simulate_particle_gcmc(
    framework,
    particle,
    calculator,
    mu: float,
    T: float,
    sigma: float = 1.4,
    charge: float = 0.0,
    vext_fn: Optional[Callable] = None,
    n_bins_z: int = 100,
    n_equil: int = 1_000,
    n_prod: int = 10_000,
    dx_max: float = 0.5,
    insert_delete_prob: float = 0.4,
    n_transitions: int = 100,
    rng: Optional[np.random.Generator] = None,
) -> dict:
    """
    Equilibrate a ``ParticleGCMC`` system and accumulate a z-resolved density.

    Works for any particle type (atom, ion, molecule).

    Parameters
    ----------
    framework : ase.Atoms or None
        Rigid host. None for pure fluid.
    particle : ase.Atoms
        Prototype insertable particle.
    calculator
        ASE MLIP calculator.
    mu : float
        β·μ (dimensionless chemical potential).
    T : float
        Temperature in K.
    sigma : float
        Hard-core COM-to-COM cutoff in Å.
    charge : float
        Particle charge (for bookkeeping).
    vext_fn : callable(pos: ndarray(N,3)) -> ndarray(N,) [eV], optional
        External potential on particle COMs.
    n_bins_z : int
        Number of z-histogram bins.
    n_equil, n_prod : int
        Equilibration / production sweeps.
    dx_max : float
        Max displacement in Å.
    insert_delete_prob : float
        Fraction of moves that are insertion/deletion.
    n_transitions : int
        MC attempts per sweep.
    rng : np.random.Generator, optional

    Returns
    -------
    dict with keys:
        'z_centers' : ndarray (n_bins_z,) Å
        'rho'       : ndarray (n_bins_z,) Å⁻³ — density profile
        'mu'        : float — β·μ used
        'T'         : float — temperature K
        'avg_n'     : float — mean particle count
        'n_trace'   : ndarray (n_prod,) — particle count per step
        'system'    : ParticleGCMC — for further analysis
    """
    if rng is None:
        rng = np.random.default_rng()

    system = ParticleGCMC(
        framework=framework,
        particle=particle,
        calculator=calculator,
        mu=mu,
        T=T,
        sigma=sigma,
        charge=charge,
        vext_fn=vext_fn,
        rng=rng,
    )

    sweep_kw = dict(
        n_transitions=n_transitions,
        insert_delete_prob=insert_delete_prob,
        dx_max=dx_max,
    )

    for _ in range(n_equil):
        system.sweep(**sweep_kw)

    # z histogram
    cell_z = float(np.linalg.norm(system._cell[2]))  # Å
    Lx = float(np.linalg.norm(system._cell[0]))
    Ly = float(np.linalg.norm(system._cell[1]))
    z_edges = np.linspace(0.0, cell_z, n_bins_z + 1)
    z_centers = 0.5 * (z_edges[:-1] + z_edges[1:])
    dz = z_edges[1] - z_edges[0]
    bin_vol = Lx * Ly * dz  # Å³

    hist = np.zeros(n_bins_z, dtype=np.float64)
    n_trace = np.zeros(n_prod, dtype=np.int32)

    for step in range(n_prod):
        system.sweep(**sweep_kw)
        n_trace[step] = system.n_particles
        if system.n_particles > 0:
            coms = system.com_positions  # (N, 3)
            z_vals = coms[:, 2] % cell_z
            counts, _ = np.histogram(z_vals, bins=z_edges)
            hist += counts.astype(np.float64)

    rho = hist / (n_prod * bin_vol)

    return {
        "z_centers": z_centers,
        "rho":       rho,
        "mu":        mu,
        "T":         T,
        "avg_n":     float(n_trace.mean()),
        "n_trace":   n_trace,
        "system":    system,
    }


# ---------------------------------------------------------------------------
# Training data generator (ionax-compatible format)
# ---------------------------------------------------------------------------

def generate_cdft_training_data(
    framework,
    particle,
    calculator,
    mu_values: Sequence[float],
    T: float,
    vext_fns: Optional[Sequence[Optional[Callable]]] = None,
    sigma: float = 1.4,
    charge: float = 0.0,
    n_bins_z: int = 100,
    n_equil: int = 1_000,
    n_prod: int = 10_000,
    dx_max: float = 0.5,
    insert_delete_prob: float = 0.4,
    n_transitions: int = 100,
    rho_min: float = 1e-12,
    rng: Optional[np.random.Generator] = None,
) -> list[dict]:
    """
    Generate (ρ, c₁, V_ext) training triples for a neural cDFT functional.

    Runs GCMC for each (mu, vext_fn) pair and computes c₁ via the
    Sammüller identity:

        c₁(z) = ln ρ(z) − β·μ_loc(z)
               = ln ρ(z) − mu + β·V_ext(z)

    where V_ext(z) is in eV and β = 1/(kB·T) in eV⁻¹.

    Output is in **ionax units**:
        - positions / lengths in nm (1 Å = 0.1 nm)
        - densities in nm⁻³ (1 Å⁻³ = 1000 nm⁻³)
        - c₁ is dimensionless (kT units)
        - V_ext in kT units (β·V_ext)

    This matches ionax's ``Grid`` convention (lx, ly, lz in nm) and the
    ``ExcessFreeEnergy.chemical_potential`` sign convention (μ_ex = −c₁_ex).

    Parameters
    ----------
    framework : ase.Atoms or None
    particle  : ase.Atoms
    calculator
        ASE MLIP calculator.
    mu_values : sequence of float
        β·μ values to sample.
    T : float
        Temperature in K.
    vext_fns : sequence of callables or None, optional
        External potential functions (eV). Defaults to [None] (no external field).
    sigma, charge, n_bins_z, n_equil, n_prod, dx_max,
    insert_delete_prob, n_transitions, rho_min : see ``simulate_particle_gcmc``.
    rng : np.random.Generator, optional

    Returns
    -------
    list of dict, one per (mu, vext_fn) pair:
        'z_nm'       : ndarray (n_bins_z,) — z-centres in nm
        'rho_nm3'    : ndarray (n_bins_z,) — density in nm⁻³
        'c1'         : ndarray (n_bins_z,) — one-body DCF (dimensionless)
        'vext_kT'    : ndarray (n_bins_z,) — β·V_ext (dimensionless)
        'mu'         : float   — β·μ used
        'T'          : float   — temperature in K
        'avg_n'      : float   — mean particle count
    """
    if vext_fns is None:
        vext_fns = [None]
    if rng is None:
        rng = np.random.default_rng()

    beta = 1.0 / (_KB_EV * T)
    samples = []

    for mu in mu_values:
        for vext_fn in vext_fns:
            result = simulate_particle_gcmc(
                framework=framework,
                particle=particle,
                calculator=calculator,
                mu=mu,
                T=T,
                sigma=sigma,
                charge=charge,
                vext_fn=vext_fn,
                n_bins_z=n_bins_z,
                n_equil=n_equil,
                n_prod=n_prod,
                dx_max=dx_max,
                insert_delete_prob=insert_delete_prob,
                n_transitions=n_transitions,
                rng=rng,
            )

            z_ang = result["z_centers"]          # Å
            rho_ang3 = result["rho"]             # Å⁻³

            # Evaluate V_ext on z-grid (eV)
            if vext_fn is not None:
                pos_grid = np.zeros((n_bins_z, 3))
                pos_grid[:, 2] = z_ang
                vext_ev = np.asarray(vext_fn(pos_grid), dtype=float)
            else:
                vext_ev = np.zeros(n_bins_z)

            vext_kT = beta * vext_ev  # dimensionless

            # Sammüller c₁: c₁(z) = ln(ρ) − μ + β·V_ext
            rho_safe = np.maximum(rho_ang3, rho_min)
            c1 = np.log(rho_safe) - mu + vext_kT

            samples.append({
                "z_nm":    z_ang * _ANG_TO_NM,
                "rho_nm3": rho_ang3 / (_ANG_TO_NM ** 3),  # Å⁻³ → nm⁻³
                "c1":      c1,
                "vext_kT": vext_kT,
                "mu":      mu,
                "T":       T,
                "avg_n":   result["avg_n"],
            })

    return samples
