#!/usr/bin/env python3
"""
Command-line interface for neuromc.

This module provides the CLI entry point for running GCMC isotherm simulations
and Widom insertion calculations.
"""

import sys
import argparse
import multiprocessing as mp
import traceback
from pathlib import Path
from typing import Union, List
from .main import run_gcmc, run_widom


def parse_pressures(pressure_str: str) -> Union[float, List[float]]:
    """
    Parse pressure string into float or list of floats.
    
    Parameters
    ----------
    pressure_str : str
        Comma-separated list of pressures or a single number
        
    Returns
    -------
    Union[float, List[float]]
        Single pressure value or list of pressure values
        
    Raises
    ------
    ValueError
        If the pressure string cannot be parsed
    """
    parts = [p.strip() for p in pressure_str.split(',')]
    
    if len(parts) == 1:
        return float(parts[0])
    
    return [float(p) for p in parts]


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='neuromc: Monte Carlo Simulations with Machine-Learned Interatomic Potentials',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # GCMC: Multiple pressure points
  neuromc \\
      --mode gcmc \\
      --adsorbent framework.xyz \\
      --adsorbate-molecule CO2 \\
      --temperature 298.0 \\
      --pressures 0.1,0.5,1.0,2.0,5.0 \\
      --n-equil 10000 \\
      --n-prod 20000 \\
      --output-dir my_results

  # GCMC: Single pressure point
  neuromc \\
      --mode gcmc \\
      --adsorbent framework.xyz \\
      --adsorbate-molecule CO2 \\
      --temperature 298.0 \\
      --pressures 1.0 \\
      --n-equil 5000 \\
      --n-prod 15000

  # Widom insertion
  neuromc \\
      --mode widom \\
      --adsorbent framework.xyz \\
      --adsorbate-molecule CO2 \\
      --temperature 298.0 \\
      --n-trials 10000 \\
      --output-dir widom_results
        """
    )
    
    parser.add_argument('--mode', type=str, default='gcmc', choices=['gcmc', 'widom', 'dft-data'],
                        help='Simulation mode: gcmc, widom, or dft-data (cDFT neural-operator data generation)')
    parser.add_argument('--adsorbent', type=str, required=True,
                        help='Path to adsorbent structure file (.xyz, .cif, etc.)')
    parser.add_argument('--adsorbate-path', type=str, default=None,
                        help='Path to adsorbate structure file (.xyz, .cif, etc.)')
    parser.add_argument('--adsorbate-molecule', type=str, default=None,
                        help='Name of adsorbate molecule (e.g., CO2, CH4) if not using file')
    parser.add_argument('--temperature', type=float, required=True,
                        help='Temperature in Kelvin (required)')
    parser.add_argument('--pressures', type=str, default=None,
                        help='Comma-separated list of pressures in bar, or single number (required for GCMC mode)')
    parser.add_argument('--n-equil', type=int, default=10000,
                        help='Number of equilibration steps for GCMC (default: 10000)')
    parser.add_argument('--n-prod', type=int, default=20000,
                        help='Number of production steps for GCMC (default: 20000)')
    parser.add_argument('--n-trials', type=int, default=10000,
                        help='Number of Widom insertion trials (default: 10000)')
    parser.add_argument('--model', type=str, required=True,
                        help='Path to MLIP model file (required). Can be a local path or Hugging Face URI (e.g., hf://your-org/your-repo).')
    parser.add_argument('--hf-token', type=str, default=None,
                        help='Hugging Face authentication token (optional, uses cached token if available)')
    parser.add_argument('--output-dir', type=str, default='results',
                        help='Output directory for results (default: results)')
    parser.add_argument('--gpu-id', type=int, default=0,
                        help='GPU device ID to use (for Widom mode, default: 0, use -1 for CPU)')
    parser.add_argument('--checkpoint-interval', type=int, default=10000,
                        help='Interval for saving checkpoints (default: 10000)')
    parser.add_argument('--write-trajectory', action='store_true',
                        help='Write trajectory files')
    parser.add_argument('--trajectory-interval', type=int, default=100,
                        help='Interval for writing structures (default: 100)')
    parser.add_argument('--overwrite-checkpoints', action='store_true',
                        help='Write trajectory files')
    # ── dft-data mode ────────────────────────────────────────────────────
    parser.add_argument('--campaign-config', type=str, default=None,
                        help='Path to campaign YAML config (required for --mode dft-data)')
    parser.add_argument('--mu-values', type=str, default=None,
                        help='Comma-separated chemical potentials in eV (overrides campaign config)')
    parser.add_argument('--n-runs', type=int, default=None,
                        help='Number of random V_ext draws per (T, μ) combo (overrides campaign config)')
    parser.add_argument('--n-blocks', type=int, default=10,
                        help='Number of production blocks for density block-averaging (default: 10)')
    parser.add_argument('--grid-dx', type=float, default=None,
                        help='Bin width for density histogram [Å] (overrides n-bins in campaign config)')
    parser.add_argument('--v-ext-config', type=str, default=None,
                        help='Path to V_ext primitive YAML (overrides v_ext section in campaign config)')
    return parser.parse_args()


def main() -> None:
    """Main entry point for the CLI."""
    try:
        mp.set_start_method('spawn')
    except RuntimeError:
        pass
    
    args = parse_arguments()
    
    # Validate arguments (dft-data mode may use campaign config for adsorbate)
    if args.mode != 'dft-data' and not args.adsorbate_path and not args.adsorbate_molecule:
        print("ERROR: Either --adsorbate-path or --adsorbate-molecule must be provided",
              file=sys.stderr)
        sys.exit(1)
    
    # Handle GPU ID for Widom mode
    gpu_id = args.gpu_id if args.gpu_id >= 0 else 'cpu'
    
    # Run simulation based on mode
    try:
        if args.mode == 'widom':
            # Widom insertion mode
            if args.pressures is not None:
                print("WARNING: --pressures is ignored in Widom mode", file=sys.stderr)
            
            run_widom(
                adsorbent_path=args.adsorbent,
                adsorbate_path=args.adsorbate_path,
                adsorbate_molecule=args.adsorbate_molecule,
                temperature=args.temperature,
                n_trials=args.n_trials,
                model_path=args.model,
                output_dir=args.output_dir,
                hf_token=args.hf_token,
                gpu_id=gpu_id
            )
        elif args.mode == 'gcmc':
            # GCMC mode
            if args.pressures is None:
                print("ERROR: --pressures is required for GCMC mode", file=sys.stderr)
                sys.exit(1)

            try:
                pressure_points = parse_pressures(args.pressures)
            except ValueError:
                print(f"ERROR: Invalid pressure format: {args.pressures}", file=sys.stderr)
                print("Please provide comma-separated numbers or a single number", file=sys.stderr)
                sys.exit(1)

            run_gcmc(
                adsorbent_path=args.adsorbent,
                adsorbate_path=args.adsorbate_path,
                adsorbate_molecule=args.adsorbate_molecule,
                temperature=args.temperature,
                pressure_points=pressure_points,
                n_equilibration_steps=args.n_equil,
                n_production_steps=args.n_prod,
                model_path=args.model,
                output_dir=args.output_dir,
                hf_token=args.hf_token,
                checkpoint_interval=args.checkpoint_interval,
                write_trajectory=args.write_trajectory,
                trajectory_interval=args.trajectory_interval,
                overwrite_checkpoints=args.overwrite_checkpoints,
            )
        elif args.mode == 'dft-data':
            _run_dft_data(args)

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


def _run_dft_data(args) -> None:
    """Entry point for --mode dft-data."""
    try:
        import yaml
    except ImportError:
        print("ERROR: pyyaml is required for dft-data mode: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    from .dft.campaign import GCMCCampaign
    from .main import _detect_backend, _load_model, _resolve_model_spec, download_model_from_huggingface
    import os

    # Load campaign config
    if args.campaign_config is None:
        print("ERROR: --campaign-config is required for --mode dft-data", file=sys.stderr)
        sys.exit(1)

    with open(args.campaign_config) as f:
        cfg = yaml.safe_load(f)

    # CLI overrides
    if args.temperature is not None:
        cfg["temperature"] = args.temperature
    if args.mu_values is not None:
        cfg["mu_values"] = [float(v) for v in args.mu_values.split(",")]
    if args.n_runs is not None:
        cfg["n_runs"] = args.n_runs
    if args.n_equil is not None:
        cfg["n_equilibration_steps"] = args.n_equil
    if args.n_prod is not None:
        cfg["n_production_steps"] = args.n_prod
    if args.output_dir != 'results':
        cfg["output_dir"] = args.output_dir
    if args.v_ext_config is not None:
        with open(args.v_ext_config) as f2:
            cfg["v_ext"] = yaml.safe_load(f2)
    if args.grid_dx is not None:
        box_z = 20.0   # will be overridden from actual structure
        cfg.setdefault("grid", {})["n_bins"] = max(1, int(box_z / args.grid_dx))
    cfg.setdefault("grid", {})["n_blocks"] = args.n_blocks

    # Model
    model_spec = args.model or cfg.get("model")
    if not model_spec:
        print("ERROR: --model is required", file=sys.stderr)
        sys.exit(1)

    model_path, hf_repo_id, hf_filename, is_hf = _resolve_model_spec(model_spec)
    if is_hf and not os.path.exists(model_path):
        model_path = download_model_from_huggingface(
            model_path, repo_id=hf_repo_id, filename=hf_filename,
            token=args.hf_token,
        )

    gpu_id = args.gpu_id if hasattr(args, 'gpu_id') and args.gpu_id >= 0 else 0
    try:
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    except ImportError:
        device = 'cpu'

    backend = _detect_backend()
    model = _load_model(model_path, device=device, backend=backend)

    # Override adsorbent/adsorbate if provided on CLI
    if args.adsorbent:
        cfg["adsorbent"] = args.adsorbent
    if args.adsorbate_path:
        cfg["adsorbate_path"] = args.adsorbate_path
    if args.adsorbate_molecule:
        cfg["adsorbate_molecule"] = args.adsorbate_molecule

    campaign = GCMCCampaign(config=cfg, model=model)
    campaign.run()


if __name__ == "__main__":
    main()

