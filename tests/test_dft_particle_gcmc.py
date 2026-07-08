"""
Tests for neuromc.dft.particle_gcmc.

Uses a minimal LinearEnergyCalc (ASE Calculator subclass) that returns
energy = e_framework + n_particle * e_per_particle, so acceptance
probabilities are deterministic and easy to reason about.
"""
import math
import numpy as np
import pytest

pytest.importorskip("ase", reason="ase not installed")

from ase import Atoms
from ase.calculators.calculator import Calculator, all_changes

from neuromc.dft.particle_gcmc import (
    ParticleGCMC,
    simulate_particle_gcmc,
    generate_cdft_training_data,
    _random_rotation_matrix,
    _KB_EV,
    _ANG_TO_NM,
)


# ---------------------------------------------------------------------------
# Mock calculator
# ---------------------------------------------------------------------------

class LinearEnergyCalc(Calculator):
    """
    ASE Calculator that returns:
        E = e_framework + n_Li * e_per_particle

    where n_Li is counted by atomic number 3 (Li).
    Deterministic — no randomness, no ML model needed.
    """
    implemented_properties = ["energy"]

    def __init__(self, e_framework: float = -10.0, e_per_particle: float = -0.1):
        super().__init__()
        self.e_framework = e_framework
        self.e_per_particle = e_per_particle

    def calculate(self, atoms=None, properties=("energy",), system_changes=all_changes):
        n_p = int(np.sum(atoms.numbers == 3))  # count Li
        self.results = {"energy": self.e_framework + n_p * self.e_per_particle}


def _make_framework(L: float = 10.0) -> Atoms:
    """Simple cubic box with a few framework atoms (not Li)."""
    return Atoms(
        "NaF",
        positions=[[L / 4, L / 4, L / 4], [3 * L / 4, 3 * L / 4, 3 * L / 4]],
        cell=[[L, 0, 0], [0, L, 0], [0, 0, L]],
        pbc=True,
    )


def _make_li_atom() -> Atoms:
    """Single Li atom at origin."""
    return Atoms("Li", positions=[[0, 0, 0]])


def _make_li2_molecule() -> Atoms:
    """Li₂ dimer as a toy molecule."""
    return Atoms("LiLi", positions=[[-0.5, 0, 0], [0.5, 0, 0]])


def _make_system(L=10.0, mu=-1.0, T=300.0, sigma=1.4, rng_seed=42):
    fw = _make_framework(L)
    particle = _make_li_atom()
    calc = LinearEnergyCalc(e_framework=-10.0, e_per_particle=-0.1)
    rng = np.random.default_rng(rng_seed)
    return ParticleGCMC(
        framework=fw, particle=particle, calculator=calc,
        mu=mu, T=T, sigma=sigma, rng=rng,
    )


# ---------------------------------------------------------------------------
# _random_rotation_matrix
# ---------------------------------------------------------------------------

class TestRandomRotation:
    def test_orthogonal(self):
        rng = np.random.default_rng(0)
        R = _random_rotation_matrix(rng)
        assert R.shape == (3, 3)
        np.testing.assert_allclose(R @ R.T, np.eye(3), atol=1e-12)

    def test_determinant_one(self):
        rng = np.random.default_rng(1)
        R = _random_rotation_matrix(rng)
        assert math.isclose(np.linalg.det(R), 1.0, abs_tol=1e-12)

    def test_distinct_each_call(self):
        rng = np.random.default_rng(2)
        R1 = _random_rotation_matrix(rng)
        R2 = _random_rotation_matrix(rng)
        assert not np.allclose(R1, R2)


# ---------------------------------------------------------------------------
# ParticleGCMC — atom mode (Li)
# ---------------------------------------------------------------------------

