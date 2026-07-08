# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**neuromc** (Neural Monte Carlo) — derived from [jackevansadl/MLIP-MC](https://github.com/jackevansadl/MLIP-MC). Performs GCMC isotherms and Widom insertion for gas adsorption in porous materials, extended with a full classical DFT subpackage (`neuromc/dft/`) for model fluids, general particle GCMC (atoms/molecules/ions), and ionax-compatible training-data generation for neural cDFT operators.

Three interchangeable MLIP backends: **fairchem**, **mace-torch**, **orb-models** — auto-detected.

## Common commands

Install for development (pick one backend):
```bash
pip install -e ".[fairchem,dev]"       # or [mace-torch,dev] or [orb-models,dev]
pip install -e ".[dft,dev]"            # DFT subpackage (JAX env recommended)
```

Run the CLI (installed as `neuromc`, defined at `neuromc/cli.py`):
```bash
neuromc --mode gcmc  --adsorbent framework.xyz --adsorbate-molecule CO2 \
        --temperature 298.0 --pressures 0.1,1.0,5.0 --model model.pt
neuromc --mode widom --adsorbent framework.xyz --adsorbate-molecule CO2 \
        --temperature 298.0 --n-trials 10000 --model model.pt
```

Models may be a local path or an `hf://org/repo[:filename]` URI; downloads cached at `$NEUROMC_CACHE` (default `~/.cache/neuromc/`).

Tests (pytest):
```bash
pytest                              # full suite
pytest tests/test_gcmc.py           # single file
pytest tests/test_gcmc.py::TestEInteractionOfAdsorption::test_calculation
pytest -k widom                     # by keyword
```

## Architecture

Three-layer structure — keep this separation intact when editing:

1. **CLI / orchestration** (`neuromc/cli.py`, `neuromc/main.py`)
   - `cli.py::main` parses args and dispatches to `run_gcmc` / `run_widom` in `main.py`.
   - `main.py` handles model resolution (`_resolve_model_spec` for `hf://`), HF caching, backend detection (`_detect_backend`), calculator loading (`_load_model`), structure loading, result aggregation, and all banner/table output.
   - Warning/logging filters are installed at `main.py` module scope — they must stay there because `mp.set_start_method('spawn')` re-imports the module in each worker.
   - The repo-root `main.py` is a thin shim importing from `neuromc.main`; keep them consistent.

2. **Physics engines** (`neuromc/src/gcmc.py`, `neuromc/src/widom.py`)
   - `MLP_GCMC`: four move types (insert/delete/translate/rotate), binary log (`log_{P}bar.bin`), restart files (`restart/`), checkpoints (`checkpoints_{P}bar/`). Restart-from-crash is first-class — check the restart path before changing log/checkpoint formats.
   - `MLP_Widom`: Widom insertion for porous-material adsorption; shares `random_position` and `vdw_overlap` helpers with the GCMC engine.
   - Both receive a pre-constructed ASE calculator as `model` and know nothing about backends.

3. **Utilities** (`neuromc/src/utilities.py`)
   - `PREOS` computes fugacities from `neuromc/data/critical_acentric.csv`; falls back to ideal-gas if adsorbate is missing — preserve this fallback.
   - `read_binary_log` / `read_widom_binary_log` parse the struct-packed binary log; re-exported from `neuromc/__init__.py` as public API.

4. **DFT subpackage** (`neuromc/dft/`)
   - `hard_rod_sim.py` — 1D GCMC (`HardRodSystem`, `simulate`). Sweep uses fixed-rate GC moves (not N-scaling) for detailed balance.
   - `rpm_sim.py` — 3D RPM ionic GCMC (`RPMSystem`).
   - `percus.py` — Percus exact FMT: `c1_percus` includes both convolution terms (ln(1−n₁) ⊛ ω₀ and n₀/(1−n₁) ⊛ ω₁). Do not simplify.
   - `oz.py` — Ornstein-Zernike inversion.
   - `widom.py` — `WidomHardRod`, `WidomRPM`.
   - `particle_gcmc.py` — `ParticleGCMC` (atoms/molecules/ions with any ASE calculator); `generate_cdft_training_data` outputs ionax-compatible c₁ profiles (kT units, nm grid). ASE is imported lazily inside methods — the `neuromc.dft` package works without ASE.

### GPU parallelism model

GCMC over multiple pressures uses `multiprocessing.Process` with **spawn** (`main.py::run_gcmc`). Each worker sets `CUDA_VISIBLE_DEVICES` / `HIP_VISIBLE_DEVICES` before importing torch — that is why `_load_model` and backend imports live inside `run_single_pressure`. Do not hoist them out. Inside a worker the device is always `'cuda'` (index 0 after masking).

### Backend abstraction

`_detect_backend` probes in order: fairchem → mace-torch → orb-models. orb-models falls back to `pretrained.orb_v3_conservative_inf_omat` when no local model path exists — preserve this.

### Output layout

- GCMC: `isotherm_data.json`, `log_{P}bar.bin`, `traj_{P}bar.xyz`, `restart/`, `checkpoints_{P}bar/`.
- Widom: `widom_results.json`, `log_widom.bin`, `widom_trajectory.xyz`, `restart/`.

Binary log is authoritative; averages in JSON are re-derived from it.
