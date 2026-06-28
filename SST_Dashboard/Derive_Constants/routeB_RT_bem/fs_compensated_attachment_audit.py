#!/usr/bin/env python3
r"""
fs_compensated_attachment_audit.py
==================================

Compensated Attachment-Lemma audit for the SST core-twist program.

Purpose
-------
This is an AUDIT runner, not a proof machine.  It tests a proposed upgrade of
Core-Cycle Attachment:

    Hol(A_core)/(2π) = chi

where the global holonomy is decomposed into a local 3D/core-clock contribution
and a compensated attachment/gluing contribution:

    chi_total = chi_local + chi_attachment.

The key Canon-candidate mode is:

    chi_local      = chi / (1 + sigma * epsilon_SE)
    chi_attachment = chi - chi_local
    chi_total      = chi

This tests whether a swirl-clock / entanglement-assisted attachment can preserve
an exact integer holonomy while redistributing the local vs global contribution.

It separates:

  [EXACT HOLONOMY]
      total_turns == chi.

  [INTEGER SELECTION]
      positive twist stiffness selects n_core=chi from the allowed integer / FR-odd sector.
      This can remain true even when total_turns is merely close to chi, so it is weaker.

  [CHARGE-LEAK / SPECTRAL-LEAK]
      a portion of the missing holonomy leaks out of the neutral spinon/framing sector.
      This is reported explicitly and is NOT Canon-safe unless the leak is zero/suppressed.

Inputs
------
The script can read core_holonomy_v2_results.csv (or a compatible CSV) to get
canonical torus rows.  If absent, it falls back to analytic T(p,q) rows.

Typical run
-----------
    python fs_compensated_attachment_audit.py \
      --input-results core_holonomy_v2_results.csv \
      --canonical-only \
      --eps-list 0,0.01,0.1,1.0

Outputs
-------
    compensated_attachment_audit_models.csv
    compensated_attachment_audit_results.csv
    compensated_attachment_audit_summary.md
    compensated_attachment_audit_phase_scan.csv
    fs_compensated_attachment_audit_outputlog.txt

Dependencies: Python stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

TAU = 2.0 * math.pi
DEFAULT_V_SWIRL = 1.09384563e6
DEFAULT_R_C = 1.40897017e-15


class Tee:
    def __init__(self, *streams):
        self.streams = streams
    def write(self, data: str) -> None:
        for s in self.streams:
            s.write(data)
            s.flush()
    def flush(self) -> None:
        for s in self.streams:
            s.flush()


def install_tee(log_path: Path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(log_path, "w", encoding="utf-8", buffering=1)
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = Tee(old_stdout, f)
    sys.stderr = Tee(old_stderr, f)
    print(f"[log] writing console output to {log_path}")
    return f, old_stdout, old_stderr


@dataclass
class GeometryRow:
    label: str
    source_type: str
    family: str
    p: Optional[int]
    q: Optional[int]
    expected_pq: Optional[int]
    torus_status: str
    torus_sl_round: Optional[int]


@dataclass
class CompModel:
    model_id: str
    description: str
    parity: str              # none | odd | even
    chi_kind: str            # matter | antimatter
    local_kind: str          # canon | renormalized | q_renormalized | passive | decohered
    attachment_kind: str     # none | exact_compensated | partial | charge_leak | residual | local_only
    status_label: str


def parse_int_or_none(x: object) -> Optional[int]:
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except Exception:
        return None


def parse_float_or_none(x: object) -> Optional[float]:
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None


def allowed_ns(parity: str, n_min: int, n_max: int) -> List[int]:
    vals = list(range(n_min, n_max + 1))
    if parity == "none":
        return vals
    if parity == "odd":
        return [n for n in vals if n % 2 != 0]
    if parity == "even":
        return [n for n in vals if n % 2 == 0]
    raise ValueError(f"unknown parity: {parity}")


def select_ns(center: Optional[float], parity: str, n_min: int, n_max: int, tol: float = 1e-12) -> Tuple[List[int], Optional[float], List[int]]:
    allowed = allowed_ns(parity, n_min, n_max)
    if center is None or not allowed:
        return [], None, allowed
    energies = [(n, (n - center) ** 2) for n in allowed]
    e_min = min(e for _, e in energies)
    selected = [n for n, e in energies if abs(e - e_min) <= tol]
    return selected, e_min, allowed


def sign_chi(kind: str) -> int:
    return -1 if kind in ("anti", "antimatter") else +1


def read_geometry_results(path: Path, canonical_only: bool, include_controls: bool) -> List[GeometryRow]:
    rows: List[GeometryRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for raw in r:
            fam = (raw.get("family") or "unknown").strip()
            if not include_controls and fam != "torus":
                continue
            status = (raw.get("torus_status") or "UNKNOWN").strip()
            if canonical_only and status not in ("PASS_DERIVED_PQ", "PASS_DERIVED_PQ_ANALYTIC_ASSUMED"):
                continue
            label = (raw.get("label") or raw.get("curve") or "curve").strip()
            rows.append(GeometryRow(
                label=label,
                source_type=(raw.get("source_type") or "csv").strip(),
                family=fam,
                p=parse_int_or_none(raw.get("p")),
                q=parse_int_or_none(raw.get("q")),
                expected_pq=parse_int_or_none(raw.get("expected_pq") or raw.get("pq")),
                torus_status=status,
                torus_sl_round=parse_int_or_none(raw.get("torus_SL_round") or raw.get("torus_sl_round")),
            ))
    return rows


def parse_q_list(s: str) -> List[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def parse_extra_torus(s: str) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    if not s.strip():
        return out
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            a, b = part.split(":", 1)
        elif "x" in part.lower():
            a, b = part.lower().split("x", 1)
        else:
            raise ValueError(f"cannot parse extra-torus entry {part!r}")
        out.append((int(a), int(b)))
    return out


def analytic_rows(p: int, q_list: Sequence[int], extra: Sequence[Tuple[int, int]]) -> List[GeometryRow]:
    rows: List[GeometryRow] = []
    for q in q_list:
        pq = p * q
        rows.append(GeometryRow(f"analytic:T({p},{q})", "analytic", "torus", p, q, pq, "PASS_DERIVED_PQ_ANALYTIC_ASSUMED", pq))
    for pp, qq in extra:
        pq = pp * qq
        rows.append(GeometryRow(f"analytic:T({pp},{qq})", "analytic", "torus", pp, qq, pq, "PASS_DERIVED_PQ_ANALYTIC_ASSUMED", pq))
    return rows


def default_models(include_diagnostics: bool = True) -> List[CompModel]:
    models = [
        CompModel(
            "C0_CANON_ATTACHED_BASELINE",
            "Baseline: exact attached canon core cycle, no redistribution; total holonomy is chi.",
            "odd", "matter", "canon", "exact_compensated", "BASELINE_EXACT_ATTACHMENT",
        ),
        CompModel(
            "C1_COMPENSATED_NEUTRAL_MATTER",
            "Compensated swirl-clock mode: local turn is renormalized, attachment supplies the missing neutral holonomy; no charge leak.",
            "odd", "matter", "renormalized", "exact_compensated", "CANON_CANDIDATE_COMPENSATED",
        ),
        CompModel(
            "C2_COMPENSATED_NEUTRAL_ANTIMATTER",
            "Same as C1 but chi=-1 mirror sector.",
            "odd", "antimatter", "renormalized", "exact_compensated", "CANON_CANDIDATE_MIRROR_COMPENSATED",
        ),
        CompModel(
            "C3_UNCOMPENSATED_LOCAL_ONLY",
            "Local swirl-clock renormalization without global compensation; tests whether local-only survives exact holonomy.",
            "odd", "matter", "renormalized", "none", "FAILS_EXACT_HOLONOMY_UNLESS_EPS_ZERO",
        ),
        CompModel(
            "C4_PARTIAL_COMPENSATION",
            "Only part of the missing holonomy is attached; useful falsifier for exactness.",
            "odd", "matter", "renormalized", "partial", "PARTIAL_COMPENSATION_DIAGNOSTIC",
        ),
        CompModel(
            "C5_CHARGE_LEAK",
            "A fraction of missing holonomy leaks out of the neutral spinon/framing sector; Canon-unsafe unless suppressed.",
            "odd", "matter", "renormalized", "charge_leak", "CHARGE_LEAK_CONSTRAINED",
        ),
        CompModel(
            "C6_DECOHERED_RESIDUAL",
            "Compensated mode with a residual decoherence error added to total holonomy; stability but not exact Canon.",
            "odd", "matter", "renormalized", "residual", "DECOHERENCE_RESIDUAL_DIAGNOSTIC",
        ),
        CompModel(
            "C7_Q_DEP_COMPENSATED",
            "q-dependent local split, but exact compensation keeps total holonomy chi. Tests if compensation can be q-independent in total.",
            "odd", "matter", "q_renormalized", "exact_compensated", "Q_DEP_LOCAL_BUT_TOTAL_EXACT",
        ),
        CompModel(
            "C8_PASSIVE_TRANSIT_COMPENSATED_TEST",
            "Passive transit center with no exact attachment; should fail as Canon mechanism.",
            "odd", "matter", "passive", "none", "PASSIVE_TRANSIT_REJECTED",
        ),
    ]
    if include_diagnostics:
        return models
    return [m for m in models if m.model_id in ("C0_CANON_ATTACHED_BASELINE", "C1_COMPENSATED_NEUTRAL_MATTER", "C2_COMPENSATED_NEUTRAL_ANTIMATTER", "C3_UNCOMPENSATED_LOCAL_ONLY", "C5_CHARGE_LEAK")]


def local_turns_for(model: CompModel, row: GeometryRow, chi: int, eps: float, args) -> float:
    sigma = args.sigma
    denom = 1.0 + sigma * eps
    if abs(denom) < 1e-15:
        # singular diagnostic; keep finite marker by returning huge value
        return math.copysign(float("inf"), chi)
    if model.local_kind == "canon":
        return float(chi)
    if model.local_kind == "renormalized":
        return float(chi) / denom
    if model.local_kind == "q_renormalized":
        q = row.q if row.q is not None else args.q_ref
        q_factor = 1.0 + args.q_slope * (float(q) - float(args.q_ref))
        return float(chi) / (1.0 + sigma * eps * q_factor)
    if model.local_kind == "passive":
        return float(args.passive_turns)
    if model.local_kind == "decohered":
        return float(chi) / denom + args.decoherence_residual
    raise ValueError(f"unknown local_kind {model.local_kind}")


def decompose_turns(model: CompModel, row: GeometryRow, eps: float, args) -> Tuple[int, float, float, float, float, float]:
    """Return chi, local, attachment, total, charge_leak, spectral_residual."""
    chi = sign_chi(model.chi_kind)
    local = local_turns_for(model, row, chi, eps, args)
    if not math.isfinite(local):
        return chi, local, float("nan"), float("nan"), float("nan"), float("nan")
    missing = float(chi) - local
    charge_leak = 0.0
    residual = 0.0

    if model.attachment_kind == "exact_compensated":
        attachment = missing
    elif model.attachment_kind == "none":
        attachment = 0.0
    elif model.attachment_kind == "partial":
        attachment = args.compensation_gain * missing
    elif model.attachment_kind == "charge_leak":
        charge_leak = args.charge_leak_fraction * missing
        attachment = (1.0 - args.charge_leak_fraction) * missing
    elif model.attachment_kind == "residual":
        attachment = missing
        residual = args.decoherence_residual
    elif model.attachment_kind == "local_only":
        attachment = 0.0
    else:
        raise ValueError(f"unknown attachment_kind {model.attachment_kind}")

    total = local + attachment + residual
    return chi, local, attachment, total, charge_leak, residual


def sl_abs_for(row: GeometryRow, n_core: int) -> Optional[int]:
    base = row.expected_pq
    if base is None:
        if row.torus_sl_round is None:
            return None
        base = abs(row.torus_sl_round)
    return int(base + abs(n_core))


def count_by(rows: Iterable[Dict[str, object]], key: str) -> Dict[str, int]:
    d: Dict[str, int] = {}
    for row in rows:
        k = str(row.get(key, ""))
        d[k] = d.get(k, 0) + 1
    return d


def write_csv(path: Path, rows: List[Dict[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print(f"[write] {path}")


def md_table(rows: List[Dict[str, object]], fields: Sequence[str], max_rows: Optional[int] = None) -> str:
    data = rows if max_rows is None else rows[:max_rows]
    lines = ["| " + " | ".join(fields) + " |", "|" + "|".join(["---"] * len(fields)) + "|"]
    for row in data:
        lines.append("| " + " | ".join(str(row.get(f, "")) for f in fields) + " |")
    if max_rows is not None and len(rows) > max_rows:
        lines.append(f"\n... {len(rows) - max_rows} more rows in CSV.\n")
    return "\n".join(lines)


def audit_status(model: CompModel, exact_hol: bool, integer_sel: bool, charge_safe: bool, eps: float) -> str:
    if model.model_id.startswith("C1") or model.model_id.startswith("C2") or model.model_id.startswith("C7"):
        if exact_hol and integer_sel and charge_safe:
            return "CANON_CANDIDATE_EXACT_COMPENSATED"
    if model.model_id.startswith("C0"):
        if exact_hol and integer_sel:
            return "BASELINE_EXACT_ATTACHMENT"
    if model.model_id.startswith("C3"):
        if eps == 0 and exact_hol:
            return "LOCAL_ONLY_TRIVIAL_EPS0"
        if integer_sel and not exact_hol:
            return "SELECTION_STABLE_BUT_HOLONOMY_NOT_EXACT"
        return "FAILS_UNCOMPENSATED"
    if model.model_id.startswith("C4"):
        if integer_sel and not exact_hol:
            return "PARTIAL_SELECTION_STABLE_NOT_EXACT"
        return "PARTIAL_COMPENSATION_FAILS_EXACTNESS"
    if model.model_id.startswith("C5"):
        if not charge_safe:
            return "CHARGE_LEAK_REJECT_OR_CONSTRAIN"
        if exact_hol:
            return "CHARGE_LEAK_SUPPRESSED_EXACT"
        return "CHARGE_LEAK_SUPPRESSED_BUT_NOT_EXACT"
    if model.model_id.startswith("C6"):
        if integer_sel and not exact_hol:
            return "DECOHERED_SELECTION_STABLE_NOT_EXACT"
        return "DECOHERED_EXACT_FAIL"
    if model.model_id.startswith("C8"):
        return "PASSIVE_TRANSIT_REJECTED"
    return model.status_label


def run(args) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]], str]:
    # Geometry.
    inp = Path(args.input_results) if args.input_results else None
    if inp and inp.exists():
        geometry = read_geometry_results(inp, canonical_only=args.canonical_only, include_controls=args.include_controls)
        print(f"[input] read {len(geometry)} rows from {inp}")
    else:
        if inp:
            print(f"[warn] input not found: {inp}; using analytic fallback")
        geometry = analytic_rows(args.p, parse_q_list(args.q_list), parse_extra_torus(args.extra_torus))
        print(f"[input] fallback analytic rows: {len(geometry)}")

    eps_values = [float(x.strip()) for x in args.eps_list.split(",") if x.strip()]
    models = default_models(include_diagnostics=not args.minimal_models)

    model_rows = [{
        "model_id": m.model_id,
        "parity": m.parity,
        "chi_kind": m.chi_kind,
        "local_kind": m.local_kind,
        "attachment_kind": m.attachment_kind,
        "status_label": m.status_label,
        "description": m.description,
    } for m in models]

    result_rows: List[Dict[str, object]] = []
    phase_scan_rows: List[Dict[str, object]] = []

    for row in geometry:
        for eps in eps_values:
            for m in models:
                chi, local, attachment, total, leak, residual = decompose_turns(m, row, eps, args)
                selected, e_min, allowed = select_ns(total if math.isfinite(total) else None, m.parity, args.n_min, args.n_max, args.degeneracy_tol)
                exact_hol = math.isfinite(total) and abs(total - chi) <= args.exact_tol
                charge_safe = (not math.isfinite(leak)) or abs(leak) <= args.charge_leak_tol
                integer_sel = (selected == [chi])
                sl_vals = []
                for n in selected:
                    v = sl_abs_for(row, n)
                    if v is not None:
                        sl_vals.append(str(v))
                target = row.expected_pq + 1 if row.expected_pq is not None else ""
                exact_pq1 = "YES" if target != "" and str(target) in sl_vals else "NO" if sl_vals else ""
                status = audit_status(m, exact_hol, integer_sel, charge_safe, eps)
                result_rows.append({
                    "curve": row.label,
                    "source_type": row.source_type,
                    "torus_status": row.torus_status,
                    "p": row.p if row.p is not None else "",
                    "q": row.q if row.q is not None else "",
                    "pq": row.expected_pq if row.expected_pq is not None else "",
                    "target_pq_plus_1_abs": target,
                    "epsilon_SE": f"{eps:.12g}",
                    "sigma": args.sigma,
                    "model_id": m.model_id,
                    "chi": chi,
                    "local_turns": f"{local:.12g}" if math.isfinite(local) else "inf/nan",
                    "attachment_turns": f"{attachment:.12g}" if math.isfinite(attachment) else "nan",
                    "total_turns": f"{total:.12g}" if math.isfinite(total) else "nan",
                    "residual_to_chi": f"{(total - chi):.12g}" if math.isfinite(total) else "nan",
                    "charge_leak_turns": f"{leak:.12g}" if math.isfinite(leak) else "nan",
                    "decoherence_residual": f"{residual:.12g}" if math.isfinite(residual) else "nan",
                    "allowed_n": ",".join(str(n) for n in allowed),
                    "selected_n_core": ",".join(str(n) for n in selected),
                    "min_energy": "" if e_min is None else f"{e_min:.12g}",
                    "sl_phys_abs": ",".join(sl_vals),
                    "exact_holonomy_chi": "YES" if exact_hol else "NO",
                    "integer_selection_chi": "YES" if integer_sel else "NO",
                    "exact_pq_plus_1": exact_pq1,
                    "charge_safe": "YES" if charge_safe else "NO",
                    "audit_status": status,
                })

        # phase scan for first few/canonical curves, but small enough to inspect.
        for r in [args.scan_min + i * args.scan_step for i in range(int(round((args.scan_max - args.scan_min) / args.scan_step)) + 1)]:
            selected_odd, _, _ = select_ns(r, "odd", args.n_min, args.n_max, args.degeneracy_tol)
            selected_none, _, _ = select_ns(r, "none", args.n_min, args.n_max, args.degeneracy_tol)
            phase_scan_rows.append({
                "curve": row.label,
                "q": row.q if row.q is not None else "",
                "pq": row.expected_pq if row.expected_pq is not None else "",
                "holonomy_turns": f"{r:.6g}",
                "selected_odd_FR": ",".join(str(n) for n in selected_odd),
                "selected_no_parity": ",".join(str(n) for n in selected_none),
                "odd_selects_plus_one": "YES" if selected_odd == [1] else "NO",
            })

    # Summary.
    omega_core = args.v_swirl / args.r_c
    t_core = TAU * args.r_c / args.v_swirl
    core_turns = omega_core * t_core / TAU
    vorticity_turns = 2.0 * core_turns
    counts = count_by(result_rows, "audit_status")
    model_counts = count_by(result_rows, "model_id")

    preview = [r for r in result_rows if str(r["curve"]).startswith("analytic:T(2,") and r["model_id"] in ("C1_COMPENSATED_NEUTRAL_MATTER", "C3_UNCOMPENSATED_LOCAL_ONLY", "C5_CHARGE_LEAK", "C8_PASSIVE_TRANSIT_COMPENSATED_TEST")]
    if not preview:
        preview = result_rows[:48]

    lines: List[str] = []
    lines.append("# Compensated Attachment Lemma audit summary")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This audit tests whether swirl-clock / entanglement-assisted attachment can redistribute local core holonomy while preserving the exact global integer `chi`.")
    lines.append("")
    lines.append("```text")
    lines.append("chi_total = chi_local + chi_attachment")
    lines.append("Canon-safe compensated mode: chi_total = chi, charge_leak = 0")
    lines.append("Important distinction: integer selection can survive small errors, but exact Canon requires exact holonomy.")
    lines.append("```")
    lines.append("")
    lines.append("## Canonical constants")
    lines.append("")
    lines.append("| quantity | value |")
    lines.append("|---|---:|")
    lines.append(f"| `||v_swirl||` | {args.v_swirl:.12e} m/s |")
    lines.append(f"| `r_c` | {args.r_c:.12e} m |")
    lines.append(f"| `Omega_core` | {omega_core:.12e} s^-1 |")
    lines.append(f"| `T_core` | {t_core:.12e} s |")
    lines.append(f"| `Omega_core*T_core/(2π)` | {core_turns:.12f} turns |")
    lines.append(f"| `omega_vorticity*T_core/(2π)` | {vorticity_turns:.12f} vorticity-turns |")
    lines.append("")
    lines.append("## Model status counts")
    lines.append("")
    lines.append(f"Rows: **{len(result_rows)}**")
    lines.append(f"Audit-status counts: `{counts}`")
    lines.append(f"Model counts: `{model_counts}`")
    lines.append("")
    lines.append("## Model catalogue")
    lines.append("")
    lines.append(md_table(model_rows, ["model_id", "local_kind", "attachment_kind", "status_label"], max_rows=None))
    lines.append("")
    lines.append("## Preview rows")
    lines.append("")
    lines.append(md_table(preview, ["curve", "epsilon_SE", "model_id", "local_turns", "attachment_turns", "total_turns", "selected_n_core", "exact_holonomy_chi", "integer_selection_chi", "charge_safe", "audit_status"], max_rows=72))
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("```text")
    lines.append("C1/C2 exact neutral compensation: local contribution may change, but attachment closes the holonomy exactly to chi. This is Canon-candidate if the compensation is confined to the neutral spinon/framing sector.")
    lines.append("C3 uncompensated local mode: can still select n=1 for small deviations, but exact holonomy fails; not sufficient for Canon exactness.")
    lines.append("C5 charge leak: any unsuppressed leak is rejected/constrained because it exports attachment into charge/spectral sectors.")
    lines.append("C6 decohered residual: selection may remain stable, but exactness is lost.")
    lines.append("C8 passive transit: rejected as the core Attachment mechanism.")
    lines.append("```")
    lines.append("")
    lines.append("## Canon-candidate statement")
    lines.append("")
    lines.append("```text")
    lines.append("[CONDITIONAL CANON-CANDIDATE]")
    lines.append("If a compensated swirl-clock/entanglement gluing connection exists such that")
    lines.append("Hol(A_core)/(2π) = chi_local + chi_attachment = chi,")
    lines.append("with charge_leak = 0 and FR odd parity active, then positive twist stiffness selects")
    lines.append("n_core = chi and SL_phys(T(p,q)) = SL_torus(T(p,q)) + chi.")
    lines.append("```")
    summary = "\n".join(lines) + "\n"
    return model_rows, result_rows, phase_scan_rows, summary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Compensated swirl-clock Attachment Lemma audit", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--input-results", default="core_holonomy_v2_results.csv", help="Prior geometry audit results CSV; fallback analytic rows if missing.")
    p.add_argument("--out-prefix", default="compensated_attachment_audit", help="Output prefix")
    p.add_argument("--canonical-only", action="store_true", help="Use only PASS_DERIVED_PQ rows from input")
    p.add_argument("--include-controls", action="store_true", help="Include non-torus controls when present")
    p.add_argument("--q-list", default="3,5,7,9,11", help="Fallback q list for T(p,q)")
    p.add_argument("--p", type=int, default=2, help="Fallback p for T(p,q)")
    p.add_argument("--extra-torus", default="3:2,3:4", help="Extra fallback controls")
    p.add_argument("--eps-list", default="0,0.01,0.1,1.0", help="Comma separated epsilon_SE values")
    p.add_argument("--sigma", type=float, default=1.0, help="Sign/coupling orientation in denominator 1+sigma*epsilon")
    p.add_argument("--compensation-gain", type=float, default=0.5, help="Partial compensation gain for C4")
    p.add_argument("--charge-leak-fraction", type=float, default=0.01, help="Fraction of missing holonomy leaking to charge sector in C5")
    p.add_argument("--charge-leak-tol", type=float, default=1e-12, help="Allowed absolute charge leak in turns")
    p.add_argument("--decoherence-residual", type=float, default=0.01, help="Residual holonomy error in C6")
    p.add_argument("--passive-turns", type=float, default=2.501, help="Passive transit turns")
    p.add_argument("--q-ref", type=float, default=3.0, help="Reference q for q dependent local split")
    p.add_argument("--q-slope", type=float, default=0.02, help="q slope for q-dependent split")
    p.add_argument("--n-min", type=int, default=-5, help="minimum n_core")
    p.add_argument("--n-max", type=int, default=5, help="maximum n_core")
    p.add_argument("--exact-tol", type=float, default=1e-12, help="Exact holonomy tolerance")
    p.add_argument("--degeneracy-tol", type=float, default=1e-12, help="selection degeneracy tolerance")
    p.add_argument("--minimal-models", action="store_true", help="Run a smaller model set")
    p.add_argument("--scan-min", type=float, default=-0.5, help="phase scan min")
    p.add_argument("--scan-max", type=float, default=3.5, help="phase scan max")
    p.add_argument("--scan-step", type=float, default=0.25, help="phase scan step")
    p.add_argument("--v-swirl", type=float, default=DEFAULT_V_SWIRL, help="SST swirl speed norm")
    p.add_argument("--r-c", type=float, default=DEFAULT_R_C, help="SST core radius")
    p.add_argument("--log-file", default="fs_compensated_attachment_audit_outputlog.txt", help="log file path")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.n_min > args.n_max:
        raise SystemExit("--n-min must be <= --n-max")
    if args.scan_step <= 0:
        raise SystemExit("--scan-step must be positive")
    if abs(1.0 + args.sigma * min([float(x.strip()) for x in args.eps_list.split(',') if x.strip()] or [0.0])) < 1e-15:
        print("[warn] denominator may be singular for some epsilon values")

    out_prefix = Path(args.out_prefix)
    log_path = Path(args.log_file)
    if not log_path.is_absolute():
        log_path = out_prefix.parent / log_path
    log_f, old_stdout, old_stderr = install_tee(log_path)
    try:
        print(f"[config] input_results={args.input_results}")
        print(f"[config] eps_list={args.eps_list}, sigma={args.sigma}")
        print("[scope] compensated swirl-clock / entanglement Attachment Lemma audit")
        model_rows, result_rows, phase_scan_rows, summary = run(args)

        model_fields = ["model_id", "parity", "chi_kind", "local_kind", "attachment_kind", "status_label", "description"]
        result_fields = [
            "curve", "source_type", "torus_status", "p", "q", "pq", "target_pq_plus_1_abs",
            "epsilon_SE", "sigma", "model_id", "chi", "local_turns", "attachment_turns", "total_turns",
            "residual_to_chi", "charge_leak_turns", "decoherence_residual", "allowed_n", "selected_n_core",
            "min_energy", "sl_phys_abs", "exact_holonomy_chi", "integer_selection_chi", "exact_pq_plus_1",
            "charge_safe", "audit_status",
        ]
        scan_fields = ["curve", "q", "pq", "holonomy_turns", "selected_odd_FR", "selected_no_parity", "odd_selects_plus_one"]
        write_csv(out_prefix.with_name(out_prefix.name + "_models.csv"), model_rows, model_fields)
        write_csv(out_prefix.with_name(out_prefix.name + "_results.csv"), result_rows, result_fields)
        write_csv(out_prefix.with_name(out_prefix.name + "_phase_scan.csv"), phase_scan_rows, scan_fields)
        summary_path = out_prefix.with_name(out_prefix.name + "_summary.md")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(summary, encoding="utf-8")
        print(f"[write] {summary_path}")
        print("[done]")
        return 0
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        log_f.close()


if __name__ == "__main__":
    raise SystemExit(main())
