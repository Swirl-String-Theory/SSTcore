#!/usr/bin/env python3
"""Generate binding_manifest.json from src/*.h and src/*_py.cpp."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from binding_inventory import default_manifest_path, generate_manifest, repo_root_from_here


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate SSTcore binding manifest.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if manifest on disk differs from generated content.",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Output path (default: src/SSTcore/resources/binding_manifest.json).",
    )
    args = parser.parse_args(argv)

    root = repo_root_from_here()
    src_dir = root / "src"
    if not src_dir.is_dir():
        print(f"ERROR: src directory not found: {src_dir}", file=sys.stderr)
        return 2

    manifest = generate_manifest(src_dir)
    out_path = Path(args.out) if args.out else default_manifest_path(root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not out_path.is_file():
            print(f"ERROR: manifest missing: {out_path}", file=sys.stderr)
            return 1
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        # Ignore timestamp-only drift.
        existing.pop("generated_at", None)
        fresh = dict(manifest)
        fresh.pop("generated_at", None)
        if existing != fresh:
            print(f"ERROR: manifest out of date: {out_path}", file=sys.stderr)
            print("Run: python scripts/gen_binding_manifest.py", file=sys.stderr)
            return 1
        print(f"OK: manifest up to date ({out_path})")
        return 0

    out_path.write_text(rendered, encoding="utf-8")
    summary = manifest["summary"]
    print(f"Wrote {out_path}")
    print(
        f"cpp_public={summary['cpp_public']} "
        f"py_bound={summary['py_bound']} "
        f"cpp_unbound={summary['cpp_unbound']} "
        f"binding_without_cpp_match={summary['binding_without_cpp_match']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
