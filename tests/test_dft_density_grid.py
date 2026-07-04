"""Tests for mlip_mc.dft.density_grid."""
import numpy as np
import pytest
from mlip_mc.dft.density_grid import DensityGrid1D, DensityGrid3D
from mlip_mc.dft.external_field import LinearRamp


class TestDensityGrid1D:
    @pytest.fixture
    def grid(self):
        return DensityGrid1D(box_z=20.0, n_bins=100, n_blocks=5, xy_area=400.0)

    def test_init(self, grid):
        assert grid.n_bins == 100
        assert len(grid.z_centers) == 100
        assert np.isclose(grid.z_centers[-1], 20.0 - 0.1)  # last bin centre

    def test_accumulate_shape(self, grid):
        pos = np.random.default_rng(0).uniform(0, 20, size=(30, 3))
        grid.accumulate(pos, steps_per_block=100)
        rho, std = grid.density()
        assert rho.shape == (100,)
        assert std.shape == (100,)

    def test_density_nonnegative(self, grid):
        pos = np.random.default_rng(1).uniform(0, 20, size=(50, 3))
        for _ in range(10):
            grid.accumulate(pos, steps_per_block=2)
        rho, _ = grid.density()
        assert (rho >= 0).all()

    def test_pbc_wrapping(self, grid):
        """Particles just above box_z should wrap to bin 0."""
        pos = np.array([[0.0, 0.0, 20.5]])  # outside — wraps to ~0.5
        grid.accumulate(pos, steps_per_block=100)
        rho, _ = grid.density()
        # Bin 0 (z ∈ [0, 0.2]) should have some density
        assert rho[0] > 0 or rho[1] > 0 or rho[2] > 0  # rough check

    def test_c1_formula(self, grid):
        """c1 = ln(rho) - beta*mu + beta*V_ext should hold element-wise."""
        pos = np.random.default_rng(2).uniform(1, 19, size=(200, 3))
        for _ in range(20):
            grid.accumulate(pos, steps_per_block=4)
        mu, T = -0.2, 300.0
        beta = 1.0 / (8.617e-5 * T)
        v_ext = LinearRamp(axis=2, slope=0.0)  # zero field → simple ideal gas test
        v_ext_grid = grid.v_ext_on_grid(v_ext)
        c1_mean, _ = grid.c1(mu, beta, v_ext_grid)
        rho_mean, _ = grid.density()
        # Where density > 0, verify the identity
        mask = rho_mean > 1e-6
        expected = np.log(rho_mean[mask]) - beta * mu + beta * v_ext_grid[mask]
        np.testing.assert_allclose(c1_mean[mask], expected, rtol=1e-5)

    def test_results_keys(self, grid):
        pos = np.random.rand(10, 3) * 20
        grid.accumulate(pos, steps_per_block=10)
        res = grid.results(mu=-0.1, beta=38.68)
        required = {'z', 'rho', 'rho_stderr', 'c1', 'c1_stderr', 'v_ext',
                    'n_bins', 'dz', 'box_z', 'xy_area', 'n_blocks', 'total_steps'}
        assert required.issubset(res.keys())

    def test_reset(self, grid):
        pos = np.random.rand(20, 3) * 20
        grid.accumulate(pos, steps_per_block=10)
        grid.reset()
        rho, _ = grid.density()
        np.testing.assert_allclose(rho, 0.0)


class TestDensityGrid3D:
    @pytest.fixture
    def grid3d(self):
        return DensityGrid3D(box=np.array([10.0, 10.0, 10.0]),
                             n_bins=(16, 16, 16), n_blocks=5)

    def test_density_shape(self, grid3d):
        pos = np.random.default_rng(0).uniform(0, 10, size=(30, 3))
        for _ in range(5):
            grid3d.accumulate(pos, steps_per_block=1)
        rho, std = grid3d.density()
        assert rho.shape == (16, 16, 16)
        assert std.shape == (16, 16, 16)

    def test_density_nonnegative(self, grid3d):
        pos = np.random.rand(50, 3) * 10
        for _ in range(5):
            grid3d.accumulate(pos, steps_per_block=1)
        rho, _ = grid3d.density()
        assert (rho >= 0).all()

    def test_grid_centers(self, grid3d):
        x, y, z = grid3d.grid_centers()
        assert len(x) == 16
        assert np.isclose(x[0], 10.0 / 32)   # first bin centre
