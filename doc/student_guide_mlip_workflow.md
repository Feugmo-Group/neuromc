# Student Guide: From CP2K Data to Transport Properties with MLIPs

## Overview of the Full Pipeline

```
CP2K DFT calculations
        ↓
  Extract training data (energies, forces, stresses)
        ↓
  Train MLIP  [MACE | fairchem | orb-models]
        ↓
  Validate MLIP against DFT holdout set
        ↓
  Run MD with torch-sim (implementation-branch)
        ↓
  Compute: g(r) · thermal conductivity · diffusion · viscosity
```

All repos you need:

| Repo | Path | Purpose |
|---|---|---|
| `MLIP-MC` | `../MLIP-MC` | GCMC + cDFT data generation |
| `torch-sim` | `../torch-sim` | GPU MD engine + RNEMD |
| `ionax` | `../ionax` | cDFT reference solver |

For torch-sim, always work on **`implementation-branch`** — it contains the RNEMD workflow and Fumi-Tosi classical model:

```bash
cd ../torch-sim
git checkout implementation-branch
pip install -e ".[dev]"
```

---

## Part 1 — Extract training data from CP2K

CP2K writes energies and forces in its output file and can write trajectories as extended XYZ. The goal is to produce a set of `.extxyz` frames where each frame carries `energy`, `forces`, and `stress` in the `info` / `arrays` fields — the format every MLIP trainer expects.

### 1.1 CP2K input settings to enable force/stress output

In your CP2K input (`*.inp`) add inside `&MOTION / &PRINT`:

```
&TRAJECTORY
  FORMAT XYZ
  FILENAME trajectory.xyz
&END TRAJECTORY
&FORCES
  FILENAME forces.xyz
&END FORCES
&STRESS
  FILENAME stress.dat
&END STRESS
```

And inside `&FORCE_EVAL / &DFT / &PRINT`:

```
&E_DENSITY_CUBE OFF &END
&STRESS_TENSOR ON &END
```

### 1.2 Parse CP2K output into extended XYZ

ASE can read CP2K output directly. Use this script to merge positions, forces, energy, and stress into a single `.extxyz` file:

```python
import numpy as np
from ase.io import read, write
from ase.units import GPa  # 1 eV/Å³ = 160.2 GPa

frames = read("trajectory.xyz", index=":")          # positions
forces_list = read("forces.xyz", index=":")         # forces (same length)

with open("stress.dat") as f:
    lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

# CP2K prints stress tensor as 3x3 in GPa; convert to eV/Å³
def parse_stress_block(lines, i):
    rows = []
    for k in range(3):
        rows.append([float(x) for x in lines[i + k].split()])
    return np.array(rows) / GPa   # GPa → eV/Å³

out_frames = []
stress_idx = 0
for frame, f_frame in zip(frames, forces_list):
    frame.arrays["forces"] = f_frame.get_positions()   # forces are in positions slot
    stress_voigt = parse_stress_block(lines, stress_idx)
    frame.info["stress"] = stress_voigt.flatten()      # 9-component flat
    stress_idx += 4                                    # 3 rows + 1 blank line
    out_frames.append(frame)

write("training_data.extxyz", out_frames)
print(f"Wrote {len(out_frames)} frames to training_data.extxyz")
```

After this you have a single `training_data.extxyz` — split it 80/10/10 for train/val/test:

```python
import random
frames = read("training_data.extxyz", index=":")
random.seed(42)
random.shuffle(frames)
n = len(frames)
write("train.extxyz",  frames[:int(0.8*n)])
write("val.extxyz",    frames[int(0.8*n):int(0.9*n)])
write("test.extxyz",   frames[int(0.9*n):])
```

---

## Part 2 — Train an MLIP

Three backends are supported. Pick one. MACE is the recommended starting point for solids.

### 2A — MACE

Install:

```bash
pip install mace-torch
```

Write a training config `mace_config.yaml`:

```yaml
# mace_config.yaml
name: "lipon_mace"

train_file: "train.extxyz"
valid_file: "val.extxyz"

model: "MACE"
num_interactions: 2
num_channels: 128
max_ell: 3
r_max: 5.0           # cutoff in Å — increase to 6.0 for ionic systems

E0s: "average"        # reference energies from training data mean
energy_weight: 1.0
forces_weight: 10.0
stress_weight: 1.0

batch_size: 10
max_num_epochs: 1000
lr: 0.01
scheduler_patience: 50
patience: 200

device: "cuda"
default_dtype: "float64"

save_cpu: true        # save a CPU-loadable checkpoint
```

Run training:

