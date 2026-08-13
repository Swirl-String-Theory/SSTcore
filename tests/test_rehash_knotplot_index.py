#!/usr/bin/env python3
"""Unit tests for tools/knotplot/rehash_knotplot_index.py (synthetic index)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "tools" / "knotplot"))

import rehash_knotplot_index as rehash  # noqa: E402

_PAYLOAD = b"<ab id=\"knot_3.1\"/>\n"
_RELPATH = "knot_3.1/knot_3.1_ab.xml"
_STALE_SHA = "0" * 64


def _make_index(tmp_path: Path, *, sha: str = _STALE_SHA, size: int = 1) -> Path:
    (tmp_path / "knot_3.1").mkdir()
    (tmp_path / _RELPATH).write_bytes(_PAYLOAD)
    index = {
        "version": 1,
        "entries": [
            {
                "id": "knot_3.1",
                "relaxed": True,
                "files": [
                    {"role": "ab_xml", "relpath": _RELPATH, "sha256": sha, "bytes": size}
                ],
            }
        ],
    }
    index_path = tmp_path / "INDEX.json"
    rehash.write_index(index, index_path)
    return index_path


def test_sha256_file_matches_hashlib(tmp_path: Path) -> None:
    path = tmp_path / "payload.bin"
    path.write_bytes(_PAYLOAD)
    assert rehash.sha256_file(path) == hashlib.sha256(_PAYLOAD).hexdigest()


def test_rehash_updates_stale_digest_without_touching_input(tmp_path: Path) -> None:
    index_path = _make_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))

    refreshed, report = rehash.rehash_index(index, tmp_path)

    assert report.updated == [_RELPATH]
    assert report.unchanged == []
    assert report.missing == []
    assert not report.in_sync
    record = refreshed["entries"][0]["files"][0]
    assert record["sha256"] == hashlib.sha256(_PAYLOAD).hexdigest()
    assert record["bytes"] == len(_PAYLOAD)
    assert index["entries"][0]["files"][0]["sha256"] == _STALE_SHA


def test_rehash_keeps_unrelated_fields(tmp_path: Path) -> None:
    index_path = _make_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))

    refreshed, _ = rehash.rehash_index(index, tmp_path)

    assert refreshed["version"] == 1
    assert refreshed["entries"][0]["relaxed"] is True
    assert refreshed["entries"][0]["files"][0]["role"] == "ab_xml"


def test_rehash_reports_in_sync_index(tmp_path: Path) -> None:
    index_path = _make_index(
        tmp_path, sha=hashlib.sha256(_PAYLOAD).hexdigest(), size=len(_PAYLOAD)
    )
    index = json.loads(index_path.read_text(encoding="utf-8"))

    _, report = rehash.rehash_index(index, tmp_path)

    assert report.unchanged == [_RELPATH]
    assert report.in_sync


def test_rehash_reports_missing_file(tmp_path: Path) -> None:
    index_path = _make_index(tmp_path)
    (tmp_path / _RELPATH).unlink()
    index = json.loads(index_path.read_text(encoding="utf-8"))

    _, report = rehash.rehash_index(index, tmp_path)

    assert report.missing == [_RELPATH]
    assert not report.in_sync


def test_write_index_uses_lf_newlines(tmp_path: Path) -> None:
    path = tmp_path / "INDEX.json"
    rehash.write_index({"version": 1, "entries": []}, path)
    raw = path.read_bytes()
    assert b"\r\n" not in raw
    assert raw.endswith(b"\n")


def test_main_check_reports_drift_without_writing(tmp_path: Path) -> None:
    index_path = _make_index(tmp_path)
    before = index_path.read_bytes()

    assert rehash.main(["--index", str(index_path), "--check"]) == 1
    assert index_path.read_bytes() == before


def test_main_rewrites_then_check_passes(tmp_path: Path) -> None:
    index_path = _make_index(tmp_path)

    assert rehash.main(["--index", str(index_path)]) == 0

    record = json.loads(index_path.read_text(encoding="utf-8"))["entries"][0]["files"][0]
    assert record["sha256"] == hashlib.sha256(_PAYLOAD).hexdigest()
    assert rehash.main(["--index", str(index_path), "--check"]) == 0


def test_main_refuses_to_write_when_file_missing(tmp_path: Path) -> None:
    index_path = _make_index(tmp_path)
    (tmp_path / _RELPATH).unlink()
    before = index_path.read_bytes()

    assert rehash.main(["--index", str(index_path)]) == 1
    assert index_path.read_bytes() == before
