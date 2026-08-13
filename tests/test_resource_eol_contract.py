#!/usr/bin/env python3
"""resources/ must check out byte-for-byte on every platform.

tests/data/resource_manifest.json and resources/knotplot/INDEX.json pin sha256 digests of
the raw bytes. Without the `-text` attribute git rewrites line endings per platform, so the
same commit yields different digests on Windows than on Linux/macOS and the wheel CI fails
on files that pass locally.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GITATTRIBUTES = REPO / ".gitattributes"


def _git_eol_records() -> list[tuple[str, str, str, str]]:
    """(index_eol, worktree_eol, attr, path) for every tracked file under resources/."""
    if not (REPO / ".git").exists():
        pytest.skip("not a git checkout")
    git = shutil.which("git")
    if not git:
        pytest.skip("git not on PATH")
    proc = subprocess.run(
        [git, "-C", str(REPO), "ls-files", "--eol", "--", "resources"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        pytest.skip(f"git ls-files failed: {proc.stderr.strip()[-200:]}")

    records = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        attrs, _, path = line.partition("\t")
        fields = attrs.split()
        if len(fields) < 3:
            continue
        records.append((fields[0], fields[1], fields[2], path.strip()))
    return records


def test_gitattributes_disables_eol_conversion_for_resources() -> None:
    assert GITATTRIBUTES.is_file(), "missing .gitattributes at repo root"
    rules = [
        line.split()
        for line in GITATTRIBUTES.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert any(
        rule[0].startswith("resources/") and "-text" in rule[1:] for rule in rules
    ), "expected a `resources/** -text` rule so hashed payloads are never EOL-converted"


def test_resources_are_marked_binary_safe() -> None:
    records = _git_eol_records()
    assert records, "no tracked files under resources/"
    unmarked = [path for _i, _w, attr, path in records if "-text" not in attr]
    assert not unmarked, (
        "resources not covered by a `-text` attribute (digests become platform "
        f"dependent): {unmarked[:10]}"
    )


def test_resources_worktree_matches_index_eol() -> None:
    records = _git_eol_records()
    converted = [
        f"{path} (index {index_eol}, worktree {worktree_eol})"
        for index_eol, worktree_eol, _attr, path in records
        if index_eol.split("/", 1)[-1] != worktree_eol.split("/", 1)[-1]
    ]
    assert not converted, (
        "git rewrote line endings on checkout; the manifests would only match on this "
        f"platform: {converted[:10]}"
    )
