#!/usr/bin/env python3
r"""
routeB_RT_bem_v18_multiknot_exponent_test.py
============================================

BEMv18 Route-B audit: multi-knot certified-length exponent test.

BEMv17 localized the open analytic burden to the first surviving residual
symbol q_{-2}.  If q_{-2} is the first surviving pair-subtracted residual, the
finite correction should use

    DeltaF_phys = DeltaF_pair / (M_max L_cert^2).

BEMv18 tests the length exponent empirically across multiple knots with
different certified lengths L_cert.  It is alpha-blind: no observed fine
structure is used or compared.

Core diagnostic
---------------
For a monomial normalizer

    N_{a,b} = M_max^a L_cert^b,

compute

    R_{a,b}(K) = |DeltaF_pair(K/0_1)| / (M_max(K)^a L_cert(K)^b).

Across a multi-knot family, the right exponent b should reduce systematic
correlation of R_{a,b} with L_cert while keeping the correction subleading.

This does not prove b=2 by itself because knot-shape effects can contribute.
It is a falsifier / identifiability test.

Modes
-----
1. Reuse existing BEMv13 output folders:
   --from-bemv13-outdirs out_3_1,out_4_1,...

2. Run BEMv13 internally for each target:
   --run-bemv13 --targets 3:1:1,4:1:1,5:1:1

3. Dry-run plan only:
   --dry-run-plan

Outputs
-------
  bemv18_target_catalog.csv
  bemv18_run_manifest.csv
  bemv18_raw_multiknot_budget.csv
  bemv18_length_exponent_scan.csv
  bemv18_exponent_certificate.csv
  bemv18_multiknot_appendix.tex
  bemv18_multiknot_report.md
  run_config_v18.json

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
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


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


def as_float(x: Any, default: float = float("nan")) -> float:
    try:
        return float(x)
    except Exception:
        return default


def parse_csv_list(s: str) -> List[str]:
    return [x.strip() for x in str(s).split(",") if x.strip()]


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


def parse_attrs_from_tag(tag: str) -> Dict[str, str]:
    return {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"', tag)}


def ideal_id_to_name(bid: str) -> str:
    parts = str(bid).split(":")
    if len(parts) >= 3:
        return f"{parts[0]}_{parts[2]}"
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return str(bid).replace(":", "_")


def name_to_default_id(name: str) -> str:
    # 5_2 -> 5:1:2
    m = re.match(r"^(\d+)_(\d+)$", name)
    if m:
        return f"{m.group(1)}:1:{m.group(2)}"
    return name


def parse_ideal_catalog(path: Path) -> Dict[str, Dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    out: Dict[str, Dict[str, Any]] = {}
    for m in re.finditer(r"<AB\b([^>]*)>", text, flags=re.I):
        attrs = parse_attrs_from_tag(m.group(1))
        bid = attrs.get("Id")
        if not bid:
            continue
        name = ideal_id_to_name(bid)
        rec = {
            "id": bid,
            "name": name,
            "conway": attrs.get("Conway", ""),
            "L_cert": as_float(attrs.get("L")),
            "D_database": as_float(attrs.get("D")),
            "n_components": int(attrs.get("n", "1").strip() or "1"),
        }
        out[bid] = rec
        out[name] = rec
    # generated reference control
    if "0_1" not in out:
        rec = {
            "id": "0:1:1",
            "name": "0_1",
            "conway": "0",
            "L_cert": 2.0 * math.pi,
            "D_database": 1.0,
            "n_components": 1,
        }
        out["0_1"] = rec
        out["0:1:1"] = rec
    return out


def resolve_targets(args, catalog: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    if args.targets_json:
        raw = json.loads(Path(args.targets_json).read_text(encoding="utf-8"))
        tokens = raw if isinstance(raw, list) else raw.get("targets", [])
    else:
        tokens = parse_csv_list(args.targets)

    out: List[Dict[str, Any]] = []
    seen = set()
    for tok in tokens:
        key = str(tok)
        rec = catalog.get(key) or catalog.get(name_to_default_id(key))
        if rec is None:
            raise ValueError(f"target {key!r} not found in ideal catalog")
        if rec["name"] == "0_1":
            continue
        if rec["name"] not in seen:
            seen.add(rec["name"])
            out.append(rec)
    return out


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


def run_bemv13_for_target(args, target: Dict[str, Any], run_dir: Path) -> Dict[str, Any]:
    v13_script = resolve_script(args.v13_script, "routeB_RT_bem_v13_certified_length_budget.py", "/mnt/data/routeB_RT_bem_v13_certified_length_budget.py")
    v8_script = resolve_script(args.v8_script, "routeB_RT_bem_v8_pair_length_budget.py", "/mnt/data/routeB_RT_bem_v8_pair_length_budget.py")

    ids = f"0:1:1,{target['id']}"
    cmd = [
        sys.executable, str(v13_script),
        "--ideal", str(args.ideal),
        "--v8-script", str(v8_script),
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
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "bemv13_stdout.txt").write_text(proc.stdout, encoding="utf-8", errors="replace")
    (run_dir / "bemv13_stderr.txt").write_text(proc.stderr, encoding="utf-8", errors="replace")
    return {
        "target": target["name"],
        "target_id": target["id"],
        "run_dir": str(run_dir),
        "returncode": proc.returncode,
        "command": " ".join(cmd),
    }


def collect_budget_from_v13(run_dir: Path, target_rec: Optional[Dict[str, Any]] = None, preferred: str = "M_Lcert2") -> Optional[Dict[str, Any]]:
    rows = read_csv(run_dir / "alpha_component_budget_v13.csv")
    if not rows:
        return None

    row = None
    for r in rows:
        if r.get("normalizer") == preferred:
            row = r
            break
    if row is None:
        row = rows[0]

    L = as_float(row.get("L_cert_target"))
    den = as_float(row.get("normalizer_denominator"))
    M = den/(L*L) if math.isfinite(den) and math.isfinite(L) and L != 0 and row.get("normalizer") in {"M_Lcert2", preferred} else float("nan")
    if not math.isfinite(M):
        # Try certified_length_audit fallback.
        cert = read_csv(run_dir / "certified_length_audit.csv")
        if cert:
            L = as_float(cert[0].get("L_cert_target_database"), L)
        # M cannot be inferred robustly without M_Lcert2 denominator.
    return {
        "target": row.get("target", target_rec.get("name") if target_rec else ""),
        "reference": row.get("reference", "0_1"),
        "L_cert": L,
        "Mmax": M,
        "DeltaF_pair_raw": as_float(row.get("DeltaF_pair_raw")),
        "leading_half_alpha_inv_cert": as_float(row.get("leading_half_alpha_inv_cert")),
        "NsoftV": as_float(row.get("NsoftV")),
        "normalizer_used_source": row.get("normalizer"),
        "alpha_inv_pred_blind_v13_source": as_float(row.get("alpha_inv_pred_blind_v13")),
        "source_run_dir": str(run_dir),
        "gate_source": row.get("gate", ""),
    }


def collect_from_existing_dirs(dirs_csv: str, preferred: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    dirs = [Path(x) for x in parse_csv_list(dirs_csv)]
    manifest = []
    budgets = []
    for d in dirs:
        b = collect_budget_from_v13(d, None, preferred)
        manifest.append({
            "target": b.get("target") if b else "",
            "run_dir": str(d),
            "returncode": 0 if b else 1,
            "mode": "reuse_bemv13",
        })
        if b:
            budgets.append(b)
    return manifest, budgets


def exponent_scan(budgets: List[Dict[str, Any]], a_values: List[float], b_values: List[float], ratio_threshold: float, min_knots: int) -> List[Dict[str, Any]]:
    pts = []
    for r in budgets:
        L = as_float(r.get("L_cert"))
        M = as_float(r.get("Mmax"))
        dF = as_float(r.get("DeltaF_pair_raw"))
        NsoftV = as_float(r.get("NsoftV"))
        if all(math.isfinite(x) for x in [L, M, dF, NsoftV]) and L > 0 and M > 0 and NsoftV > 0:
            pts.append((r.get("target", ""), L, M, abs(dF), NsoftV))
    rows = []
    for a in a_values:
        for b in b_values:
            if len(pts) < min_knots:
                rows.append({
                    "a_M_exponent": a,
                    "b_L_exponent": b,
                    "n_knots": len(pts),
                    "normalizer_formula": f"M^{a:g} L^{b:g}",
                    "slope_logR_vs_logL": "",
                    "corr_logR_logL": "",
                    "std_logR": "",
                    "max_subleading_ratio": "",
                    "score": "",
                    "gate": "FAIL_NOT_ENOUGH_KNOTS",
                    "note": "CANONICAL_CANDIDATE_M_LCERT2" if abs(a-1)<1e-12 and abs(b-2)<1e-12 else "",
                })
                continue

            xs, ys, ratios = [], [], []
            for _, L, M, dF, NsoftV in pts:
                R = dF / ((M**a) * (L**b))
                xs.append(math.log(L))
                ys.append(math.log(abs(R) + 1e-300))
                ratios.append(abs(R)/(NsoftV * L))
            x = np.asarray(xs, dtype=float)
            y = np.asarray(ys, dtype=float)
            A = np.column_stack([np.ones_like(x), x])
            beta, *_ = np.linalg.lstsq(A, y, rcond=None)
            intercept, slope = float(beta[0]), float(beta[1])
            resid = y - (A @ beta)
            corr = float(np.corrcoef(x, y)[0,1]) if len(x) > 1 and np.std(x) > 0 and np.std(y) > 0 else 0.0
            std_logR = float(np.std(y, ddof=1)) if len(y) > 1 else 0.0
            resid_std = float(np.std(resid, ddof=1)) if len(resid) > 1 else 0.0
            max_ratio = float(np.max(ratios)) if ratios else float("nan")
            score = abs(slope) + 0.25*resid_std + (10.0 if max_ratio > ratio_threshold else 0.0)
            gate = "PASS_MULTIKNOT_EXPONENT_DIAGNOSTIC" if max_ratio <= ratio_threshold else "FAIL_NOT_SUBLEADING"
            rows.append({
                "a_M_exponent": a,
                "b_L_exponent": b,
                "n_knots": len(pts),
                "normalizer_formula": f"M^{a:g} L^{b:g}",
                "slope_logR_vs_logL": slope,
                "corr_logR_logL": corr,
                "std_logR": std_logR,
                "residual_std_after_length_fit": resid_std,
                "max_subleading_ratio": max_ratio,
                "score": score,
                "gate": gate,
                "note": "CANONICAL_CANDIDATE_M_LCERT2" if abs(a-1)<1e-12 and abs(b-2)<1e-12 else "",
            })
    return rows


def choose_certificate(scan_rows: List[Dict[str, Any]], canonical_a: float = 1.0, canonical_b: float = 2.0) -> Dict[str, Any]:
    usable = [r for r in scan_rows if r.get("gate") != "FAIL_NOT_ENOUGH_KNOTS" and r.get("score") not in ("", None)]
    if not usable:
        canon = next((r for r in scan_rows if r.get("note") == "CANONICAL_CANDIDATE_M_LCERT2"), {})
        return {
            "selected_exponent_a": "",
            "selected_exponent_b": "",
            "selected_formula": "",
            "canonical_formula": "M^1 L^2",
            "canonical_gate": canon.get("gate", "FAIL_NOT_ENOUGH_KNOTS"),
            "certificate_status": "FAIL_NOT_ENOUGH_KNOTS",
            "interpretation": "Need at least three knots with valid BEMv13 budgets.",
        }
    best = sorted(usable, key=lambda r: as_float(r.get("score"), 1e99))[0]
    canon = next((r for r in usable if abs(as_float(r.get("a_M_exponent"))-canonical_a)<1e-12 and abs(as_float(r.get("b_L_exponent"))-canonical_b)<1e-12), None)
    canonical_selected = canon is not None and best is canon
    if canon is None:
        status = "FAIL_CANONICAL_NOT_EVALUATED"
    elif canonical_selected and canon.get("gate") == "PASS_MULTIKNOT_EXPONENT_DIAGNOSTIC":
        status = "PASS_CANONICAL_B2_SELECTED"
    elif canon.get("gate") == "PASS_MULTIKNOT_EXPONENT_DIAGNOSTIC":
        status = "PASS_CANONICAL_SUBLEADING_BUT_NOT_BEST_SCORE"
    else:
        status = "FAIL_CANONICAL_B2_NOT_SUBLEADING"
    return {
        "selected_exponent_a": best.get("a_M_exponent"),
        "selected_exponent_b": best.get("b_L_exponent"),
        "selected_formula": best.get("normalizer_formula"),
        "selected_score": best.get("score"),
        "canonical_formula": "M^1 L^2",
        "canonical_score": canon.get("score") if canon else "",
        "canonical_slope_logR_vs_logL": canon.get("slope_logR_vs_logL") if canon else "",
        "canonical_corr_logR_logL": canon.get("corr_logR_logL") if canon else "",
        "canonical_max_subleading_ratio": canon.get("max_subleading_ratio") if canon else "",
        "canonical_gate": canon.get("gate") if canon else "",
        "certificate_status": status,
        "interpretation": "Multi-knot exponent diagnostic is a falsifier; shape factors remain a confounder.",
    }


def write_appendix(path: Path, cert: Dict[str, Any]) -> None:
    tex = r"""
