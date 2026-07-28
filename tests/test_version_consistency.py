"""Optie A: package and canon version strings must stay identical."""
from __future__ import annotations

from pathlib import Path

import pytest

sst = pytest.importorskip("SSTcore")

ROOT = Path(__file__).resolve().parents[1]


def test_python_canon_alias_matches_version() -> None:
    assert sst.__version__ == "0.8.28"
    assert getattr(sst, "CANON_VERSION", None) == sst.__version__


def test_header_macros_match() -> None:
    text = (ROOT / "include" / "sstcore_version.h").read_text(encoding="utf-8")
    assert '#define SSTCORE_VERSION "0.8.28"' in text
    assert '#define SSTCORE_CANON_VERSION "0.8.28"' in text


def test_package_json_matches() -> None:
    import json

    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert pkg["version"] == sst.__version__


def test_setup_py_matches() -> None:
    text = (ROOT / "setup.py").read_text(encoding="utf-8")
    assert f'__version__ = "{sst.__version__}"' in text
