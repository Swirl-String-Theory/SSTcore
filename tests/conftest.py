"""Pytest hooks for SSTcore tests.

- **Local / CMake**: prepend typical build output dirs so ``sstbindings*.pyd`` / ``.so`` resolve.
- **Wheel CI** (``SST_WHEEL_TEST=1``): remove the repository root from ``sys.path`` so pytest does
  not load the source ``SSTcore/`` package (no extensions) ahead of the installed wheel — same idea
  as the smoke test's ``cd "$(mktemp -d)"``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _strip_repo_root_from_sys_path() -> None:
    """When testing an installed wheel, drop checkout root so site-packages wins."""
    if os.environ.get("SST_WHEEL_TEST") != "1":
        return
    root = _repo_root()
    root_norm = os.path.normcase(os.path.normpath(str(root.resolve())))

    def _is_repo_entry(p: str) -> bool:
        if not p:
            return False
        try:
            return os.path.normcase(os.path.normpath(os.path.abspath(p))) == root_norm
        except OSError:
            return False

    sys.path[:] = [p for p in sys.path if not _is_repo_entry(p)]


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
