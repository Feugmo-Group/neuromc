"""
GCMCCampaign: sweep over (μ, T, V_ext) configurations and write one
HDF5 sample per run.

The three learnable operators this dataset supports:
  G₁: V_ext(r) → ρ(r)                          (forward DFT problem)
  G₂: ρ(r)     → c⁽¹⁾(r)   [= δF_exc/δρ]       (neural functional)
  G₃: c⁽¹⁾(r)  → F_exc       (thermodynamic integration)

G₁ and G₂ are trained directly from (v_ext, rho, c1) triples in each sample.
G₃ requires additional thermodynamic-integration logic (planned in mlip_mc/dft/ti.py).

Campaign YAML schema (see configs/campaign_sammuller.yaml):
  temperature: 300.0         # K  (or list for sweep)
  mu_values: [-0.5, -0.3, -0.1, 0.1]   # eV
  n_runs: 50                 # random V_ext draws per (T, μ)
  n_equilibration_steps: 5000
  n_production_steps: 20000
  n_blocks: 10
  grid:
    n_bins: 200
    axis: 2                  # project onto z
  v_ext:
    type: fourier            # random Fourier draw; or composite
    n_modes: 4
    amplitude_scale: 0.1     # eV
    L: null                  # null → use box length along axis
  model: path/to/model.pt    # or hf://org/repo
  adsorbent: path/to/frame.xyz
  adsorbate_molecule: CO2
  output_dir: ./cdft_data
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np
from ase import Atoms
from ase.build import molecule
from ase.io import read
from ase.units import bar, kB
from ase.data import vdw_radii

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

from .external_field import ExternalField, FourierSeries, random_fourier_field, from_dict
from .density_grid import DensityGrid1D
from .sample_writer import SampleWriter


class GCMCCampaign:
    """
    Run a sweep of GCMC simulations with varying (μ, T, V_ext) and
    write one HDF5 sample per run.

    Parameters
    ----------
    config : dict
        Campaign configuration (see module docstring for schema).
    model : any
        ASE-compatible calculator (pre-loaded MLIP or analytic pair potential).
    """

    def __init__(self, config: dict, model: Any) -> None:
        self.cfg = config
        self.model = model

        self.output_dir = Path(config.get("output_dir", "cdft_data"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Thermodynamic state space
        temps = config.get("temperature", 300.0)
        self.temperatures = [temps] if isinstance(temps, (int, float)) else list(temps)
        self.mu_values = list(config.get("mu_values", [-0.3]))
        self.n_runs = int(config.get("n_runs", 10))

        # MC parameters
        self.n_equil = int(config.get("n_equilibration_steps", 5000))
        self.n_prod  = int(config.get("n_production_steps", 20000))
        self.n_blocks = int(config.get("grid", {}).get("n_blocks", config.get("n_blocks", 10)))

        # Grid parameters
        grid_cfg = config.get("grid", {})
        self.n_bins = int(grid_cfg.get("n_bins", 200))
        self.axis   = int(grid_cfg.get("axis", 2))

        # V_ext template
        self.v_ext_cfg = config.get("v_ext", {"type": "fourier", "n_modes": 4,
                                               "amplitude_scale": 0.1})

        # Seed for reproducibility
        self._rng = np.random.default_rng(config.get("seed", None))

        # Load structures
        adsorbent_path = config.get("adsorbent")
        self.atoms_frame = _load_frame(adsorbent_path)
        self.box = np.diag(self.atoms_frame.get_cell())

        ads_path = config.get("adsorbate_path")
        ads_mol  = config.get("adsorbate_molecule")
        self.atoms_ads, self.adsorbate_name = _load_adsorbate(ads_path, ads_mol)

    # ------------------------------------------------------------------
    def run(self) -> list[Path]:
        """Execute the campaign and return list of written HDF5 files."""
        from mlip_mc.src.gcmc import MLP_GCMC
        from mlip_mc.src.utilities import PREOS

        written = []
        run_idx = 0

        for T in self.temperatures:
            beta = 1.0 / (kB * T)
            for mu in self.mu_values:
                for _ in range(self.n_runs):
                    v_ext = self._sample_v_ext()
                    sample_path = self._run_single(
                        T=T, mu=mu, beta=beta,
                        v_ext=v_ext, run_idx=run_idx,
                    )
                    written.append(sample_path)
                    run_idx += 1
                    print(f"[campaign] run {run_idx:04d}  T={T}K  μ={mu:.3f}eV  → {sample_path.name}",
                          flush=True)

        print(f"\n[campaign] Done. {len(written)} samples in {self.output_dir}", flush=True)
        return written

    # ------------------------------------------------------------------
    def _sample_v_ext(self) -> ExternalField:
        """Draw a random V_ext from the configured distribution."""
        cfg = dict(self.v_ext_cfg)  # copy
        kind = cfg.get("type", "fourier")
        if kind == "fourier":
            L = cfg.get("L") or float(self.box[self.axis])
            return random_fourier_field(
                axis=self.axis,
                n_modes=int(cfg.get("n_modes", 4)),
                amplitude_scale=float(cfg.get("amplitude_scale", 0.1)),
                L=L,
                rng=self._rng,
            )
        # Composite / other — delegate to from_dict (deterministic)
        return from_dict(cfg)

    # ------------------------------------------------------------------
    def _run_single(
        self,
        T: float,
        mu: float,
        beta: float,
        v_ext: ExternalField,
        run_idx: int,
    ) -> Path:
        from mlip_mc.src.gcmc import MLP_GCMC

        run_id = f"run_{run_idx:05d}"
        run_output = self.output_dir / run_id
        run_output.mkdir(exist_ok=True)

        # Compute fugacity — ideal gas fallback if molecule not in PREOS table
        from ase.units import bar as _bar
        P_bar = np.exp(beta * mu)      # activity → approximate pressure
        P = P_bar * _bar
        try:
            from mlip_mc.src.utilities import PREOS
            eos = PREOS.from_name(self.adsorbate_name)
            fugacity = eos.calculate_fugacity(T, P)
        except Exception:
            fugacity = P               # ideal gas

        # Density grid — 1D planar projection
        box_z = float(self.box[self.axis])
        xy_area = float(self.box[(self.axis + 1) % 3] * self.box[(self.axis + 2) % 3])
        grid = DensityGrid1D(
            box_z=box_z,
            n_bins=self.n_bins,
            n_blocks=self.n_blocks,
            xy_area=xy_area,
        )

        # GCMC run
        gcmc = MLP_GCMC(
            model=self.model,
            atoms_frame=self.atoms_frame.copy(),
            atoms_ads=self.atoms_ads.copy(),
            T=T,
            P=P,
            fugacity=fugacity,
            device=getattr(self.model, 'device', 'cpu'),
            vdw_radii=vdw_radii,
            debug=False,
            output_dir=str(run_output),
            n_equilibration_steps=self.n_equil,
            n_production_steps=self.n_prod,
            external_field=v_ext,
            density_grid=grid,
        )
        gcmc.run(N=self.n_equil + self.n_prod)

        # Sample writer
        v_ext_grid = grid.v_ext_on_grid(v_ext)
        grid_results = grid.results(mu=mu, beta=beta, external_field=v_ext)

        # Capture V_ext spec for metadata
        v_ext_spec = _v_ext_to_dict(v_ext)

        metadata = {
            "T": T,
            "mu": mu,
            "beta": beta,
            "box": self.box.tolist(),
            "axis": self.axis,
            "n_equil": self.n_equil,
            "n_prod": self.n_prod,
            "adsorbate": self.adsorbate_name,
            "run_id": run_id,
            "v_ext_spec": json.dumps(v_ext_spec),
        }

        writer = SampleWriter(output_dir=self.output_dir, run_id=run_id)
        return writer.write(grid_results=grid_results, metadata=metadata)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_frame(path: Optional[str]) -> Atoms:
    if path is None:
        raise ValueError("campaign config must provide 'adsorbent' path")
    atoms = read(path)
    return Atoms(numbers=atoms.numbers, positions=atoms.positions,
                 cell=atoms.cell, pbc=atoms.pbc)


def _load_adsorbate(ads_path: Optional[str], ads_mol: Optional[str]):
    if ads_path is not None:
        atoms = read(ads_path)
        atoms = Atoms(numbers=atoms.numbers, positions=atoms.positions)
        return atoms, atoms.get_chemical_formula().replace(' ', '')
    if ads_mol is not None:
        atoms = molecule(ads_mol)
        return Atoms(numbers=atoms.numbers, positions=atoms.positions), ads_mol
    raise ValueError("provide 'adsorbate_path' or 'adsorbate_molecule' in campaign config")


def _v_ext_to_dict(v_ext) -> dict:
    """Serialise V_ext to a JSON-safe dict for metadata storage."""
    from .external_field import (FourierSeries, HardWall, LinearRamp,
                                  GaussianPocket, Sinusoid, CompositeField)
    if isinstance(v_ext, FourierSeries):
        return {"type": "fourier", "axis": v_ext.axis, "n_modes": v_ext.n_modes,
                "amplitudes": v_ext.amplitudes.tolist(),
                "phases": v_ext.phases.tolist(), "L": v_ext.L}
    if isinstance(v_ext, HardWall):
        return {"type": "hard_wall", "axis": v_ext.axis,
                "z_lo": v_ext.z_lo, "z_hi": v_ext.z_hi, "strength": v_ext.strength}
    if isinstance(v_ext, LinearRamp):
        return {"type": "linear_ramp", "axis": v_ext.axis, "slope": v_ext.slope}
    if isinstance(v_ext, GaussianPocket):
        return {"type": "gaussian", "center": v_ext.center.tolist(),
                "amplitude": v_ext.amplitude, "sigma": v_ext.sigma}
    if isinstance(v_ext, Sinusoid):
        return {"type": "sinusoid", "axis": v_ext.axis,
                "amplitude": v_ext.amplitude, "frequency": v_ext.frequency,
                "phase": v_ext.phase}
    if isinstance(v_ext, CompositeField):
        return {"type": "composite", "components": [_v_ext_to_dict(c) for c in v_ext.components]}
    return {"type": str(type(v_ext).__name__)}


def from_yaml(path: Union[str, Path]) -> "GCMCCampaign":
    """Load a GCMCCampaign from a YAML file (model must be provided separately)."""
    raise NotImplementedError(
        "Use GCMCCampaign(config, model) directly. "
        "Load the model via mlip_mc.main._load_model() first."
    )
