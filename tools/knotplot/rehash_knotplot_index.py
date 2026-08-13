#!/usr/bin/env python3
"""Refresh the sha256/bytes fields in resources/knotplot/INDEX.json from disk.

The full index is written by import_workbench_knotplot.py, which needs the SST-Workbench
tree. When only the stored bytes change (e.g. an end-of-line normalisation), rehashing the
existing index is enough and keeps roles, aliases and provenance untouched.

Usage (from repo root):
  python tools/knotplot/rehash_knotplot_index.py            # rewrite INDEX.json
  python tools/knotplot/rehash_knotplot_index.py --check    # report drift, exit 1
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from io_text import write_text_lf

DEFAULT_INDEX = Path(__file__).resolve().parents[2] / "resources" / "knotplot" / "INDEX.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class RehashReport:
    """Per-file outcome of a rehash pass."""

    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def in_sync(self) -> bool:
        return not self.updated and not self.missing


def rehash_index(index: dict, root: Path) -> tuple[dict, RehashReport]:
    """Return a copy of ``index`` with sha256/bytes taken from the files under ``root``."""
    refreshed = copy.deepcopy(index)
    report = RehashReport()
    for entry in refreshed.get("entries") or []:
        for record in entry.get("files") or []:
            relpath = record.get("relpath")
            if not relpath:
                continue
            path = root / relpath
            if not path.is_file():
                report.missing.append(relpath)
                continue
            digest = sha256_file(path)
            size = path.stat().st_size
            if record.get("sha256") == digest and record.get("bytes") == size:
                report.unchanged.append(relpath)
            else:
                record["sha256"] = digest
                record["bytes"] = size
                report.updated.append(relpath)
    return refreshed, report


def write_index(index: dict, path: Path) -> None:
    """Write the index as LF-terminated JSON (resources/ is checked out verbatim)."""
    write_text_lf(path, json.dumps(index, indent=2) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="path to INDEX.json")
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 when a digest is stale or a file is missing",
    )
    args = parser.parse_args(argv)

    index_path: Path = args.index
    if not index_path.is_file():
        parser.error(f"index not found: {index_path}")

    index = json.loads(index_path.read_text(encoding="utf-8"))
    refreshed, report = rehash_index(index, index_path.parent)

    for relpath in report.missing:
        print(f"missing: {relpath}")
    for relpath in report.updated:
        print(f"{'stale' if args.check else 'rehashed'}: {relpath}")
    print(
        f"{len(report.unchanged)} in sync, {len(report.updated)} "
        f"{'stale' if args.check else 'rehashed'}, {len(report.missing)} missing"
    )

    if args.check:
        return 0 if report.in_sync else 1
    if report.missing:
        print("refusing to write: index references files that are not on disk")
        return 1
    if report.updated:
        write_index(refreshed, index_path)
        print(f"wrote {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
