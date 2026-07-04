"""Tests for mlip_mc.dft.sample_writer (HDF5 I/O)."""
import numpy as np
import pytest
import tempfile
from pathlib import Path

try:
    import h5py
    _H5PY = True
except ImportError:
    _H5PY = False

from mlip_mc.dft.density_grid import DensityGrid1D
from mlip_mc.dft.external_field import random_fourier_field


@pytest.mark.skipif(not _H5PY, reason="h5py not installed")
class TestSampleWriter:
    @pytest.fixture
    def sample_data(self):
        """Generate a minimal grid result dict."""
        grid = DensityGrid1D(box_z=20.0, n_bins=50, n_blocks=5, xy_area=400.0)
        rng = np.random.default_rng(0)
        pos = rng.uniform(1, 19, size=(30, 3))
        for _ in range(10):
            grid.accumulate(pos, steps_per_block=2)
        v_ext = random_fourier_field(n_modes=4, L=20.0, rng=rng)
        return grid.results(mu=-0.2, beta=38.68, external_field=v_ext), v_ext

    def test_write_and_load(self, sample_data, tmp_path):
        from mlip_mc.dft.sample_writer import SampleWriter, load_sample
        grid_results, v_ext = sample_data

        writer = SampleWriter(output_dir=tmp_path, run_id="test_run_000")
        path = writer.write(
            grid_results=grid_results,
            metadata={'T': 300.0, 'mu': -0.2, 'beta': 38.68,
                      'box': [20.0, 20.0, 20.0], 'adsorbate': 'Ar',
                      'v_ext_spec': '{}'},
        )
        assert path.exists()

        sample = load_sample(path)
        assert sample['rho'].shape == (50,)
        assert sample['c1'].shape == (50,)
        assert sample['v_ext'].shape == (50,)
        assert sample['z'].shape == (50,)
        assert 'T' in sample['metadata']
        assert sample['metadata']['T'] == pytest.approx(300.0)

    def test_file_named_correctly(self, sample_data, tmp_path):
        from mlip_mc.dft.sample_writer import SampleWriter
        grid_results, _ = sample_data
        writer = SampleWriter(tmp_path, run_id="myrun_042")
        path = writer.write(grid_results=grid_results, metadata={'T': 300.0, 'mu': 0.0})
        assert path.name == "myrun_042.h5"

    def test_arrays_are_float32(self, sample_data, tmp_path):
        from mlip_mc.dft.sample_writer import SampleWriter, load_sample
        grid_results, _ = sample_data
        writer = SampleWriter(tmp_path, run_id="dtype_test")
        path = writer.write(grid_results=grid_results, metadata={'T': 300.0, 'mu': 0.0})
        sample = load_sample(path)
        assert sample['rho'].dtype == np.float32
        assert sample['c1'].dtype == np.float32

    def test_missing_h5py_raises(self, monkeypatch):
        import mlip_mc.dft.sample_writer as sw
        monkeypatch.setattr(sw, '_H5PY', False)
        with pytest.raises(ImportError, match='h5py'):
            sw.SampleWriter('/tmp', 'test')
