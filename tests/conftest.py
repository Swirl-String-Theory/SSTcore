"""Pytest hooks for SSTcore tests.

- **Local / CMake**: prepend typical build output dirs so native modules (e.g. ``sstcore._native``) resolve.
- **Wheel CI** (``SST_WHEEL_TEST=1``): remove checkout paths so site-packages wins, then re-add
  ``tests/`` only so test helpers (``sstcore_test_import``) remain importable.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


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


def _allow_missing_resources() -> bool:
    """Opt-out for deliberate resource-absence probes (deelplan res-0)."""
    return os.environ.get("SSTCORE_ALLOW_MISSING_RESOURCES", "").strip() == "1"


@pytest.fixture
def require_ideal():
    """Fail loudly when Gilbert ideal resources are missing (no silent skip).

    Owned by deelplan res-0 / res-1. Set SSTCORE_ALLOW_MISSING_RESOURCES=1 only
    for intentional breakage probes.
    """
    from sstcore_test_import import load_sstcore_package

    sst = load_sstcore_package()
    root = sst.get_resources_dir()
    if root is None:
        if _allow_missing_resources():
            pytest.skip("SSTCORE_ALLOW_MISSING_RESOURCES=1 and resources dir missing")
        pytest.fail(
            "SSTcore resources directory not resolved (deelplan res-0/res-1). "
            "Expected get_resources_dir() to find resources/."
        )
    ideal = sst.get_ideal_txt_path()
    if ideal is None or not ideal.is_file():
        if _allow_missing_resources():
            pytest.skip("SSTCORE_ALLOW_MISSING_RESOURCES=1 and ideal.txt missing")
        pytest.fail(
            "Gilbert ideal.txt not resolved via get_ideal_txt_path() "
            "(deelplan res-0/res-1). Expected resources/ideal.txt or resources/ideal/ideal.txt."
        )
    return sst


@pytest.fixture
def require_knotplot():
    """Fail loudly when knotplot resources are missing (no silent skip).

    Owned by deelplan res-0 / res-3. Set SSTCORE_ALLOW_MISSING_RESOURCES=1 only
    for intentional breakage probes.
    """
    from sstcore_test_import import load_sstcore_package

    sst = load_sstcore_package()
    kp_dir = sst.get_knotplot_dir()
    if kp_dir is None or not kp_dir.is_dir():
        if _allow_missing_resources():
            pytest.skip("SSTCORE_ALLOW_MISSING_RESOURCES=1 and knotplot dir missing")
        pytest.fail(
            "knotplot directory not resolved via get_knotplot_dir() "
            "(deelplan res-0/res-3). Expected resources/knotplot/."
        )
    kp_path = sst.get_knotplot_ideal_path("knot_3.1")
    if kp_path is None or not kp_path.is_file():
        if _allow_missing_resources():
            pytest.skip("SSTCORE_ALLOW_MISSING_RESOURCES=1 and knot_3.1 ideal missing")
        pytest.fail(
            "knotplot trefoil not resolved via get_knotplot_ideal_path('knot_3.1') "
            "(deelplan res-0/res-3). Expected a knotplot ideal/AB file for knot_3.1."
        )
    return sst
