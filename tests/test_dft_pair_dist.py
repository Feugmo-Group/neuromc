"""Tests for mlip_mc.dft.pair_dist."""
import numpy as np
import pytest
from mlip_mc.dft.pair_dist import PairDistBulk, PairDistPlanar


class TestPairDistBulk:
    @pytest.fixture
    def acc(self):
        return PairDistBulk(r_max=8.0, n_bins=200, n_frame=0)

    def _fake_atoms(self, n_ads, box=20.0, n_frame=0):
        """Return a minimal mock with the interface accumulate() needs."""
        rng = np.random.default_rng(42)
        pos = rng.uniform(1, box - 1, size=(n_frame + n_ads, 3))
        cell = np.diag([box, box, box])
        total = n_frame + n_ads

        class _Atoms:
            def __len__(self):
                return total

            def get_positions(self):
                return pos

            def get_cell(self):
                return cell

        return _Atoms()

    def test_gr_shape(self, acc):
        atoms = self._fake_atoms(20)
        acc.accumulate(atoms)
        r, g = acc.gr(rho_bulk=0.01)
        assert r.shape == (200,)
        assert g.shape == (200,)

    def test_gr_nonnegative(self, acc):
        atoms = self._fake_atoms(30)
        for _ in range(5):
            acc.accumulate(atoms)
        _, g = acc.gr(rho_bulk=0.01)
        assert (g >= 0).all()

    def test_gr_zero_before_accumulate(self, acc):
        _, g = acc.gr(rho_bulk=0.01)
        np.testing.assert_array_equal(g, 0.0)

    def test_gr_ideal_gas(self):
        """For an ideal gas, g(r) ≈ 1 in the bulk."""
        rng = np.random.default_rng(0)
        n_ads, box = 200, 30.0
        acc = PairDistBulk(r_max=10.0, n_bins=300, n_frame=0)

        class _Atoms:
            def __len__(self):
                return n_ads

            def get_positions(self):
                return rng.uniform(0, box, size=(n_ads, 3))

            def get_cell(self):
                return np.diag([box, box, box])

        for _ in range(50):
            acc.accumulate(_Atoms())

        rho_bulk = n_ads / box**3
        r, g = acc.gr(rho_bulk)
        # mid-range bins (2–8 Å) should average to ~1 for ideal gas
        mask = (r > 2.0) & (r < 8.0)
        assert abs(g[mask].mean() - 1.0) < 0.15

    def test_skip_single_particle(self, acc):
        """Frames with fewer than 2 adsorbates are skipped."""
        atoms = self._fake_atoms(1)
        acc.accumulate(atoms)
        assert acc._n_frames == 0

    def test_n_frame_excludes_framework(self):
        """n_frame framework atoms should not appear in pairs."""
        rng = np.random.default_rng(7)
        n_frame = 5
        n_ads = 10
        pos = rng.uniform(0, 20, size=(n_frame + n_ads, 3))
        cell = np.diag([20.0, 20.0, 20.0])

        class _Atoms:
            def __len__(self):
                return n_frame + n_ads

            def get_positions(self):
                return pos

            def get_cell(self):
                return cell

        acc = PairDistBulk(r_max=8.0, n_bins=100, n_frame=n_frame)
        acc.accumulate(_Atoms())
        assert acc._n_particles_sum == n_ads

    def test_structure_factor_shape(self, acc):
        atoms = self._fake_atoms(20)
        for _ in range(3):
            acc.accumulate(atoms)
        k, Sk = acc.structure_factor(rho_bulk=0.01, k_max=10.0, n_k=50)
        assert k.shape == (50,)
        assert Sk.shape == (50,)

    def test_structure_factor_low_k_limit(self):
        """S(k→0) should be finite and positive."""
        rng = np.random.default_rng(1)
        n_ads, box = 100, 25.0
        acc = PairDistBulk(r_max=10.0, n_bins=300, n_frame=0)

        class _Atoms:
            def __len__(self):
                return n_ads

            def get_positions(self):
                return rng.uniform(0, box, size=(n_ads, 3))

            def get_cell(self):
                return np.diag([box, box, box])

        for _ in range(30):
            acc.accumulate(_Atoms())

        k, Sk = acc.structure_factor(rho_bulk=n_ads / box**3, n_k=50)
        assert Sk[0] > 0


class TestPairDistPlanar:
    @pytest.fixture
    def acc(self):
        return PairDistPlanar(box_z=20.0, n_bins=50, n_frame=0)

    def _make_atoms(self, n_ads, n_frame=0, box_z=20.0):
        rng = np.random.default_rng(3)
        total = n_frame + n_ads
        pos = rng.uniform(0, box_z, size=(total, 3))

        class _Atoms:
            def __len__(self):
                return total

            def get_positions(self):
                return pos

        return _Atoms()

    def test_g_zz_shape(self, acc):
        atoms = self._make_atoms(30)
        for _ in range(5):
            acc.accumulate(atoms)
        rho_z = np.ones(50) * 0.01
        g = acc.g_zz(rho_z)
        assert g.shape == (50, 50)

    def test_g_zz_nonnegative(self, acc):
        atoms = self._make_atoms(30)
        for _ in range(5):
            acc.accumulate(atoms)
        rho_z = np.ones(50) * 0.01
        g = acc.g_zz(rho_z)
        assert (g >= 0).all()

    def test_g_zz_zero_before_accumulate(self, acc):
        g = acc.g_zz(np.ones(50))
        np.testing.assert_array_equal(g, 0.0)

    def test_symmetry(self, acc):
        """g(z1, z2) should be symmetric."""
        rng = np.random.default_rng(5)
        n_ads = 30

        class _Atoms:
            def get_positions(self):
                return rng.uniform(0, 20, size=(n_ads, 3))

        for _ in range(10):
            acc.accumulate(_Atoms())

        rho_z = np.ones(50) * 0.005
        g = acc.g_zz(rho_z)
        np.testing.assert_allclose(g, g.T, atol=1e-12)

    def test_skip_single_particle(self, acc):
        atoms = self._make_atoms(1)
        acc.accumulate(atoms)
        assert acc._n_frames == 0
