"""Tests for SSTcore_source_v*.zip bundle (make + unpack)."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from source_zip_common import (  # noqa: E402
    MANIFEST_NAME,
    collect_source_files,
    read_version,
    should_exclude_file,
)
from make_source_zip import build_source_zip  # noqa: E402


@pytest.mark.parametrize(
    "rel",
    [
        "build/foo.obj",
        "tests/__pycache__/x.pyc",
        "resources/knotplot/knot_3.1/knot_3.1_ideal.txt",
        "resources/Knots_FourierSeries/3_1/knot.3_1.stl",
        "resources/Results/knotplot/knot_3.1/knot_3.1_ideal.txt",
        "SST_Dashboard/gui_tabs/foo.py",
        "ideal_database.txt",
    ],
)
def test_should_exclude_file(rel: str) -> None:
    assert should_exclude_file(rel)


def test_should_include_canonical_paths() -> None:
    assert not should_exclude_file("resources/ideal.txt")
    assert not should_exclude_file("src/SSTcore/__init__.py")
    assert not should_exclude_file("resources/README.md")


def test_collect_source_files_includes_readme() -> None:
    files = collect_source_files(REPO_ROOT)
    assert "resources/README.md" in files
    assert "src/SSTcore/__init__.py" in files
    assert not any("resources/knotplot/" in f for f in files)
    assert not any(f.endswith(".stl") for f in files)


def test_build_source_zip_smoke(tmp_path: Path) -> None:
    if not (REPO_ROOT / "resources" / "ideal.txt").is_file():
        pytest.skip("resources/ideal.txt missing")
    out = tmp_path / "SSTcore_source_test.zip"
    build_source_zip(REPO_ROOT, out)
    assert out.is_file()

    version = read_version(REPO_ROOT)
    prefix = f"SSTcore-v{version}/"
    with zipfile.ZipFile(out) as zf:
        names = {n.replace("\\", "/") for n in zf.namelist()}
        assert f"{prefix}resources/ideal.txt" in names
        assert f"{prefix}resources/README.md" in names
        assert f"{prefix}resources/ideal_12_data.zip" in names
        assert f"{prefix}resources/knotplot.zip" in names
        assert f"{prefix}resources/Knots_FourierSeries.zip" in names
        assert not any(n.lower().endswith(".stl") for n in names)
        assert not any("/resources/knotplot/knot_" in n for n in names)

        manifest = json.loads(zf.read(f"{prefix}resources/{MANIFEST_NAME}"))
        assert manifest["version"] == version
        assert "*.stl" in manifest.get("excluded_patterns", [])


def test_unpack_roundtrip(tmp_path: Path) -> None:
    if not (REPO_ROOT / "resources" / "ideal.txt").is_file():
        pytest.skip("resources/ideal.txt missing")

    out = tmp_path / "bundle.zip"
    build_source_zip(REPO_ROOT, out)
    extract = tmp_path / "checkout"
    with zipfile.ZipFile(out) as zf:
        zf.extractall(extract)

    version = read_version(REPO_ROOT)
    root = extract / f"SSTcore-v{version}"
    manifest_src = root / "resources" / MANIFEST_NAME

    work = tmp_path / "work"
    shutil.copytree(
        root,
        work,
        ignore=shutil.ignore_patterns(
            "resources/ideal_12_data.zip",
            "resources/knotplot.zip",
            "resources/Knots_FourierSeries.zip",
            "resources/Results.zip",
        ),
    )
    for name in (
        "ideal_12_data.zip",
        "knotplot.zip",
        "Knots_FourierSeries.zip",
        "Results.zip",
    ):
        src = root / "resources" / name
        if src.is_file():
            shutil.copy(src, work / "resources" / name)

    from unpack_source_resources import unpack_resources  # noqa: E402

    unpack_resources(work, force=True, quiet=True)
    assert (work / "resources" / "ideal.txt").is_file()
    fseries = list((work / "resources" / "Knots_FourierSeries").rglob("*.fseries"))
    assert fseries, "expected .fseries after unpack"
    assert not any(p.suffix.lower() == ".stl" for p in (work / "resources" / "Knots_FourierSeries").rglob("*"))
