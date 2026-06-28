#!/usr/bin/env python3
r"""
routeB_RT_bem_v18_extended_local_scan_knotplot.py
=================================================

Extended BEMv18 local scanner with KnotPlot-style IDs and link-aware cataloguing.

Target policy
-------------
1. include all ordinary knots in ideal.txt up to and including 7 crossings;
2. add selected higher ordinary knots if available:
       8_1, 9_1, 9_2, 10_1
3. add KnotPlot-style 11-crossing aliases if available:
       K11a367, K11a247
4. catalog, but do not run by default, the links:
       L2a1, L4a1, L5a1, L6a1, L8a1, L6a4, L6n1

Why links are skipped by default
--------------------------------
The current BEMv8/BEMv13 Route-B code path is single-component centered-curve
based.  Multi-component link records in ideal.txt usually require a different
geometry parser and pair-reference construction.  This wrapper therefore
catalogs link IDs, but keeps the run target list to single-component knots
unless you explicitly override the scripts downstream.

No observed alpha is used.

Scale-role convention: r_c, R_horn, and a_tube
----------------------------------------------
Route-B BEM is a dimensionless certified-geometry programme.  Its numerical
normalizers use L_cert, M_max, and DeltaF_pair; they do not require inserting a
physical core radius into the BEM score.

When a physical radius is discussed, use

    r_c == R_horn

where R_horn is the horn-torus / return-flow circulation radius.  Do not
silently identify r_c with the local ideal-tube radius.  Use

    a_tube = R_horn / chi_h = r_c / chi_h
    ell_K_phys = 2 * a_tube * L_cert

The dimensionless Route-B normalizer remains

    N_RT = M_max * L_cert**2

while physical reconstruction uses

    L_phys**2 = 4 * a_tube**2 * L_cert**2
              = 4 * r_c**2 * L_cert**2 / chi_h**2

Only if chi_h is later made knot-dependent should a separate horn-effective
scan use M_max * (L_cert / chi_h(K))**2.  BEMv1--BEMv19 default mode is the
certified dimensionless geometry mode.

"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: List[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def parse_attrs(tag: str) -> Dict[str, str]:
    return {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"', tag)}


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


def ideal_id_to_name(bid: str) -> str:
    """Map ideal IDs to stable names.

    Numeric Brian Gilbert IDs:
        5:1:2 -> 5_2
        7:1:4 -> 7_4

    KnotPlot-style IDs:
        K11a367 -> K11a367
        L6n1    -> L6n1
    """
    s = str(bid)
    parts = s.split(":")
    if len(parts) >= 3:
        return f"{parts[0]}_{parts[2]}"
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return s.replace(":", "_")


def name_to_id(name: str) -> str:
    m = re.match(r"^(\d+)_(\d+)$", name)
    if m:
        return f"{m.group(1)}:1:{m.group(2)}"
    return name


def infer_crossing_and_kind(bid: str, name: str) -> Tuple[Any, str]:
    s = str(bid)
    parts = s.split(":")
    if len(parts) >= 3 and parts[0].isdigit():
        return int(parts[0]), "ordinary_knot"
    m = re.match(r"^K(\d+)[a-zA-Z]\d+$", s)
    if m:
        return int(m.group(1)), "knotplot_knot"
    m = re.match(r"^L(\d+)[a-zA-Z]\d+$", s)
    if m:
        return int(m.group(1)), "knotplot_link"
    return "", "unknown"


def parse_ideal(path: Path) -> Dict[str, Dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    out: Dict[str, Dict[str, Any]] = {}
    for m in re.finditer(r"<AB\b([^>]*)>", text, flags=re.I):
        attrs = parse_attrs(m.group(1))
        bid = attrs.get("Id", "")
        if not bid:
            continue
        name = ideal_id_to_name(bid)
        crossing, kind = infer_crossing_and_kind(bid, name)
        rec = {
            "id": bid,
            "name": name,
            "crossing": crossing,
            "index": name.split("_")[1] if "_" in name else "",
            "kind": kind,
            "conway": attrs.get("Conway", ""),
            "L_cert": float(attrs["L"]) if attrs.get("L") else "",
            "D_database": float(attrs["D"]) if attrs.get("D") else "",
            "n_components": int(attrs.get("n", "1").strip() or "1"),
        }
        out[bid] = rec
        out[name] = rec
    return out


def load_aliases(path: Path) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"knot_aliases": {}, "link_ids": {}}


def resolve_token(catalog: Dict[str, Dict[str, Any]], token: str) -> Dict[str, Any] | None:
    key = token if token in catalog else name_to_id(token)
    return catalog.get(key)


def select_targets(catalog: Dict[str, Dict[str, Any]], aliases: Dict[str, Any], max_crossing: int, extras: str, knotplot_11: str, link_ids: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    run_targets: List[Dict[str, Any]] = []
    link_catalog: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    seen = set()

    # Ordinary knots through max_crossing.
    ordinary = []
    for key, rec in catalog.items():
        if key != rec["id"]:
            continue
        if rec["kind"] == "ordinary_knot" and isinstance(rec["crossing"], int) and 3 <= rec["crossing"] <= max_crossing:
            if int(rec.get("n_components", 1)) == 1:
                ordinary.append(rec)
    ordinary.sort(key=lambda r: (int(r["crossing"]), int(r["index"]) if str(r["index"]).isdigit() else 0))

    for rec in ordinary:
        if rec["id"] not in seen:
            seen.add(rec["id"])
            run_targets.append(rec)

    # Selected ordinary extras.
    for token in [x.strip() for x in extras.split(",") if x.strip()]:
        rec = resolve_token(catalog, token)
        if rec is None:
            missing.append({"requested": token, "resolved_id": name_to_id(token), "status": "MISSING_FROM_IDEAL"})
            continue
        if int(rec.get("n_components", 1)) != 1:
            missing.append({"requested": token, "resolved_id": rec["id"], "status": "SKIP_NON_SINGLE_COMPONENT"})
            continue
        if rec["id"] not in seen:
            seen.add(rec["id"])
            run_targets.append(rec)

    # KnotPlot 11-knot aliases.
    knot_aliases = aliases.get("knot_aliases", {})
    for token in [x.strip() for x in knotplot_11.split(",") if x.strip()]:
        rec = resolve_token(catalog, token)
        if rec is None:
            missing.append({"requested": token, "resolved_id": token, "status": "MISSING_FROM_IDEAL"})
            continue
        rec = dict(rec)
        if token in knot_aliases:
            rec["display_alias"] = knot_aliases[token].get("display_alias", "")
            rec["alias_note"] = knot_aliases[token].get("note", "")
        if int(rec.get("n_components", 1)) != 1:
            missing.append({"requested": token, "resolved_id": rec["id"], "status": "SKIP_NON_SINGLE_COMPONENT"})
            continue
        if rec["id"] not in seen:
            seen.add(rec["id"])
            run_targets.append(rec)

    # Link catalog only.
    link_meta = aliases.get("link_ids", {})
    for token in [x.strip() for x in link_ids.split(",") if x.strip()]:
        rec = resolve_token(catalog, token)
        if rec is None:
            missing.append({"requested": token, "resolved_id": token, "status": "MISSING_FROM_IDEAL_LINK"})
            continue
        rec = dict(rec)
        rec["run_supported_by_current_bem"] = link_meta.get(token, {}).get("run_supported_by_current_bem", False)
        rec["catalog_status"] = "CATALOG_ONLY_LINK"
        link_catalog.append(rec)

    return run_targets, link_catalog, missing, ordinary


def resolve_script(primary: str, local_name: str, fallback: str) -> Path:
    if primary:
        p = Path(primary)
        if p.exists():
            return p
        raise FileNotFoundError(p)
    p = Path(__file__).with_name(local_name)
    if p.exists():
        return p
    p = Path(fallback)
    if p.exists():
        return p
    raise FileNotFoundError(f"could not find {local_name} or {fallback}")


def run_target(args, target: Dict[str, Any], run_dir: Path) -> Dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    done = run_dir / "alpha_component_budget_v13.csv"
    if done.exists() and not args.force:
        return {"target": target["name"], "target_id": target["id"], "run_dir": str(run_dir), "returncode": 0, "mode": "skip_existing", "status": "SKIP_EXISTING"}

    v13 = resolve_script(args.v13_script, "routeB_RT_bem_v13_certified_length_budget.py", "/mnt/data/routeB_RT_bem_v13_certified_length_budget.py")
    v8 = resolve_script(args.v8_script, "routeB_RT_bem_v8_pair_length_budget.py", "/mnt/data/routeB_RT_bem_v8_pair_length_budget.py")
    ids = f"0:1:1,{target['id']}"
    cmd = [
        sys.executable, str(v13),
        "--ideal", str(args.ideal),
        "--v8-script", str(v8),
        "--outdir", str(run_dir),
        "--ideal-xml-knot-ids", ids,
        "--target", target["name"],
        "--reference", "0_1",
        "--n-center", str(args.n_center),
        "--n-theta", str(args.n_theta),
        "--n-sphere", str(args.n_sphere),
        "--tube-fraction", str(args.tube_fraction),
        "--outer-factor", str(args.outer_factor),
        "--pair-fit-min-M", str(args.pair_fit_min_M),
        "--pair-fit-tail-frac", str(args.pair_fit_tail_frac),
        "--length-samples", str(args.length_samples),
        "--normalizers", args.normalizers,
        "--preferred-normalizer", args.preferred_normalizer,
        "--subrun-timeout", str(args.subrun_timeout),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.target_run_timeout)
    (run_dir / "bemv13_stdout.txt").write_text(proc.stdout, encoding="utf-8", errors="replace")
    (run_dir / "bemv13_stderr.txt").write_text(proc.stderr, encoding="utf-8", errors="replace")
    return {"target": target["name"], "target_id": target["id"], "run_dir": str(run_dir), "returncode": proc.returncode, "mode": "run_bemv13", "status": "PASS" if proc.returncode == 0 else "FAIL", "command": " ".join(cmd)}


def run_aggregate(args, run_dirs: List[Path], aggregate_dir: Path) -> int:
    v18 = resolve_script(args.v18_script, "routeB_RT_bem_v18_multiknot_exponent_test.py", "/mnt/data/routeB_RT_bem_v18_multiknot_exponent_test.py")
    aggregate_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(v18),
        "--ideal", str(args.ideal),
        "--from-bemv13-outdirs", ",".join(str(p) for p in run_dirs),
        "--outdir", str(aggregate_dir),
        "--preferred-normalizer", args.preferred_normalizer,
        "--scan-a", args.scan_a,
        "--scan-b", args.scan_b,
        "--ratio-threshold", str(args.ratio_threshold),
        "--min-knots", str(args.min_knots),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.aggregate_timeout)
    (aggregate_dir / "aggregate_stdout.txt").write_text(proc.stdout, encoding="utf-8", errors="replace")
    (aggregate_dir / "aggregate_stderr.txt").write_text(proc.stderr, encoding="utf-8", errors="replace")
    return proc.returncode


def write_report(outdir: Path, run_targets: List[Dict[str, Any]], links: List[Dict[str, Any]], missing: List[Dict[str, Any]], manifest: List[Dict[str, Any]], aggregate_status: str) -> None:
    lines = [
        "# BEMv18 extended KnotPlot-aware scan report",
        "",
        "Run targets are single-component knot records only. Link IDs are catalogued separately because the current BEM route is not link-geometry aware.",
        "",
        "## Run targets",
        "",
    ]
    for r in run_targets:
        alias = f" / alias `{r.get('display_alias')}`" if r.get("display_alias") else ""
        lines.append(f"- `{r['name']}` / `{r['id']}`{alias}: `L_cert={r.get('L_cert')}`")
    lines += ["", "## Catalogued links, not run by default", ""]
    if links:
        for r in links:
            lines.append(f"- `{r['id']}`: `L_cert={r.get('L_cert')}`, `n_components={r.get('n_components')}`")
    else:
        lines.append("- none found")
    lines += ["", "## Missing / skipped", ""]
    if missing:
        for r in missing:
            lines.append(f"- `{r['requested']}` -> `{r['resolved_id']}`: `{r['status']}`")
    else:
        lines.append("- none")
    lines += ["", "## Run status", ""]
    if manifest:
        ok = sum(1 for r in manifest if str(r.get("returncode")) == "0")
        lines.append(f"- successful/available BEMv13 runs: `{ok}/{len(manifest)}`")
        lines.append(f"- aggregate status: `{aggregate_status}`")
    else:
        lines.append("- dry-run plan only")
    (outdir / "KNOTPLOT_SCAN_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v18_knotplot")
    ap.add_argument("--alias-json", default="BEMv18_knotplot_aliases.json")
    ap.add_argument("--max-crossing", type=int, default=7)
    ap.add_argument("--extras", default="8_1,9_1,9_2,10_1")
    ap.add_argument("--knotplot-11", default="K11a367,K11a247")
    ap.add_argument("--link-ids", default="L2a1,L4a1,L5a1,L6a1,L8a1,L6a4,L6n1")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry-run-plan", action="store_true")
    ap.add_argument("--force", action="store_true")

    ap.add_argument("--v13-script", default="")
    ap.add_argument("--v8-script", default="")
    ap.add_argument("--v18-script", default="")

    ap.add_argument("--n-center", type=int, default=24)
    ap.add_argument("--n-theta", type=int, default=5)
    ap.add_argument("--n-sphere", type=int, default=96)
    ap.add_argument("--tube-fraction", type=float, default=0.30)
    ap.add_argument("--outer-factor", type=float, default=3.0)
    ap.add_argument("--pair-fit-min-M", type=int, default=8)
    ap.add_argument("--pair-fit-tail-frac", type=float, default=0.75)
    ap.add_argument("--length-samples", type=int, default=12000)
    ap.add_argument("--normalizers", default="raw,Mmax,Lcert,Lcert2,Lcert3,M_Lcert,M_Lcert2")
    ap.add_argument("--preferred-normalizer", default="M_Lcert2")
    ap.add_argument("--subrun-timeout", type=int, default=1800)
    ap.add_argument("--target-run-timeout", type=int, default=2400)

    ap.add_argument("--scan-a", default="1")
    ap.add_argument("--scan-b", default="0,1,2,3,4")
    ap.add_argument("--ratio-threshold", type=float, default=0.05)
    ap.add_argument("--min-knots", type=int, default=3)
    ap.add_argument("--aggregate-timeout", type=int, default=1200)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    catalog = parse_ideal(Path(args.ideal))
    alias_path = Path(args.alias_json)
    if not alias_path.exists():
        alias_path = Path(__file__).with_name(args.alias_json)
    aliases = json.loads(alias_path.read_text(encoding="utf-8")) if alias_path.exists() else {"knot_aliases": {}, "link_ids": {}}

    run_targets, links, missing, ordinary = select_targets(catalog, aliases, args.max_crossing, args.extras, args.knotplot_11, args.link_ids)

    write_csv(outdir / "target_catalog_run_available.csv", run_targets)
    write_csv(outdir / "target_catalog_links_available.csv", links)
    write_csv(outdir / "target_catalog_missing_or_skipped.csv", missing)
    (outdir / "targets_run_available.json").write_text(json.dumps([r["id"] for r in run_targets], indent=2), encoding="utf-8")
    (outdir / "targets_links_available.json").write_text(json.dumps([r["id"] for r in links], indent=2), encoding="utf-8")

    manifest = []
    aggregate_status = "NOT_RUN"
    if args.run and not args.dry_run_plan:
        runs_dir = outdir / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        for target in run_targets:
            result = run_target(args, target, runs_dir / safe_name(target["name"]))
            manifest.append(result)
            write_csv(outdir / "run_manifest.csv", manifest)
        ok_dirs = [Path(r["run_dir"]) for r in manifest if str(r.get("returncode")) == "0"]
        if ok_dirs:
            rc = run_aggregate(args, ok_dirs, outdir / "aggregate")
            aggregate_status = "PASS" if rc == 0 else f"FAIL_RETURN_{rc}"
        else:
            aggregate_status = "FAIL_NO_SUCCESSFUL_RUNS"
    else:
        for target in run_targets:
            manifest.append({"target": target["name"], "target_id": target["id"], "L_cert": target.get("L_cert"), "mode": "dry_run_plan", "status": "PLANNED"})
        write_csv(outdir / "run_manifest.csv", manifest)

    write_report(outdir, run_targets, links, missing, manifest, aggregate_status)
    (outdir / "run_config_knotplot_scan.json").write_text(json.dumps({"args": vars(args)}, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 78)
    print("BEMv18 KnotPlot-aware extended scan setup complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    print(f"run targets: {len(run_targets)}")
    print(f"catalogued links: {len(links)}")
    print(f"missing/skipped: {len(missing)}")
    for r in missing:
        print(f"{r['status']}: {r['requested']} -> {r['resolved_id']}")
    print(f"aggregate_status: {aggregate_status}")
    print("wrote: target_catalog_run_available.csv, target_catalog_links_available.csv, target_catalog_missing_or_skipped.csv")


if __name__ == "__main__":
    main()
