"""Pytest hooks for SSTcore tests.

- **Local / CMake**: prepend typical build output dirs so native modules (e.g. ``sstcore._native``) resolve.
- **Wheel CI** (``SST_WHEEL_TEST=1``): remove checkout paths so site-packages wins, then re-add
  ``tests/`` only so test helpers (``sstcore_test_import``) remain importable.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _tests_dir() -> Path:
    return Path(__file__).resolve().parent


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


def _ensure_tests_helpers_on_sys_path() -> None:
    """Keep ``tests/`` importable for shared helpers while the package comes from the wheel."""
    if os.environ.get("SST_WHEEL_TEST") != "1":
        return
    tests_dir = str(_tests_dir().resolve())
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)


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
    _ensure_tests_helpers_on_sys_path()
    _prepend_repo_build_dirs()


def pytest_sessionstart(session) -> None:  # noqa: ARG001
    _strip_repo_root_from_sys_path()
    _ensure_tests_helpers_on_sys_path()
