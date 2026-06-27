#!/usr/bin/env python3
"""Unpack nested resource archives listed in resources/source_bundle_manifest.json."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from source_zip_common import MANIFEST_NAME, REPO_ROOT


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_manifest(repo_root: Path) -> dict:
    path = repo_root / "resources" / MANIFEST_NAME
    if not path.is_file():
        raise SystemExit(
            f"error: missing {path}\n"
            "This checkout may be a full git clone (resources already on disk) "
            "or you need the source ZIP bundle with nested archives."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def unpack_resources(repo_root: Path, *, force: bool = False, quiet: bool = False) -> int:
    manifest = _load_manifest(repo_root)
    unpacked = 0
    skipped = 0

    for entry in manifest.get("archives", []):
        zip_rel = entry["path"]
        target_rel = entry["target"]
        expected_sha = entry.get("sha256")
        zip_path = repo_root / zip_rel.replace("/", "\\")
        target_dir = repo_root / target_rel.replace("/", "\\")

        if not zip_path.is_file():
            if entry.get("optional"):
                if not quiet:
                    print(f"skip optional (missing): {zip_rel}")
                skipped += 1
                continue
            raise SystemExit(f"error: missing required archive {zip_path}")

        if expected_sha:
            actual = _sha256_file(zip_path)
            if actual != expected_sha:
                raise SystemExit(
                    f"error: checksum mismatch for {zip_rel}\n"
                    f"  expected {expected_sha}\n"
                    f"  got      {actual}"
                )

        if target_dir.is_dir() and any(target_dir.iterdir()) and not force:
            if not quiet:
                print(f"skip (exists): {target_rel}/")
            skipped += 1
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(target_dir)
        unpacked += 1
        if not quiet:
            print(f"unpacked {zip_rel} -> {target_rel}/ ({entry.get('file_count', '?')} files)")

    if not quiet:
        readme = repo_root / "resources" / "README.md"
        if readme.is_file():
            print(f"See also {readme}")
        print(f"done: unpacked={unpacked} skipped={skipped}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Unpack SSTcore nested resource ZIPs")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--force", action="store_true", help="Re-extract even if target dirs exist")
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args(argv)
    return unpack_resources(args.repo_root, force=args.force, quiet=args.quiet)


if __name__ == "__main__":
    raise SystemExit(main())
