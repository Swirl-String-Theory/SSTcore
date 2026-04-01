"""
Legacy module name for the alternate native binding build.

Prefer ``import SSTcore`` or ``from SSTcore import ...``.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys


def _load_cmake_extension() -> None:
    for entry in sys.path:
        base = pathlib.Path(entry) if entry else pathlib.Path(".")
        if not base.is_dir():
            continue
        for f in sorted(base.glob("sstbindings*.pyd")) + sorted(base.glob("sstbindings*.so")):
            if not f.name.startswith("sstbindings"):
                continue
            spec = importlib.util.spec_from_file_location(__name__, f)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[__name__] = mod
            return
    raise ImportError(
        "sstbindings: use `pip install SSTcore`, or add the CMake build directory "
        "(containing sstbindings*.pyd / sstbindings*.so) to sys.path before the repo root."
    )


try:
    from SSTcore._bindings import *  # noqa: F401, F403
except ImportError:
    _load_cmake_extension()
