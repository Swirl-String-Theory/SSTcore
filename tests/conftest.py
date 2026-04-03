"""Pytest hooks: prepend typical CMake output dirs so local builds resolve sstbindings*.pyd/.so."""

from __future__ import annotations

import sys
from pathlib import Path


def _prepend_repo_build_dirs() -> None:
    root = Path(__file__).resolve().parent.parent
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


def pytest_configure(config) -> None:  # noqa: ARG001
    _prepend_repo_build_dirs()
