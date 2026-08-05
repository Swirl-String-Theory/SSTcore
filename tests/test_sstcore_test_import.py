#!/usr/bin/env python3
"""Regression tests for the shared dev/wheel import helper.

An editable install (`__editable__.sstcore-*.pth`) appends src/ *behind* site-packages. The
loader used to skip its own insert when that entry already existed, so scripts run outside
pytest silently imported an installed wheel - which is how CRLF digests from a stale wheel
ended up in tests/data/resource_manifest.json.
"""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path

import pytest

import sstcore_test_import
from sstcore_test_import import load_sstcore_package

REPO = Path(__file__).resolve().parent.parent
SRC = (REPO / "src").resolve()

pytestmark = pytest.mark.skipif(
    os.environ.get("SST_WHEEL_TEST") == "1",
    reason="wheel mode imports the installed package on purpose",
)


def test_loader_prefers_checkout_when_src_is_late_on_syspath(monkeypatch) -> None:
    src = str(SRC)
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != src] + [src])

    module = load_sstcore_package()

    assert Path(module.__file__).resolve().is_relative_to(SRC)
    assert sys.path[0] == src


def test_loader_does_not_duplicate_src_entry(monkeypatch) -> None:
    src = str(SRC)
    monkeypatch.setattr(sys, "path", [src] + [p for p in sys.path if p != src] + [src])

    load_sstcore_package()

    assert sys.path.count(src) == 1


def test_loader_rejects_foreign_sstcore(monkeypatch, tmp_path: Path) -> None:
    foreign = types.ModuleType("SSTcore")
    foreign.__file__ = str(tmp_path / "site-packages" / "SSTcore" / "__init__.py")
    monkeypatch.setattr(
        sstcore_test_import.importlib, "import_module", lambda name: foreign
    )

    with pytest.raises(ImportError, match="instead of the checkout"):
        load_sstcore_package()