% BEMv18 appendix snippet
% Multi-knot certified-length exponent test.
% Alpha-blind: no observed fine-structure value is used.

\subsection{Multi-knot test for the certified-length exponent}

\paragraph{Status.}
This subsection describes a falsifier for the BEMv17 symbol claim that the
first surviving R--T residual is \(q_{-2}\).  If the residual has scale weight
\(L^{-2}\), then the finite correction should be normalized by
\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
\]

For each knot \(K_i\), define the raw pair correction
\[
\Delta F_i=\Delta F_{\rm pair}(K_i/0_1),
\]
the retained mode count \(M_i\), and the certified length \(L_i=L_{\rm cert}(K_i)\).
For a general monomial normalizer
\[
\mathcal N_{a,b}=M_i^a L_i^b,
\]
define
\[
R_{a,b}(K_i)=
\frac{|\Delta F_i|}
{M_i^aL_i^b}.
\]
The BEMv17 target is
\[
a=1,\qquad b=2.
\]

\paragraph{Diagnostic.}
The exponent \(b\) is tested by scanning \(R_{a,b}\) across multiple knots and
checking whether systematic correlation with \(L_i\) is reduced while the
finite correction remains subleading:
\[
\frac{R_{a,b}(K_i)}
{N_{\rm soft}V_{\rm soft}L_i}
\ll 1.
\]
This is not a proof, because knot-shape factors may also enter.  It is a
necessary falsifiability test: if \(b=2\) fails across several certified
lengths, the \(q_{-2}\) interpretation is weakened.

