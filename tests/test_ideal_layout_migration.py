#!/usr/bin/env python3
"""Deelplan res-1: Gilbert ideal data lives under resources/ideal/ with flat fallback."""

from __future__ import annotations

from pathlib import Path

import pytest

from sstcore_test_import import load_sstcore_package

sstcore = load_sstcore_package()


def test_ideal_sources_resolve_under_ideal_subdir(require_ideal) -> None:
    sst = require_ideal
    root = sst.get_resources_dir()
    assert root is not None
    for key in sst.list_ideal_source_files():
        path = sst.get_ideal_file_path(key)
        assert path is not None, f"missing ideal source {key}"
        assert path.is_file()
        # New layout: .../resources/ideal/<basename>
        assert path.parent.name == "ideal", f"{key} resolved outside ideal/: {path}"
        assert "ideal" in path.resolve().relative_to(root.resolve()).parts


def test_ideal_txt_and_12_data_under_ideal(require_ideal) -> None:
    sst = require_ideal
    ideal = sst.get_ideal_txt_path()
    assert ideal is not None
    assert ideal.name == "ideal.txt"
    assert ideal.parent.name == "ideal"

    d12 = sst.get_ideal_12_data_dir()
    assert d12 is not None
    assert d12.is_dir()
    assert d12.name == "ideal_12_data"
    assert d12.parent.name == "ideal"


def test_flat_legacy_shim_via_sstcore_resources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A resources root that only has the flat ideal.txt must still resolve."""
    flat = tmp_path / "resources"
    flat.mkdir()
    (flat / "ideal.txt").write_text('<DATA><AB Id="9:9:9" L="1" D="1"></AB></DATA>\n', encoding="utf-8")
    monkeypatch.setenv("SSTCORE_RESOURCES", str(flat))
    # Bypass import cache: call the function on the loaded module after env set.
    path = sstcore.get_ideal_file_path("ideal")
    assert path is not None
    assert path.name == "ideal.txt"
    assert path.parent == flat.resolve()


def test_find_ideal_ab_still_works_after_move(require_ideal) -> None:
    block = require_ideal.find_ideal_ab_block_by_id("3:1:1")
    assert block is not None
    assert 'Id="3:1:1"' in block
    assert 'Conway="3"' in block


def test_traversal_guard_rejects_slash_keys(require_ideal) -> None:
    assert require_ideal.get_ideal_file_path("ideal/ideal.txt") is None
    assert require_ideal.get_ideal_file_path("../ideal.txt") is None
