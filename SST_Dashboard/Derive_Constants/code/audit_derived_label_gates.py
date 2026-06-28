#!/usr/bin/env python3
"""
audit_derived_label_gates.py

Audit whether the current three-paper + numerical package may honestly label
the fine-structure-scale result as "derived".

The script distinguishes:

    fundamental_derived
        All foundational coefficients and the far-field normalization are
        independently derived/certified.

    closure_derived
        E_star and alpha_cell are derived from explicitly stated closure
        hypotheses, but at least one foundational coefficient remains an
        assumption/ansatz.

    conditional_internal
        The numerical machinery is internally consistent, but the physical
        identification remains conditional.

    not_derived
        Required numerical gates fail.

This is not a physics proof. It is a reproducibility/audit gate that prevents
overclaiming in the manuscripts.

Typical usage
-------------
    python audit_derived_label_gates.py \
      --batch-summary batch_summary.csv \
      --batch-controls batch_controls.csv \
      --batch-aggregate batch_aggregate_stats.csv \
      --outdir outputs_derived_label_audit

With far-field/phase certificates:
    python audit_derived_label_gates.py \
      --batch-summary batch_summary.csv \
      --batch-controls batch_controls.csv \
      --batch-aggregate batch_aggregate_stats.csv \
      --phase-certificate outputs_Kcell_phase_certificate/phase_stiffness_certificate.csv \
      --farfield-certificate outputs_farfield_two_cell/alpha_farfield_certificate.csv \
      --outdir outputs_derived_label_audit

Future, if independent derivations exist:
    python audit_derived_label_gates.py ... --prove-16pi3 --prove-11-48 --prove-Rcell --prove-Kcell-independent
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


def read_csv_optional(path: Optional[str]) -> Optional[pd.DataFrame]:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    return pd.read_csv(p)


def bool_from_cert(df: Optional[pd.DataFrame], status_col: str = "status") -> bool:
    if df is None or len(df) == 0 or status_col not in df.columns:
        return False
    return str(df[status_col].iloc[0]).strip().lower() == "pass"


def get_first(df: Optional[pd.DataFrame], col: str, default=np.nan):
    if df is None or len(df) == 0 or col not in df.columns:
        return default
    return df[col].iloc[0]


def audit(args) -> pd.DataFrame:
    batch = read_csv_optional(args.batch_summary)
    controls = read_csv_optional(args.batch_controls)
    agg = read_csv_optional(args.batch_aggregate)
    phase = read_csv_optional(args.phase_certificate)
    far = read_csv_optional(args.farfield_certificate)

    rows: List[Dict[str, object]] = []

    def add(component, decision, label_allowed, evidence, requirement, severity="info"):
        rows.append({
            "component": component,
            "decision": decision,
            "label_allowed": label_allowed,
            "evidence": evidence,
            "requirement_for_derived_label": requirement,
            "severity": severity,
        })

    # A_K theorem.
    add(
        "local Biot-Savart coefficient A_K -> 1/(4pi)",
        "derived",
        "derived",
        "local-induction logarithmic coefficient is a standard theorem for smooth slender filaments",
        "retain theorem statement and dimensional normalization",
    )

    # Main batch stability.
    if batch is not None and len(batch):
        n_total = len(batch)
        n_success = int((batch["status"].astype(str) == "E0_derived").sum()) if "status" in batch else 0
        success_fraction = n_success / max(n_total, 1)
        E_mean = float(batch["E_star"].mean()) if "E_star" in batch else np.nan
        E_std = float(batch["E_star"].std(ddof=0)) if "E_star" in batch else np.nan
        rel_std = E_std / E_mean if np.isfinite(E_mean) and E_mean != 0 else np.nan
        stable = success_fraction >= args.min_success_fraction and np.isfinite(rel_std) and rel_std <= args.max_rel_std
        add(
            "BEM/NLS finite-cell stationary aspect E_star",
            "closure-derived" if stable else "not_derived",
            "closure-derived" if stable else "not allowed",
            f"{n_success}/{n_total} successful; E_mean={E_mean:.12g}; rel_std={rel_std:.3e}",
            f"success_fraction>={args.min_success_fraction} and rel_std<={args.max_rel_std}",
            "required",
        )
    else:
        stable = False
        add(
            "BEM/NLS finite-cell stationary aspect E_star",
            "not_derived",
            "not allowed",
            "batch_summary.csv missing",
            "supply batch_summary.csv with stable E_star runs",
            "required",
        )

    # Controls.
    bem_only_fails = False
    if controls is not None and len(controls):
        if "pressure_mode" in controls and "status" in controls:
            bem = controls[controls["pressure_mode"].astype(str) == "none"]
            bem_only_fails = len(bem) > 0 and not any(bem["status"].astype(str) == "E0_derived")
        add(
            "BEM-only negative control",
            "passed" if bem_only_fails else "missing_or_failed",
            "supports conditional closure" if bem_only_fails else "not decisive",
            "BEM-only does not find E0" if bem_only_fails else "no BEM-only failure found",
            "BEM-only should not produce the claimed E_star",
            "required",
        )
    else:
        add(
            "BEM-only negative control",
            "missing",
            "not decisive",
            "batch_controls.csv missing",
            "supply controls including pressure_mode=none",
            "required",
        )

    # Foundational coefficients.
    add(
        "zeroth pressure prefactor 16*pi/3",
        "derived" if args.prove_16pi3 else "open_coefficient",
        "derived" if args.prove_16pi3 else "closure hypothesis only",
        "user flag --prove-16pi3 supplied" if args.prove_16pi3 else "no variational derivation supplied",
        "derive 16*pi/3 from a specified pressure-cell variational principle without alpha/CODATA",
        "blocking",
    )
    add(
        "NLS finite-shell correction 11/48",
        "derived" if args.prove_11_48 else "open_coefficient",
        "derived" if args.prove_11_48 else "closure hypothesis only",
        "user flag --prove-11-48 supplied" if args.prove_11_48 else "no GP/NLS core-profile expansion deriving 11/48 supplied",
        "derive 11/48 from NLS/GP finite-core asymptotics or a controlled shell expansion",
        "blocking",
    )
    add(
        "cell-radius closure R_cell=2 L_K",
        "derived" if args.prove_Rcell else "open_closure",
        "derived" if args.prove_Rcell else "closure hypothesis only",
        "user flag --prove-Rcell supplied" if args.prove_Rcell else "no stationarity/geometry proof supplied",
        "derive chi_R=2 or include chi_R sensitivity as an assumption",
        "blocking",
    )

    # Far-field and phase stiffness.
    phase_pass = bool_from_cert(phase)
    phase_mode = str(get_first(phase, "mode", "missing"))
    if args.prove_Kcell_independent:
        k_decision = "independent_candidate"
        k_label = "derived"
        k_evidence = "--prove-Kcell-independent supplied"
    elif phase_pass and phase_mode == "override_lambda":
        k_decision = "operator-measured_candidate"
        k_label = "derived candidate"
        k_evidence = "phase certificate uses override_lambda measurement and passes"
    elif phase_pass:
        k_decision = "internal_normalization"
        k_label = "conditional only"
        k_evidence = f"phase certificate passes but mode={phase_mode}; this is an internal normalization certificate"
    else:
        k_decision = "missing"
        k_label = "not allowed"
        k_evidence = "phase_stiffness_certificate.csv missing or not pass"
    add(
        "far-field stiffness K_cell=E_eff/(8*pi)",
        k_decision,
        k_label,
        k_evidence,
        "independently measure Lambda_phi from a one-cell phase-Hessian operator without inserting E_eff/4",
        "blocking",
    )

    far_pass = bool_from_cert(far)
    add(
        "two-cell far-field coefficient C_far -> alpha_cell",
        "conditional_certificate_passed" if far_pass else "missing_or_failed",
        "conditional far-field" if far_pass else "not allowed",
        "far-field certificate pass" if far_pass else "alpha_farfield_certificate.csv missing or fail",
        "show C_far(R) -> alpha_cell; still conditional on K_cell normalization",
        "required",
    )

    # Overall decision.
    foundational_ok = args.prove_16pi3 and args.prove_11_48 and args.prove_Rcell
    k_ok = args.prove_Kcell_independent or (phase_pass and phase_mode == "override_lambda")
    if stable and bem_only_fails and foundational_ok and k_ok and far_pass:
        overall = "fundamental_derived"
        allowed = "derived"
        evidence = "all blocking gates passed"
    elif stable and bem_only_fails:
        overall = "closure_derived_not_fundamental"
        allowed = "closure-derived / conditional"
        evidence = "stable E_star from closure hypotheses; foundational coefficient gates remain open"
    else:
        overall = "not_derived"
        allowed = "not allowed"
        evidence = "one or more required numerical gates failed"

    add(
        "OVERALL fine-structure-scale claim",
        overall,
        allowed,
        evidence,
        "for fundamental derived: pass E_star stability, negative controls, coefficient derivations, independent K_cell, and far-field certificate",
        "overall",
    )

    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--batch-summary", default="batch_summary.csv")
    p.add_argument("--batch-controls", default="batch_controls.csv")
    p.add_argument("--batch-aggregate", default="batch_aggregate_stats.csv")
    p.add_argument("--phase-certificate", default=None)
    p.add_argument("--farfield-certificate", default=None)
    p.add_argument("--outdir", default="outputs_derived_label_audit")
    p.add_argument("--min-success-fraction", type=float, default=1.0)
    p.add_argument("--max-rel-std", type=float, default=5e-7)

    p.add_argument("--prove-16pi3", action="store_true")
    p.add_argument("--prove-11-48", action="store_true")
    p.add_argument("--prove-Rcell", action="store_true")
    p.add_argument("--prove-Kcell-independent", action="store_true")
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    df = audit(args)
    df.to_csv(outdir / "derived_label_audit.csv", index=False)

    overall = df[df["component"] == "OVERALL fine-structure-scale claim"].iloc[0]
    lines = [
        "# Derived-label audit",
        "",
        f"Overall decision: **{overall['decision']}**",
        f"Allowed label: **{overall['label_allowed']}**",
        "",
        "## Blocking open items",
    ]
    blocking = df[(df["severity"] == "blocking") & (~df["decision"].astype(str).str.contains("derived|independent", regex=True))]
    if len(blocking) == 0:
        lines.append("None.")
    else:
        for _, r in blocking.iterrows():
            lines.append(f"- **{r['component']}**: {r['decision']}. Required: {r['requirement_for_derived_label']}")
    lines += ["", "## Full audit table", ""]
    lines.append(df.to_markdown(index=False))
    (outdir / "derived_label_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(df.to_string(index=False))
    print(f"\nWrote {outdir/'derived_label_audit.csv'}")
    print(f"Wrote {outdir/'derived_label_summary.md'}")


if __name__ == "__main__":
    main()
