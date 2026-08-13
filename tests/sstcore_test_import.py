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

    # The editable install (__editable__.sstcore-*.pth) appends src/ *after* site-packages,
    # so a plain "insert if absent" leaves an installed wheel shadowing the checkout.
    src = str(_SRC.resolve())
    while src in sys.path:
        sys.path.remove(src)
    sys.path.insert(0, src)

    for name in ("SSTcore", "sstcore"):
        sys.modules.pop(name, None)

    module = importlib.import_module("SSTcore")
    origin = Path(getattr(module, "__file__", "") or "").resolve()
    if not origin.is_relative_to(_SRC):
        raise ImportError(
            f"Imported SSTcore from {origin} instead of the checkout under {_SRC}. "
            "Set SST_WHEEL_TEST=1 to test an installed wheel on purpose."
        )
    return module
