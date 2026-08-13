#!/usr/bin/env python3
"""Validate installed SSTcore resources, including knotplot exports via INDEX.json."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


SST = pytest.importorskip("SSTcore", exc_type=ImportError)


def test_resources_dir_available_after_install() -> None:
    resources_dir = SST.get_resources_dir()
    assert resources_dir is not None, "SSTcore resources directory is not resolved"
    assert resources_dir.is_dir(), f"Resources path is not a directory: {resources_dir}"


def test_knotplot_ideal_files_load_via_public_api() -> None:
    knotplot_dir = SST.get_knotplot_dir()
    assert knotplot_dir is not None, "knotplot directory is not resolved by SSTcore"
    assert knotplot_dir.is_dir(), f"knotplot path is not a directory: {knotplot_dir}"

    index_path = knotplot_dir / "INDEX.json"
    assert index_path.is_file(), "resources/knotplot/INDEX.json missing"

    index = json.loads(index_path.read_text(encoding="utf-8"))
    entries = index.get("entries") or []
    assert entries, "INDEX.json has no entries"

    checked = 0
    for entry in entries:
        if not entry.get("relaxed"):
            continue
        kid = entry["id"]
        resolved_path = SST.get_knotplot_ideal_path(kid)
        assert resolved_path is not None, f"API did not resolve knotplot path for {kid}"
        assert resolved_path.is_file(), f"Resolved path is not a file for {kid}: {resolved_path}"

        text = SST.knotplot(kid)
        assert text is not None, f"knotplot() returned None for {kid}"
        assert text.strip(), f"knotplot() returned empty content for {kid}"
        checked += 1

    assert checked > 0, "No relaxed INDEX entries were validated"
