# neuromc

**Neural Monte Carlo** — training-data generation for neural classical density functional theory (cDFT) operators, via Grand Canonical Monte Carlo and Widom insertion with machine-learned interatomic potentials.

> **Derived from** [jackevansadl/MLIP-MC](https://github.com/jackevansadl/MLIP-MC). The original package targets gas adsorption in porous materials; neuromc repurposes and extends the same GCMC engine to generate density profiles, excess chemical potentials, and c₁ functionals for training neural operators that replace classical FMT+MSA functionals inside [ionax](https://github.com/Feugmo-Group/ionax).

---

## Project tools

neuromc is part of a three-package ecosystem:

| Package | Role | Repo |
|---|---|---|
| **neuromc** | Generate MC/GCMC training data (density profiles, c₁, μ_ex) | this repo |
| **ionax** | JAX-based PNP + cDFT/DDFT solver; target for the neural operators | `../ionax` |
| **torch-sim** | GPU MD engine; RNEMD, Green-Kubo, g(r), viscosity after MLIP training | `../torch-sim` (`implementation-branch`) |

The intended workflow:

```
neuromc  →  training dataset (z, ρ, c₁, V_ext)
    ↓
Train neural operator  (replaces FMT+MSA in ionax)
    ↓
ionax  →  fast neural cDFT/DDFT for solid electrolytes
    ↓
torch-sim  →  MD transport properties (κ, D, η, g(r))
```

### torch-sim — what is implemented (`implementation-branch`)

Transport property calculations live in the `implementation-branch` of torch-sim:

| Feature | Class / function | File |
|---|---|---|
| Thermal conductivity (RNEMD) | `RNEMD` | `torch_sim/workflows/RNEMD.py` |
| Thermal conductivity (Green-Kubo) | `HeatFluxAutoCorrelation` | `torch_sim/properties/correlations.py` |
| Diffusion coefficient | `VelocityAutoCorrelation` | `torch_sim/properties/correlations.py` |
| Radial distribution function g(r) | `RadialDistributionFunction` | `torch_sim/properties/correlations.py` |
| Shear viscosity (Green-Kubo) | `PressureAutoCorrelation` | `torch_sim/properties/correlations.py` |
| Classical ionic reference | `FumiTosiModel` | `torch_sim/models/fumi_tosi.py` |

**Neighbor-list acceleration — NVIDIA nvalchemiops**: torch-sim automatically uses [`nvalchemiops`](https://github.com/NVIDIA/nvalchemiops), NVIDIA's CUDA-accelerated neighbor-list library, when it is installed. This is purely a speed optimization (it is not a dispersion correction) that accelerates the pair-distance search at every MD step. Priority order at runtime:

```
nvalchemiops  (CUDA kernel, fastest — NVIDIA GPU only)
vesin         (cross-platform, fast)
torch_nl      (pure PyTorch, always available)
```

Install on NVIDIA hardware:

```bash
pip install nvalchemiops
```

No code changes are needed — `torchsim_nl()` detects and uses it automatically.

---

## What neuromc generates

| Module | Output |
|---|---|
| `neuromc.dft.hard_rod_sim` | 1D GCMC density profiles ρ(x) for hard-rod model fluid |
| `neuromc.dft.rpm_sim` | 3D RPM ionic GCMC density profiles ρ±(z) |
| `neuromc.dft.particle_gcmc` | GCMC density profiles for **atoms, molecules, or ions** with any MLIP |
| `neuromc.dft.widom` | Excess chemical potential μ_ex via Widom insertion |
| `neuromc.dft.percus` | Exact Percus/FMT c₁ functional (1D reference) |
| `neuromc.dft.oz` | Ornstein-Zernike inversion for pair correlations c⁽²⁾ |
| `neuromc.dft.generate_cdft_training_data` | ionax-compatible dataset: (z_nm, ρ_nm³, c₁, V_ext, μ, T) |

---

## Installation

### With uv (recommended)

```bash
git clone https://github.com/Feugmo-Group/neuromc.git
cd neuromc

# Core + DFT subpackage
uv sync --extra dft

# Core + MACE backend + DFT
uv sync --extra mace-torch --extra dft

# Core + fairchem backend
uv sync --extra fairchem

# Core + orb-models backend
uv sync --extra orb-models

# Everything
uv sync --extra full
```

### With pip

```bash
git clone https://github.com/Feugmo-Group/neuromc.git
cd neuromc

# Core + MACE backend (recommended)
pip install -e ".[mace-torch,dft,dev]"

# Or with fairchem
pip install -e ".[fairchem,dft,dev]"

# Or with orb-models
pip install -e ".[orb-models,dft,dev]"
```

### Optional dependencies summary

| Extra | What it adds |
|---|---|
| `mace-torch` | MACE-MP MLIP backend |
| `fairchem` | fairchem / UMA MLIP backend |
| `orb-models` | orb-models MLIP backend |
| `dft` | JAX, equinox, optax, scipy — needed for `neuromc.dft` |
| `full` | `dft` + MACE in one command |
| `dev` | pytest, ruff |

Model weights are resolved automatically. Pass a local path or an `hf://org/repo[:filename]` URI; downloads are cached at `$NEUROMC_CACHE` (default `~/.cache/neuromc/`).

---

## Python API

### Generate ionax-compatible training data (main use case)

```python
from neuromc.dft.particle_gcmc import generate_cdft_training_data
from ase.io import read

framework  = read("lipon_supercell.xyz")   # host structure
li_atom    = read("Li.xyz")                # particle to insert
calculator = ...                           # any ASE Calculator (MACE, orb, etc.)

dataset = generate_cdft_training_data(
    framework, li_atom, calculator,
    mu_values=[-4.0, -3.5, -3.0, -2.5],   # chemical potentials (eV)
    T=600.0,                                # temperature (K)
)

# Each entry in dataset:
# {
#   'z_nm'     : np.ndarray  — grid positions in nm
#   'rho_nm3'  : np.ndarray  — density in nm⁻³
#   'c1'       : np.ndarray  — one-body direct correlation (kT units)
#   'vext_kT'  : np.ndarray  — external potential (kT units)
#   'mu'       : float       — chemical potential (eV)
#   'T'        : float       — temperature (K)
#   'avg_n'    : float       — average particle count
# }
```

The `c₁(z)` column is the training target for a neural operator implementing `ExcessFreeEnergy.chemical_potential()` in ionax.

### 1D hard-rod model fluid (Sammüller 2024 benchmark)

```python
from neuromc.dft.hard_rod_sim import simulate
from neuromc.dft.percus import c1_percus, dft_minimize

# GCMC density profile
x, rho_mc, _ = simulate(L=30.0, mu=-1.0, T=1.0,
                         vext_fn=lambda x: 0.0,
                         n_prod=100_000)

# Exact Percus DFT profile
x_dft, rho_dft = dft_minimize(
    L=30.0, mu=-1.0, T=1.0,
    vext_fn=lambda x: 0.0,
    c1_fn=c1_percus,
)
```

### Widom insertion — excess chemical potential

```python
from neuromc.dft.widom import widom_hard_rod, widom_rpm

# Hard rods
result = widom_hard_rod(L=30.0, mu=-1.0, T=1.0)
print(f"mu_ex = {result['mu_ex']:.4f},  henry = {result['henry']:.4f}")

# RPM ionic system
result = widom_rpm(Lx=10.0, Ly=10.0, Lz=20.0,
                   mu_plus=-2.0, mu_minus=-2.0)
print(f"mu_ex+/- = {result['mu_ex_plus']:.3f}, {result['mu_ex_minus']:.3f}")
```

### GCMC density profile for any particle

```python
from neuromc.dft.particle_gcmc import simulate_particle_gcmc

z_centers, rho, mu, T, avg_n, n_trace, system = simulate_particle_gcmc(
    framework, li_atom, calculator,
    mu=-3.5, T=600.0,
)
```

---

## Architecture

### 1. DFT subpackage (`neuromc/dft/`) — primary

| File | Contents |
|---|---|
| `particle_gcmc.py` | `ParticleGCMC`, `simulate_particle_gcmc`, `generate_cdft_training_data` |
| `hard_rod_sim.py` | 1D GCMC: `HardRodSystem`, `simulate`, `generate_random_vext` |
| `rpm_sim.py` | 3D RPM ionic GCMC: `RPMSystem` |
| `percus.py` | Percus exact FMT: `c1_percus`, `dft_minimize` |
| `oz.py` | Ornstein-Zernike inversion: `oz_invert`, `oz_solve` |
| `widom.py` | `WidomHardRod`, `WidomRPM`, convenience drivers |
| `neural_functional.py` | Neural operator interface for trained c₁ models |
| `sample_writer.py` | HDF5 writer for training datasets |
| `campaign.py` | Multi-condition campaign runner |
| `density_grid.py` | Grid and density field helpers |
| `pair_dist.py` | Pair distribution utilities |
| `external_field.py` | External potential helpers |

ASE is imported lazily inside methods — `neuromc.dft` works without ASE for pure model-fluid calculations.

### 2. MLIP-MC legacy engines (`neuromc/src/`) — inherited

Retained from the original MLIP-MC for porous-material adsorption use cases:

- `gcmc.py` — `MLP_GCMC`: four move types, binary log, restart, checkpoints
- `widom.py` — `MLP_Widom`: Widom insertion with MLIP energy
- `utilities.py` — `PREOS` (Peng-Robinson EOS), binary log readers

### 3. CLI (`neuromc/cli.py`, `neuromc/main.py`) — inherited

Retained from MLIP-MC. Dispatches `--mode gcmc` and `--mode widom` for MLIP-driven porous-material simulations. GPU parallelism over pressures uses `multiprocessing` with the **spawn** start method; MLIP imports stay inside worker functions to preserve GPU isolation.

---

## MLIP backends

Three backends are supported and auto-detected in order:

| Backend | Extra | Notes |
|---|---|---|
| **fairchem** | `fairchem` | UMA / eSEN foundation models |
| **mace-torch** | `mace-torch` | MACE-MP; `dispersion=True` for D3 correction |
| **orb-models** | `orb-models` | Falls back to `orb_v3_conservative_inf_omat` if no local path given |

---

## Tests

```bash
pytest                                                               # full suite
pytest tests/test_dft_widom.py                                      # Widom insertion
pytest tests/test_dft_particle_gcmc.py                              # particle GCMC (requires ASE)
pytest tests/test_gcmc.py                                           # legacy GCMC
pytest -k hard_rod                                                   # by keyword
pytest tests/test_gcmc.py::TestEInteractionOfAdsorption::test_calculation
```

75 tests pass without ASE. 37 additional tests (particle GCMC) require an ASE-enabled environment.

---

## Key physics

**Sammüller identity** — neural functional training target:

```
c₁(r) = ln ρ(r) − βμ_loc(r)
```

**Percus c₁** — full FMT functional derivative (1D exact):

```
c₁(r) = [(ln(1−n₁)) ⊛ ω₀](r) − [(n₀/(1−n₁)) ⊛ ω₁](r)
```

**Tonks EOS** — exact bulk 1D hard-rod equation of state:

```
βμ = ln(ρ/(1−ρ)) + ρ/(1−ρ)
```

**Widom insertion**:

```
exp(−β·μ_ex) = ⟨exp(−β·ΔU)⟩_N
```

---

## Paper examples

### Sammüller et al. 2024 — Neural functional theory for 1D hard rods

The Sammüller workflow trains a neural operator to learn c₁([ρ]) from GCMC data.
neuromc reproduces this entirely in Python using the hard-rod engine and Percus reference.

```python
import numpy as np
from neuromc.dft.hard_rod_sim import simulate, generate_random_vext
from neuromc.dft.percus import c1_percus, dft_minimize
from neuromc.dft.widom import widom_hard_rod

L, T = 20.0, 1.0
rng = np.random.default_rng(42)

# ── Step 1: generate training snapshots under random external potentials ──────
dataset = []
for _ in range(200):
    vext_fn = generate_random_vext(L, rng=rng, n_sin=3, amplitude=2.0)
    mu = rng.uniform(-2.0, 0.5)

    x, rho, mu_loc = simulate(L=L, mu=mu, T=T, vext_fn=vext_fn,
                               n_equil=5_000, n_prod=50_000)

    # Sammüller identity: c₁(x) = ln ρ(x) − βμ_loc(x)
    # (set ρ floor to avoid log(0))
    c1 = np.log(np.maximum(rho, 1e-12)) - mu_loc

    dataset.append({"x": x, "rho": rho, "c1": c1,
                    "vext": np.array([vext_fn(xi) for xi in x]),
                    "mu": mu})

# ── Step 2: compare GCMC density to Percus DFT on a new profile ──────────────
vext_test = generate_random_vext(L, rng=rng)
x_dft, rho_dft = dft_minimize(L=L, mu=-0.5, T=T,
                               vext_fn=vext_test, c1_fn=c1_percus)
x_mc, rho_mc, _ = simulate(L=L, mu=-0.5, T=T, vext_fn=vext_test,
                             n_prod=100_000)

# ── Step 3: Widom — excess chemical potential ─────────────────────────────────
res = widom_hard_rod(L=L, mu=-0.5, T=T)
print(f"mu_ex = {res['mu_ex']:.4f}   (exact: {-np.log(1 - rho_mc.mean()):.4f})")
```

The `dataset` list — with fields `x`, `rho`, `c1`, `vext`, `mu` — is the direct input
for training the neural functional in the Sammüller 2024 tutorial
([sfalmo/NeuralDFT-Tutorial](https://github.com/sfalmo/NeuralDFT-Tutorial)).

---

### Bui & Cox 2025 — Ionic structure at electrified interfaces

The Bui & Cox workflow uses the 3D RPM model to generate ionic density profiles ρ±(z)
near a charged wall and compute μ_ex± for each species.

```python
import numpy as np
from neuromc.dft.rpm_sim import RPMSystem
from neuromc.dft.widom import widom_rpm

# ── System parameters ─────────────────────────────────────────────────────────
Lx, Ly, Lz = 10.0, 10.0, 30.0   # box dimensions (σ units; σ = ion diameter)
mu_plus  = -3.0                   # β·μ for cations
mu_minus = -3.0                   # β·μ for anions
beta     = 1.0                    # inverse temperature

# ── Step 1: equilibrate the RPM system ───────────────────────────────────────
rng = np.random.default_rng(0)
system = RPMSystem(Lx=Lx, Ly=Ly, Lz=Lz,
                   mu_plus=mu_plus, mu_minus=mu_minus,
                   beta=beta, rng=rng)

for _ in range(5_000):
    system.sweep(n_transitions=100)

# ── Step 2: production — accumulate density profiles ─────────────────────────
n_bins = 100
z_edges = np.linspace(system.z_wall, Lz - system.z_wall, n_bins + 1)
dz = z_edges[1] - z_edges[0]
hist_plus  = np.zeros(n_bins)
hist_minus = np.zeros(n_bins)

for _ in range(20_000):
    system.sweep(n_transitions=100)
    if system.n_plus > 0:
        import numpy as _np
        pos_p = _np.array(system._pos_plus)
        hist_plus  += _np.histogram(pos_p[:, 2],  bins=z_edges)[0]
    if system.n_minus > 0:
        pos_m = _np.array(system._pos_minus)
        hist_minus += _np.histogram(pos_m[:, 2], bins=z_edges)[0]

bin_vol = Lx * Ly * dz
rho_plus  = hist_plus  / (20_000 * bin_vol)
rho_minus = hist_minus / (20_000 * bin_vol)
z_centers = 0.5 * (z_edges[:-1] + z_edges[1:])

# ── Step 3: Widom insertion — μ_ex for each species ──────────────────────────
res = widom_rpm(Lx=Lx, Ly=Ly, Lz=Lz,
                mu_plus=mu_plus, mu_minus=mu_minus,
                beta=beta, n_equil=2_000, n_prod=10_000)

print(f"mu_ex(+) = {res['mu_ex_plus']:.4f}")
print(f"mu_ex(-) = {res['mu_ex_minus']:.4f}")

# ── Step 4: c₁±(z) as ionax training target ──────────────────────────────────
# c₁(z) = ln ρ(z) − βμ_loc(z)   (no external potential here → μ_loc = μ)
c1_plus  = np.log(np.maximum(rho_plus,  1e-12)) - mu_plus
c1_minus = np.log(np.maximum(rho_minus, 1e-12)) - mu_minus

# Convert to ionax units (nm, nm⁻³)
_ANG_TO_NM = 0.1
z_nm      = z_centers * _ANG_TO_NM
rho_p_nm3 = rho_plus  * 1000.0
rho_m_nm3 = rho_minus * 1000.0
```

The `(z_nm, rho_p_nm3, c1_plus)` and `(z_nm, rho_m_nm3, c1_minus)` arrays are
directly compatible with the `ExcessFreeEnergy.chemical_potential()` interface in ionax.

---

## Citation

If you use neuromc, please cite both this package and the original MLIP-MC it is derived from:

```bibtex
@software{neuromc,
  title  = {{neuromc}: Neural Monte Carlo --- Training-Data Generation for Neural
            cDFT Operators with Machine-Learned Interatomic Potentials},
  author = {Tetsassi Feugmo, Conrard},
  url    = {https://github.com/Feugmo-Group/neuromc},
  year   = {2026},
}

@software{mlip_mc,
  title  = {{MLIP-MC}: Monte Carlo Simulations with Machine-Learned Interatomic Potentials},
  author = {Evans, Jack D. and others},
  url    = {https://github.com/jackevansadl/MLIP-MC},
}
```

For the classical DFT and neural functional theory components:

```bibtex
@article{sammüller2024neural,
  title   = {Neural functional theory for inhomogeneous fluids: Fundamentals and applications},
  author  = {Samm{\"u}ller, Florian and Hermann, Sophie and Schmidt, Matthias},
  journal = {J. Phys.: Condens. Matter},
  volume  = {36},
  pages   = {243002},
  year    = {2024},
}

@article{bui2025ionic,
  title   = {Ionic Structure at Electrified Interfaces from Classical Density Functional Theory},
  author  = {Bui, Alice T. and Cox, Stephen J.},
  journal = {Phys. Rev. Lett.},
  volume  = {134},
  pages   = {148001},
  year    = {2025},
}
```
