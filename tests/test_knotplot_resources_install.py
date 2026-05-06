#!/usr/bin/env python3
"""Validate installed SSTcore resources, including knotplot ideal files."""

from __future__ import annotations

from pathlib import Path

import pytest


SST = pytest.importorskip("SSTcore", exc_type=ImportError)


def _discover_knotplot_dirs(knotplot_dir: Path) -> list[Path]:
    return sorted(p for p in knotplot_dir.glob("knot_*") if p.is_dir())


def _extract_knot_id(knot_dir: Path) -> str:
    # Strip "knot_" prefix because API accepts both "knot_X" and "X".
    return knot_dir.name[5:] if knot_dir.name.startswith("knot_") else knot_dir.name


def test_resources_dir_available_after_install() -> None:
    resources_dir = SST.get_resources_dir()
    assert resources_dir is not None, "SSTcore resources directory is not resolved"
    assert resources_dir.is_dir(), f"Resources path is not a directory: {resources_dir}"


def test_knotplot_ideal_files_load_via_public_api() -> None:
    knotplot_dir = SST.get_knotplot_dir()
    assert knotplot_dir is not None, "knotplot directory is not resolved by SSTcore"
    assert knotplot_dir.is_dir(), f"knotplot path is not a directory: {knotplot_dir}"

    knot_dirs = _discover_knotplot_dirs(knotplot_dir)
    assert knot_dirs, "No knot_* directories found under resources/knotplot"

    checked = 0
    for knot_dir in knot_dirs:
        expected = knot_dir / f"{knot_dir.name}_ideal.txt"
        if not expected.is_file():
            # Some directories may contain alternate assets only; skip those.
            continue

        knot_id = _extract_knot_id(knot_dir)
        resolved_path = SST.get_knotplot_ideal_path(knot_id)
        assert resolved_path is not None, f"API did not resolve knotplot path for {knot_id}"
        assert resolved_path.is_file(), f"Resolved path is not a file for {knot_id}: {resolved_path}"

        text = SST.knotplot(knot_id)
        assert text is not None, f"knotplot() returned None for {knot_id}"
        assert text.strip(), f"knotplot() returned empty content for {knot_id}"
        checked += 1

    assert checked > 0, "No knot_*/knot_*_ideal.txt files were validated"
