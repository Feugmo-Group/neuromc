"""Tests for neuromc.dft.widom."""
import math
import numpy as np
import pytest

from neuromc.dft.hard_rod_sim import HardRodSystem
from neuromc.dft.rpm_sim import RPMSystem
from neuromc.dft.widom import (
    WidomHardRod,
    WidomRPM,
    widom_hard_rod,
    widom_rpm,
)


# ---------------------------------------------------------------------------
# WidomHardRod
# ---------------------------------------------------------------------------

class TestWidomHardRod:
    def _make_empty_system(self, L=10.0, mu=-2.0):
        rng = np.random.default_rng(42)
        return HardRodSystem(L=L, mu=mu, rng=rng)

    def _make_dilute_system(self, L=20.0, mu=-3.0):
        """Few particles — high free volume."""
        rng = np.random.default_rng(0)
        sys = HardRodSystem(L=L, mu=mu, rng=rng)
        for _ in range(200):
            sys.sweep()
        return sys

    def test_output_keys(self):
        sys = self._make_empty_system()
        widom = WidomHardRod(sys, n_bins=50)
        result = widom.run(n_insertions=100, rng=np.random.default_rng(1))
        for key in ("mu_ex", "henry", "free_volume_fraction", "x_centers", "insertion_profile"):
            assert key in result

    def test_empty_system_free_volume_one(self):
        """Empty box: every insertion succeeds → free_volume = 1."""
        sys = self._make_empty_system()
        widom = WidomHardRod(sys, n_bins=50)
        result = widom.run(n_insertions=500, rng=np.random.default_rng(2))
        assert result["free_volume_fraction"] == pytest.approx(1.0)

    def test_empty_system_mu_ex_zero(self):
        """Empty box: μ_ex = 0 (no interactions)."""
        sys = self._make_empty_system()
        widom = WidomHardRod(sys, n_bins=50)
        result = widom.run(n_insertions=500, rng=np.random.default_rng(3))
        assert result["mu_ex"] == pytest.approx(0.0, abs=1e-10)

    def test_full_system_free_volume_low(self):
        """Packed system: free volume < 0.5."""
        rng = np.random.default_rng(10)
        sys = HardRodSystem(L=5.0, mu=3.0, rng=rng)  # high mu → dense
        for _ in range(2000):
            sys.sweep()
        widom = WidomHardRod(sys, n_bins=50)
        result = widom.run(n_insertions=2000, rng=rng)
        assert result["free_volume_fraction"] < 0.5

    def test_henry_equals_free_volume(self):
        """For hard rods henry = P(no overlap) = free_volume_fraction."""
        sys = self._make_dilute_system()
        widom = WidomHardRod(sys, n_bins=50)
        result = widom.run(n_insertions=500, rng=np.random.default_rng(5))
        assert result["henry"] == pytest.approx(result["free_volume_fraction"])

    def test_mu_ex_equals_minus_log_henry(self):
        sys = self._make_dilute_system()
        widom = WidomHardRod(sys, n_bins=50)
        result = widom.run(n_insertions=500, rng=np.random.default_rng(6))
        if result["henry"] > 0:
            expected = -math.log(result["henry"])
            assert result["mu_ex"] == pytest.approx(expected, rel=1e-6)

    def test_output_shapes(self):
        sys = self._make_empty_system()
        n_bins = 30
        widom = WidomHardRod(sys, n_bins=n_bins)
        result = widom.run(n_insertions=100, rng=np.random.default_rng(7))
        assert result["x_centers"].shape == (n_bins,)
        assert result["insertion_profile"].shape == (n_bins,)

    def test_insertion_profile_non_negative(self):
        sys = self._make_dilute_system()
        widom = WidomHardRod(sys, n_bins=40)
        result = widom.run(n_insertions=300, rng=np.random.default_rng(8))
        assert np.all(result["insertion_profile"] >= 0.0)


# ---------------------------------------------------------------------------
# widom_hard_rod convenience driver
# ---------------------------------------------------------------------------

class TestWidomHardRodDriver:
    def test_returns_dict(self):
        result = widom_hard_rod(
            L=10.0, mu=-1.0, T=1.0,
            n_equil=100, n_prod=200, n_insertions_per_step=5,
            n_bins=50, rng=np.random.default_rng(20),
        )
        assert isinstance(result, dict)

    def test_bulk_mu_ex_positive(self):
        """Hard rods at finite density: μ_ex > 0 (free volume < 1)."""
        result = widom_hard_rod(
            L=10.0, mu=0.0, T=1.0,
            n_equil=200, n_prod=500, n_insertions_per_step=10,
            n_bins=50, rng=np.random.default_rng(21),
        )
        assert result["mu_ex"] >= 0.0

    def test_rho_and_profile_shapes_match(self):
        n_bins = 40
        result = widom_hard_rod(
            L=10.0, mu=-1.0,
            n_equil=100, n_prod=200, n_insertions_per_step=5,
            n_bins=n_bins, rng=np.random.default_rng(22),
        )
        assert result["rho"].shape == (n_bins,)
        assert result["insertion_profile"].shape == (n_bins,)
        assert result["x_centers"].shape == (n_bins,)


