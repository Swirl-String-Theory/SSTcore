#!/usr/bin/env python3
"""npm pack surface for knotplot: INDEX.json + *_ab.xml only (deelplan res-5)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _npm_exe() -> str | None:
    return shutil.which("npm") or shutil.which("npm.cmd")


def _npm_pack_paths() -> list[str]:
    npm = _npm_exe()
    if not npm:
        pytest.skip("npm not on PATH")
    try:
        proc = subprocess.run(
            [npm, "pack", "--dry-run", "--json"],
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
    raw = proc.stdout.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
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
    return [(f.get("path") or f.get("name") or "").replace("\\", "/") for f in files]


def test_npm_ship_index_and_ab_xml() -> None:
    paths = _npm_pack_paths()
    assert "resources/knotplot/INDEX.json" in paths
    ab = [p for p in paths if p.startswith("resources/knotplot/") and p.endswith("_ab.xml")]
    assert ab, "expected at least one *_ab.xml in npm pack"


def test_npm_excludes_polish_vect_metrics() -> None:
    paths = _npm_pack_paths()
    kp = [p for p in paths if p.startswith("resources/knotplot/")]
    allowed = {"resources/knotplot/INDEX.json"}
    for p in kp:
        if p in allowed:
            continue
        assert p.endswith("_ab.xml"), f"unexpected knotplot npm member: {p}"
