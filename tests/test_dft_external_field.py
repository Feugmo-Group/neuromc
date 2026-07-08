"""Tests for neuromc.dft.external_field."""
import numpy as np
import pytest
from neuromc.dft.external_field import (
    HardWall, LinearRamp, GaussianPocket, Sinusoid, FourierSeries,
    CompositeField, random_fourier_field, from_dict,
)


@pytest.fixture
def pos():
    rng = np.random.default_rng(42)
    return rng.uniform(0, 20, size=(50, 3))


class TestHardWall:
    def test_shape(self, pos):
        wall = HardWall(axis=2, z_lo=0.0, z_hi=20.0)
        result = wall(pos)
        assert result.shape == (50,)

    def test_repulsive_near_wall(self):
        wall = HardWall(axis=2, z_lo=0.0, z_hi=20.0, strength=1.0)
        close_pos = np.array([[0.0, 0.0, 0.01]])
        far_pos = np.array([[0.0, 0.0, 10.0]])
        assert wall(close_pos)[0] > wall(far_pos)[0]

    def test_total_energy(self, pos):
        wall = HardWall()
        assert isinstance(wall.total_energy(pos), float)


class TestLinearRamp:
    def test_linear_in_axis(self):
        ramp = LinearRamp(axis=2, slope=1.0)
        pos = np.array([[0, 0, 5.0], [0, 0, 10.0]])
        np.testing.assert_allclose(ramp(pos), [5.0, 10.0])

    def test_zero_slope(self, pos):
        ramp = LinearRamp(axis=2, slope=0.0)
        np.testing.assert_allclose(ramp(pos), 0.0)


class TestGaussianPocket:
    def test_maximum_at_center(self):
        g = GaussianPocket(center=np.array([10, 10, 10]), amplitude=-1.0, sigma=2.0)
        center_pos = np.array([[10, 10, 10]])
        off_pos = np.array([[10, 10, 15]])
        assert g(center_pos)[0] < g(off_pos)[0]   # negative amplitude → more negative at center

    def test_shape(self, pos):
        g = GaussianPocket()
        assert g(pos).shape == (50,)


class TestSinusoid:
    def test_amplitude(self):
        s = Sinusoid(axis=2, amplitude=0.5, frequency=1.0 / 20.0, phase=0.0)
        pos = np.array([[0, 0, 0.0]])
        np.testing.assert_allclose(s(pos)[0], 0.0, atol=1e-12)

    def test_shape(self, pos):
        s = Sinusoid()
        assert s.shape(pos) if hasattr(s, 'shape') else s(pos).shape == (50,)


class TestFourierSeries:
    def test_zero_amplitudes(self):
        f = FourierSeries(amplitudes=np.zeros(4), phases=np.zeros(4), L=20.0)
        pos = np.random.rand(10, 3) * 20
        np.testing.assert_allclose(f(pos), 0.0)

    def test_shape(self, pos):
        f = FourierSeries(n_modes=4, amplitudes=np.ones(4) * 0.1,
                          phases=np.zeros(4), L=20.0)
        assert f(pos).shape == (50,)

    def test_single_mode_matches_sinusoid(self):
        A, phi, L = 0.1, 0.5, 20.0
        f = FourierSeries(n_modes=1, amplitudes=np.array([A]), phases=np.array([phi]), L=L)
        s = Sinusoid(axis=2, amplitude=A, frequency=1.0 / L, phase=phi)
        pos = np.random.default_rng(0).uniform(0, L, size=(20, 3))
        np.testing.assert_allclose(f(pos), s(pos), atol=1e-12)


class TestCompositeField:
    def test_additivity(self, pos):
        a = LinearRamp(axis=2, slope=0.1)
        b = LinearRamp(axis=2, slope=0.2)
        c = CompositeField([a, b])
        np.testing.assert_allclose(c(pos), a(pos) + b(pos))

    def test_add_operator(self, pos):
        a = LinearRamp(axis=2, slope=0.1)
        b = LinearRamp(axis=2, slope=0.2)
        c = a + b
        assert isinstance(c, CompositeField)
        np.testing.assert_allclose(c(pos), a(pos) + b(pos))


class TestRandomFourierField:
    def test_returns_fourier_series(self):
        f = random_fourier_field(n_modes=4, L=20.0)
        assert isinstance(f, FourierSeries)

    def test_different_seeds_differ(self):
        f1 = random_fourier_field(rng=np.random.default_rng(1))
        f2 = random_fourier_field(rng=np.random.default_rng(2))
        assert not np.allclose(f1.amplitudes, f2.amplitudes)

    def test_same_seed_reproducible(self):
        f1 = random_fourier_field(rng=np.random.default_rng(0))
        f2 = random_fourier_field(rng=np.random.default_rng(0))
        np.testing.assert_array_equal(f1.amplitudes, f2.amplitudes)


class TestFromDict:
    def test_hard_wall(self, pos):
        f = from_dict({'type': 'hard_wall', 'axis': 2, 'z_lo': 0.0,
                       'z_hi': 20.0, 'strength': 1000.0})
        assert f(pos).shape == (50,)

    def test_linear_ramp(self, pos):
        f = from_dict({'type': 'linear_ramp', 'axis': 1, 'slope': 0.05})
        np.testing.assert_allclose(f(pos), 0.05 * pos[:, 1])

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match='Unknown V_ext primitive'):
            from_dict({'type': 'nonexistent'})