# ---------------------------------------------------------------------------
# WidomRPM
# ---------------------------------------------------------------------------

class TestWidomRPM:
    def _make_empty_rpm(self):
        rng = np.random.default_rng(99)
        return RPMSystem(Lx=5.0, Ly=5.0, Lz=10.0, mu_plus=-5.0, mu_minus=-5.0, rng=rng)

    def _make_dilute_rpm(self):
        rng = np.random.default_rng(77)
        sys = RPMSystem(Lx=5.0, Ly=5.0, Lz=10.0, mu_plus=-3.0, mu_minus=-3.0, rng=rng)
        for _ in range(50):
            sys.sweep(n_transitions=20)
        return sys

    def test_output_keys(self):
        sys = self._make_empty_rpm()
        widom = WidomRPM(sys, n_bins_z=20)
        result = widom.run(n_insertions=50, rng=np.random.default_rng(100))
        for key in ("mu_ex_plus", "mu_ex_minus", "henry_plus", "henry_minus",
                    "z_centers", "profile_plus", "profile_minus"):
            assert key in result

    def test_empty_system_henry_near_one(self):
        """Empty system: no pair interactions → henry ≈ 1."""
        sys = self._make_empty_rpm()
        widom = WidomRPM(sys, n_bins_z=20)
        result = widom.run(n_insertions=200, rng=np.random.default_rng(101))
        assert result["henry_plus"]  == pytest.approx(1.0, abs=0.05)
        assert result["henry_minus"] == pytest.approx(1.0, abs=0.05)

    def test_empty_system_mu_ex_near_zero(self):
        sys = self._make_empty_rpm()
        widom = WidomRPM(sys, n_bins_z=20)
        result = widom.run(n_insertions=200, rng=np.random.default_rng(102))
        assert result["mu_ex_plus"]  == pytest.approx(0.0, abs=0.1)
        assert result["mu_ex_minus"] == pytest.approx(0.0, abs=0.1)

    def test_output_shapes(self):
        sys = self._make_empty_rpm()
        n_bins = 15
        widom = WidomRPM(sys, n_bins_z=n_bins)
        result = widom.run(n_insertions=50, rng=np.random.default_rng(103))
        assert result["z_centers"].shape    == (n_bins,)
        assert result["profile_plus"].shape  == (n_bins,)
        assert result["profile_minus"].shape == (n_bins,)

    def test_profiles_non_negative(self):
        sys = self._make_dilute_rpm()
        widom = WidomRPM(sys, n_bins_z=20)
        result = widom.run(n_insertions=100, rng=np.random.default_rng(104))
        assert np.all(result["profile_plus"]  >= 0.0)
        assert np.all(result["profile_minus"] >= 0.0)

    def test_mu_ex_minus_log_henry_consistency(self):
        sys = self._make_dilute_rpm()
        widom = WidomRPM(sys, n_bins_z=20)
        result = widom.run(n_insertions=200, rng=np.random.default_rng(105))
        for label in ("plus", "minus"):
            h = result[f"henry_{label}"]
            mu = result[f"mu_ex_{label}"]
            if h > 0:
                assert mu == pytest.approx(-math.log(h), rel=1e-6)


# ---------------------------------------------------------------------------
# widom_rpm convenience driver
# ---------------------------------------------------------------------------

class TestWidomRPMDriver:
    def test_returns_dict_with_density(self):
        result = widom_rpm(
            Lx=4.0, Ly=4.0, Lz=8.0,
            mu_plus=-4.0, mu_minus=-4.0,
            n_equil=50, n_prod=100, n_insertions_per_step=5,
            n_bins_z=20, rng=np.random.default_rng(200),
        )
        for key in ("rho_plus", "rho_minus", "z_centers",
                    "mu_ex_plus", "mu_ex_minus"):
            assert key in result

    def test_density_non_negative(self):
        result = widom_rpm(
            Lx=4.0, Ly=4.0, Lz=8.0,
            mu_plus=-4.0, mu_minus=-4.0,
            n_equil=50, n_prod=100, n_insertions_per_step=5,
            n_bins_z=20, rng=np.random.default_rng(201),
        )
        assert np.all(result["rho_plus"]  >= 0.0)
        assert np.all(result["rho_minus"] >= 0.0)

    def test_shapes_consistent(self):
        n_bins = 25
        result = widom_rpm(
            Lx=4.0, Ly=4.0, Lz=8.0,
            mu_plus=-4.0, mu_minus=-4.0,
            n_equil=50, n_prod=100, n_insertions_per_step=5,
            n_bins_z=n_bins, rng=np.random.default_rng(202),
        )
        for key in ("z_centers", "rho_plus", "rho_minus",
                    "profile_plus", "profile_minus"):
            assert result[key].shape == (n_bins,), key
