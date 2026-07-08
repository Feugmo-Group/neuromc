"""
GPU-accelerated GCMC data generation via TorchSim + nvalchemi.

Architecture
------------
BatchedGCMCRunner runs N independent GCMC chains simultaneously on one GPU.
Each chain has its own (μ, T, V_ext_seed).  At each MC step, all N trial
configurations are evaluated in a single batched MLIP forward pass via
TorchSim's SimState + ModelInterface, eliminating N-1 Python ↔ GPU round-trips.

Dependency hierarchy (all optional — falls back to ASE serial if absent):
  torch-sim-atomistic   → batched SimState, MACE/FAIRchem/ORB wrappers
  nvalchemi-toolkit     → nvalchemi.data.Batch + Warp neighbor lists
  warp-lang             → Warp kernels for vdW overlap / histogram (Phase 3)

Usage
-----
    from neuromc.dft.gpu import BatchedGCMCRunner, build_torchsim_model

    model = build_torchsim_model("mace-mp", device="cuda")
    runner = BatchedGCMCRunner(
        model=model,
        atoms_frame=frame,
        atoms_ads_list=[ads] * n_chains,
        T_list=[300.0] * n_chains,
        mu_list=[-0.5, -0.3, -0.1, 0.1, ...],   # one per chain
        v_ext_list=[v_ext_0, v_ext_1, ...],       # one per chain
        n_equil=5000,
        n_prod=20000,
        device="cuda",
    )
    samples = runner.run()   # returns list[dict] with rho, c1 per chain
"""

from __future__ import annotations

import warnings
from typing import Any, Optional

import numpy as np

try:
    import torch
    _TORCH = True
except ImportError:
    _TORCH = False

try:
    import torch_sim as ts
    from torch_sim.state import SimState
    _TORCHSIM = True
except ImportError:
    _TORCHSIM = False
    warnings.warn(
        "torch-sim-atomistic not installed; GPU batched GCMC unavailable. "
        "Install with: pip install torch-sim-atomistic",
        ImportWarning,
        stacklevel=2,
    )

try:
    from nvalchemi.data import AtomicData, Batch
    _NVALCHEMI = True
except ImportError:
    _NVALCHEMI = False


def build_torchsim_model(backend: str, device: str = "cuda", model_path: Optional[str] = None):
    """
    Load a TorchSim-compatible MLIP model.

    Parameters
    ----------
    backend : str
        One of 'mace-mp', 'mace', 'fairchem', 'orb-models'.
    device : str
        'cuda' or 'cpu'.
    model_path : str, optional
        Local checkpoint path (required for 'fairchem' and custom MACE).

    Returns
    -------
    torch_sim ModelInterface instance.
    """
    if not _TORCHSIM:
        raise ImportError("torch-sim-atomistic is required: pip install torch-sim-atomistic")

    device_obj = torch.device(device)

    if backend in ("mace-mp", "mace_mp"):
        from mace.calculators.foundations_models import mace_mp
        from torch_sim.models.mace import MaceModel
        raw = mace_mp(model="medium", return_raw_model=True)
        return MaceModel(model=raw, device=device_obj, compute_forces=True)

    if backend in ("mace", "mace-torch"):
        from mace.calculators.foundations_models import mace_mp
        from torch_sim.models.mace import MaceModel
        if model_path is None:
            raise ValueError("model_path is required for custom MACE checkpoints")
        import mace
        raw = mace.load_model(model_path)
        return MaceModel(model=raw, device=device_obj, compute_forces=True)

    if backend == "fairchem":
        from torch_sim.models.fairchem import FairchemModel
        if model_path is None:
            raise ValueError("model_path is required for FAIRchem")
        return FairchemModel(checkpoint_path=model_path, device=device_obj)

    if backend in ("orb-models", "orb"):
        from torch_sim.models.orb import OrbModel
        return OrbModel(device=device_obj)

    raise ValueError(f"Unknown backend: {backend!r}. "
                     f"Choose from: mace-mp, mace, fairchem, orb-models")


