#!/usr/bin/env python3
"""
Classify a KnotPlot/ridgerunner outdir into catalog status levels:

  relaxed-seed | near-ideal-candidate | near-ideal | certified-ideal

Writes outdir/catalog_status.json. Never auto-assigns certified-ideal.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


REF_PATH = Path(__file__).resolve().parent / "reference_ropelengths.json"

# Candidate gate (default -rr polish)
CAND_RESIDUAL = 0.01
# Strict near-ideal
STRICT_RESIDUAL = 0.005
STRICT_EPS_R = 0.0005  # 0.05%
STRICT_MULTISTART = 0.0002  # 0.02%
STRICT_RES_CONV = 0.0002  # 0.02% Δ_600→1200
STRICT_THICKNESS = 0.0001  # 0.01% from 0.5
UNIFORM_EDGE_RATIO = 1.02
UNIFORM_EDGE_CV = 0.005  # 0.5%
TARGET_THICKNESS = 0.5


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_references() -> dict[str, Any]:
    if not REF_PATH.is_file():
        return {}
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


def resolve_reference(
    folder_name: str, polish_ropes: list[float], refs: dict[str, Any]
) -> tuple[float | None, str]:
    """Return (R_ref, source_label)."""
    keys = [folder_name]
    # knot_3.1 → 3_1, torus_2.3 → 2_3, etc.
    for prefix in ("knot_", "torus_", "link_"):
        if folder_name.startswith(prefix):
            keys.append(folder_name[len(prefix) :].replace(".", "_"))
            keys.append(folder_name[len(prefix) :])
            break
    for key in keys:
        if key in refs and "ropelength" in refs[key]:
            return float(refs[key]["ropelength"]), str(
                refs[key].get("source", key)
            )
        for _k, v in refs.items():
            aliases = v.get("aliases") or []
            if key in aliases and "ropelength" in v:
                return float(v["ropelength"]), str(v.get("source", _k))
    if polish_ropes:
        return min(polish_ropes), "best-known numerical"
    return None, "none"


def find_polish_metrics(outdir: Path) -> list[tuple[Path, dict[str, Any]]]:
    """N=300 polish metrics only (exclude N600/N1200 ladder labels)."""
    hits: list[tuple[Path, dict[str, Any]]] = []
    for p in sorted(outdir.glob("*_polish.metrics.json")):
        name = p.name.lower()
        if "n600" in name or "n1200" in name or "uniform" in name:
            continue
        data = load_json(p)
        if data:
            hits.append((p, data))
    return hits


def pick_primary_polish(
    outdir: Path, polishes: list[tuple[Path, dict[str, Any]]]
) -> tuple[Path, dict[str, Any]] | None:
    if not polishes:
        return None
    sel = load_json(outdir / "seed_selection.json") or {}
    selected = sel.get("selected")
    if selected:
        stem = Path(selected).stem
        for path, data in polishes:
            if stem in path.name or path.name.startswith(stem):
                return path, data
        # polish stem is seed_stem_rr_..._polish
        for path, data in polishes:
            if stem in path.stem:
                return path, data
    # Prefer lowest residual
    return min(
        polishes,
        key=lambda t: (
            t[1].get("residual")
            if t[1].get("residual") is not None
            else float("inf")
        ),
    )


def find_ladder_metrics(outdir: Path, tag: str) -> dict[str, Any] | None:
    """tag = N600_polish or N1200_polish."""
    for p in outdir.glob(f"*_{tag}.metrics.json"):
        return load_json(p)
    for p in outdir.glob(f"*{tag}*.metrics.json"):
        if "uniform" in p.name.lower():
            continue
        return load_json(p)
    return None


def find_uniform_resample(outdir: Path, polish_stem: str | None) -> dict[str, Any] | None:
    cands = list(outdir.glob("*_polish_uniform_N300.resample.json"))
    if not cands:
        cands = list(outdir.glob("*_uniform_N300.resample.json"))
    if polish_stem:
        for c in cands:
            if polish_stem.replace("_polish", "") in c.stem or polish_stem in c.stem:
                return load_json(c)
    return load_json(cands[0]) if cands else None


def check_pass_fail(ok: bool | None) -> str:
    if ok is None:
        return "not-tested"
    return "pass" if ok else "fail"


def classify(outdir: Path) -> dict[str, Any]:
    outdir = outdir.resolve()
    refs = load_references()
    seed = load_json(outdir / "seed_selection.json") or {}
    topo = seed.get("topology_status", "")
    topo_ok = topo == "topology-verified" or "verified" in str(topo).lower()

    polishes = find_polish_metrics(outdir)
    primary = pick_primary_polish(outdir, polishes)

    reasons: list[str] = []
    checks: dict[str, str] = {}

    if primary is None:
        status = "relaxed-seed"
        reasons.append("no ridgerunner polish metrics found")
        checks["topology"] = check_pass_fail(topo_ok if seed else None)
        return {
            "status": status,
            "ideal": False,
            "strict_near_ideal": False,
            "folder": outdir.name,
            "reference": None,
            "epsilon_R": None,
            "primary_polish": None,
            "checks": checks,
            "reason": reasons,
        }

    ppath, pm = primary
    residual = pm.get("residual")
    ropelength = pm.get("ropelength")
    thickness = pm.get("thickness")
    edge_ratio = pm.get("edge_length_ratio")
    edge_cv = pm.get("edge_length_cv")

    ropes = [
        float(d["ropelength"])
        for _, d in polishes
        if d.get("ropelength") is not None
    ]
    r_ref, r_src = resolve_reference(outdir.name, ropes, refs)
    eps_r = None
    if r_ref and ropelength is not None and r_ref > 0:
        eps_r = (float(ropelength) - r_ref) / r_ref

    # Topology
    checks["topology"] = check_pass_fail(topo_ok)
    if topo_ok:
        reasons.append("topology verified")
    else:
        reasons.append("topology not verified")

    # Candidate residual
    cand_res_ok = residual is not None and float(residual) <= CAND_RESIDUAL
    checks["residual_candidate"] = check_pass_fail(cand_res_ok)
    if cand_res_ok:
        reasons.append(f"residual ≤ {CAND_RESIDUAL}")
    else:
        reasons.append(f"residual above {CAND_RESIDUAL}")

    # Strict residual
    strict_res_ok = residual is not None and float(residual) <= STRICT_RESIDUAL
    checks["residual_strict"] = check_pass_fail(strict_res_ok)
    if not strict_res_ok:
        reasons.append(f"residual above {STRICT_RESIDUAL}")

    # epsilon_R
    eps_ok = eps_r is not None and eps_r <= STRICT_EPS_R
    checks["ropelength_excess"] = check_pass_fail(
        eps_ok if eps_r is not None else None
    )
    if eps_ok:
        reasons.append("ropelength threshold passed")
    elif eps_r is not None:
        reasons.append(f"ropelength excess {eps_r:.6%} above {STRICT_EPS_R:.2%}")

    # Raw RR edges → warn only
    if edge_ratio is not None and float(edge_ratio) > 1.10:
        checks["raw_edge_ratio"] = "warn"
        reasons.append(f"raw edge-ratio {edge_ratio:.4g} (warn only)")
    else:
        checks["raw_edge_ratio"] = "pass" if edge_ratio is not None else "not-tested"
    if edge_cv is not None and float(edge_cv) > 0.01:
        checks["raw_edge_cv"] = "warn"
        reasons.append(f"raw edge-CV {float(edge_cv):.4%} (warn only)")
    else:
        checks["raw_edge_cv"] = "pass" if edge_cv is not None else "not-tested"

    # Thickness
    thick_ok = None
    if thickness is not None:
        thick_ok = abs(float(thickness) - TARGET_THICKNESS) / TARGET_THICKNESS <= STRICT_THICKNESS
    checks["thickness"] = check_pass_fail(thick_ok)

    # Multi-start spread among polish ropelengths
    ms_ok = None
    if len(ropes) >= 2:
        rmin, rmax = min(ropes), max(ropes)
        spread = (rmax - rmin) / rmin if rmin > 0 else None
        ms_ok = spread is not None and spread <= STRICT_MULTISTART
        checks["multistart_spread"] = check_pass_fail(ms_ok)
        if ms_ok:
            reasons.append("multi-start ropelength spread OK")
        else:
            reasons.append("multi-start spread above 0.02%")
    else:
        checks["multistart_spread"] = "not-tested"
        reasons.append("multi-start not tested")

    # Resolution convergence N600 / N1200
    m600 = find_ladder_metrics(outdir, "N600_polish")
    m1200 = find_ladder_metrics(outdir, "N1200_polish")
    res_conv_ok = None
    if m600 and m1200:
        r600 = m600.get("ropelength")
        r1200 = m1200.get("ropelength")
        res600 = m600.get("residual")
        res1200 = m1200.get("residual")
        res_ok = (
            res600 is not None
            and res1200 is not None
            and float(res600) <= STRICT_RESIDUAL
            and float(res1200) <= STRICT_RESIDUAL
        )
        if r600 and r1200 and float(r1200) > 0:
            delta = abs(float(r1200) - float(r600)) / float(r1200)
            res_conv_ok = res_ok and delta <= STRICT_RES_CONV
        else:
            res_conv_ok = False
        checks["resolution_convergence"] = check_pass_fail(res_conv_ok)
        if res_conv_ok:
            reasons.append("resolution convergence 600→1200 OK")
        else:
            reasons.append("resolution convergence failed")
    else:
        checks["resolution_convergence"] = "not-tested"
        reasons.append("resolution convergence not yet demonstrated")

    # Uniform VortexLab mesh
    u = find_uniform_resample(outdir, ppath.stem)
    uni_ok = None
    if u:
        comps = u.get("components") or []
        if comps:
            er = comps[0].get("edge_ratio")
            cv = comps[0].get("edge_cv")
            # also top-level relative length
            uni_ok = True
            if er is not None and float(er) > UNIFORM_EDGE_RATIO:
                uni_ok = False
            if cv is not None and float(cv) > UNIFORM_EDGE_CV:
                uni_ok = False
            for c in comps[1:]:
                if c.get("edge_ratio") is not None and float(c["edge_ratio"]) > UNIFORM_EDGE_RATIO:
                    uni_ok = False
                if c.get("edge_cv") is not None and float(c["edge_cv"]) > UNIFORM_EDGE_CV:
                    uni_ok = False
        checks["uniform_mesh"] = check_pass_fail(uni_ok)
        if uni_ok:
            reasons.append("VortexLab uniform mesh OK")
        elif uni_ok is False:
            reasons.append("VortexLab uniform mesh gate failed")
    else:
        checks["uniform_mesh"] = "not-tested"

    # Constraint anomalies: residual missing / NaN
    anomaly = residual is None or (
        isinstance(residual, float) and not math.isfinite(residual)
    )
    checks["constraint_anomalies"] = "fail" if anomaly else "pass"

    # Decide status
    candidate_ok = (
        topo_ok
        and cand_res_ok
        and checks["constraint_anomalies"] == "pass"
    )
    strict_ok = (
        candidate_ok
        and strict_res_ok
        and eps_ok
        and ms_ok is True
        and res_conv_ok is True
        and thick_ok is True
        and uni_ok is True
    )

    if strict_ok:
        status = "near-ideal"
    elif candidate_ok:
        status = "near-ideal-candidate"
    else:
        status = "relaxed-seed"

    return {
        "status": status,
        "ideal": False,
        "strict_near_ideal": bool(strict_ok),
        "folder": outdir.name,
        "reference": (
            {"ropelength": r_ref, "source": r_src} if r_ref is not None else None
        ),
        "epsilon_R": eps_r,
        "primary_polish": str(ppath),
        "primary_metrics": {
            "residual": residual,
            "ropelength": ropelength,
            "thickness": thickness,
            "edge_length_ratio": edge_ratio,
            "edge_length_cv": edge_cv,
        },
        "checks": checks,
        "reason": reasons,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("outdir", type=Path, help="knots/<id> folder")
    ap.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="default: outdir/catalog_status.json",
    )
    args = ap.parse_args()
    outdir = args.outdir.resolve()
    if not outdir.is_dir():
        print(f"ERROR: not a directory: {outdir}", file=sys.stderr)
        return 1
    result = classify(outdir)
    out = args.json_out or (outdir / "catalog_status.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"status: {result['status']}")
    print(f"strict_near_ideal: {result['strict_near_ideal']}")
    print(f"epsilon_R: {result.get('epsilon_R')}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
