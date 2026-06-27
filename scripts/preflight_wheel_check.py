#!/usr/bin/env python3
"""Fail if built wheels contain no native extension modules (.so / .pyd)."""
from __future__ import annotations

import glob
import sys
import zipfile

CANON_PKG = "SSTcore"


def _check_package_layout(names: list[str], archive: str) -> None:
    if not any(n.startswith(f"{CANON_PKG}/") for n in names):
        print(f"error: {archive} missing {CANON_PKG}/ package tree", file=sys.stderr)
        raise SystemExit(1)


def main() -> int:
    wheels = sorted(glob.glob("dist/*.whl"))
    if not wheels:
        print("error: no wheels under dist/*.whl", file=sys.stderr)
        return 1
    for whl in wheels:
        with zipfile.ZipFile(whl) as zf:
            names = zf.namelist()
        _check_package_layout(names, whl)
        native = [n for n in names if n.endswith((".so", ".pyd"))]
        print(f"{whl} native_modules {len(native)}")
        for n in native[:10]:
            print(f"  {n}")
        if not native:
            print(f"error: wheel has no .so/.pyd: {whl}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
