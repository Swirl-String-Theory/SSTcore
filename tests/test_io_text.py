#!/usr/bin/env python3
"""Unit tests for tools/knotplot/io_text.write_text_lf (Python 3.9+ safe LF writes)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "tools" / "knotplot"))

from io_text import write_text_lf  # noqa: E402


def test_write_text_lf_preserves_lf_bytes(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    write_text_lf(path, "a\nb\n")
    assert path.read_bytes() == b"a\nb\n"


def test_write_text_lf_does_not_introduce_crlf(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    write_text_lf(path, "line1\nline2\n")
    raw = path.read_bytes()
    assert b"\r\n" not in raw
    assert raw.count(b"\n") == 2


def test_write_text_lf_encodes_utf8(tmp_path: Path) -> None:
    path = tmp_path / "utf8.txt"
    write_text_lf(path, "café\n")
    assert path.read_bytes() == "café\n".encode("utf-8")
