# neuromc

**Neural Monte Carlo** — Grand Canonical Monte Carlo, classical density functional theory, and neural functional theory data generation, powered by machine-learned interatomic potentials.

> **Derived from** [jackevansadl/MLIP-MC](https://github.com/jackevansadl/MLIP-MC), which provides the original GCMC engine for gas adsorption in porous materials. neuromc extends that foundation with a full classical DFT subpackage, general particle GCMC for atoms/molecules/ions, Widom insertion, and a training-data pipeline for neural operators targeting the [ionax](../ionax) PNP-cDFT solver.

---

## What neuromc does

| Module | Capability |
|---|---|
| `neuromc` (core) | GCMC isotherms and Widom insertion for gas adsorption using any MLIP backend |
| `neuromc.dft` | 1D hard-rod and 3D RPM model-fluid GCMC + Percus/FMT classical DFT |
| `neuromc.dft.particle_gcmc` | General GCMC for **atoms, molecules, and ions** with any ASE calculator |
| `neuromc.dft.widom` | Widom test-particle insertion (hard rods + RPM ionic system) |
| `neuromc.dft.percus` | Percus exact 1D FMT functional with full c₁ (both convolution terms) |
| `neuromc.dft.oz` | Ornstein-Zernike inversion for c⁽²⁾ and pair correlations |

The `neuromc.dft` subpackage generates training data for neural operators that replace classical FMT+MSA functionals inside ionax, enabling fast neural cDFT/DDFT for solid electrolytes.

---

## Installation

Pick one MLIP backend. The package auto-detects whichever is installed.

```bash
# Clone
git clone https://github.com/Feugmo-Group/neuromc.git
cd neuromc

# Install with MACE backend (recommended)
pip install -e ".[mace-torch,dev]"

# Or with fairchem
pip install -e ".[fairchem,dev]"

# Or with orb-models
pip install -e ".[orb-models,dev]"

# Install the full DFT subpackage (JAX environment recommended)
pip install -e ".[dft,dev]"
```

Model weights are resolved automatically. Pass a local path or an `hf://org/repo[:filename]` URI; downloads are cached at `$NEUROMC_CACHE` (default `~/.cache/neuromc/`).

---

## CLI — gas adsorption (core)

The `neuromc` command provides two simulation modes.

### GCMC isotherm

```bash
neuromc --mode gcmc \
        --adsorbent framework.xyz \
        --adsorbate-molecule CO2 \
        --temperature 298.0 \
        --pressures 0.1,1.0,5.0 \
        --model model.pt
```

### Widom insertion (Henry coefficient)

```bash
neuromc --mode widom \
        --adsorbent framework.xyz \
        --adsorbate-molecule CO2 \
        --temperature 298.0 \
        --n-trials 10000 \
        --model model.pt
```

Output lands in `results/` by default (`--output-dir` to override):

```
results/
  isotherm_data.json          # GCMC aggregate
  log_{P}bar.bin              # binary log (authoritative)
  traj_{P}bar.xyz
  restart/restart_{P}bar.*
  widom_results.json          # Widom
  log_widom.bin
```

---

## Python API — classical DFT and model fluids

### 1D hard-rod fluid (Sammüller 2024)

```python
from neuromc.dft.hard_rod_sim import simulate
from neuromc.dft.percus import c1_percus, dft_minimize

# GCMC density profile
x, rho_mc, _ = simulate(L=30.0, mu=-1.0, T=1.0,
                         vext_fn=lambda x: 0.0,
                         n_prod=100_000)

# Percus DFT profile
x_dft, rho_dft = dft_minimize(
    L=30.0, mu=-1.0, T=1.0,
    vext_fn=lambda x: 0.0,
    c1_fn=c1_percus,
)
```

### Widom insertion

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

### General particle GCMC (atoms / molecules / ions)

Works with any ASE calculator — MLIP, classical force field, or mock.

```python
from neuromc.dft.particle_gcmc import simulate_particle_gcmc, generate_cdft_training_data
from ase.io import read

framework  = read("lipon_supercell.xyz")
li_atom    = read("Li.xyz")        # single Li atom
calculator = ...                   # any ASE Calculator

z_centers, rho, *_ = simulate_particle_gcmc(
    framework, li_atom, calculator,
    mu=-3.5, T=600.0,
)

# Generate ionax-compatible training data
dataset = generate_cdft_training_data(
    framework, li_atom, calculator,
    mu_values=[-4.0, -3.5, -3.0, -2.5],
    T=600.0,
)
# Each entry: z_nm, rho_nm3, c1, vext_kT, mu, T, avg_n
```

The `c₁(z)` values directly implement `ExcessFreeEnergy.chemical_potential()` from the ionax interface (kT units, nm grid).

---

## Architecture

Three-layer structure:

### 1. CLI / orchestration (`neuromc/cli.py`, `neuromc/main.py`)

`cli.py::main` parses arguments and dispatches to `run_gcmc` / `run_widom` in `main.py`. Model resolution (`hf://` URIs), backend detection, and calculator loading all live in `main.py`. GPU parallelism over pressures uses `multiprocessing` with the **spawn** start method — calculator imports must stay inside worker functions to preserve GPU isolation.

### 2. Physics engines (`neuromc/src/`)

- `gcmc.py` — `MLP_GCMC`: four move types (insert/delete/translate/rotate), binary log, restart files, checkpoints
- `widom.py` — `MLP_Widom`: Widom insertion for porous-material gas adsorption
- `utilities.py` — `PREOS` (Peng-Robinson EOS for fugacities), binary log readers

### 3. Classical DFT subpackage (`neuromc/dft/`)

| File | Contents |
|---|---|
| `hard_rod_sim.py` | 1D GCMC for hard rods; `HardRodSystem`, `simulate` |
| `rpm_sim.py` | 3D RPM ionic GCMC; `RPMSystem` |
| `percus.py` | Percus exact FMT; `c1_percus`, `dft_minimize` |
| `oz.py` | Ornstein-Zernike inversion; `oz_invert`, `oz_solve` |
| `widom.py` | `WidomHardRod`, `WidomRPM` and convenience drivers |
| `particle_gcmc.py` | `ParticleGCMC`, `simulate_particle_gcmc`, `generate_cdft_training_data` |
| `pair_dist.py` | Pair distribution function utilities |
| `density_grid.py` | Grid and density field helpers |
| `neural_functional.py` | Neural operator interface for trained c₁ models |
| `sample_writer.py` | HDF5 output for training datasets |
| `campaign.py` | Multi-condition campaign runner |
| `external_field.py` | External potential helpers |

---

## MLIP backends

Three backends are supported and auto-detected in order:

| Backend | Install | Notes |
|---|---|---|
| **fairchem** | `pip install fairchem-core` | UMA / eSEN foundation models |
| **mace-torch** | `pip install mace-torch` | MACE-MP; `dispersion=True` adds D3 correction |
| **orb-models** | `pip install orb-models` | Falls back to pretrained `orb_v3_conservative_inf_omat` if no local path given |

---

## Tests

```bash
pytest                                       # full suite
pytest tests/test_gcmc.py                   # core GCMC
pytest tests/test_dft_widom.py              # DFT Widom
pytest tests/test_dft_particle_gcmc.py      # particle GCMC (requires ASE)
pytest -k hard_rod                          # by keyword
pytest tests/test_gcmc.py::TestEInteractionOfAdsorption::test_calculation  # single test
```

75 tests pass without ASE. 37 additional tests (particle GCMC) require an ASE-enabled environment.

---

## Key physics

**Tonks EOS** (exact, 1D hard rods):

```
βμ = ln(ρ/(1−ρ)) + ρ/(1−ρ)
```

**Percus c₁** (full FMT functional derivative):

```
c₁(r) = [(ln(1−n₁)) ⊛ ω₀](r) − [(n₀/(1−n₁)) ⊛ ω₁](r)
```

**Sammüller identity** (neural functional training target):

```
c₁(r) = ln ρ(r) − βμ_loc(r)
```

**Widom insertion**:

```
exp(−β·μ_ex) = ⟨exp(−β·ΔU)⟩_N
```

---

## Citation

If you use neuromc, please cite the original MLIP-MC package:

```bibtex
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