```bash
mace_run_train --config mace_config.yaml
```

Outputs land in `./results/lipon_mace/`:

```
results/lipon_mace/
  lipon_mace_run-123_epoch-1000.model        ← best checkpoint
  lipon_mace_run-123_stagetwo.model          ← after stage-2 (lower lr)
  lipon_mace_run-123_compiled.model          ← torchscript (fastest inference)
```

Use the compiled model for simulations:

```python
model_path = "results/lipon_mace/lipon_mace_run-123_compiled.model"
```

### 2B — fairchem (UMA / eSEN)

Install:

```bash
pip install fairchem-core
```

fairchem fine-tuning uses LMDB datasets. Convert your extxyz first:

```python
from fairchem.core.preprocessing import AtomsToGraphs
from ase.io import read
import lmdb, pickle, os

a2g = AtomsToGraphs(max_neigh=50, radius=6.0,
                    r_energy=True, r_forces=True, r_stress=True)

def write_lmdb(frames, path):
    os.makedirs(path, exist_ok=True)
    db = lmdb.open(os.path.join(path, "data.lmdb"), map_size=int(1e11))
    with db.begin(write=True) as txn:
        for i, atoms in enumerate(frames):
            data = a2g.convert(atoms)
            txn.put(str(i).encode(), pickle.dumps(data))
    db.close()

write_lmdb(read("train.extxyz", index=":"), "lmdb/train")
write_lmdb(read("val.extxyz",   index=":"), "lmdb/val")
```

Then fine-tune a pretrained checkpoint (e.g. UMA-SM):

```bash
python -m fairchem.core.main \
  --mode train \
  --config-yml finetune_config.yml \
  --checkpoint uma-sm.pt
```

### 2C — orb-models

Install:

```bash
pip install orb-models
```

orb-models exposes pretrained models directly. Fine-tune:

```python
from orb_models.forcefield import pretrained
from orb_models.forcefield.atomic_system import ase_atoms_to_atom_graphs
from ase.io import read

model = pretrained.orb_v3_conservative_inf_omat()
# Fine-tuning follows orb-models documentation; see:
# https://github.com/orbital-materials/orb-models
```

For quick evaluation without fine-tuning, `MLIP-MC` will fall back to the pretrained checkpoint automatically when no local model path is found (see `mlip_mc/main.py::_load_model`).

---

## Part 3 — Validate the MLIP

Before running expensive MD, check that the MLIP reproduces DFT on the test set.

```python
import torch
import numpy as np
from ase.io import read
from torch_sim.models.mace import MaceModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MaceModel(
    model="results/lipon_mace/lipon_mace_run-123_compiled.model",
    device=device,
    dtype=torch.float64,
    compute_forces=True,
    compute_stress=True,
)

test_frames = read("test.extxyz", index=":")
e_dft, e_mlip, f_dft, f_mlip = [], [], [], []

for atoms in test_frames:
    atoms.calc = None  # strip old calc
    import torch_sim as ts
    state = ts.state.initialize_state(atoms, device, torch.float64)
    out = model(state)
    e_mlip.append(out["energy"].item() / len(atoms))
    e_dft.append(atoms.info["energy"] / len(atoms))
    f_mlip.append(out["forces"].cpu().numpy())
    f_dft.append(atoms.arrays["forces"])

e_rmse = np.sqrt(np.mean((np.array(e_mlip) - np.array(e_dft))**2)) * 1000  # meV/atom
f_rmse = np.sqrt(np.mean((np.concatenate(f_mlip) - np.concatenate(f_dft))**2))

print(f"Energy RMSE: {e_rmse:.1f} meV/atom")   # target < 5 meV/atom
print(f"Force  RMSE: {f_rmse:.3f} eV/Å")       # target < 0.1 eV/Å
```

---

## Part 4 — Run MD with torch-sim

### 4.1 Load the structure and create a SimState

```python
import torch
import torch_sim as ts
from ase.io import read

device = torch.device("cuda")
dtype  = torch.float32

atoms = read("lipon_supercell.xyz")   # your relaxed supercell
state = ts.state.initialize_state(atoms, device, dtype)
```

### 4.2 Load the MLIP calculator

Pick whichever backend you trained:

