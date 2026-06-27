"""Patch C: export-resources CLI smoke tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from sstcore_test_import import load_sstcore_package

sstcore = load_sstcore_package()


def test_list_ideal_source_files():
    files = sstcore.list_ideal_source_files()
    assert "ideal" in files
    assert files["ideal"] == "ideal.txt"


def test_load_ideal_ab_embedded_trefoil():
    block = sstcore.load_ideal_ab_embedded("3:1:1")
    assert block is not None
    assert 'Id="3:1:1"' in block


def test_list_embedded_fseries_ids_includes_trefoil():
    ids = sstcore.list_embedded_fseries_ids()
    if not ids:
        pytest.skip("Knots_FourierSeries not in resources")
    assert any(x.startswith("3_1") for x in ids)


def test_export_resources_cli(tmp_path):
    from SSTcore.cli import export_resources

    manifest = tmp_path / "manifest.json"
    report = export_resources(tmp_path / "out", manifest_path=manifest)
    assert (tmp_path / "out" / "ideal.txt").is_file()
    assert manifest.is_file()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["files"]
    assert any(f["path"] == "ideal.txt" for f in data["files"])
    assert report["file_count"] > 0


def test_module_casing_shim():
    assert hasattr(sstcore, "get_resources_dir")
    assert hasattr(sstcore, "find_ideal_by_id")
    from SSTcore.cli import export_resources as _exp

    assert callable(_exp)