class TestParticleGCMCAtom:
    def test_init_no_particles(self):
        sys = _make_system()
        assert sys.n_particles == 0

    def test_is_not_molecule(self):
        sys = _make_system()
        assert not sys._is_molecule

    def test_initial_energy_cached(self):
        sys = _make_system()
        # Framework has 2 atoms (Na, F), no Li — energy should be e_framework
        assert math.isfinite(sys._cached_energy)

    def test_trial_insert_high_mu_accepts(self):
        """Very large mu → insertion almost always accepted."""
        sys = _make_system(mu=100.0)
        accepted = sum(sys.trial_insert() for _ in range(50))
        assert accepted > 0

    def test_trial_insert_very_low_mu_rejects(self):
        """Very negative mu → insertions mostly rejected."""
        sys = _make_system(mu=-100.0)
        accepted = sum(sys.trial_insert() for _ in range(50))
        assert accepted < 10  # stochastic but should be rare

    def test_trial_delete_empty_returns_false(self):
        sys = _make_system()
        result = sys.trial_delete()
        assert result is False

    def test_insert_delete_recovers_zero_particles(self):
        """Insert then force-delete until empty."""
        sys = _make_system(mu=50.0, rng_seed=7)
        # Force an insertion
        for _ in range(100):
            if sys.trial_insert():
                break
        assert sys.n_particles >= 1
        # Force deletions
        sys._mu = -100.0
        for _ in range(200):
            sys.trial_delete()
        assert sys.n_particles == 0

    def test_translate_preserves_n_particles(self):
        sys = _make_system(mu=50.0, rng_seed=8)
        for _ in range(100):
            sys.trial_insert()
        n_before = sys.n_particles
        for _ in range(50):
            sys.trial_translate(dx_max=0.2)
        assert sys.n_particles == n_before

    def test_rotate_is_noop_for_atom(self):
        """trial_rotate should return False for single-atom particle."""
        sys = _make_system(mu=50.0)
        for _ in range(20):
            sys.trial_insert()
        result = sys.trial_rotate()
        assert result is False

    def test_energy_cache_updated_after_insert(self):
        sys = _make_system(mu=50.0, rng_seed=9)
        E_before = sys._cached_energy
        for _ in range(100):
            if sys.trial_insert():
                break
        # Energy should have changed
        assert sys._cached_energy != E_before

    def test_acceptance_rates_keys(self):
        sys = _make_system()
        rates = sys.acceptance_rates()
        for key in ("insert", "delete", "translate", "rotate"):
            assert key in rates

    def test_com_positions_shape(self):
        sys = _make_system(mu=50.0, rng_seed=10)
        for _ in range(100):
            sys.trial_insert()
        coms = sys.com_positions
        assert coms.ndim == 2
        assert coms.shape[1] == 3
        assert coms.shape[0] == sys.n_particles

    def test_trial_insert_counter(self):
        sys = _make_system()
        for _ in range(10):
            sys.trial_insert()
        assert sys.n_insert_trial == 10

    def test_trial_delete_counter(self):
        sys = _make_system()
        for _ in range(5):
            sys.trial_delete()
        assert sys.n_delete_trial == 5

    def test_sweep_runs_without_error(self):
        sys = _make_system(mu=0.0)
        sys.sweep(n_transitions=50)


# ---------------------------------------------------------------------------
# ParticleGCMC — molecule mode (Li₂)
# ---------------------------------------------------------------------------

class TestParticleGCMCMolecule:
    def _make_mol_system(self, mu=0.0, rng_seed=42):
        fw = _make_framework(L=15.0)
        particle = _make_li2_molecule()
        calc = LinearEnergyCalc(e_framework=-10.0, e_per_particle=-0.1)
        rng = np.random.default_rng(rng_seed)
        return ParticleGCMC(
            framework=fw, particle=particle, calculator=calc,
            mu=mu, T=300.0, sigma=2.0, rng=rng,
        )

    def test_is_molecule(self):
        sys = self._make_mol_system()
        assert sys._is_molecule

    def test_particle_rel_shape(self):
        sys = self._make_mol_system()
        assert sys._particle_rel.shape == (2, 3)

    def test_insert_adds_both_atoms(self):
        """Inserting a Li₂ dimer should appear in the built Atoms object."""
        sys = self._make_mol_system(mu=100.0)
        for _ in range(50):
            if sys.trial_insert():
                break
        atoms = sys._build_atoms()
        n_li = int(np.sum(atoms.numbers == 3))
        assert n_li == 2 * sys.n_particles

    def test_rotate_changes_orientation(self):
        sys = self._make_mol_system(mu=100.0, rng_seed=5)
        for _ in range(50):
            if sys.trial_insert():
                break
        assert sys.n_particles >= 1
        orient_before = sys._orientations[0].copy()
        for _ in range(100):
            sys.trial_rotate()
        # After many rotations, orientation should have changed
        assert not np.allclose(sys._orientations[0], orient_before)

    def test_rotate_counter(self):
        sys = self._make_mol_system(mu=100.0)
        for _ in range(50):
            sys.trial_insert()
        for _ in range(20):
            sys.trial_rotate()
        assert sys.n_rotate_trial == 20

    def test_sweep_molecule(self):
        sys = self._make_mol_system(mu=0.0)
        sys.sweep(n_transitions=100)