```python
# --- MACE ---
from torch_sim.models.mace import MaceModel
model = MaceModel(
    model="results/lipon_mace/lipon_mace_run-123_compiled.model",
    device=device,
    dtype=torch.float64,
    compute_forces=True,
    compute_stress=True,
)

# --- fairchem ---
from torch_sim.models.fairchem import FairChemModel
model = FairChemModel(
    model="path/to/checkpoint.pt",   # or a pretrained model name string
    device=device,
    compute_stress=True,
)

# --- orb-models ---
from torch_sim.models.orb import OrbModel
import torch
orb_loaded = torch.load("path/to/orb_model.pt", map_location=device)
model = OrbModel(
    model=orb_loaded,
    device=device,
    compute_stress=True,
    conservative=True,
)
```

> **Neighbor lists**: torch-sim automatically uses NVIDIA `nvalchemiops` (CUDA-accelerated) if installed, falling back to `vesin` then pure-PyTorch. To install the fast backend:
> `pip install nvalchemiops`

### 4.3 Equilibration (NVT)

```python
equil_state = ts.integrate(
    system=state,
    model=model,
    integrator=ts.Integrator.nvt_nose_hoover,
    n_steps=10_000,
    timestep=0.001,          # 1 fs in ps
    temperature=600.0,       # K
)
```

---

## Part 5 — Compute transport properties

### 5.1 Thermal conductivity via RNEMD (Müller-Plathe)

**File**: `torch_sim/workflows/RNEMD.py`

This is the primary method implemented on `implementation-branch`.

**Constraints**:
- Single element only (velocity swaps assume equal masses)
- Single system (`n_systems = 1`)
- Cell must be diagonal
- `nslabs` must be even

```python
from torch_sim.workflows.RNEMD import RNEMD

# Option A: use your existing equilibrated state
sim = RNEMD(system_state=equil_state, nslabs=20)

# Option B: build a fresh random single-element box
sim_state = RNEMD.create_simple_system(
    atomic_number=3,                        # Li = 3
    box_dimensions_angs=(20.0, 20.0, 60.0),
    n_atoms=500,
    pbc=[True, True, True],
    device=device,
    dtype=dtype,
)
sim = RNEMD(system_state=sim_state, nslabs=20)

# Run
sim.run_simulation(
    model=model,
    timestep_ps=0.001,          # 1 fs
    W=100,                      # exchange every 100 steps
    nsteps_total=200_000,       # 200 ps total (must be divisible by W)
    temp_K=600.0,
    perform_geometry_optimization=True,
    perform_equilibration=True,
    n_equil_step=10_000,
    n_exchanges_per_step=1,
    data_folder_path_abs="/absolute/path/to/output/rnemd_results",
)

# Extract κ
sim.post_simulation_processing(compute_running_values=True, save_simulation_results=True)
# Results written to rnemd_results/simulation_data.h5
```

Read results back:

```python
import h5py
import numpy as np
import matplotlib.pyplot as plt

with h5py.File("rnemd_results/simulation_data.h5", "r") as f:
    kappa      = float(f["final_thermal_conductivity"][()])   # W/(m·K)
    kappa_run  = np.array(f["running_thermal_conductivity"])  # convergence trace
    slab_T     = np.array(f["slabwise_temperature"])          # (steps, nslabs)

print(f"κ = {kappa:.2f} W/(m·K)")

plt.plot(kappa_run)
plt.xlabel("Exchange step")
plt.ylabel("κ  [W/(m·K)]")
plt.title("Running thermal conductivity")
plt.savefig("kappa_convergence.png", dpi=150)
```

### 5.2 Thermal conductivity via Green-Kubo (HFACF)

An alternative to RNEMD that works for multi-element systems.
**File**: `torch_sim/properties/correlations.py` — `HeatFluxAutoCorrelation`

```python
from torch_sim.properties.correlations import HeatFluxAutoCorrelation

hfacf_calc = HeatFluxAutoCorrelation(
    model=model,
    window_size=500,            # correlation window (steps)
    device=device,
    use_running_average=True,
    normalize=True,
)

reporter = ts.TrajectoryReporter(
    filenames="hfacf_run.h5",
    state_frequency=0,          # don't save raw trajectory
    prop_calculators={10: {"hfacf": hfacf_calc}},
)

ts.integrate(
    system=equil_state,
    model=model,
    integrator=ts.Integrator.nvt_nose_hoover,
    n_steps=100_000,
    timestep=0.001,
    temperature=600.0,
    trajectory_reporter=reporter,
)

# Integrate HFACF → κ
hfacf = hfacf_calc.hfacf.cpu().numpy()   # (window_size,)
dt_s  = 0.001e-12                         # timestep in seconds
V_m3  = equil_state.volume.item() * 1e-30
kT    = 1.380649e-23 * 600.0

kappa_gk = (V_m3 / (3 * kT)) * np.trapz(hfacf, dx=dt_s)
print(f"κ (Green-Kubo) = {kappa_gk:.2f} W/(m·K)")
```

