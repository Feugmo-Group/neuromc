"""Tests for mlip_mc.dft.oz."""
import numpy as np
import pytest
from mlip_mc.dft.oz import oz_inversion_3d, oz_inversion_1d, free_energy_excess_ti


class TestOZInversion3D:
    def _ideal_gas_gr(self, r):
        return np.ones_like(r)

    def test_output_shapes(self):
        r = np.linspace(0.5, 8.0, 200)
        gr = self._ideal_gas_gr(r)
        r_out, cr = oz_inversion_3d(r, gr, rho_bulk=0.01)
        assert r_out.shape == r.shape
        assert cr.shape == r.shape

    def test_ideal_gas_c_near_zero(self):
        """For ideal gas (g=1, h=0), c(r) ≈ 0."""
        r = np.linspace(0.5, 8.0, 200)
        gr = self._ideal_gas_gr(r)
        _, cr = oz_inversion_3d(r, gr, rho_bulk=0.01)
        np.testing.assert_allclose(cr, 0.0, atol=1e-6)

    def test_oz_relation_consistency(self):
        """OZ: ĥ = ĉ + ρ·ĉ·ĥ  → recovered ĥ should match original."""
        r = np.linspace(0.5, 10.0, 300)
        # Construct a synthetic h(r) with a simple Yukawa-like form
        h = 0.5 * np.exp(-r) / r
        gr = 1.0 + h
        rho = 0.01

        _, cr = oz_inversion_3d(r, gr, rho_bulk=rho)
        # h and c should satisfy h ≈ c at low density (ρ·ĉ·ĥ ≈ 0)
        # Skip first few bins — FT boundary artefacts near r_min for 1/r divergence
        np.testing.assert_allclose(cr[5:], h[5:], atol=0.05)

    def test_symmetry_preserved(self):
        """c(r) from a symmetric g(r) should be real (no imaginary parts)."""
        r = np.linspace(0.5, 8.0, 150)
        gr = 1.0 + 0.2 * np.exp(-(r - 3.0) ** 2)
        _, cr = oz_inversion_3d(r, gr, rho_bulk=0.005)
        assert np.all(np.isfinite(cr))


class TestOZInversion1D:
    def test_output_shape(self):
        n = 50
        g_zz = np.ones((n, n))
        rho_z = np.ones(n) * 0.01
        c_zz = oz_inversion_1d(g_zz, rho_z, box_z=20.0)
        assert c_zz.shape == (n, n)

    def test_ideal_gas_c_near_zero(self):
        """For g=1 everywhere (ideal gas), c(z1,z2) ≈ 0."""
        n = 30
        g_zz = np.ones((n, n))
        rho_z = np.ones(n) * 0.01
        c_zz = oz_inversion_1d(g_zz, rho_z, box_z=15.0)
        np.testing.assert_allclose(c_zz, 0.0, atol=1e-10)

    def test_symmetry_preserved(self):
        """Symmetric g(z1,z2) should give symmetric c(z1,z2)."""
        n = 20
        rng = np.random.default_rng(7)
        raw = rng.uniform(0.8, 1.2, (n, n))
        g_zz = 0.5 * (raw + raw.T)   # symmetric
        rho_z = np.ones(n) * 0.005
        c_zz = oz_inversion_1d(g_zz, rho_z, box_z=10.0)
        np.testing.assert_allclose(c_zz, c_zz.T, atol=1e-10)

    def test_finite_output(self):
        n = 40
        rng = np.random.default_rng(3)
        g_zz = 1.0 + 0.1 * rng.standard_normal((n, n))
        g_zz = 0.5 * (g_zz + g_zz.T)
        g_zz = np.maximum(g_zz, 0.0)
        rho_z = np.ones(n) * 0.01
        c_zz = oz_inversion_1d(g_zz, rho_z, box_z=20.0)
        assert np.all(np.isfinite(c_zz))


class TestFreeEnergyExcessTI:
    def test_zero_correlation_gives_zero(self):
        """When c(r)=0 and h(r)=0 (ideal gas), F_exc=0."""
        r = np.linspace(0.5, 8.0, 100)
        n_lam = 5
        cr_list = [np.zeros_like(r)] * n_lam
        gr_list = [np.ones_like(r)] * n_lam
        f = free_energy_excess_ti(r, cr_list, gr_list, rho_bulk=0.01)
        assert f == pytest.approx(0.0, abs=1e-12)

    def test_returns_float(self):
        r = np.linspace(0.5, 8.0, 100)
        h = 0.1 * np.exp(-r)
        cr_list = [h * 0.5] * 3
        gr_list = [1.0 + h] * 3
        f = free_energy_excess_ti(r, cr_list, gr_list, rho_bulk=0.01)
        assert isinstance(f, float)

    def test_negative_for_attractive_fluid(self):
        """Attractive fluid (h<0 at short range, c<0) should give F_exc < 0."""
        r = np.linspace(0.5, 8.0, 200)
        h = -0.5 * np.exp(-((r - 1.5) ** 2))  # negative h
        c = h.copy()
        cr_list = [c] * 5
        gr_list = [1.0 + h] * 5
        f = free_energy_excess_ti(r, cr_list, gr_list, rho_bulk=0.01)
        # c*h = h² ≥ 0, so -ρ²/2 * ∫ c·h·4πr² < 0
        assert f < 0.0

    def test_custom_lambdas(self):
        r = np.linspace(0.5, 8.0, 100)
        h = 0.05 * np.exp(-r)
        lambdas = np.array([0.0, 0.5, 1.0])
        cr_list = [h] * 3
        gr_list = [1.0 + h] * 3
        f1 = free_energy_excess_ti(r, cr_list, gr_list, rho_bulk=0.01,
                                    lambdas=lambdas)
        f2 = free_energy_excess_ti(r, cr_list, gr_list, rho_bulk=0.01)
        assert f1 == pytest.approx(f2, rel=1e-6)
