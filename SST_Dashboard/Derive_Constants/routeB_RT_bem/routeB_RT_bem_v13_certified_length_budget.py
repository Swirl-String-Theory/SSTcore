#!/usr/bin/env python3
r"""
routeB_RT_bem_v13_certified_length_budget.py
============================================

BEMv13 Route-B audit: certified-length branch.

BEMv12 showed that the printed Fourier coefficients can give a stable
arclength that is slightly different from the database L column.  BEMv13
therefore separates:

  geometry source:
      Fourier coefficients are used for BEM geometry / spectra.

  certified length source:
      the database L column is used for the leading longitudinal scale.

No observed alpha is used.

Budget
------
For target K=3_1 and reference 0_1:

  alpha_inv_pred_blind_v13(q)
    = 1/2 [ N_soft V_soft L_cert(K)
            + DeltaF_pair(K/ref) / N_q(L_cert, M_max, ...) ].

Default certified normalizer:

  N_q = M_max * L_cert^2     (M_Lcert2)

Outputs
-------
  certified_length_audit.csv
  certified_normalizer_candidates.csv
  alpha_component_budget_v13.csv
  certified_length_report.md
  run_config_v13.json

BEMv13 can reuse an existing BEMv8 output folder via --from-bemv8-outdir,
or launch BEMv8 internally.

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


# ---------------------------------------------------------------------------
# CSV/helpers
# ---------------------------------------------------------------------------

def read_csv_rows(path: Path) -> List[Dict[str, str]]:
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


def parse_id_csv(s: str) -> List[str]:
    return [x.strip() for x in str(s).split(",") if x.strip()]


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


# ---------------------------------------------------------------------------
# ideal.txt parser, database L provenance
# ---------------------------------------------------------------------------

def parse_attrs_from_tag(tag: str) -> Dict[str, str]:
    return {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"', tag)}


def ideal_id_to_name(bid: str) -> str:
    parts = str(bid).split(":")
    if len(parts) >= 3:
        return f"{parts[0]}_{parts[2]}"
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return str(bid).replace(":", "_")


def parse_ideal_database_lengths(path: Path) -> Dict[str, Dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    out: Dict[str, Dict[str, Any]] = {}
    for m in re.finditer(r"<AB\b([^>]*)>", text, flags=re.I):
        attrs = parse_attrs_from_tag(m.group(1))
        bid = attrs.get("Id")
        if not bid:
            continue
        try:
            L = float(str(attrs.get("L", "")).strip())
        except Exception:
            L = None
        try:
            D = float(str(attrs.get("D", "")).strip())
        except Exception:
            D = None
        name = ideal_id_to_name(bid)
        rec = {
            "id": bid,
            "name": name,
            "conway": attrs.get("Conway", ""),
            "L_database": L,
            "D_database": D,
            "n_components": int(attrs.get("n", "1").strip() or "1"),
        }
        out[bid] = rec
        out[name] = rec
    # Always allow exact generated unknot certification.
    if "0_1" not in out:
        rec = {
            "id": "0:1:1",
            "name": "0_1",
            "conway": "0",
            "L_database": 2.0 * math.pi,
            "D_database": 1.0,
            "n_components": 1,
        }
        out["0_1"] = rec
        out["0:1:1"] = rec
    return out


def resolve_length_record(lengths: Dict[str, Dict[str, Any]], token: str) -> Dict[str, Any]:
    if token in lengths:
        return lengths[token]
    parts = str(token).split(":")
    if len(parts) >= 2:
        name = f"{parts[0]}_{parts[1]}"
        if name in lengths:
            return lengths[name]
    raise ValueError(f"could not resolve database length for {token!r}")


# ---------------------------------------------------------------------------
# Optional BEMv8 execution
# ---------------------------------------------------------------------------

def run_bemv8(v8_script: Path, args, outdir: Path) -> None:
    cmd = [
        sys.executable, str(v8_script),
        "--ideal", str(args.ideal),
        "--outdir", str(outdir),
        "--ideal-xml-knot-ids", args.ideal_xml_knot_ids,
        "--target", args.target,
        "--reference", args.reference,
        "--n-center", str(args.n_center),
        "--n-theta", str(args.n_theta),
        "--n-sphere", str(args.n_sphere),
        "--tube-fraction", str(args.tube_fraction),
        "--outer-factor", str(args.outer_factor),
        "--mu-mode", args.mu_mode,
        "--mu-value", str(args.mu_value),
        "--boundary-subspace", args.boundary_subspace,
        "--fit-min-M", str(args.fit_min_M),
        "--counterterm-fit-min-M", str(args.counterterm_fit_min_M),
        "--fit-tail-frac", str(args.fit_tail_frac),
        "--counterterm-tail-frac", str(args.counterterm_tail_frac),
        "--fit-models", args.fit_models,
        "--counterterm-models", args.counterterm_models,
        "--soft-index-count", str(args.soft_index_count),
        "--soft-volume-mode", args.soft_volume_mode,
        "--soft-volume-value", str(args.soft_volume_value),
        "--length-samples", str(args.length_samples),
        "--length-source", "geometric_raw",
        "--length-fit-model", args.length_fit_model,
        "--length-coeff", args.length_coeff,
        "--length-fit-min-M", str(args.length_fit_min_M),
        "--length-fit-tail-frac", str(args.length_fit_tail_frac),
        "--pair-fit-model", args.pair_fit_model,
        "--pair-fit-min-M", str(args.pair_fit_min_M),
        "--pair-fit-tail-frac", str(args.pair_fit_tail_frac),
    ]
    if args.no_auto_add_unknot:
        cmd.append("--no-auto-add-unknot")
    if args.keep_constant:
        cmd.append("--keep-constant")
    if args.max_raw_modes > 0:
        cmd += ["--max-raw-modes", str(args.max_raw_modes)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.subrun_timeout)
    (outdir / "bemv8_stdout.txt").write_text(proc.stdout, encoding="utf-8", errors="replace")
    (outdir / "bemv8_stderr.txt").write_text(proc.stderr, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"BEMv8 subrun failed, see {outdir}/bemv8_stderr.txt")


# ---------------------------------------------------------------------------
# Budget calculations
# ---------------------------------------------------------------------------

def soft_volume(args) -> float:
    if args.soft_volume_mode == "none":
        return 0.0
    if args.soft_volume_mode == "unit_ball":
        return 4.0 * math.pi / 3.0
    if args.soft_volume_mode == "sphere_surface":
        return 4.0 * math.pi
    if args.soft_volume_mode == "numeric":
        return float(args.soft_volume_value)
    raise ValueError(args.soft_volume_mode)


def get_target_pair_row(rows: List[Dict[str, str]], target: str, reference: str) -> Dict[str, str]:
    for r in rows:
        if r.get("knot") == target and r.get("reference", reference) == reference:
            return r
    for r in rows:
        if r.get("knot") == target:
            return r
    if len(rows) == 1:
        return rows[0]
    raise ValueError(f"no pair row for target={target} reference={reference}")


def get_v8_length_row(rows: List[Dict[str, str]], target: str) -> Optional[Dict[str, str]]:
    for r in rows:
        if r.get("knot") == target:
            return r
    return None


def denominator(name: str, ctx: Dict[str, float]) -> Tuple[float, str]:
    L = ctx["L_cert"]
    M = ctx["Mmax"]
    NsoftV = ctx["NsoftV"]
    full = NsoftV * L
    half = 0.5 * full
    sqrtM = math.sqrt(M) if M > 0 else float("nan")
    table = {
        "raw": (1.0, "no correction normalizer"),
        "Mmax": (M, "M_max"),
        "sqrtM": (sqrtM, "sqrt(M_max)"),
        "Lcert": (L, "certified length"),
        "Lcert2": (L*L, "certified length squared"),
        "Lcert3": (L*L*L, "certified length cubed"),
        "NsoftV": (NsoftV, "N_soft V_soft"),
        "NsoftV_Lcert": (NsoftV*L, "N_soft V_soft L_cert"),
        "leading_full_cert": (full, "full leading bracket term NsoftV L_cert"),
        "leading_half_cert": (half, "half leading term"),
        "M_Lcert": (M*L, "M_max L_cert"),
        "sqrtM_Lcert": (sqrtM*L, "sqrt(M_max) L_cert"),
        "M_Lcert2": (M*L*L, "M_max L_cert^2"),
    }
    if name not in table:
        raise ValueError(f"unknown normalizer {name!r}")
    return table[name]


def build_outputs(outdir: Path, bemv8_dir: Path, args) -> Dict[str, Any]:
    lengths = parse_ideal_database_lengths(Path(args.ideal))
    target_rec = resolve_length_record(lengths, args.target)
    ref_rec = resolve_length_record(lengths, args.reference)

    target_name = target_rec["name"]
    ref_name = ref_rec["name"]
    L_cert = float(target_rec["L_database"])
    L_ref_cert = float(ref_rec["L_database"])

    pair_rows = read_csv_rows(bemv8_dir / "pair_subtracted_correction.csv")
    length_phys_rows = read_csv_rows(bemv8_dir / "spectral_length_estimate_phys.csv")
    if not pair_rows:
        raise RuntimeError(f"missing {bemv8_dir}/pair_subtracted_correction.csv")

    pair = get_target_pair_row(pair_rows, target_name, ref_name)
    DeltaF_pair = as_float(pair.get("DeltaF_pair"))
    Mmax = as_float(pair.get("M_max", pair.get("max_common_modes")))
    if not math.isfinite(Mmax):
        Mmax = as_float(pair.get("max_common_modes"))

    v8_len = get_v8_length_row(length_phys_rows, target_name)
    L_v8_used = as_float(v8_len.get("L_used")) if v8_len else float("nan")
    L_v8_geom = as_float(v8_len.get("L_geom_raw")) if v8_len else float("nan")

    NsoftV = int(args.soft_index_count) * soft_volume(args)
    leading_full_cert = NsoftV * L_cert
    leading_half_cert = 0.5 * leading_full_cert

    cert_rows = [{
        "target": target_name,
        "target_id": target_rec["id"],
        "reference": ref_name,
        "reference_id": ref_rec["id"],
        "L_cert_target_database": L_cert,
        "L_cert_reference_database": L_ref_cert,
        "L_v8_geom_raw_if_available": L_v8_geom,
        "L_v8_used_if_available": L_v8_used,
        "delta_L_v8_geom_minus_cert": (L_v8_geom - L_cert) if math.isfinite(L_v8_geom) else "",
        "scale_geom_to_cert": (L_cert / L_v8_geom) if math.isfinite(L_v8_geom) and abs(L_v8_geom) > 0 else "",
        "NsoftV": NsoftV,
        "leading_full_cert": leading_full_cert,
        "leading_half_alpha_inv_cert": leading_half_cert,
        "status": "CERTIFIED_LENGTH_FROM_IDEAL_DATABASE_L_COLUMN_ALPHA_BLIND",
    }]
    write_csv(outdir / "certified_length_audit.csv", cert_rows)

    ctx = {
        "L_cert": L_cert,
        "Mmax": Mmax,
        "NsoftV": NsoftV,
    }

    norm_names = [x.strip() for x in args.normalizers.split(",") if x.strip()]
    normalizer_rows: List[Dict[str, Any]] = []
    candidate_rows: List[Dict[str, Any]] = []
    for norm in norm_names:
        den, desc = denominator(norm, ctx)
        if math.isfinite(den) and abs(den) > 1e-300:
            DeltaF_phys = DeltaF_pair / den
            gate_numeric = "PASS_NUMERIC"
        else:
            DeltaF_phys = float("nan")
            gate_numeric = "FAIL_BAD_DENOMINATOR"

        half_corr = 0.5 * DeltaF_phys if math.isfinite(DeltaF_phys) else float("nan")
        alpha_pred = leading_half_cert + half_corr if math.isfinite(half_corr) else float("nan")
        ratio = abs(DeltaF_phys) / abs(leading_full_cert) if math.isfinite(DeltaF_phys) and abs(leading_full_cert) > 0 else float("nan")
        gate = (
            "PASS_SUBLEADING_CORRECTION"
            if gate_numeric == "PASS_NUMERIC"
            and math.isfinite(ratio)
            and ratio <= args.subleading_threshold
            else "FAIL_NOT_SUBLEADING"
        )
        if gate_numeric != "PASS_NUMERIC":
            gate = gate_numeric

        normalizer_rows.append({
            "normalizer": norm,
            "description": desc,
            "denominator": den,
            "DeltaF_pair_raw": DeltaF_pair,
            "DeltaF_phys_cert_normalized": DeltaF_phys,
            "correction_to_leading_ratio": ratio,
            "gate": gate,
        })
        candidate_rows.append({
            "target": target_name,
            "reference": ref_name,
            "normalizer": norm,
            "L_cert_target": L_cert,
            "NsoftV": NsoftV,
            "leading_full_cert": leading_full_cert,
            "leading_half_alpha_inv_cert": leading_half_cert,
            "DeltaF_pair_raw": DeltaF_pair,
            "normalizer_denominator": den,
            "DeltaF_phys_cert_normalized": DeltaF_phys,
            "finite_correction_half_cert": half_corr,
            "alpha_inv_pred_blind_v13": alpha_pred,
            "correction_to_leading_ratio": ratio,
            "subleading_threshold": args.subleading_threshold,
            "gate": gate,
            "status": "ALPHA_BLIND_CERTIFIED_LENGTH_CANDIDATE_NOT_CODATA_COMPARISON",
        })

    write_csv(outdir / "certified_normalizer_candidates.csv", normalizer_rows)
    write_csv(outdir / "alpha_component_budget_v13.csv", candidate_rows)

    # Select preferred normalizer if present and passing, else smallest ratio passing, else smallest ratio.
    selected = None
    preferred = [r for r in candidate_rows if r["normalizer"] == args.preferred_normalizer]
    if preferred and preferred[0]["gate"] == "PASS_SUBLEADING_CORRECTION":
        selected = preferred[0]
    else:
        passers = [r for r in candidate_rows if r["gate"] == "PASS_SUBLEADING_CORRECTION"]
        if passers:
            selected = sorted(passers, key=lambda r: as_float(r["correction_to_leading_ratio"], 1e99))[0]
        elif candidate_rows:
            selected = sorted(candidate_rows, key=lambda r: as_float(r["correction_to_leading_ratio"], 1e99))[0]

    return {
        "selected": selected,
        "target_name": target_name,
        "ref_name": ref_name,
        "cert_rows": cert_rows,
        "candidate_rows": candidate_rows,
        "pair_row": pair,
        "bemv8_dir": str(bemv8_dir),
    }


def write_report(outdir: Path, result: Dict[str, Any], args, source: str) -> None:
    selected = result["selected"]
    lines = []
    lines.append("# BEMv13 certified-length budget report")
    lines.append("")
    lines.append("This report is alpha-blind: it does not contain or compare with observed fine structure.")
    lines.append("")
    lines.append("BEMv13 uses the database `L` column as the certified longitudinal length, while the Fourier coefficients remain the BEM geometry source.")
    lines.append("")
    lines.append("The working budget is")
    lines.append("")
    lines.append(r"\[")
    lines.append(r"\alpha^{-1}_{\rm pred,blind}")
    lines.append(r"=")
    lines.append(r"\frac12\left[N_{\rm soft}V_{\rm soft}L_{\rm cert}(3_1)")
    lines.append(r"+\Delta F_{\rm pair}/\mathcal N_q\right].")
    lines.append(r"\]")
    lines.append("")
    lines.append("## Selected candidate")
    lines.append("")
    if selected:
        for k, v in selected.items():
            lines.append(f"- `{k}`: `{v}`")
    else:
        lines.append("- no selected candidate")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("A passing candidate only shows that the certified-length branch and finite-correction normalizer are internally alpha-blind and subleading.")
    lines.append("The next gate is a BEMv14 convergence grid for the certified-length budget, reusing the BEMv10 stability logic.")
    lines.append("")
    lines.append(f"Input/source: `{source}`")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("- `certified_length_audit.csv`")
    lines.append("- `certified_normalizer_candidates.csv`")
    lines.append("- `alpha_component_budget_v13.csv`")
    (outdir / "certified_length_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v13_certified")
    ap.add_argument("--v8-script", default="")
    ap.add_argument("--from-bemv8-outdir", default="")

    ap.add_argument("--ideal-xml-knot-ids", default="0:1:1,3:1:1,4:1:1")
    ap.add_argument("--target", default="3_1")
    ap.add_argument("--reference", default="0_1")

    # BEMv8 pass-through.
    ap.add_argument("--n-center", type=int, default=32)
    ap.add_argument("--n-theta", type=int, default=6)
    ap.add_argument("--n-sphere", type=int, default=144)
    ap.add_argument("--tube-fraction", type=float, default=0.30)
    ap.add_argument("--outer-factor", type=float, default=2.6)
    ap.add_argument("--mu-mode", choices=["inverse_tube_radius", "inverse_outer_radius", "fixed", "zero"], default="inverse_outer_radius")
    ap.add_argument("--mu-value", type=float, default=1.0)
    ap.add_argument("--boundary-subspace", choices=["all", "tube", "sphere"], default="all")
    ap.add_argument("--keep-constant", action="store_true")
    ap.add_argument("--no-auto-add-unknot", action="store_true")
    ap.add_argument("--max-raw-modes", type=int, default=0)

    ap.add_argument("--fit-min-M", type=int, default=4)
    ap.add_argument("--counterterm-fit-min-M", type=int, default=4)
    ap.add_argument("--fit-tail-frac", type=float, default=0.75)
    ap.add_argument("--counterterm-tail-frac", type=float, default=0.75)
    ap.add_argument("--fit-models", default="sqrt,sqrt+inv,sqrt+inv+threehalf")
    ap.add_argument("--counterterm-models", default="hk,hk+inv_sqrt,hk+inv_sqrt+inv")

    ap.add_argument("--soft-index-count", type=int, default=4)
    ap.add_argument("--soft-volume-mode", choices=["none", "unit_ball", "sphere_surface", "numeric"], default="unit_ball")
    ap.add_argument("--soft-volume-value", type=float, default=0.0)

    ap.add_argument("--length-samples", type=int, default=12000)
    ap.add_argument("--length-fit-model", default="hk+inv_sqrt+inv")
    ap.add_argument("--length-coeff", default="A_M")
    ap.add_argument("--length-fit-min-M", type=int, default=4)
    ap.add_argument("--length-fit-tail-frac", type=float, default=0.75)

    ap.add_argument("--pair-fit-model", default="hk+inv_sqrt+inv")
    ap.add_argument("--pair-fit-min-M", type=int, default=4)
    ap.add_argument("--pair-fit-tail-frac", type=float, default=0.75)

    # BEMv13.
    ap.add_argument("--normalizers", default="raw,Mmax,sqrtM,Lcert,Lcert2,Lcert3,NsoftV,NsoftV_Lcert,leading_full_cert,leading_half_cert,M_Lcert,sqrtM_Lcert,M_Lcert2")
    ap.add_argument("--preferred-normalizer", default="M_Lcert2")
    ap.add_argument("--subleading-threshold", type=float, default=0.05)
    ap.add_argument("--subrun-timeout", type=int, default=300)

    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.from_bemv8_outdir:
        bemv8_dir = Path(args.from_bemv8_outdir)
        if not bemv8_dir.exists():
            raise FileNotFoundError(bemv8_dir)
        source = f"existing BEMv8 outdir={bemv8_dir}"
    else:
        bemv8_dir = outdir / "bemv8_base"
        bemv8_dir.mkdir(parents=True, exist_ok=True)
        v8_script = Path(args.v8_script) if args.v8_script else Path(__file__).with_name("routeB_RT_bem_v8_pair_length_budget.py")
        if not v8_script.exists():
            fallback = Path("/mnt/data/routeB_RT_bem_v8_pair_length_budget.py")
            if fallback.exists():
                v8_script = fallback
            else:
                raise FileNotFoundError(f"BEMv8 script not found: {v8_script}")
        run_bemv8(v8_script, args, bemv8_dir)
        source = f"BEMv8 subrun={bemv8_dir}"

    result = build_outputs(outdir, bemv8_dir, args)
    write_report(outdir, result, args, source)

    config = {"args": vars(args), "source": source, "bemv8_dir": str(bemv8_dir)}
    (outdir / "run_config_v13.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")

    sel = result["selected"] or {}
    print("="*78)
    print("Route B BEMv13 certified-length budget complete")
    print("="*78)
    print(f"outdir: {outdir}")
    print(f"source: {source}")
    print(f"selected normalizer: {sel.get('normalizer')}")
    print(f"gate: {sel.get('gate')}")
    print(f"L_cert_target: {sel.get('L_cert_target')}")
    print(f"leading_half_alpha_inv_cert: {sel.get('leading_half_alpha_inv_cert')}")
    print(f"finite_correction_half_cert: {sel.get('finite_correction_half_cert')}")
    print(f"alpha_inv_pred_blind_v13: {sel.get('alpha_inv_pred_blind_v13')}")
    print("wrote: certified_length_audit.csv, certified_normalizer_candidates.csv, alpha_component_budget_v13.csv, certified_length_report.md")


if __name__ == "__main__":
    main()