### 5.3 Diffusion coefficient (VACF / Green-Kubo)

**File**: `torch_sim/properties/correlations.py` — `VelocityAutoCorrelation`

```python
from torch_sim.properties.correlations import VelocityAutoCorrelation

vacf_calc = VelocityAutoCorrelation(
    window_size=1000,
    device=device,
    use_running_average=True,
)

reporter = ts.TrajectoryReporter(
    filenames="vacf_run.h5",
    prop_calculators={1: {"vacf": vacf_calc}},
)

ts.integrate(
    system=equil_state,
    model=model,
    integrator=ts.Integrator.nvt_nose_hoover,
    n_steps=200_000,
    timestep=0.001,
    temperature=600.0,
    trajectory_reporter=reporter,
)

vacf = vacf_calc.vacf.cpu().numpy()   # (window_size,)
dt_s = 0.001e-12

# Green-Kubo: D = (1/3) ∫ VACF dt
D_m2s = (1/3) * np.trapz(vacf, dx=dt_s)
print(f"D = {D_m2s:.3e} m²/s")
```

### 5.4 Radial distribution function g(r)

**Not yet in torch-sim** — compute it with ASE after saving a trajectory:

```python
import numpy as np
from ase.io import read
from ase.geometry import get_distances

def compute_gr(traj_file, rmax=8.0, nbins=200, species_pair=None):
    """Compute g(r) from an ASE trajectory file."""
    frames = read(traj_file, index=":")
    bins   = np.linspace(0, rmax, nbins + 1)
    dr     = bins[1] - bins[0]
    hist   = np.zeros(nbins, dtype=float)

    for atoms in frames:
        n  = len(atoms)
        V  = atoms.get_volume()
        for i in range(n):
            dists, _ = get_distances(atoms.positions[i:i+1],
                                     atoms.positions,
                                     cell=atoms.cell,
                                     pbc=atoms.pbc)
            dists = dists.ravel()
            dists = dists[dists > 1e-6]
            h, _  = np.histogram(dists, bins=bins)
            hist += h

    # Normalise
    r_centers = 0.5 * (bins[:-1] + bins[1:])
    rho       = len(frames[0]) / frames[0].get_volume()
    shell_vol = (4/3) * np.pi * (bins[1:]**3 - bins[:-1]**3)
    norm      = len(frames) * len(frames[0]) * rho * shell_vol
    gr        = hist / norm
    return r_centers, gr

# First save a trajectory during equilibration
reporter = ts.TrajectoryReporter("traj.h5", state_frequency=100)
ts.integrate(system=equil_state, model=model,
             integrator=ts.Integrator.nvt_nose_hoover,
             n_steps=100_000, timestep=0.001, temperature=600.0,
             trajectory_reporter=reporter)

# Then read and compute g(r)
# (convert h5 to extxyz first, or read directly with ts.io)
r, gr = compute_gr("traj.extxyz", rmax=8.0)

import matplotlib.pyplot as plt
plt.plot(r, gr)
plt.axhline(1, ls="--", c="gray")
plt.xlabel("r  [Å]")
plt.ylabel("g(r)")
plt.savefig("gr.png", dpi=150)
```

### 5.5 Viscosity (Green-Kubo, pressure tensor ACF)

**Not yet wrapped** — `compute_instantaneous_pressure_tensor` is available in `torch_sim/quantities.py`, but no ACF integrator exists yet. Collect pressure tensors manually:

```python
import torch
import numpy as np
from torch_sim.quantities import compute_instantaneous_pressure_tensor

pxy_trace = []

def record_pressure(state, _model=None):
    P = compute_instantaneous_pressure_tensor(
        momenta=state.momenta,
        masses=state.masses,
        forces=model(state)["forces"],
        positions=state.positions,
        volume=state.volume,
    )
    pxy_trace.append(P[0, 1].item())   # Pxy component [eV/Å³]
    return torch.tensor([P[0, 1].item()], device=state.device)

reporter = ts.TrajectoryReporter(
    filenames="pxy_trace.h5",
    prop_calculators={1: {"pxy": record_pressure}},
)

ts.integrate(
    system=equil_state,
    model=model,
    integrator=ts.Integrator.nvt_nose_hoover,
    n_steps=200_000,
    timestep=0.001,
    temperature=600.0,
    trajectory_reporter=reporter,
)

# Green-Kubo: η = (V/kT) ∫ <Pxy(0)·Pxy(t)> dt
pxy    = np.array(pxy_trace)
# autocorrelation via FFT
n      = len(pxy)
f      = np.fft.rfft(pxy - pxy.mean(), n=2*n)
acf    = np.fft.irfft(f * np.conj(f))[:n] / n

V_m3   = equil_state.volume.item() * 1e-30
kT_J   = 1.380649e-23 * 600.0
eV_A3_to_Pa = 1.6021766e-19 / 1e-30   # 1 eV/Å³ = 1.602e11 Pa
dt_s   = 0.001e-12

eta_Pas = (V_m3 / kT_J) * np.trapz(acf * eV_A3_to_Pa**2, dx=dt_s)
print(f"η = {eta_Pas:.3e} Pa·s")
```

