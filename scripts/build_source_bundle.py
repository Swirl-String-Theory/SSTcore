#!/usr/bin/env python3
"""Build SSTcore-source-bundle-0.8.28.zip with lean resources + Workbench knots overlay."""
from __future__ import annotations

import os
import shutil
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WB_KNOTS = Path(r"c:\workspace\projects\SST-Workbench\KnotPlot\knots")
WB_CATALOG = Path(r"c:\workspace\projects\SST-Workbench\KnotPlot\knotplot_knots_data.js")
OUT_ZIP = ROOT / "SSTcore-source-bundle-0.8.28.zip"
STAGE = ROOT / ".cursor" / "_zip_stage" / "SSTcore"

FORBIDDEN_EXT = {".pyd", ".zip", ".stl", ".bin", ".pyc", ".node", ".obj", ".lib", ".dll", ".so", ".dylib", ".exe", ".pdb", ".a", ".o", ".log"}
KNOT_EXT = {".txt", ".json", ".vect", ".kpc"}
FIXED_MTIME = time.mktime(time.strptime("2026-01-01", "%Y-%m-%d"))


def is_rr(path: Path, base: Path) -> bool:
    try:
        rel = path.relative_to(base)
    except ValueError:
        return False
    return any(p.endswith(".rr") for p in rel.parts)


def skip_junk(path: Path) -> bool:
    parts = set(path.parts)
    return "__pycache__" in parts or ".pytest_cache" in parts or "node_modules" in parts


def copy_file(src: Path, dst: Path) -> None:
    if src.suffix.lower() in FORBIDDEN_EXT:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    os.utime(dst, (FIXED_MTIME, FIXED_MTIME))


def copy_tree_filtered(src: Path, dst: Path) -> int:
    n = 0
    if not src.is_dir():
        return 0
    for p in src.rglob("*"):
        if not p.is_file() or skip_junk(p):
            continue
        if p.suffix.lower() in FORBIDDEN_EXT:
            continue
        rel = p.relative_to(src)
        copy_file(p, dst / rel)
        n += 1
    return n


def main() -> int:
    if STAGE.parent.exists():
        shutil.rmtree(STAGE.parent)
    STAGE.mkdir(parents=True)

    for d in ("src", "include", "examples", "tests", "cmake", "scripts", "lib"):
        print(f"copy {d}:", copy_tree_filtered(ROOT / d, STAGE / d))

    for name in (
        "CMakeLists.txt",
        "setup.py",
        "package.json",
        "package-lock.json",
        "index.js",
        "index.d.ts",
        "binding.gyp",
        "NODE_BUILD.md",
        ".npmignore",
        ".nvmrc",
        "pyproject.toml",
        "requirements.txt",
        "requirements_clean.txt",
        "requirements_full.txt",
        "LICENSE",
    ):
        p = ROOT / name
        if p.exists():
            copy_file(p, STAGE / name)

    # README.md (accept Readme.md)
    readme = ROOT / "README.md"
    if not readme.exists():
        for cand in ROOT.iterdir():
            if cand.is_file() and cand.name.lower() == "readme.md":
                readme = cand
                break
    if readme.exists():
        copy_file(readme, STAGE / "README.md")

    res = STAGE / "resources"
    res.mkdir(parents=True)
    src_res = ROOT / "resources"
    for p in src_res.glob("ideal*.txt"):
        copy_file(p, res / p.name)
    for p in src_res.glob("idealLinks*.txt"):
        copy_file(p, res / p.name)
    for sub in ("ideal_12_data", "Knots_FourierSeries", "schemas"):
        s = src_res / sub
        if s.is_dir():
            for p in s.rglob("*"):
                if p.is_file() and not is_rr(p, s) and not skip_junk(p) and p.suffix.lower() not in FORBIDDEN_EXT:
                    copy_file(p, res / sub / p.relative_to(s))

    for name in (
        "knots_data_fourier.js",
        "knots_data_ideal.js",
        "knots_data_knotplot.js",
        "load_knot_catalogs.js",
        "load_knot_catalogs.d.ts",
        "knot_id_crosswalk.csv",
        "knot_meta_skeleton.csv",
        "sstcore_taxonomy_knot.schema.json",
        "binding_manifest.json",
        "fseries_batch_results.csv",
        "README.md",
    ):
        p = src_res / name
        if p.is_file():
            copy_file(p, res / name)

    kp_dst = res / "knotplot"
    kp_src = src_res / "knotplot"
    if kp_src.is_dir():
        for p in kp_src.rglob("*"):
            if not p.is_file() or is_rr(p, kp_src) or skip_junk(p):
                continue
            if p.suffix.lower() not in KNOT_EXT:
                continue
            copy_file(p, kp_dst / p.relative_to(kp_src))

    if WB_KNOTS.is_dir():
        for p in WB_KNOTS.rglob("*"):
            if not p.is_file() or is_rr(p, WB_KNOTS) or p.suffix.lower() not in KNOT_EXT:
                continue
            if p.suffix.lower() in FORBIDDEN_EXT:
                continue
            copy_file(p, kp_dst / p.relative_to(WB_KNOTS))

    if WB_CATALOG.is_file():
        copy_file(WB_CATALOG, res / "knotplot_knots_data.js")
        copy_file(WB_CATALOG, res / "knots_data_knotplot.js")

    if OUT_ZIP.exists():
        OUT_ZIP.unlink()

    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in STAGE.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(STAGE).as_posix()
            info = zipfile.ZipInfo(rel, date_time=time.localtime(FIXED_MTIME)[:6])
            info.compress_type = zipfile.ZIP_DEFLATED
            with p.open("rb") as f:
                zf.writestr(info, f.read())

    shutil.rmtree(STAGE.parent)
    print("Wrote", OUT_ZIP, "bytes=", OUT_ZIP.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
