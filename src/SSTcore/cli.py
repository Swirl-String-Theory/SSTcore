"""SSTcore command-line interface (Patch C)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# Default Gilbert ideal files and resource directories to export.
DEFAULT_IDEAL_FILES = (
    "ideal.txt",
    "ideal_short.txt",
    "ideal_11a.txt",
    "ideal_11n.txt",
    "idealLinks.txt",
    "idealLinks_10a.txt",
    "idealLinks_10n.txt",
    "knot_id_crosswalk.csv",
)

DEFAULT_RESOURCE_DIRS = (
    "Knots_FourierSeries",
    "knotplot",
    "ideal_12_data",
)

LARGE_DIR_WARN_BYTES = 200 * 1024 * 1024


def _import_pkg():
    try:
        import SSTcore as pkg
    except ImportError:
        import sstcore as pkg
    return pkg


def _resources_root(pkg) -> Path:
    root = pkg.get_resources_dir()
    if root is None:
        raise SystemExit("SSTcore resources directory not found.")
    return Path(root)


def _dir_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return total


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_export_entries(
    resources: Path,
    *,
    include_exports: bool,
) -> Iterable[Tuple[Path, Path]]:
    """Yield (src, rel_dest) pairs relative to export root."""
    for name in DEFAULT_IDEAL_FILES:
        src = resources / name
        if src.is_file():
            yield src, Path(name)

    for dirname in DEFAULT_RESOURCE_DIRS:
        src = resources / dirname
        if src.is_dir():
            for fp in src.rglob("*"):
                if fp.is_file():
                    yield fp, fp.relative_to(resources)

    if include_exports:
        for sub in ("exports", "SST_Dashboard/exports"):
            src = resources.parent / sub if sub.startswith("SST") else resources / sub
            if not src.is_dir():
                alt = Path.cwd() / sub
                src = alt if alt.is_dir() else src
            if src.is_dir():
                for fp in src.rglob("*"):
                    if fp.is_file():
                        yield fp, Path("exports") / fp.relative_to(src)


def export_resources(
    dest: Path,
    *,
    list_only: bool = False,
    include_exports: bool = False,
    manifest_path: Optional[Path] = None,
) -> Dict[str, Any]:
    pkg = _import_pkg()
    resources = _resources_root(pkg)
    dest = dest.resolve()

    entries = list(_iter_export_entries(resources, include_exports=include_exports))
    if not entries:
        raise SystemExit(f"No exportable resources under {resources}")

    large_dirs = []
    for dirname in DEFAULT_RESOURCE_DIRS:
        d = resources / dirname
        if d.is_dir():
            sz = _dir_size(d)
            if sz >= LARGE_DIR_WARN_BYTES:
                large_dirs.append((dirname, sz))

    report: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(resources),
        "dest": str(dest),
        "file_count": len(entries),
        "large_dir_warnings": [
            {"path": name, "bytes": size} for name, size in large_dirs
        ],
        "files": [],
    }

    if large_dirs and not list_only:
        for name, size in large_dirs:
            print(
                f"Warning: {name}/ is ~{size / (1024 * 1024):.1f} MiB",
                file=sys.stderr,
            )

    if list_only:
        for src, rel in entries:
            print(rel.as_posix())
        return report

    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    for i, (src, rel) in enumerate(entries, 1):
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        copied += 1
        if copied % 500 == 0:
            print(f"  copied {copied}/{len(entries)}...", file=sys.stderr)

    manifest_files: List[Dict[str, Any]] = []
    for src, rel in entries:
        out = dest / rel
        manifest_files.append(
            {
                "path": rel.as_posix(),
                "bytes": out.stat().st_size,
                "sha256": _sha256_file(out),
            }
        )
    report["files"] = manifest_files

    if manifest_path is not None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Manifest written: {manifest_path}")

    print(f"Exported {len(entries)} files to {dest}")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="SSTcore", description="SSTcore tooling")
    sub = parser.add_subparsers(dest="command")

    exp = sub.add_parser("export-resources", help="Copy bundled SSTcore resources to disk")
    exp.add_argument(
        "--dest",
        required=True,
        help="Output directory for exported resources",
    )
    exp.add_argument(
        "--list-only",
        action="store_true",
        help="Print relative paths only; do not copy",
    )
    exp.add_argument(
        "--include-exports",
        action="store_true",
        help="Also copy exports/ trees when present",
    )
    exp.add_argument(
        "--manifest",
        default="",
        help="Write JSON manifest with SHA256 checksums to this path",
    )
    return parser


def export_resources_entry() -> int:
    """Console script entry: ``sstcore-export-resources --dest ...``."""
    return main(["export-resources", *sys.argv[1:]])


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "export-resources":
        manifest = Path(args.manifest) if args.manifest else None
        export_resources(
            Path(args.dest),
            list_only=args.list_only,
            include_exports=args.include_exports,
            manifest_path=manifest,
        )
        return 0

    parser.print_help()
    return 0 if argv is not None else 1
