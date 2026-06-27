#!/usr/bin/env python3
"""Build dist/SSTcore_source_vX.Y.Z.zip — compact audit bundle with nested resource archives."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from source_zip_common import (
    MANIFEST_NAME,
    NESTED_SPECS,
    REPO_ROOT,
    collect_source_files,
    iter_files_for_nested_dir,
    read_version,
    repo_rel_path,
)

SOURCE_ZIP_README = """SSTcore source bundle
=====================

Large resource trees are nested under resources/*.zip.

Before build or tests:
  python scripts/unpack_source_resources.py

See resources/README.md for details.
"""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _add_file_to_zip(zf: zipfile.ZipFile, disk_path: Path, arcname: str) -> None:
    arc = arcname.replace("\\", "/")
    info = zipfile.ZipInfo(filename=arc)
    info.compress_type = zipfile.ZIP_DEFLATED
    data = disk_path.read_bytes()
    zf.writestr(info, data)


def build_nested_archive(repo_root: Path, spec, staging_resources: Path) -> dict | None:
    files = list(iter_files_for_nested_dir(repo_root, spec.rel_dir))
    if not files:
        if spec.optional:
            return None
        raise RuntimeError(f"required resource dir empty or missing: {spec.rel_dir}")

    excluded_stl = 0
    if spec.rel_dir == "resources/Knots_FourierSeries":
        base = repo_root / "resources" / "Knots_FourierSeries"
        if base.is_dir():
            excluded_stl = sum(1 for p in base.rglob("*.stl") if p.is_file())

    zip_path = staging_resources / Path(spec.zip_name).name
    dir_name = spec.rel_dir.split("/")[-1]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            inner = path.relative_to(repo_rel_path(repo_root, spec.rel_dir))
            arc = f"{dir_name}/{inner.as_posix()}"
            zf.write(path, arcname=arc)

    entry: dict = {
        "path": spec.zip_name,
        "target": spec.target,
        "sha256": _sha256_file(zip_path),
        "file_count": len(files),
    }
    if spec.optional:
        entry["optional"] = True
    if spec.rel_dir == "resources/Results":
        entry["excluded_subtree"] = "knotplot"
    if excluded_stl:
        entry["excluded_stl"] = excluded_stl
    return entry


def _norm_zip_name(name: str) -> str:
    return name.replace("\\", "/")


def validate_main_zip(zf: zipfile.ZipFile, version: str, manifest: dict) -> None:
    name_map = {_norm_zip_name(n): n for n in zf.namelist()}
    names = set(name_map)
    prefix = f"SSTcore-v{version}/"

    def has(suffix: str) -> bool:
        return (prefix + suffix) in names

    required = [
        "src/SSTcore/__init__.py",
        "resources/ideal.txt",
        "resources/README.md",
        f"resources/{MANIFEST_NAME}",
        "setup.py",
    ]
    for r in required:
        if not has(r):
            raise RuntimeError(f"source zip missing {prefix}{r}")

    for spec in NESTED_SPECS:
        if spec.optional:
            continue
        if not has(spec.zip_name):
            raise RuntimeError(f"source zip missing nested archive {spec.zip_name}")

    for n in names:
        low = n.lower()
        if low.endswith(".stl"):
            raise RuntimeError(f".stl in source zip: {n}")
        if ".pyc" in low or "__pycache__" in low:
            raise RuntimeError(f"bytecode in source zip: {n}")
        if "/src/SSTcore/resources/" in n:
            raise RuntimeError(f"junction leak in source zip: {n}")
        for loose_prefix in ("ideal_12_data/", "knotplot/", "Knots_FourierSeries/"):
            marker = f"/resources/{loose_prefix}"
            if marker in n and not n.endswith(".zip"):
                tail = n.split(marker, 1)[-1]
                if tail and not tail.startswith("../"):
                    raise RuntimeError(f"loose resource file in zip (use nested): {n}")

    for entry in manifest.get("archives", []):
        zip_arc = prefix + entry["path"]
        if zip_arc not in names:
            if entry.get("optional"):
                continue
            raise RuntimeError(f"manifest archive not in zip: {entry['path']}")
        raw_name = name_map[zip_arc]
        data = zf.read(raw_name)
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        try:
            with zipfile.ZipFile(tmp_path) as inner:
                for inner_name in inner.namelist():
                    if inner_name.lower().endswith(".stl"):
                        raise RuntimeError(f".stl inside {entry['path']}: {inner_name}")
        finally:
            tmp_path.unlink(missing_ok=True)


def build_source_zip(
    repo_root: Path,
    output: Path,
    *,
    dry_run: bool = False,
) -> Path:
    version = read_version(repo_root)
    files = collect_source_files(repo_root)
    prefix = f"SSTcore-v{version}/"

    if dry_run:
        print(f"dry-run: would pack {len(files)} files -> {output}")
        for spec in NESTED_SPECS:
            n = len(list(iter_files_for_nested_dir(repo_root, spec.rel_dir)))
            print(f"  nested {spec.zip_name}: {n} files (optional={spec.optional})")
        return output

    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="sstcore_source_zip_"))
    try:
        staging_resources = staging / "resources"
        staging_resources.mkdir(parents=True)

        archives: list[dict] = []
        nested_zip_rels: set[str] = set()
        for spec in NESTED_SPECS:
            entry = build_nested_archive(repo_root, spec, staging_resources)
            if entry is None:
                continue
            archives.append(entry)
            nested_zip_rels.add(spec.zip_name)

        manifest = {
            "version": version,
            "excluded_patterns": ["*.stl", "Results/knotplot/**"],
            "archives": archives,
        }
        manifest_path = staging_resources / MANIFEST_NAME
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            readme_info = zipfile.ZipInfo(filename=prefix + "SOURCE_ZIP_README.txt")
            readme_info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(readme_info, SOURCE_ZIP_README)

            for rel in files:
                if rel in nested_zip_rels or rel == f"resources/{MANIFEST_NAME}":
                    continue
                disk = repo_rel_path(repo_root, rel)
                if not disk.is_file():
                    continue
                _add_file_to_zip(zf, disk, prefix + rel)

            for entry in archives:
                zip_name = Path(entry["path"]).name
                disk = staging_resources / zip_name
                _add_file_to_zip(zf, disk, prefix + entry["path"])

            _add_file_to_zip(zf, manifest_path, prefix + f"resources/{MANIFEST_NAME}")

            validate_main_zip(zf, version, manifest)

        print(f"ok: {output} ({len(files)} source files + {len(archives)} nested archives)")
        return output
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build SSTcore_source_vX.Y.Z.zip")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path (default: dist/SSTcore_source_vVERSION.zip)",
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    version = read_version(args.repo_root)
    output = args.output or (args.repo_root / "dist" / f"SSTcore_source_v{version}.zip")

    try:
        build_source_zip(args.repo_root, output, dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
