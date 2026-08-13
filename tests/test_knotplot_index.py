#!/usr/bin/env python3
"""Validate resources/knotplot/INDEX.json contract after the Workbench import."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sstcore_test_import import load_sstcore_package

sstcore = load_sstcore_package()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def knotplot_index() -> dict:
    root = sstcore.get_knotplot_dir()
    assert root is not None
    path = root / "INDEX.json"
    assert path.is_file()
    return json.loads(path.read_text(encoding="utf-8"))


def test_index_schema(knotplot_index: dict) -> None:
    assert knotplot_index.get("version") == 1
    assert "entries" in knotplot_index
    assert "legacy_aliases" in knotplot_index
    assert knotplot_index["counts"]["total"] == len(knotplot_index["entries"])


def test_files_match_sha256(knotplot_index: dict) -> None:
    root = sstcore.get_knotplot_dir()
    assert root is not None
    missing = []
    mismatched = []
    for entry in knotplot_index["entries"]:
        for f in entry.get("files") or []:
            path = root / f["relpath"]
            if not path.is_file():
                missing.append(f["relpath"])
                continue
            digest = _sha256(path)
            if digest != f["sha256"]:
                mismatched.append(f["relpath"])
    assert not missing, f"missing: {missing[:10]}"
    assert not mismatched, f"sha mismatch: {mismatched[:10]}"


def test_relaxed_have_geometry_and_ab(knotplot_index: dict) -> None:
    root = sstcore.get_knotplot_dir()
    assert root is not None
    relaxed = [e for e in knotplot_index["entries"] if e.get("relaxed")]
    assert len(relaxed) >= 1
    for entry in relaxed:
        roles = {f["role"] for f in entry.get("files") or []}
        assert "uniform_n300" in roles or "shared_final" in roles, entry["id"]
        assert "ab_xml" in roles, entry["id"]
        assert "audit_metrics" in roles or "audit_polish" in roles or "shared_final" in roles, entry["id"]
        ab = root / entry["id"] / f"{entry['id']}_ab.xml"
        assert ab.is_file()


def test_stubs_have_kpc_no_geometry(knotplot_index: dict) -> None:
    root = sstcore.get_knotplot_dir()
    assert root is not None
    stubs = [e for e in knotplot_index["entries"] if not e.get("relaxed")]
    assert stubs
    for entry in stubs:
        roles = {f["role"] for f in entry.get("files") or []}
        assert "build_script" in roles, entry["id"]
        assert "uniform_n300" not in roles, entry["id"]
        assert "shared_final" not in roles, entry["id"]
        assert "ab_xml" not in roles, entry["id"]
        folder = root / entry["id"]
        assert not list(folder.glob("*uniform*"))
        assert not list(folder.glob("*_ab.xml"))
        assert not list(folder.glob("*_final.txt"))


def test_no_monopole_or_pyd_or_rr(knotplot_index: dict) -> None:
    root = sstcore.get_knotplot_dir()
    assert root is not None
    bad = []
    for p in root.rglob("*"):
        name = p.name.lower()
        if "monopole" in name:
            bad.append(str(p))
        if p.suffix.lower() == ".pyd":
            bad.append(str(p))
        if p.is_dir() and p.name.endswith(".rr"):
            bad.append(str(p))
    assert not bad, f"forbidden artifacts remain: {bad[:10]}"


def test_legacy_aliases_resolve(knotplot_index: dict) -> None:
    aliases = knotplot_index.get("legacy_aliases") or {}
    ids = {e["id"] for e in knotplot_index["entries"]}
    for legacy, target in aliases.items():
        assert target in ids, f"alias {legacy} → {target} missing"
        # At least one known alias must resolve via API when target is relaxed
        entry = next(e for e in knotplot_index["entries"] if e["id"] == target)
        if entry.get("relaxed"):
            path = sstcore.get_knotplot_ideal_path(legacy)
            assert path is not None, f"API failed for legacy alias {legacy}"