\paragraph{BEMv18 result.}
The selected exponent candidate is
\[
a=__A__,\qquad b=__B__,
\]
with formula
\[
__FORMULA__.
\]
The canonical \(q_{-2}\) candidate \(M_{\max}L_{\rm cert}^{2}\) has status
\[
\boxed{\text{__STATUS__}}.
\]
""".strip()
    tex = (tex
           .replace("__A__", str(cert.get("selected_exponent_a","")))
           .replace("__B__", str(cert.get("selected_exponent_b","")))
           .replace("__FORMULA__", str(cert.get("selected_formula","")))
           .replace("__STATUS__", str(cert.get("certificate_status",""))))
    path.write_text(tex + "\n", encoding="utf-8")


def write_report(path: Path, targets: List[Dict[str, Any]], budgets: List[Dict[str, Any]], cert: Dict[str, Any]) -> None:
    lines = [
        "# BEMv18 multi-knot exponent test",
        "",
        "This report is alpha-blind. It does not contain or compare against observed fine structure.",
        "",
        "## Goal",
        "",
        "Test whether the BEMv17 target exponent",
        "",
        r"\[",
        r"b=2",
        r"\]",
        "",
        "is empirically consistent across several knots with different certified lengths.",
        "",
        "The canonical normalizer is",
        "",
        r"\[",
        r"\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.",
        r"\]",
        "",
        "## Targets",
        "",
    ]
    for t in targets:
        lines.append(f"- `{t.get('name')}` / `{t.get('id')}`: `L_cert={t.get('L_cert')}`")
    lines += [
        "",
        "## Valid budgets collected",
        "",
        f"- `{len(budgets)}` valid BEMv13 budgets",
        "",
        "## Certificate",
        "",
    ]
    for k, v in cert.items():
        lines.append(f"- `{k}`: `{v}`")
    lines += [
        "",
        "## Interpretation",
        "",
        "If the status is `FAIL_NOT_ENOUGH_KNOTS`, run BEMv18 with at least three target knots. If the canonical candidate passes but is not best-score, this supports subleading behavior but does not uniquely identify b=2. If it is selected, that is strong empirical support for the q_{-2} route.",
        "",
        "## Next gate",
        "",
        r"\[",
        r"\boxed{\text{BEMv19: multi-knot production grid or explicit }q_{-2}\text{ symbolic derivation.}}",
        r"\]",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v18_multiknot")
    ap.add_argument("--targets", default="3:1:1,4:1:1,5:1:1,5:1:2,6:1:1")
    ap.add_argument("--targets-json", default="")
    ap.add_argument("--from-bemv13-outdirs", default="")
    ap.add_argument("--run-bemv13", action="store_true")
    ap.add_argument("--dry-run-plan", action="store_true")
    ap.add_argument("--v13-script", default="")
    ap.add_argument("--v8-script", default="")

    # BEMv13 lightweight pass-through defaults.
    ap.add_argument("--n-center", type=int, default=8)
    ap.add_argument("--n-theta", type=int, default=3)
    ap.add_argument("--n-sphere", type=int, default=14)
    ap.add_argument("--tube-fraction", type=float, default=0.34)
    ap.add_argument("--outer-factor", type=float, default=2.4)
    ap.add_argument("--pair-fit-min-M", type=int, default=4)
    ap.add_argument("--pair-fit-tail-frac", type=float, default=0.75)
    ap.add_argument("--length-samples", type=int, default=4000)
    ap.add_argument("--normalizers", default="raw,Mmax,Lcert,Lcert2,Lcert3,M_Lcert,M_Lcert2")
    ap.add_argument("--preferred-normalizer", default="M_Lcert2")
    ap.add_argument("--subrun-timeout", type=int, default=300)
    ap.add_argument("--target-run-timeout", type=int, default=600)

    # Exponent scan.
    ap.add_argument("--scan-a", default="1")
    ap.add_argument("--scan-b", default="0,1,2,3,4")
    ap.add_argument("--ratio-threshold", type=float, default=0.05)
    ap.add_argument("--min-knots", type=int, default=3)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    catalog = parse_ideal_catalog(Path(args.ideal))
    targets = resolve_targets(args, catalog)
    write_csv(outdir / "bemv18_target_catalog.csv", targets)

    manifest: List[Dict[str, Any]] = []
    budgets: List[Dict[str, Any]] = []

    if args.from_bemv13_outdirs:
        manifest, budgets = collect_from_existing_dirs(args.from_bemv13_outdirs, args.preferred_normalizer)

    if args.run_bemv13 and not args.dry_run_plan:
        runs_dir = outdir / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        for t in targets:
            rd = runs_dir / t["name"]
            m = run_bemv13_for_target(args, t, rd)
            manifest.append({**m, "mode": "run_bemv13"})
            if m["returncode"] == 0:
                b = collect_budget_from_v13(rd, t, args.preferred_normalizer)
                if b:
                    budgets.append(b)

    if args.dry_run_plan:
        for t in targets:
            manifest.append({
                "target": t["name"],
                "target_id": t["id"],
                "L_cert": t["L_cert"],
                "mode": "dry_run_plan",
                "command_hint": f"run BEMv13 for {t['name']} then rerun BEMv18 with --from-bemv13-outdirs",
                "returncode": "",
            })

    write_csv(outdir / "bemv18_run_manifest.csv", manifest)
    write_csv(outdir / "bemv18_raw_multiknot_budget.csv", budgets)

    a_values = [float(x.strip()) for x in args.scan_a.split(",") if x.strip()]
    b_values = [float(x.strip()) for x in args.scan_b.split(",") if x.strip()]
    scan = exponent_scan(budgets, a_values, b_values, args.ratio_threshold, args.min_knots)
    write_csv(outdir / "bemv18_length_exponent_scan.csv", scan)

    cert = choose_certificate(scan)
    cert.update({
        "n_targets_requested": len(targets),
        "n_valid_budgets": len(budgets),
        "uses_observed_alpha": "no",
        "next_gate": "BEMv19_MULTI_KNOT_PRODUCTION_OR_Q_MINUS_2_SYMBOL_DERIVATION",
    })
    write_csv(outdir / "bemv18_exponent_certificate.csv", [cert])
    write_appendix(outdir / "bemv18_multiknot_appendix.tex", cert)
    write_report(outdir / "bemv18_multiknot_report.md", targets, budgets, cert)

    (outdir / "run_config_v18.json").write_text(json.dumps({"args": vars(args)}, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 78)
    print("Route B BEMv18 multi-knot exponent test complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    print(f"targets requested: {len(targets)}")
    print(f"valid budgets: {len(budgets)}")
    print(f"certificate: {cert.get('certificate_status')}")
    print(f"selected formula: {cert.get('selected_formula')}")
    print("wrote: bemv18_target_catalog.csv, bemv18_run_manifest.csv,")
    print("       bemv18_raw_multiknot_budget.csv, bemv18_length_exponent_scan.csv,")
    print("       bemv18_exponent_certificate.csv, bemv18_multiknot_appendix.tex,")
    print("       bemv18_multiknot_report.md")


if __name__ == "__main__":
    main()
