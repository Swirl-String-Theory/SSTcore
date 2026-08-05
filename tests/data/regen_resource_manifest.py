#!/usr/bin/env python3
"""Regenerate tests/data/resource_manifest.json from the live SSTcore resource API.

Usage (from repo root):
  python tests/data/regen_resource_manifest.py

The inventory test asserts every entry exists with a matching SHA256. After a
legitimate resource change (e.g. deelplan res-3 knotplot swap), regenerate and
review the diff rather than hand-editing.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

_TESTS = Path(__file__).resolve().parent.parent
_REPO = _TESTS.parent
if str(_TESTS) not in sys.path:
    sys.path.insert(0, str(_TESTS))

from sstcore_test_import import load_sstcore_package  # noqa: E402


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest() -> dict:
    sst = load_sstcore_package()
    root = sst.get_resources_dir()
    if root is None:
        raise SystemExit("get_resources_dir() returned None")

    entries: list[dict] = []

    for key in sst.list_ideal_source_files():
        path = sst.get_ideal_file_path(key)
        if path is None or not path.is_file():
            continue
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        entries.append(
            {
                "id": key,
                "kind": "ideal",
                "relpath": rel,
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
        )

    favorites = None
    for candidate in (root / "ideal" / "ideal_favorites.txt", root / "ideal_favorites.txt"):
        if candidate.is_file():
            favorites = candidate
            break
    if favorites is not None:
        rel = favorites.resolve().relative_to(root.resolve()).as_posix()
        entries.append(
            {
                "id": "ideal_favorites.txt",
                "kind": "ideal_aux",
                "relpath": rel,
                "sha256": _sha256(favorites),
                "bytes": favorites.stat().st_size,
            }
        )

    kp = sst.get_knotplot_dir()
    if kp is not None and kp.is_dir():
        index_path = kp / "INDEX.json"
        if index_path.is_file():
            import json as _json

            index = _json.loads(index_path.read_text(encoding="utf-8"))
            for entry in index.get("entries") or []:
                if not entry.get("relaxed"):
                    continue
                kid = entry["id"]
                resolved = sst.get_knotplot_ideal_path(kid)
                if resolved is None or not resolved.is_file():
                    continue
                rel = resolved.resolve().relative_to(root.resolve()).as_posix()
                entries.append(
                    {
                        "id": kid,
                        "kind": "knotplot_ideal",
                        "relpath": rel,
                        "sha256": _sha256(resolved),
                        "bytes": resolved.stat().st_size,
                    }
                )
        else:
            for knot_dir in sorted(
                p for p in kp.iterdir() if p.is_dir() and p.name != "__pycache__"
            ):
                kid = knot_dir.name
                resolved = sst.get_knotplot_ideal_path(kid)
                if resolved is None or not resolved.is_file():
                    continue
                rel = resolved.resolve().relative_to(root.resolve()).as_posix()
                entries.append(
                    {
                        "id": kid,
                        "kind": "knotplot_ideal",
                        "relpath": rel,
                        "sha256": _sha256(resolved),
                        "bytes": resolved.stat().st_size,
                    }
                )

    kfs = sst.get_knots_fourier_series_dir()
    if kfs is not None and kfs.is_dir():
        for label in ("3_1", "4_1", "5_1"):
            exact = f"knot.{label}.fseries"
            found: Path | None = None
            for dirpath, _dirs, files in os.walk(kfs):
                if exact in files:
                    found = Path(dirpath) / exact
                    break
            if found is None:
                continue
            rel = found.resolve().relative_to(root.resolve()).as_posix()
            entries.append(
                {
                    "id": label,
                    "kind": "fseries",
                    "relpath": rel,
                    "sha256": _sha256(found),
                    "bytes": found.stat().st_size,
                }
            )

    return {
        "version": 1,
        "description": (
            "API-driven resource inventory for deelplan res-0. "
            "Regenerate with: python -m tests.data.regen_resource_manifest"
        ),
        "entries": entries,
    }


def main() -> int:
    # Prefer the checkout src/ tree so regen matches pytest's pythonpath=["src"].
    src = str(_REPO / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    for name in ("SSTcore", "sstcore"):
        sys.modules.pop(name, None)

    manifest = build_manifest()
    out = Path(__file__).resolve().parent / "resource_manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(manifest['entries'])} entries)")
    sample = next((e for e in manifest["entries"] if e["kind"] == "ideal"), None)
    if sample:
        print(f"sample ideal relpath: {sample['relpath']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
