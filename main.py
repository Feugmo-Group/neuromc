#!/usr/bin/env python3
"""
neuromc — Neural Monte Carlo

Standalone entry point. Imports from the neuromc package to avoid duplication.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent.absolute()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from neuromc.main import main
except ImportError as e:
    print("ERROR: Could not import neuromc package.")
    print(f"Import error: {e}")
    print("\nPlease install: pip install -e .")
    sys.exit(1)

if __name__ == "__main__":
    main()
