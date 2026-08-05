#!/usr/bin/env python3
"""Integrity checks for vendored KnotPlot/ridgerunner tooling (deelplan res-5)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools" / "knotplot"


def test_vendored_md_exists_and_names_sources() -> None:
    md = TOOLS / "VENDORED.md"
    assert md.is_file(), "tools/knotplot/VENDORED.md missing"
    text = md.read_text(encoding="utf-8")
    assert "SST-Workbench" in text
    assert "KnotPlot/ridgerunner" in text or "ridgerunner/" in text
    assert "bin/" in text
    assert "testpaths" in text or "pyproject.toml" in text


def test_no_bin_out_or_caches() -> None:
    forbidden_names = {"bin", "out", "__pycache__", ".pytest_cache"}
    for path in TOOLS.rglob("*"):
        if path.name in forbidden_names and path.is_dir():
            raise AssertionError(f"forbidden directory under tools/knotplot: {path}")


def test_no_duplicate_gilbert_helpers() -> None:
    for name in ("gilbert_reader.py", "ideal_resolver.py"):
        hits = list(TOOLS.rglob(name))
        assert not hits, f"{name} must not be duplicated under tools/knotplot: {hits}"


def test_ridgerunner_scripts_present() -> None:
    rr = TOOLS / "ridgerunner"
    assert rr.is_dir()
    assert (rr / "README.md").is_file()
    assert (rr / "run_catalog_knot.py").is_file()
    assert list(rr.glob("test_*.py")), "expected upstream test_*.py references"
    assert (TOOLS / "import_workbench_knotplot.py").is_file()
    assert (TOOLS / "knotplot_txt_to_vect.py").is_file()