# ---------------------------------------------------------------------------
# ParticleGCMC — no framework (pure fluid)
# ---------------------------------------------------------------------------

class TestParticleGCMCPureFluid:
    def test_no_framework_insert(self):
        L = 10.0
        particle = Atoms("Li", positions=[[0, 0, 0]], cell=[[L, 0, 0], [0, L, 0], [0, 0, L]], pbc=True)
        calc = LinearEnergyCalc(e_framework=0.0, e_per_particle=-0.05)
        rng = np.random.default_rng(99)
        sys = ParticleGCMC(
            framework=None, particle=particle, calculator=calc,
            mu=2.0, T=300.0, sigma=1.0, rng=rng,
        )
        accepted = sum(sys.trial_insert() for _ in range(50))
        assert accepted >= 0  # just check it runs

    def test_no_framework_no_hard_core_against_frame(self):
        L = 10.0
        particle = Atoms("Li", positions=[[0, 0, 0]], cell=[[L, 0, 0], [0, L, 0], [0, 0, L]], pbc=True)
        calc = LinearEnergyCalc()
        sys = ParticleGCMC(framework=None, particle=particle, calculator=calc,
                           mu=0.0, T=300.0, sigma=0.5)
        # Inserting at a specific position should not trigger framework overlap
        com = np.array([5.0, 5.0, 5.0])
        assert not sys._hard_core_overlap(com)


# ---------------------------------------------------------------------------
# simulate_particle_gcmc — integration
# ---------------------------------------------------------------------------

class TestSimulateParticleGCMC:
    def test_returns_dict_with_keys(self):
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        result = simulate_particle_gcmc(
            framework=fw, particle=particle, calculator=calc,
            mu=0.0, T=300.0, sigma=1.4,
            n_equil=5, n_prod=10, n_transitions=5, n_bins_z=20,
            rng=np.random.default_rng(0),
        )
        for key in ("z_centers", "rho", "mu", "T", "avg_n", "n_trace", "system"):
            assert key in result

    def test_shapes_consistent(self):
        n_bins = 15
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        result = simulate_particle_gcmc(
            framework=fw, particle=particle, calculator=calc,
            mu=0.0, T=300.0, n_equil=5, n_prod=20,
            n_transitions=5, n_bins_z=n_bins,
            rng=np.random.default_rng(1),
        )
        assert result["z_centers"].shape == (n_bins,)
        assert result["rho"].shape == (n_bins,)
        assert result["n_trace"].shape == (20,)

    def test_rho_non_negative(self):
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        result = simulate_particle_gcmc(
            framework=fw, particle=particle, calculator=calc,
            mu=0.0, T=300.0, n_equil=5, n_prod=20, n_transitions=5,
            rng=np.random.default_rng(2),
        )
        assert np.all(result["rho"] >= 0.0)

    def test_avg_n_matches_trace(self):
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        result = simulate_particle_gcmc(
            framework=fw, particle=particle, calculator=calc,
            mu=0.0, T=300.0, n_equil=5, n_prod=20, n_transitions=5,
            rng=np.random.default_rng(3),
        )
        assert result["avg_n"] == pytest.approx(result["n_trace"].mean())


# ---------------------------------------------------------------------------
# generate_cdft_training_data — ionax-compatible output
# ---------------------------------------------------------------------------

