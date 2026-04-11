#!/usr/bin/env python3
"""Compatibility wrapper for running obbyinstaller from a source checkout."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from obbyconfigs.installer import main

if __name__ == "__main__":
    raise SystemExit(main())
