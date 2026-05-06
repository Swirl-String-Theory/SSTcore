"""Pytest hooks for SSTcore tests.

- **Local / CMake**: prepend typical build output dirs so native modules (e.g. ``SSTcore._native``) resolve.
- **Wheel CI** (``SST_WHEEL_TEST=1``): remove **every** ``sys.path`` entry that resolves inside the
  checkout (repo root *and* subdirs like ``tests/``). Pytest injects those paths before imports;
  stripping only the repo root is not enough — a ``tests/`` prefix can still resolve ``SSTcore/``
  from the tree and shadow the wheel (pure ``__init__.py``, no ``_native``).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _strip_repo_root_from_sys_path() -> None:
    """When testing an installed wheel, drop any checkout paths so site-packages wins."""
    if os.environ.get("SST_WHEEL_TEST") != "1":
        return
    root = _repo_root().resolve()

    def _is_under_repo(p: str) -> bool:
        if not p:
            return False
        try:
            resolved = Path(p).resolve()
        except OSError:
            return False
        if resolved == root:
            return True
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            return False

    sys.path[:] = [p for p in sys.path if not _is_under_repo(p)]


def _prepend_repo_build_dirs() -> None:
    if os.environ.get("SST_WHEEL_TEST") == "1":
        return
    root = _repo_root()
    for d in (
        root / "build" / "Debug",
        root / "build" / "Release",
        root / "build" / "RelWithDebInfo",
        root / "cmake-build-debug",
        root / "cmake-build-release",
        root / "cmake-build-relwithdebinfo",
    ):
        if d.is_dir():
            s = str(d.resolve())
            if s not in sys.path:
                sys.path.insert(0, s)


_strip_repo_root_from_sys_path()


def pytest_configure(config) -> None:  # noqa: ARG001
    _strip_repo_root_from_sys_path()
    _prepend_repo_build_dirs()
