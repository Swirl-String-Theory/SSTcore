#!/usr/bin/env python3
"""Fail if the Python package directory is not ``SSTcore/`` in wheels/sdist."""
from __future__ import annotations

import glob
import os
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANON_DIR = "SSTcore"
SRC_PKG_INIT = REPO_ROOT / "src" / CANON_DIR / "__init__.py"


def _git_tracked_package_paths() -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "ls-files", f"src/{CANON_DIR}/", f"{CANON_DIR}/", "sstcore/"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def check_source_tree() -> None:
    if not SRC_PKG_INIT.is_file():
        legacy = REPO_ROOT / CANON_DIR / "__init__.py"
        lower = REPO_ROOT / "sstcore" / "__init__.py"
        if legacy.is_file() or lower.is_file():
            raise SystemExit(
                "error: Python package not under src/SSTcore/. "
                "Move to src-layout: git mv SSTcore src/SSTcore (or sstcore → src/SSTcore)."
            )
        raise SystemExit(f"error: missing {SRC_PKG_INIT}")


def check_git_index() -> None:
    tracked = _git_tracked_package_paths()
    bad = [p for p in tracked if p.startswith("sstcore/") and not p.startswith("src/")]
    if bad:
        raise SystemExit(
            "error: git tracks lowercase root package paths:\n  "
            + "\n  ".join(bad[:20])
        )


def check_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
    if not any(n.startswith(f"{CANON_DIR}/") for n in names):
        raise SystemExit(f"error: wheel {path} missing {CANON_DIR}/ package tree")


def check_sdist(path: Path) -> None:
    with tarfile.open(path, "r:*") as tf:
        names = tf.getnames()
    if not any(n.endswith(f"/{CANON_DIR}/__init__.py") for n in names):
        raise SystemExit(f"error: sdist {path} missing .../{CANON_DIR}/__init__.py")


def main() -> int:
    check_git_index()
    check_source_tree()

    for whl in sorted(glob.glob(str(REPO_ROOT / "dist" / "*.whl"))):
        check_wheel(Path(whl))
        print(f"ok wheel package layout: {whl}")

    for sdist in sorted(glob.glob(str(REPO_ROOT / "dist" / "*.tar.gz"))):
        check_sdist(Path(sdist))
        print(f"ok sdist package layout: {sdist}")

    print(f"ok source layout: src/{CANON_DIR}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
