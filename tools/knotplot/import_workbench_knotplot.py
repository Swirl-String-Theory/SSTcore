#!/usr/bin/env python3
"""Import filtered SST-Workbench KnotPlot exports into SSTcore resources/knotplot/.

Prefer knots/final/{id}_final.txt (shared best snapshot) as the canonical centerline.
Matching VECT is resolved from the entity folder via alias.polish_path (sibling .vect,
else {stem}.rr/{stem}.final.vect). Never copies .rr/ workspaces, .dat, intermediate
coarse/eqfinal stages, build_effort_active.kpc, or ridgerunner/out/fseries trees.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from io_text import write_text_lf

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise SystemExit("numpy is required for AB-XML regeneration") from exc

DEFAULT_WB = Path(r"c:\workspace\projects\SST-Workbench\KnotPlot")
# Aligned with SST-Workbench KnotPlot/ridgerunner/classify_catalog_status.py
STATUS_RANK = {
    "stalled-not-converged": 0,
    "relaxed-seed": 1,
    "near-ideal-candidate": 2,
    "converged-local-candidate": 3,
    "near-ideal": 4,
    "certified-ideal": 5,
}

# Historical SSTcore knot_* prefixes → Workbench folder names.
LEGACY_ALIASES = {
    "knot_T2.3": "torus_2.3",
    "knot_T2.5": "torus_2.5",
    "knot_T2.7": "torus_2.7",
    "knot_TL2.4": "torus_2.4",
    "knot_TL2.6": "torus_2.6",
    "knot_TL2.8": "torus_2.8",
    "knot_TL3.3_Gear": "torus_3.3",
    "knot_TL3.6": "torus_3.6",
    "knot_TL3.9": "torus_3.9",
    "knot_TL6.15": "torus_6.15",
    "knot_TL6.9": "torus_6.9",
    "knot_0.2.1": "link_0.2.1",
    "knot_0.3.1": "link_0.3.1",
    "knot_2.2.1": "link_2.2.1",
    "knot_4.2.1": "link_4.2.1",
    "knot_5.2.1": "link_5.2.1",
    "knot_6.2.1": "link_6.2.1",
    "knot_6.3.1": "link_6.3.1",
    "knot_6.3.2": "link_6.3.2",
    "knot_6.3.3": "link_6.3.3",
    "knot_7.2.5": "link_7.2.5",
    "knot_7.2.6": "link_7.2.6",
    "knot_7.2.8": "link_7.2.8",
    "knot_8.2.1": "link_8.2.1",
    "knot_9.2.20": "link_9.2.20",
    "knot_9.2.40": "link_9.2.40",
}

SKIP_ENTITY_DIRS = frozenset({"final", "__pycache__"})
TEXT_SUFFIXES = frozenset({".txt", ".json", ".xml", ".kpc", ".vect", ".js", ".md", ".csv"})


def copy_resource_file(src: Path, out_path: Path) -> None:
    """Copy resource bytes; normalize text payloads to LF for cross-platform sha256."""
    if src.suffix.lower() in TEXT_SUFFIXES:
        data = src.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        out_path.write_bytes(data)
    else:
        shutil.copy2(src, out_path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_xyz_components(path: Path) -> list[np.ndarray]:
    components: list[np.ndarray] = []
    current: list[list[float]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            if current:
                components.append(np.asarray(current, dtype=float))
                current = []
            continue
        fields = stripped.replace(",", " ").split()
        if len(fields) < 3:
            continue
        try:
            xyz = [float(fields[0]), float(fields[1]), float(fields[2])]
        except ValueError:
            continue
        if not all(math.isfinite(v) for v in xyz):
            raise ValueError(f"{path}:{line_number}: non-finite coordinate")
        current.append(xyz)
    if current:
        components.append(np.asarray(current, dtype=float))
    if not components:
        raise ValueError(f"{path}: no XYZ components found")
    return components


def component_length(points: np.ndarray) -> float:
    edges = np.roll(points, -1, axis=0) - points
    return float(np.linalg.norm(edges, axis=1).sum())


def dft_coefficients(points: np.ndarray, max_harmonic: int | None = None) -> list[dict]:
    """Periodic samples → A cos(It) + B sin(It) (same convention as Workbench builder)."""
    n = len(points)
    spectrum = np.fft.rfft(points, axis=0)
    full_max = n // 2
    hmax = full_max if max_harmonic is None else min(max_harmonic, full_max)
    coeffs: list[dict] = []
    for harmonic in range(hmax + 1):
        if harmonic == 0 or (n % 2 == 0 and harmonic == n // 2):
            a = spectrum[harmonic].real / n
            b = np.zeros(3)
        else:
            a = 2.0 * spectrum[harmonic].real / n
            b = -2.0 * spectrum[harmonic].imag / n
        a[np.abs(a) < 5e-16] = 0.0
        b[np.abs(b) < 5e-16] = 0.0
        coeffs.append({"I": harmonic, "A": [float(v) for v in a], "B": [float(v) for v in b]})
    return coeffs


def _fmt_triplet(vals: Iterable[float]) -> str:
    return ",".join(f"{v: .9f}" for v in vals)


def ab_xml_from_centerline(
    path: Path,
    *,
    ab_id: str,
    max_harmonic: int | None = 64,
) -> str:
    components = parse_xyz_components(path)
    # Use the longest component as the primary AB curve (matches legacy single-AB exports).
    primary = max(components, key=component_length)
    length = component_length(primary)
    coeffs = dft_coefficients(primary, max_harmonic=max_harmonic)
    # Skip DC term I=0 for Gilbert AB compatibility (legacy files start at I=1).
    lines = [
        '<DATA Title="Generated from Ridgerunner shared final / uniform N300" '
        'Author="import_workbench_knotplot.py" Date="generated locally">',
        f'  <AB Id="{ab_id}" Conway="" L="{length:.12f}" D="1.000000">',
    ]
    for row in coeffs:
        if row["I"] == 0:
            continue
        lines.append(
            f'    <Coeff I="{row["I"]:3d}" A="{_fmt_triplet(row["A"])}" B="{_fmt_triplet(row["B"])}" />'
        )
    lines.append("  </AB>")
    lines.append("</DATA>")
    lines.append("")
    return "\n".join(lines)


def guess_ab_id(folder_name: str, catalog: Optional[dict]) -> str:
    if catalog:
        ref = catalog.get("reference") or {}
        src = str(ref.get("source") or "")
        m = re.search(r"(\d+(?::\d+)+)", src)
        if m:
            return m.group(1)
    # knot_3.1 → 3:1:1 ; knot_10.123 → 10:123:1
    m = re.match(r"^knot_(\d+)\.(\d+)$", folder_name)
    if m:
        return f"{m.group(1)}:{m.group(2)}:1"
    return folder_name


def entity_kind(name: str) -> str:
    if name.startswith("link_"):
        return "link"
    if name.startswith("torus_"):
        return "torus"
    return "knot"


def status_ok(status: Optional[str], min_status: str) -> bool:
    if not status:
        return False
    return STATUS_RANK.get(status, -1) >= STATUS_RANK.get(min_status, 1)


def list_entity_dirs(knots_root: Path) -> list[Path]:
    return sorted(
        p
        for p in knots_root.iterdir()
        if p.is_dir() and p.name not in SKIP_ENTITY_DIRS and not p.name.startswith(".")
    )


def load_final_alias(final_dir: Path, entity_id: str) -> Optional[dict[str, Any]]:
    alias_path = final_dir / f"{entity_id}_final.alias.json"
    if not alias_path.is_file():
        return None
    return json.loads(alias_path.read_text(encoding="utf-8"))


def resolve_shared_final(
    final_dir: Path, entity_id: str
) -> tuple[Optional[Path], Optional[dict[str, Any]]]:
    """Prefer knots/final/{id}_final.txt; fall back to alias path pointers."""
    alias = load_final_alias(final_dir, entity_id)
    shared = final_dir / f"{entity_id}_final.txt"
    if shared.is_file():
        return shared, alias
    if alias:
        for key in ("shared_final", "source_final", "final_txt"):
            cand = alias.get(key)
            if cand:
                path = Path(str(cand))
                if path.is_file():
                    return path, alias
    return None, alias


def polish_stem_from_alias_or_catalog(
    entity_dir: Path,
    catalog: dict,
    alias: Optional[dict[str, Any]],
) -> Optional[str]:
    if alias:
        polish_path = alias.get("polish_path")
        if polish_path:
            stem = Path(str(polish_path)).stem
            if stem:
                return stem
    primary = catalog.get("primary_polish") or ""
    if primary:
        stem = Path(primary).name
        stem = stem.replace(".metrics.json", "").replace(".json", "")
        if stem.endswith(".txt"):
            stem = stem[: -len(".txt")]
        if stem:
            return stem
    uniforms = sorted(entity_dir.glob("*_polish_uniform_N300.txt"))
    if uniforms:
        return uniforms[-1].name.replace("_uniform_N300.txt", "")
    return None


def resolve_audit_vect(entity_dir: Path, polish_stem: str) -> Optional[Path]:
    """Sibling {stem}.vect first; else single file {stem}.rr/{stem}.final.vect."""
    sibling = entity_dir / f"{polish_stem}.vect"
    if sibling.is_file():
        return sibling
    rr_final = entity_dir / f"{polish_stem}.rr" / f"{polish_stem}.final.vect"
    if rr_final.is_file():
        return rr_final
    return None


def pick_primary_uniform(entity_dir: Path, catalog: dict, polish_stem: Optional[str]) -> Optional[Path]:
    if polish_stem:
        candidate = entity_dir / f"{polish_stem}_uniform_N300.txt"
        if candidate.is_file():
            return candidate
    uniforms = sorted(entity_dir.glob("*_polish_uniform_N300.txt"))
    if not uniforms:
        return None
    primary = catalog.get("primary_polish") or ""
    if primary:
        stem = Path(primary).name
        stem = stem.replace(".metrics.json", "").replace(".json", "")
        if stem.endswith("_polish"):
            candidate = entity_dir / f"{stem}_uniform_N300.txt"
            if candidate.is_file():
                return candidate
    return uniforms[-1]


def classify_entity(
    entity_dir: Path,
    min_status: str,
    *,
    final_dir: Path,
) -> dict[str, Any]:
    catalog_path = entity_dir / "catalog_status.json"
    catalog = None
    status = None
    if catalog_path.is_file():
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        status = catalog.get("status")

    status_qualifies = status_ok(status, min_status)
    files: list[dict[str, Any]] = []

    def add(src: Path, role: str, dest_name: Optional[str] = None) -> None:
        if not src.is_file():
            return
        files.append(
            {
                "src": src,
                "role": role,
                "dest_name": dest_name or src.name,
            }
        )

    # Always keep id-specific build script (not build_effort_active.kpc).
    for kpc in sorted(entity_dir.glob("build_*.kpc")):
        if kpc.name == "build_effort_active.kpc":
            continue
        add(kpc, "build_script")

    for analytic in sorted(entity_dir.glob("*_analytic_D1.txt")):
        add(analytic, "analytic_seed")

    centerline: Optional[Path] = None
    shared_txt, alias = resolve_shared_final(final_dir, entity_dir.name)
    # Shared finals are the curated best snapshots — import even if catalog status
    # is still below --min-status (e.g. stalled-not-converged with a final/).
    import_geometry = (status_qualifies and catalog is not None) or shared_txt is not None
    if import_geometry:
        geom: list[dict[str, Any]] = []

        def add_geom(src: Path, role: str, dest_name: Optional[str] = None) -> None:
            if not src.is_file():
                return
            geom.append(
                {
                    "src": src,
                    "role": role,
                    "dest_name": dest_name or src.name,
                }
            )

        if shared_txt is not None:
            add_geom(shared_txt, "shared_final", dest_name=f"{entity_dir.name}_final.txt")
            metrics = final_dir / f"{entity_dir.name}_final.metrics.json"
            if not metrics.is_file() and alias and alias.get("final_metrics"):
                metrics = Path(str(alias["final_metrics"]))
            add_geom(metrics, "shared_final_metrics", dest_name=f"{entity_dir.name}_final.metrics.json")
            if alias is not None:
                alias_src = final_dir / f"{entity_dir.name}_final.alias.json"
                if alias_src.is_file():
                    add_geom(alias_src, "shared_final_alias", dest_name=f"{entity_dir.name}_final.alias.json")
            centerline = shared_txt

        catalog_for_pick = catalog or {}
        polish_stem = polish_stem_from_alias_or_catalog(entity_dir, catalog_for_pick, alias)
        uniform = pick_primary_uniform(entity_dir, catalog_for_pick, polish_stem)
        if uniform is not None:
            add_geom(uniform, "uniform_n300")
            add_geom(Path(str(uniform).replace(".txt", ".resample.json")), "resample")
            if centerline is None:
                centerline = uniform

        if polish_stem:
            polish_txt = entity_dir / f"{polish_stem}.txt"
            add_geom(polish_txt, "audit_polish")
            add_geom(entity_dir / f"{polish_stem}.metrics.json", "audit_metrics")
            vect = resolve_audit_vect(entity_dir, polish_stem)
            if vect is not None:
                add_geom(vect, "audit_vect", dest_name=f"{polish_stem}.vect")
            if centerline is None and polish_txt.is_file():
                centerline = polish_txt

        # Placeholder catalogs (status without polish/final) stay stubs.
        if centerline is not None:
            if catalog_path.is_file():
                add(catalog_path, "catalog_status")
            add(entity_dir / "seed_selection.json", "seed_selection")
            files.extend(geom)
            files.append(
                {
                    "src": None,
                    "role": "ab_xml",
                    "dest_name": f"{entity_dir.name}_ab.xml",
                    "ab_id": guess_ab_id(entity_dir.name, catalog),
                    "centerline": centerline,
                }
            )

    relaxed = centerline is not None

    return {
        "id": entity_dir.name,
        "kind": entity_kind(entity_dir.name),
        "status": status or ("shared-final" if relaxed else "stub"),
        "relaxed": relaxed,
        "epsilon_R": (catalog or {}).get("epsilon_R") if relaxed else None,
        "files": files,
        "catalog": catalog,
    }


def build_plan(workbench_root: Path, dest: Path, min_status: str) -> dict[str, Any]:
    knots_root = workbench_root / "knots"
    if not knots_root.is_dir():
        raise SystemExit(f"Workbench knots dir missing: {knots_root}")
    final_dir = knots_root / "final"

    entities = [
        classify_entity(d, min_status, final_dir=final_dir) for d in list_entity_dirs(knots_root)
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workbench_root": str(workbench_root),
        "dest": str(dest),
        "min_status": min_status,
        "counts": {
            "total": len(entities),
            "relaxed": sum(1 for e in entities if e["relaxed"]),
            "stub": sum(1 for e in entities if not e["relaxed"]),
        },
        "legacy_aliases": dict(LEGACY_ALIASES),
        "entities": entities,
    }


def apply_plan(plan: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    dest = Path(plan["dest"]).resolve()
    workbench_root = Path(plan["workbench_root"]).resolve()
    index_entries: list[dict[str, Any]] = []
    planned_ids = {e["id"] for e in plan["entities"]}

    # Windows paths are case-insensitive: refuse dest that collides with the Workbench tree.
    try:
        dest.relative_to(workbench_root)
        raise SystemExit(
            f"refusing to write dest inside workbench_root (case-insensitive collision?): "
            f"dest={dest} workbench_root={workbench_root}"
        )
    except ValueError:
        pass

    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)
        # Drop orphan entity dirs left from a previous import layout.
        for child in list(dest.iterdir()):
            if child.is_dir() and child.name not in planned_ids and child.name != "__pycache__":
                shutil.rmtree(child)

    for entity in plan["entities"]:
        entity_dest = dest / entity["id"]
        copied: list[dict[str, Any]] = []
        ab_relpath = None
        if not dry_run:
            if entity_dest.is_dir():
                shutil.rmtree(entity_dest)
            entity_dest.mkdir(parents=True, exist_ok=True)

        for item in entity["files"]:
            role = item["role"]
            dest_name = item["dest_name"]
            out_path = entity_dest / dest_name

            if role == "ab_xml":
                centerline = item.get("centerline")
                if centerline is None or not Path(centerline).is_file():
                    continue
                text = ab_xml_from_centerline(Path(centerline), ab_id=item["ab_id"])
                if not dry_run:
                    write_text_lf(out_path, text)
                    digest = sha256_file(out_path)
                    size = out_path.stat().st_size
                else:
                    payload = text.encode("utf-8")
                    digest = hashlib.sha256(payload).hexdigest()
                    size = len(payload)
                ab_relpath = f"{entity['id']}/{dest_name}"
                copied.append(
                    {
                        "role": role,
                        "relpath": ab_relpath,
                        "source": str(centerline),
                        "sha256": digest,
                        "bytes": size,
                    }
                )
                continue

            src_raw = item.get("src")
            if src_raw is None:
                continue
            src = Path(src_raw)
            if not src.is_file():
                continue
            if not dry_run:
                copy_resource_file(src, out_path)
            digest = (
                sha256_file(src)
                if dry_run
                else sha256_file(out_path if out_path.is_file() else src)
            )
            copied.append(
                {
                    "role": role,
                    "relpath": f"{entity['id']}/{dest_name}",
                    "source": str(src),
                    "source_name": src.name,
                    "sha256": digest,
                    "bytes": src.stat().st_size,
                }
            )

        index_entries.append(
            {
                "id": entity["id"],
                "kind": entity["kind"],
                "status": entity["status"],
                "relaxed": entity["relaxed"],
                "epsilon_R": entity["epsilon_R"],
                "ab_xml": ab_relpath,
                "files": copied,
            }
        )

    index = {
        "version": 1,
        "generated_at": plan["generated_at"],
        "min_status": plan["min_status"],
        "workbench_root": plan["workbench_root"],
        "counts": plan["counts"],
        "legacy_aliases": plan["legacy_aliases"],
        "entries": index_entries,
    }

    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)
        # resources/ is checked out verbatim (.gitattributes -text), so keep LF on Windows too.
        write_text_lf(dest / "INDEX.json", json.dumps(index, indent=2) + "\n")

    return index


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbench-root", type=Path, default=DEFAULT_WB)
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "resources" / "knotplot",
    )
    parser.add_argument(
        "--min-status",
        default="relaxed-seed",
        choices=sorted(STATUS_RANK, key=STATUS_RANK.get),
    )
    parser.add_argument("--dry-run", action="store_true", help="Plan only; write nothing")
    parser.add_argument("--json-out", type=Path, default=None, help="Write plan/index JSON here")
    args = parser.parse_args(argv)

    plan = build_plan(args.workbench_root.resolve(), args.dest.resolve(), args.min_status)
    index = apply_plan(plan, dry_run=args.dry_run)

    summary = {
        "dry_run": args.dry_run,
        "counts": plan["counts"],
        "dest": str(args.dest),
        "sample_relaxed": [e["id"] for e in plan["entities"] if e["relaxed"]][:5],
        "sample_stub": [e["id"] for e in plan["entities"] if not e["relaxed"]][:5],
    }
    print(json.dumps(summary, indent=2))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = {"plan_counts": plan["counts"], "index": index}
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
