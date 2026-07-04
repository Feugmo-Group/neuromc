# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

MLIP-MC performs Monte Carlo simulations (GCMC isotherms and Widom insertion) of gas adsorption in porous materials using machine-learned interatomic potentials on top of the ASE framework. Three interchangeable MLIP backends are supported: **fairchem**, **mace-torch**, and **orb-models** — the package auto-detects whichever one is installed.

## Common commands

Install for development (pick one backend):
```bash
pip install -e ".[fairchem,dev]"       # or [mace-torch,dev] or [orb-models,dev]
```

Run the CLI (installed as `mlip_mc`, defined at `mlip_mc/cli.py`):
```bash
mlip_mc --mode gcmc  --adsorbent framework.xyz --adsorbate-molecule CO2 \
        --temperature 298.0 --pressures 0.1,1.0,5.0 --model model.pt
mlip_mc --mode widom --adsorbent framework.xyz --adsorbate-molecule CO2 \
        --temperature 298.0 --n-trials 10000 --model model.pt
```

Models may be a local path or an `hf://org/repo[:filename]` URI; downloads are cached at `$MLIP_MC_CACHE` (default `~/.cache/mlip-mc/<repo>/<filename>`).

Tests (pytest):
```bash
pytest                              # full suite
pytest tests/test_gcmc.py           # single file
pytest tests/test_gcmc.py::TestEInteractionOfAdsorption::test_calculation  # single test
pytest -k widom                     # by keyword
```

## Architecture

Three-layer structure — keep this separation intact when editing:

1. **CLI / orchestration** (`mlip_mc/cli.py`, `mlip_mc/main.py`)
   - `cli.py::main` parses args and dispatches to `run_gcmc` / `run_widom` in `main.py`.
   - `main.py` handles model resolution (`_resolve_model_spec` for the `hf://` scheme), HF download/caching, backend detection (`_detect_backend`), calculator loading (`_load_model`), structure loading via ASE, and result aggregation. It also owns all pretty-printed banner/table output.
   - `main.py` at the top-level module scope installs warning/logging filters — these must stay at module scope because `mp.set_start_method('spawn')` re-imports this module inside each worker process, and the filters need to reapply there.
   - The top-level `main.py` in the repo root is a thin shim that imports from `mlip_mc.main`; keep them consistent.

2. **Physics engines** (`mlip_mc/src/gcmc.py`, `mlip_mc/src/widom.py`)
   - `MLP_GCMC` implements Grand Canonical MC with four move types (insertion / deletion / translation / rotation, thresholds in `MOVE_PROBABILITIES`). It writes a binary log (`log_{P}bar.bin`), per-step restart files under `restart/`, periodic checkpoints under `checkpoints_{P}bar/`, and an optional trajectory. Restart-from-crash is a first-class feature — check the restart-loading path before changing log/checkpoint formats.
   - `MLP_Widom` implements Widom insertion; only computes energies of random insertions and tracks Boltzmann-weighted averages. It shares helpers (`random_position`, `vdw_overlap`) with the GCMC engine.
   - Both take a pre-constructed ASE calculator as `model` — they do not know about backends.

3. **Utilities** (`mlip_mc/src/utilities.py`)
   - `PREOS` (Peng-Robinson equation of state) computes fugacities from critical-property table `mlip_mc/data/critical_acentric.csv`. If the adsorbate name is missing from the table, callers fall back to ideal-gas (`fugacity = P`) — preserve this fallback.
   - `read_binary_log` / `read_widom_binary_log` parse the custom struct-packed binary log format; these are part of the public API (re-exported from `mlip_mc/__init__.py`) and consumers depend on their record layout.

### GPU parallelism model

GCMC over multiple pressures uses `multiprocessing.Process` with the **spawn** start method (`main.py::run_gcmc`). Each worker sets `CUDA_VISIBLE_DEVICES` / `HIP_VISIBLE_DEVICES` **before** importing torch or the MLIP backend — this is why `_load_model` and its imports live inside `run_single_pressure` rather than at module top. Do not hoist those imports out; doing so breaks GPU isolation. Inside a worker the device is always `'cuda'` (never `'cuda:N'`), because masking makes the selected GPU appear as index 0.

### Backend abstraction

`_detect_backend` probes installed packages in a fixed order (fairchem → mace-torch → orb-models) and `_load_model` branches on the returned name. orb-models is special: if the user-supplied `model_path` does not exist on disk, `_load_model` falls back to the pretrained checkpoint (`pretrained.orb_v3_conservative_inf_omat`) rather than erroring. Preserve that behavior for orb-models specifically.

### Output layout

Every run writes to `output_dir` (default `results/`):
- GCMC: `isotherm_data.json` (aggregate), plus per-pressure `log_{P}bar.bin`, `traj_{P}bar.xyz`, `restart/restart_{P}bar.{xyz,json}`, `checkpoints_{P}bar/checkpoint_{step}/`.
- Widom: `widom_results.json`, `log_widom.bin`, `widom_trajectory.xyz`, `restart/restart_widom.{xyz,json}`.

The binary log is authoritative — averages in `isotherm_data.json` are re-derived from it in `run_single_pressure` (falling back to `.npz` / `.json` legacy formats if the `.bin` is absent).