class BatchedGCMCRunner:
    """
    Run N independent GCMC chains in parallel on one GPU using TorchSim.

    Each chain has its own chemical potential, temperature, and external field.
    All trial-configuration energies are evaluated in a single batched model call
    per MC step, giving a ~N× speedup over N serial ASE-calculator chains.

    Parameters
    ----------
    model : torch_sim ModelInterface
        GPU-resident MLIP model (from build_torchsim_model).
    atoms_frame : ase.Atoms
        Framework structure (shared across all chains).
    atoms_ads_list : list[ase.Atoms]
        Adsorbate molecule per chain (usually all the same).
    T_list : list[float]
        Temperature [K] per chain.
    mu_list : list[float]
        Chemical potential [eV] per chain.
    v_ext_list : list[ExternalField]
        External potential per chain (from neuromc.dft.external_field).
    n_equil : int
        Equilibration steps per chain.
    n_prod : int
        Production steps per chain.
    n_bins : int
        Density histogram bins.
    n_blocks : int
        Block-averaging blocks.
    device : str
        'cuda' or 'cpu'.
    """

    def __init__(
        self,
        model,
        atoms_frame,
        atoms_ads_list: list,
        T_list: list[float],
        mu_list: list[float],
        v_ext_list: list,
        n_equil: int = 5000,
        n_prod: int = 20000,
        n_bins: int = 200,
        n_blocks: int = 10,
        device: str = "cuda",
    ) -> None:
        if not _TORCHSIM:
            raise ImportError("torch-sim-atomistic is required for BatchedGCMCRunner")

        self.model = model
        self.atoms_frame = atoms_frame
        self.atoms_ads_list = atoms_ads_list
        self.T_list = T_list
        self.mu_list = mu_list
        self.v_ext_list = v_ext_list
        self.n_chains = len(mu_list)
        self.n_equil = n_equil
        self.n_prod = n_prod
        self.n_bins = n_bins
        self.n_blocks = n_blocks
        self.device = torch.device(device)

        assert len(T_list) == self.n_chains
        assert len(v_ext_list) == self.n_chains

        from ase.units import kB
        self.betas = [1.0 / (kB * T) for T in T_list]

    # ------------------------------------------------------------------
    def run(self) -> list[dict]:
        """
        Execute all chains and return per-chain sample dicts.

        Each dict contains: rho, c1, v_ext_grid, z, rho_stderr, c1_stderr,
        total_steps, mu, T — ready for SampleWriter.write().
        """
        from ..density_grid import DensityGrid1D

        box = np.diag(self.atoms_frame.get_cell())
        box_z = float(box[2])
        xy_area = float(box[0] * box[1])

        # Per-chain density grids and GCMC state
        grids = [
            DensityGrid1D(box_z=box_z, n_bins=self.n_bins,
                          n_blocks=self.n_blocks, xy_area=xy_area)
            for _ in range(self.n_chains)
        ]

        # Initialise chain states: each starts as empty framework
        chain_atoms = [self.atoms_frame.copy() for _ in range(self.n_chains)]
        chain_Z = [0] * self.n_chains  # adsorbate count per chain

        steps_per_block = max(1, self.n_prod // self.n_blocks)
        n_total = self.n_equil + self.n_prod

        print(f"[BatchedGCMCRunner] {self.n_chains} chains × {n_total} steps on {self.device}",
              flush=True)

        for step in range(n_total):
            self._batch_step(
                step=step,
                chain_atoms=chain_atoms,
                chain_Z=chain_Z,
                grids=grids,
                steps_per_block=steps_per_block,
            )

            if (step + 1) % max(1, n_total // 10) == 0:
                avg_Z = np.mean(chain_Z)
                print(f"  step {step+1}/{n_total}  avg_N_ads={avg_Z:.1f}", flush=True)

        # Collect results
        results = []
        for i, (grid, mu, T, beta, v_ext) in enumerate(
            zip(grids, self.mu_list, self.T_list, self.betas, self.v_ext_list)
        ):
            r = grid.results(mu=mu, beta=beta, external_field=v_ext)
            r["mu"] = mu
            r["T"] = T
            results.append(r)

        return results

    # ------------------------------------------------------------------
    def _batch_step(
        self,
        step: int,
        chain_atoms: list,
        chain_Z: list[int],
        grids: list,
        steps_per_block: int,
    ) -> None:
        """Propose and evaluate N trials in one batched forward pass."""
        from ase import Atoms
        from neuromc.src.utilities import random_position, vdw_overlap
        from ase.units import bar, kB
        from ase.data import vdw_radii

        vdw = vdw_radii - 0.35
        n_frame = len(self.atoms_frame)

        trial_atoms_list = []
        move_types = []
        chain_indices = []

        # Propose one move per chain
        for i in range(self.n_chains):
            atoms = chain_atoms[i]
            Z = chain_Z[i]
            ads = self.atoms_ads_list[i]
            n_ads = len(ads)
            switch = np.random.rand()

            if switch < 0.25:                          # insertion
                trial = atoms + ads.copy()
                pos = trial.get_positions()
                pos[-n_ads:] = random_position(pos[-n_ads:], atoms.get_cell())
                trial.set_positions(pos)
                move_types.append(("insert", i, Z, n_ads))
            elif switch < 0.5 and Z > 0:              # deletion
                idx = np.random.randint(Z)
                trial = atoms.copy()
                del trial[n_frame + n_ads * idx: n_frame + n_ads * (idx + 1)]
                move_types.append(("delete", i, Z, n_ads))
            elif switch < 0.75 and Z > 0:             # translation
                trial = atoms.copy()
                pos = trial.get_positions()
                idx = np.random.randint(Z)
                pos[n_frame + n_ads * idx: n_frame + n_ads * (idx + 1)] += (
                    0.5 * (np.random.rand(3) - 0.5)
                )
                trial.set_positions(pos)
                move_types.append(("translate", i, Z, n_ads))
            else:                                      # no-op (e.g. Z=0, deletion skipped)
                trial = atoms.copy()
                move_types.append(("noop", i, Z, n_ads))

            trial_atoms_list.append(trial)
            chain_indices.append(i)

        # Batched energy evaluation via TorchSim
        trial_energies = self._batched_energy(trial_atoms_list)
        current_energies = self._batched_energy(chain_atoms)

        # Metropolis per chain
        for (move, ci, Z, n_ads), e_trial, e_curr in zip(
            move_types, trial_energies, current_energies
        ):
            if move == "noop":
                continue

            v_ext = self.v_ext_list[ci]
            beta = self.betas[ci]
            T = self.T_list[ci]
            mu = self.mu_list[ci]
            atoms = chain_atoms[ci]
            trial = trial_atoms_list[chain_indices.index(ci)]

            # External-field contribution
            def vext_sum(a):
                if v_ext is None or chain_Z[ci] == 0:
                    return 0.0
                return float(v_ext(a.get_positions()[n_frame:]).sum())

            dE = (e_trial + vext_sum(trial)) - (e_curr + vext_sum(atoms))

            if move == "insert":
                from ase.units import bar as _bar
                P = np.exp(beta * mu) * _bar
                V = np.linalg.det(np.array(self.atoms_frame.get_cell()))
                Z_new = Z + 1
                acc = min(1.0, V * beta * P / Z_new * np.exp(-beta * dE))
                if np.random.rand() < acc:
                    chain_atoms[ci] = trial
                    chain_Z[ci] = Z_new

            elif move == "delete":
                from ase.units import bar as _bar
                P = np.exp(beta * mu) * _bar
                V = np.linalg.det(np.array(self.atoms_frame.get_cell()))
                acc = min(1.0, (Z + 1) / V / beta / P * np.exp(-beta * dE))
                if np.random.rand() < acc:
                    chain_atoms[ci] = trial
                    chain_Z[ci] = Z - 1

            else:  # translate / rotate
                acc = min(1.0, np.exp(-beta * dE))
                if np.random.rand() < acc:
                    chain_atoms[ci] = trial

        # Density accumulation (production phase)
        for i, (atoms, Z) in enumerate(zip(chain_atoms, chain_Z)):
            if step >= self.n_equil and Z > 0:
                n_ads = len(self.atoms_ads_list[i])
                ads_pos = atoms.get_positions()[n_frame:]
                grids[i].accumulate(ads_pos, steps_per_block)

    # ------------------------------------------------------------------
    def _batched_energy(self, atoms_list: list) -> list[float]:
        """
        Evaluate energies for a list of ASE Atoms in a single TorchSim forward pass.

        Falls back to sequential ASE-calculator evaluation if TorchSim model
        does not accept the batch structure.
        """
        if not _TORCHSIM or not atoms_list:
            return [0.0] * len(atoms_list)

        try:
            states = [
                ts.io.atoms_to_state(a, device=self.device)
                for a in atoms_list
            ]
            batch = ts.state.concatenate_states(states)
            with torch.no_grad():
                out = self.model(batch)
            energies = out["energy"].cpu().numpy().tolist()
            return energies
        except Exception as exc:
            warnings.warn(f"Batched eval failed ({exc}); falling back to serial", RuntimeWarning)
            # Serial fallback
            from ase.calculators.calculator import Calculator
            results = []
            for a in atoms_list:
                a2 = a.copy()
                a2.calc = self.model  # TorchSim models are also ASE calculators
                results.append(float(a2.get_potential_energy()))
            return results
