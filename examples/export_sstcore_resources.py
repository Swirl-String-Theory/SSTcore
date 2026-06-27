#!/usr/bin/env python3
"""Thin wrapper around ``python -m SSTcore export-resources``."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from SSTcore.cli import export_resources_entry

if __name__ == "__main__":
    raise SystemExit(export_resources_entry())
