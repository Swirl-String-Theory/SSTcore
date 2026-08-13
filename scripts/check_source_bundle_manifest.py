#!/usr/bin/env python3
"""Fail if paths required by package.json / source-bundle CI are missing."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "scripts/",
    "lib/resource_helpers.js",
    "lib/resource_helpers.d.ts",
    "LICENSE",
    "package.json",
    "CMakeLists.txt",
    "setup.py",
    "index.js",
    "index.d.ts",
    "binding.gyp",
    "src/",
    "include/",
    "resources/ideal.txt",
    "resources/Knots_FourierSeries/",
]


def _exists_ci(rel: str) -> bool:
    """Path exists; README.md also matches Readme.md on case-sensitive filesystems."""
    p = ROOT / rel.rstrip("/")
    if rel.endswith("/"):
        return p.is_dir()
    if p.is_file():
        return True
    if rel.lower() == "readme.md":
        for cand in ROOT.iterdir():
            if cand.is_file() and cand.name.lower() == "readme.md":
                return True
    return False


def main() -> int:
    missing: list[str] = []
    for rel in REQUIRED:
        if not _exists_ci(rel):
            missing.append(rel)
    if not _exists_ci("README.md"):
        missing.append("README.md")

    # package.json files[] entries that are source (not build outputs)
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    for entry in pkg.get("files", []):
        if any(entry.startswith(p) for p in ("dist/", "prebuilds/")):
            continue  # optional build artifacts
        if "*" in entry:
            continue
        if not _exists_ci(entry):
            missing.append(f"package.json:{entry}")

    missing = sorted(set(missing))
    if missing:
        print("source-bundle manifest missing:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 1
    print(f"OK: required paths present under {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