---

## Part 6 — Classical reference with Fumi-Tosi

Before running with the MLIP, validate your workflow against the classical Fumi-Tosi potential for LiX systems (already implemented in `implementation-branch`). It is much faster and gives a known reference.

```python
from torch_sim.models.fumi_tosi import FumiTosiModel

model_ft = FumiTosiModel(
    atomic_number_zi=3,                           # Li
    ionic_charge_i=1,
    ionic_charge_j=-1,
    sigma_ij=torch.tensor([1.632, 2.401, 3.170]), # Li-Li, Li-Cl, Cl-Cl (Å)
    a=torch.tensor([0.04557, 1.2485, 69.29]),
    b=torch.tensor([2.920]),
    c=torch.tensor([0.01873, 1.4982, 139.21]),
    d=torch.tensor([0.04557, 1.2485, 69.29]),
    rc=7.0,
    device=device,
    dtype=torch.float32,
    compute_forces=True,
    compute_stress=True,
    use_neighbor_list=True,
)
```

Run the same RNEMD protocol with `model_ft` first to make sure units and workflow are correct, then swap in the MLIP.

---

## Part 7 — Checklist

| Step | Done? |
|---|---|
| CP2K → `training_data.extxyz` with energy, forces, stress | ☐ |
| Split 80/10/10 train/val/test | ☐ |
| MACE training: energy RMSE < 5 meV/atom, force RMSE < 0.1 eV/Å | ☐ |
| Geometry optimization of supercell with MLIP | ☐ |
| NVT equilibration (target T ± 10 K) | ☐ |
| RNEMD: κ converged (running κ flat over last 30%) | ☐ |
| Green-Kubo HFACF: κ agrees with RNEMD within 20% | ☐ |
| VACF → diffusion coefficient D | ☐ |
| g(r): first peak position matches experiment | ☐ |
| Pressure ACF → viscosity η | ☐ |
| Compare MLIP vs Fumi-Tosi (classical reference) | ☐ |

---

## Key file locations

```
torch-sim/
  torch_sim/workflows/RNEMD.py              # RNEMD driver (RNEMD class)
  torch_sim/models/mace.py                  # MaceModel (+ MaceUrls pretrained URLs)
  torch_sim/models/fairchem.py              # FairChemModel
  torch_sim/models/orb.py                   # OrbModel
  torch_sim/models/fumi_tosi.py             # FumiTosiModel (classical reference)
  torch_sim/properties/correlations.py      # VelocityAutoCorrelation, HeatFluxAutoCorrelation
  torch_sim/quantities.py                   # calc_heat_flux, compute_instantaneous_pressure_tensor
  torch_sim/neighbors/alchemiops.py         # NVIDIA nvalchemiops neighbor list (speed)

MLIP-MC/
  mlip_mc/cli.py                            # mlip_mc CLI entry point
  mlip_mc/dft/particle_gcmc.py             # General GCMC (atoms/molecules/ions)
  mlip_mc/dft/hard_rod_sim.py              # 1D hard-rod GCMC
  mlip_mc/dft/percus.py                    # Percus exact DFT (c₁ functional)
  mlip_mc/dft/widom.py                     # Widom insertion
```

## NVIDIA nvalchemiops (the "alchemy" tool)

This is **not** a dispersion correction. It is NVIDIA's CUDA-accelerated neighbor list library that torch-sim uses automatically. Priority order at runtime:

```
nvalchemiops  (fastest, NVIDIA GPU only)
vesin         (cross-platform fallback)
torch_nl      (pure PyTorch, always available)
```

Install it if you are on an NVIDIA GPU:

```bash
pip install nvalchemiops
```

torch-sim detects it automatically — no code changes needed.

D3 dispersion (long-range vdW correction) is a separate thing inside the MACE model, enabled with `dispersion=True` when loading a MACE-MP foundation model. For a fine-tuned model it is already implicit if you trained on DFT data that includes dispersion.
