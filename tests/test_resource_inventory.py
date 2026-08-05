#!/usr/bin/env python3
"""API-driven resource inventory: every manifest entry must exist with matching SHA256.

Missing or altered resources fail by name (no silent skip). Owned by deelplan res-0.
Regenerate the manifest after legitimate data changes with:
  python tests/data/regen_resource_manifest.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sstcore_test_import import load_sstcore_package

sstcore = load_sstcore_package()

_MANIFEST = Path(__file__).resolve().parent / "data" / "resource_manifest.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def resource_manifest() -> dict:
    assert _MANIFEST.is_file(), f"resource manifest missing: {_MANIFEST}"
    return json.loads(_MANIFEST.read_text(encoding="utf-8"))


def test_resources_dir_resolves() -> None:
    root = sstcore.get_resources_dir()
    assert root is not None, "get_resources_dir() returned None"
    assert root.is_dir()


def test_manifest_not_empty(resource_manifest: dict) -> None:
    assert resource_manifest.get("version") == 1
    entries = resource_manifest.get("entries") or []
    assert len(entries) > 0
    kinds = {e["kind"] for e in entries}
    assert "ideal" in kinds
    assert "knotplot_ideal" in kinds
    assert "fseries" in kinds


def test_every_manifest_entry_exists_with_matching_sha256(resource_manifest: dict) -> None:
    """Fail loudly naming any missing or altered resource file."""
    root = sstcore.get_resources_dir()
    assert root is not None
    root = root.resolve()

    missing: list[str] = []
    mismatched: list[str] = []

    for entry in resource_manifest["entries"]:
        rel = entry["relpath"]
        path = (root / rel).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            missing.append(f"{entry['id']}: path escapes resources root ({rel})")
            continue
        if not path.is_file():
            missing.append(f"{entry['id']}: missing file {rel}")
            continue
        digest = _sha256(path)
        if digest != entry["sha256"]:
            mismatched.append(
                f"{entry['id']}: sha256 mismatch for {rel} "
                f"(expected {entry['sha256'][:12]}…, got {digest[:12]}…)"
            )

    assert not missing, "Missing resource files:\n  - " + "\n  - ".join(missing)
    assert not mismatched, "Altered resource files:\n  - " + "\n  - ".join(mismatched)


def test_ideal_keys_resolve_via_api(resource_manifest: dict) -> None:
    ideal_ids = [e["id"] for e in resource_manifest["entries"] if e["kind"] == "ideal"]
    assert ideal_ids, "manifest has no ideal entries"
    for key in ideal_ids:
        path = sstcore.get_ideal_file_path(key)
        assert path is not None, f"get_ideal_file_path({key!r}) returned None"
        assert path.is_file(), f"ideal file missing for {key}: {path}"


def test_knotplot_ids_resolve_via_api(resource_manifest: dict) -> None:
    kp_ids = [e["id"] for e in resource_manifest["entries"] if e["kind"] == "knotplot_ideal"]
    assert kp_ids, "manifest has no knotplot_ideal entries"
    assert "knot_3.1" in kp_ids
    for kid in kp_ids:
        path = sstcore.get_knotplot_ideal_path(kid)
        assert path is not None, f"get_knotplot_ideal_path({kid!r}) returned None"
        assert path.is_file(), f"knotplot ideal missing for {kid}: {path}"


def test_fseries_stems_loadable(resource_manifest: dict) -> None:
    labels = [e["id"] for e in resource_manifest["entries"] if e["kind"] == "fseries"]
    assert "3_1" in labels
    for label in labels:
        text = sstcore.get_knot_fseries(label)
        assert text, f"get_knot_fseries({label!r}) returned empty"
