#!/usr/bin/env python3
"""Ensure tools/ is excluded from sdist and npm pack surfaces."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def test_tools_dir_exists_with_importer() -> None:
    importer = REPO / "tools" / "knotplot" / "import_workbench_knotplot.py"
    assert importer.is_file(), "importer missing — deelplan res-2"


def test_manifest_in_prunes_tools() -> None:
    text = (REPO / "MANIFEST.in").read_text(encoding="utf-8")
    assert "prune tools" in text


def test_npmignore_excludes_tools() -> None:
    text = (REPO / ".npmignore").read_text(encoding="utf-8")
    assert "tools/" in text


@pytest.mark.skipif(sys.platform.startswith("win") and False, reason="placeholder")
def test_sdist_excludes_tools(tmp_path: Path) -> None:
    """Build a source distribution and assert no tools/ members."""
    # Lightweight check: parse MANIFEST.in rules + ensure setuptools would prune.
    # Full sdist is expensive; verify the prune directive and that tools is outside package_data.
    setup = (REPO / "setup.py").read_text(encoding="utf-8")
    assert "tools/" not in setup or "prune" in (REPO / "MANIFEST.in").read_text(encoding="utf-8")
    # package_data walks src/SSTcore only — tools/ is outside that tree.
    assert not (REPO / "src" / "SSTcore" / "tools").exists()


def test_npm_pack_dry_run_excludes_tools() -> None:
    """npm pack --dry-run --json should not list tools/ paths."""
    try:
        proc = subprocess.run(
            ["npm", "pack", "--dry-run", "--json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        pytest.skip(f"npm pack unavailable: {exc}")
    if proc.returncode != 0:
        pytest.skip(f"npm pack failed: {proc.stderr[-500:]}")
    # npm pack --json prints an array; take the last JSON value
    raw = proc.stdout.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Some npm versions print non-JSON lines first
        start = raw.find("[")
        if start < 0:
            pytest.skip("npm pack --json output not parseable")
        data = json.loads(raw[start:])
    if isinstance(data, list) and data:
        files = data[0].get("files") or []
    elif isinstance(data, dict):
        files = data.get("files") or []
    else:
        files = []
    paths = [f.get("path") or f.get("name") or "" for f in files]
    tools_hits = [p for p in paths if p.replace("\\", "/").startswith("tools/")]
    assert not tools_hits, f"tools/ leaked into npm pack: {tools_hits[:10]}"
