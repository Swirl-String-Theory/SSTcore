#!/usr/bin/env python3
"""
Editable install of SSTcore from this repository root.

Uses the same Python interpreter as this script (``sys.executable``).

Usage (from anywhere):

    python path/to/SSTcore/dev_editable_install.py

Or from the repo root:

    python dev_editable_install.py

Extra pip args:

    python dev_editable_install.py --no-build-isolation

If setup fails with ``PermissionError`` under ``build/temp`` (shared clone / another user’s
artifacts), set a writable directory: ``set SSTCORE_SETUP_BUILD_TEMP=%TEMP%\\sst_embed`` then rerun.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    setup = root / "setup.py"
    if not setup.is_file():
        print(f"error: expected setup.py at {setup}", file=sys.stderr)
        return 1

    cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
    cmd.extend(sys.argv[1:])
    return subprocess.call(cmd, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
