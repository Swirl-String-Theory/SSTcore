#!/usr/bin/env python3
"""Fail if built wheels contain no native extension modules (.so / .pyd)."""
from __future__ import annotations

import glob
import sys
import zipfile


def main() -> int:
    wheels = sorted(glob.glob("dist/*.whl"))
    if not wheels:
        print("error: no wheels under dist/*.whl", file=sys.stderr)
        return 1
    for whl in wheels:
        with zipfile.ZipFile(whl) as zf:
            names = zf.namelist()
        native = [n for n in names if n.endswith((".so", ".pyd"))]
        print(f"{whl} native_modules {len(native)}")
        for n in native[:10]:
            print(f"  {n}")
        if not native:
            print(f"error: wheel has no .so/.pyd: {whl}", file=sys.stderr)
            for n in names[:80]:
                print(f"  {n}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
