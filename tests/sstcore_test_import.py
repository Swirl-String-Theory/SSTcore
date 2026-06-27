"""Shared SSTcore import helper for tests (src-layout checkout vs installed wheel)."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"


def load_sstcore_package():
    """Return the ``SSTcore`` package (``src/SSTcore`` in dev, site-packages in wheel CI)."""
    if os.environ.get("SST_WHEEL_TEST") == "1":
        return importlib.import_module("SSTcore")

    if not (_SRC / "SSTcore" / "__init__.py").is_file():
        raise ImportError(f"Expected src/SSTcore/__init__.py under {_ROOT}")

    src = str(_SRC.resolve())
    if src not in sys.path:
        sys.path.insert(0, src)

    for name in ("SSTcore", "sstcore"):
        sys.modules.pop(name, None)

    return importlib.import_module("SSTcore")
