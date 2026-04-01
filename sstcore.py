"""
Legacy module name for the native SSTcore bindings.

Prefer ``import SSTcore`` or ``from SSTcore import ...``.

After ``pip install SSTcore``, this re-exports :mod:`SSTcore._native`.
If you build with CMake only, put the directory that contains ``sstcore*.pyd`` / ``sstcore*.so``
on :data:`sys.path` *before* the repository root so the extension is found below.
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
        for f in sorted(base.glob("sstcore*.pyd")) + sorted(base.glob("sstcore*.so")):
            if not f.name.startswith("sstcore"):
                continue
            spec = importlib.util.spec_from_file_location(__name__, f)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[__name__] = mod
            return
    raise ImportError(
        "sstcore: use `pip install SSTcore`, or add the CMake build directory "
        "(containing sstcore*.pyd / sstcore*.so) to sys.path before the repo root."
    )


try:
    from SSTcore._native import *  # noqa: F401, F403
except ImportError:
    _load_cmake_extension()