class TestGenerateCDFTTrainingData:
    def test_returns_list(self):
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        samples = generate_cdft_training_data(
            framework=fw, particle=particle, calculator=calc,
            mu_values=[-1.0], T=300.0,
            n_equil=5, n_prod=10, n_transitions=5, n_bins_z=20,
            rng=np.random.default_rng(10),
        )
        assert isinstance(samples, list)
        assert len(samples) == 1

    def test_multiple_mu_values(self):
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        samples = generate_cdft_training_data(
            framework=fw, particle=particle, calculator=calc,
            mu_values=[-1.0, 0.0, 1.0], T=300.0,
            n_equil=5, n_prod=10, n_transitions=5, n_bins_z=20,
            rng=np.random.default_rng(11),
        )
        assert len(samples) == 3

    def test_keys_present(self):
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        samples = generate_cdft_training_data(
            framework=fw, particle=particle, calculator=calc,
            mu_values=[-1.0], T=300.0,
            n_equil=5, n_prod=10, n_transitions=5, n_bins_z=20,
            rng=np.random.default_rng(12),
        )
        for key in ("z_nm", "rho_nm3", "c1", "vext_kT", "mu", "T", "avg_n"):
            assert key in samples[0]

    def test_units_conversion(self):
        """z should be in nm and rho in nm⁻³ (not Å units)."""
        L_ang = 8.0
        fw = _make_framework(L=L_ang)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        samples = generate_cdft_training_data(
            framework=fw, particle=particle, calculator=calc,
            mu_values=[-1.0], T=300.0,
            n_equil=5, n_prod=10, n_transitions=5, n_bins_z=20,
            rng=np.random.default_rng(13),
        )
        s = samples[0]
        # z in nm: max should be ~ L_ang * 0.1 = 0.8 nm
        assert s["z_nm"].max() < L_ang * _ANG_TO_NM * 1.1

    def test_c1_sammüller_identity(self):
        """c₁ = ln(ρ_ang3) - mu + beta*V_ext must hold."""
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        mu_val = 0.0
        T_val = 300.0
        beta = 1.0 / (_KB_EV * T_val)
        samples = generate_cdft_training_data(
            framework=fw, particle=particle, calculator=calc,
            mu_values=[mu_val], T=T_val,
            n_equil=5, n_prod=20, n_transitions=5, n_bins_z=20,
            rho_min=1e-12,
            rng=np.random.default_rng(14),
        )
        s = samples[0]
        # rho_nm3 → rho_ang3
        rho_ang3 = s["rho_nm3"] * (_ANG_TO_NM ** 3)
        vext_kT = s["vext_kT"]  # = beta * V_ext_eV = 0 here (no vext_fn)
        rho_safe = np.maximum(rho_ang3, 1e-12)
        c1_expected = np.log(rho_safe) - mu_val + vext_kT
        np.testing.assert_allclose(s["c1"], c1_expected, rtol=1e-6)

    def test_vext_fn_applied(self):
        """With a vext_fn, vext_kT should be non-zero."""
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        T_val = 300.0
        beta = 1.0 / (_KB_EV * T_val)

        def vext(pos):  # pos: (N,3) Å → returns (N,) eV
            return 0.1 * np.ones(len(pos))

        samples = generate_cdft_training_data(
            framework=fw, particle=particle, calculator=calc,
            mu_values=[-1.0], T=T_val,
            vext_fns=[vext],
            n_equil=5, n_prod=10, n_transitions=5, n_bins_z=20,
            rng=np.random.default_rng(15),
        )
        s = samples[0]
        # vext_kT = beta * 0.1 everywhere
        np.testing.assert_allclose(s["vext_kT"], beta * 0.1, rtol=1e-6)

    def test_vext_none_gives_zero_vext_kT(self):
        fw = _make_framework(L=8.0)
        particle = _make_li_atom()
        calc = LinearEnergyCalc()
        samples = generate_cdft_training_data(
            framework=fw, particle=particle, calculator=calc,
            mu_values=[-1.0], T=300.0, vext_fns=[None],
            n_equil=5, n_prod=10, n_transitions=5, n_bins_z=20,
            rng=np.random.default_rng(16),
        )
        np.testing.assert_allclose(samples[0]["vext_kT"], 0.0)
