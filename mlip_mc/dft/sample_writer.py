"""
HDF5 sample writer for cDFT neural-operator training data.

Schema (one file per GCMC run):
    /metadata/           (attrs: T, mu, box, n_prod_steps, seed, framework_id,
                                 adsorbate, backend, git_sha, timestamp)
    /grid/z              float32 (n_bins,)   — bin centres [Å]
    /fields/rho          float32 (n_bins,)   — ρ(z) [Å⁻³]
    /fields/rho_stderr   float32 (n_bins,)
    /fields/c1           float32 (n_bins,)   — c⁽¹⁾(z)
    /fields/c1_stderr    float32 (n_bins,)
    /fields/v_ext        float32 (n_bins,)   — V_ext(z) [eV]
    /stats/total_steps   int64
    /stats/n_blocks      int64
    /stats/n_bins        int64

The schema is intentionally aligned with ionax's results.npz keys
(rho_plus → rho, potential → v_ext, x → z) for easy cross-loading.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

try:
    import h5py
    _H5PY = True
except ImportError:
    _H5PY = False


class SampleWriter:
    """
    Write one HDF5 sample file per GCMC run.

    Parameters
    ----------
    output_dir : str or Path
        Directory where sample files are written.
    run_id : str
        Unique identifier for this run (e.g. "run_0042").
    compress : bool
        Enable gzip compression for array datasets.
    """

    def __init__(
        self,
        output_dir: Union[str, Path],
        run_id: str,
        compress: bool = True,
    ) -> None:
        if not _H5PY:
            raise ImportError(
                "h5py is required to write samples: pip install h5py"
            )
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.compress = compress

    @property
    def path(self) -> Path:
        return self.output_dir / f"{self.run_id}.h5"

    def write(
        self,
        grid_results: dict,
        metadata: dict,
    ) -> Path:
        """
        Write one sample to HDF5.

        Parameters
        ----------
        grid_results : dict
            Output of DensityGrid1D.results() — contains rho, c1, v_ext,
            z, rho_stderr, c1_stderr, total_steps, n_blocks, n_bins, dz,
            box_z, xy_area.
        metadata : dict
            Simulation metadata: T, mu, box [Lx,Ly,Lz], seed, framework_id,
            adsorbate, backend, n_prod_steps, v_ext_spec (JSON string).

        Returns
        -------
        Path to the written file.
        """
        kwargs = {"compression": "gzip", "compression_opts": 4} if self.compress else {}

        with h5py.File(self.path, "w") as f:
            # ── metadata ────────────────────────────────────────────────────
            grp_meta = f.create_group("metadata")
            grp_meta.attrs["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            for k, v in metadata.items():
                if isinstance(v, (list, np.ndarray)):
                    grp_meta.attrs[k] = np.asarray(v).tolist()
                else:
                    grp_meta.attrs[k] = v

            # ── grid ────────────────────────────────────────────────────────
            grp_grid = f.create_group("grid")
            grp_grid.create_dataset("z", data=grid_results["z"].astype(np.float32), **kwargs)
            grp_grid["z"].attrs["units"] = "Angstrom"

            # ── fields ──────────────────────────────────────────────────────
            grp_fields = f.create_group("fields")
            _write = lambda name, arr, units="": (
                grp_fields.create_dataset(name, data=arr.astype(np.float32), **kwargs),
                grp_fields[name].attrs.update({"units": units}),
            )
            _write("rho",        grid_results["rho"],        "Angstrom^-3")
            _write("rho_stderr", grid_results["rho_stderr"], "Angstrom^-3")
            _write("c1",         grid_results["c1"],         "dimensionless")
            _write("c1_stderr",  grid_results["c1_stderr"],  "dimensionless")
            _write("v_ext",      grid_results["v_ext"],      "eV")

            # ── stats ────────────────────────────────────────────────────────
            grp_stats = f.create_group("stats")
            grp_stats.attrs["total_steps"] = int(grid_results["total_steps"])
            grp_stats.attrs["n_blocks"]    = int(grid_results["n_blocks"])
            grp_stats.attrs["n_bins"]      = int(grid_results["n_bins"])
            grp_stats.attrs["dz_angstrom"] = float(grid_results["dz"])
            grp_stats.attrs["box_z"]       = float(grid_results["box_z"])
            grp_stats.attrs["xy_area"]     = float(grid_results["xy_area"])

        return self.path


def load_sample(path: Union[str, Path]) -> dict:
    """
    Read an HDF5 sample back into numpy arrays.

    Returns a flat dict with keys: z, rho, rho_stderr, c1, c1_stderr,
    v_ext, metadata (dict), stats (dict).
    """
    if not _H5PY:
        raise ImportError("h5py is required: pip install h5py")
    result = {}
    with h5py.File(path, "r") as f:
        result["z"]          = f["grid/z"][:]
        result["rho"]        = f["fields/rho"][:]
        result["rho_stderr"] = f["fields/rho_stderr"][:]
        result["c1"]         = f["fields/c1"][:]
        result["c1_stderr"]  = f["fields/c1_stderr"][:]
        result["v_ext"]      = f["fields/v_ext"][:]
        result["metadata"]   = dict(f["metadata"].attrs)
        result["stats"]      = dict(f["stats"].attrs)
    return result
