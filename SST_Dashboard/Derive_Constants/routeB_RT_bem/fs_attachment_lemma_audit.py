#!/usr/bin/env python3
r"""
fs_attachment_lemma_audit.py
============================

Attachment-Lemma audit for the SST core-twist program.

Purpose
-------
This is an AUDIT runner, not a proof machine.  It tests whether a proposed
U(1)-connection / core-holonomy model can turn the local canonical core cycle

    Omega_core*T_core = 2*pi

into a GLOBAL closed-knot framing holonomy

    Hol(A_core)/(2*pi) = chi = +/-1.

It deliberately separates the following claims:

  [DERIVED GEOMETRY]
      Canonical torus-surface framing gives |SL_torus(T(p,q))| = p*q.

  [FR-GATE / CONDITIONAL]
      If core-frame winding realizes the non-trivial Finkelstein--Rubinstein
      loop of the neutral spinon/Hopfion sector, n_core is odd.

  [KINEMATIC IDENTITY]
      Omega_core*T_core = 2*pi by the SST definitions
      Omega_core = ||v_swirl||/r_c and T_core = 2*pi*r_c/||v_swirl||.

  [ATTACHMENT / OPEN]
      The local core cycle must attach globally as the physical ribbon/frame
      holonomy of the closed knot.  This is the load-bearing open lemma.

  [ENERGY / CONDITIONAL]
      Given global attachment and positive twist stiffness C_T > 0,
      E_twist(n) = k*(n - center)^2 selects the integer sector nearest the
      attached holonomy center.  In the odd FR sector, center=chi selects
      n_core=chi.

Inputs
------
The script can either:

  1. read a prior v2 geometry audit CSV, e.g. core_holonomy_v2_results.csv,
     and build attachment rows from its curves; or
  2. fall back to analytic T(p,q) rows from --q-list, without redoing Gauss
     linking integration.

This script is intentionally a connection/holonomy-model audit; it does not
redo the heavy source-curve geometry.  Use fs_core_twist_audit_v2.py first if
you need a fresh target-free torus-framing check.

Default run
-----------
    python fs_attachment_lemma_audit.py --input-results core_holonomy_v2_results.csv

Fallback analytic run
---------------------
    python fs_attachment_lemma_audit.py --q-list 3,5,7,9,11

Outputs
-------
    attachment_lemma_audit_models.csv
    attachment_lemma_audit_results.csv
    attachment_lemma_audit_summary.md
    attachment_lemma_lock_scan.csv
    fs_attachment_lemma_audit_outputlog.txt

Dependencies: Python stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

TAU = 2.0 * math.pi

# Canon constants used in the current SST audit line.
DEFAULT_V_SWIRL = 1.09384563e6       # m/s
DEFAULT_R_C = 1.40897017e-15         # m


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Data models
# -----------------------------------------------------------------------------

@dataclass
class GeometryRow:
    label: str
    source_type: str
    family: str
    p: Optional[int]
    q: Optional[int]
    expected_pq: Optional[int]
    torus_status: str
    torus_sl_abs: Optional[float]
    torus_sl_round: Optional[int]
    notes: str = ""

    @property
    def is_torus_target(self) -> bool:
        return self.family == "torus" and self.expected_pq is not None

    @property
    def is_canonical_geometry(self) -> bool:
        return self.is_torus_target and self.torus_status == "PASS_DERIVED_PQ"


@dataclass
class ConnectionModel:
    model_id: str
    description: str
    parity: str                    # none | odd | even
    connection: str                # none | fr_only | canon_core_cycle | passive_transit | q_dependent_lock | noisy_lock
    attachment: str                # none | local_only | global | passive_transit
    chirality: str                 # unsigned | matter | antimatter
    center_kind: str               # none | zero | chi | passive | q_dependent | noisy
    epistemic_status: str


@dataclass
class SelectionResult:
    selected: List[int]
    min_energy: Optional[float]
    center: Optional[float]
    allowed: List[int]


# -----------------------------------------------------------------------------
# Small utilities
# -----------------------------------------------------------------------------

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


def sign_chi(chirality: str) -> Optional[int]:
    if chirality == "matter":
        return +1
    if chirality in ("antimatter", "anti"):
        return -1
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


def select_n(center: Optional[float], parity: str, n_min: int, n_max: int, k_twist: float = 1.0, tol: float = 1e-12) -> SelectionResult:
    allowed = allowed_ns(parity, n_min, n_max)
    if center is None or not allowed:
        return SelectionResult([], None, center, allowed)
    energies = [(n, k_twist * (n - center) ** 2) for n in allowed]
    e_min = min(e for _, e in energies)
    selected = [n for n, e in energies if abs(e - e_min) <= tol]
    return SelectionResult(selected, e_min, center, allowed)


def abs_phys_sl(row: GeometryRow, n_core: Optional[int], convention: str = "absolute") -> Optional[int]:
    """Return absolute reported |SL_phys| for the audit rows.

    The audit reports absolute lepton-ladder values.  For canonical torus target
    rows this is expected_pq + |n_core| under co-oriented signed convention.
    For non-canonical source diagnostics, use rounded fitted |SL_torus| when
    available, but mark the row separately by torus_status.
    """
    if n_core is None:
        return None
    base: Optional[int]
    if row.expected_pq is not None and row.torus_status == "PASS_DERIVED_PQ":
        base = row.expected_pq
    elif row.torus_sl_round is not None:
        base = abs(row.torus_sl_round)
    elif row.expected_pq is not None:
        base = row.expected_pq
    else:
        return None
    return int(base + abs(n_core))


def conditional_target_abs(row: GeometryRow) -> Optional[int]:
    if row.expected_pq is None:
        return None
    return row.expected_pq + 1


# -----------------------------------------------------------------------------
# Geometry input
# -----------------------------------------------------------------------------

def read_geometry_results(path: Path, torus_only: bool = True) -> List[GeometryRow]:
    rows: List[GeometryRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for raw in r:
            family = raw.get("family", "").strip() or "unknown"
            if torus_only and family != "torus":
                continue
            label = raw.get("label", "").strip() or raw.get("canonical_label", "curve")
            row = GeometryRow(
                label=label,
                source_type=raw.get("source_type", "csv").strip() or "csv",
                family=family,
                p=parse_int_or_none(raw.get("p")),
                q=parse_int_or_none(raw.get("q")),
                expected_pq=parse_int_or_none(raw.get("expected_pq")),
                torus_status=raw.get("torus_status", "UNKNOWN").strip() or "UNKNOWN",
                torus_sl_abs=parse_float_or_none(raw.get("torus_SL_abs")),
                torus_sl_round=parse_int_or_none(raw.get("torus_SL_round")),
                notes=raw.get("notes", ""),
            )
            rows.append(row)
    return rows


def analytic_geometry_rows(p: int, q_list: Sequence[int], extra_torus: Sequence[Tuple[int, int]]) -> List[GeometryRow]:
    rows: List[GeometryRow] = []
    for q in q_list:
        pq = p * q
        rows.append(GeometryRow(
            label=f"analytic:T({p},{q})",
            source_type="analytic",
            family="torus",
            p=p,
            q=q,
            expected_pq=pq,
            torus_status="PASS_DERIVED_PQ_ANALYTIC_ASSUMED",
            torus_sl_abs=float(pq),
            torus_sl_round=pq,
            notes="fallback analytic row; assumes canonical torus-surface theorem rather than recomputing linking",
        ))
    for pp, qq in extra_torus:
        pq = pp * qq
        rows.append(GeometryRow(
            label=f"analytic:T({pp},{qq})",
            source_type="analytic",
            family="torus",
            p=pp,
            q=qq,
            expected_pq=pq,
            torus_status="PASS_DERIVED_PQ_ANALYTIC_ASSUMED",
            torus_sl_abs=float(pq),
            torus_sl_round=pq,
            notes="extra analytic control row; assumes canonical torus-surface theorem",
        ))
    return rows


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
            raise ValueError(f"cannot parse extra torus spec '{part}', use '3:2,3:4'")
        out.append((int(a), int(b)))
    return out


# -----------------------------------------------------------------------------
# Connection models
# -----------------------------------------------------------------------------

def default_models() -> List[ConnectionModel]:
    return [
        ConnectionModel(
            model_id="A0_FREE_NONE",
            description="Free frame: no FR parity and no holonomy attachment; default integer twist is 0.",
            parity="none",
            connection="none",
            attachment="none",
            chirality="unsigned",
            center_kind="zero",
            epistemic_status="FREE_FRAME_NO_ATTACHMENT",
        ),
        ConnectionModel(
            model_id="A1_FR_ONLY",
            description="FR parity only: n_core restricted to odd integers, no sign/holonomy center; lowest odd pair is ±1.",
            parity="odd",
            connection="fr_only",
            attachment="none",
            chirality="unsigned",
            center_kind="zero",
            epistemic_status="FR_PARITY_ONLY_LOWEST_ODD",
        ),
        ConnectionModel(
            model_id="A2_CANON_CYCLE_LOCAL_ONLY",
            description="Canonical core cycle Omega*T=2π exists locally but is not globally attached; no n_core theorem.",
            parity="none",
            connection="canon_core_cycle",
            attachment="local_only",
            chirality="unsigned",
            center_kind="none",
            epistemic_status="LOCAL_IDENTITY_ONLY_ATTACHMENT_REQUIRED",
        ),
        ConnectionModel(
            model_id="A3_CANON_ATTACHED_MATTER",
            description="FR odd + global core-cycle attachment + matter chirality; center=+1.",
            parity="odd",
            connection="canon_core_cycle",
            attachment="global",
            chirality="matter",
            center_kind="chi",
            epistemic_status="ATTACHED_MATTER_CONDITIONAL",
        ),
        ConnectionModel(
            model_id="A4_CANON_ATTACHED_ANTIMATTER",
            description="FR odd + global core-cycle attachment + antimatter chirality; center=-1.",
            parity="odd",
            connection="canon_core_cycle",
            attachment="global",
            chirality="antimatter",
            center_kind="chi",
            epistemic_status="ATTACHED_ANTIMATTER_CONDITIONAL",
        ),
        ConnectionModel(
            model_id="A5_PASSIVE_TRANSIT_NONE",
            description="Passive transit model with non-integer holonomy center; audit should not produce pq+1 exactly.",
            parity="none",
            connection="passive_transit",
            attachment="passive_transit",
            chirality="unsigned",
            center_kind="passive",
            epistemic_status="PASSIVE_ADVECTION_FAILS",
        ),
        ConnectionModel(
            model_id="A6_PASSIVE_TRANSIT_FR_ODD",
            description="Passive transit plus FR odd restriction; still selects the nearest odd integer, typically 3, not 1.",
            parity="odd",
            connection="passive_transit",
            attachment="passive_transit",
            chirality="unsigned",
            center_kind="passive",
            epistemic_status="PASSIVE_ADVECTION_FAILS_EVEN_WITH_FR",
        ),
        ConnectionModel(
            model_id="A7_Q_DEPENDENT_LOCK_MATTER",
            description="Perturbed phase-lock: center=1+slope*(q-q_ref); tests whether exact q-independent attachment is required.",
            parity="odd",
            connection="q_dependent_lock",
            attachment="global",
            chirality="matter",
            center_kind="q_dependent",
            epistemic_status="Q_DEPENDENT_LOCK_DIAGNOSTIC",
        ),
        ConnectionModel(
            model_id="A8_NOISY_LOCK_MATTER",
            description="Deterministic noise-like perturbation around center=+1; tests stability margin but not exact Canon derivation.",
            parity="odd",
            connection="noisy_lock",
            attachment="global",
            chirality="matter",
            center_kind="noisy",
            epistemic_status="NOISY_LOCK_STABILITY_DIAGNOSTIC",
        ),
    ]


def center_for_model(model: ConnectionModel, row: GeometryRow, args) -> Optional[float]:
    if model.center_kind == "none":
        return None
    if model.center_kind == "zero":
        return 0.0
    if model.center_kind == "chi":
        chi = sign_chi(model.chirality)
        if chi is None:
            return None
        return float(chi)
    if model.center_kind == "passive":
        return float(args.passive_turns)
    if model.center_kind == "q_dependent":
        q = row.q if row.q is not None else args.q_ref
        return 1.0 + args.q_slope * (float(q) - float(args.q_ref))
    if model.center_kind == "noisy":
        # Deterministic pseudo-noise based on p,q; no RNG dependence.
        q = row.q if row.q is not None else args.q_ref
        p = row.p if row.p is not None else args.p
        phase = math.sin(12.9898 * p + 78.233 * q) * 43758.5453
        frac = phase - math.floor(phase)
        eps = args.noise_amp * (2.0 * frac - 1.0)
        return 1.0 + eps
    raise ValueError(f"unknown center kind: {model.center_kind}")


def candidate_flag(model: ConnectionModel, selected: SelectionResult, row: GeometryRow) -> str:
    if model.model_id == "A3_CANON_ATTACHED_MATTER":
        if selected.selected == [1] and row.expected_pq is not None:
            return "CONDITIONAL_CANON_CANDIDATE"
    if model.model_id == "A4_CANON_ATTACHED_ANTIMATTER":
        if selected.selected == [-1] and row.expected_pq is not None:
            return "CONDITIONAL_MIRROR_SECTOR"
    if model.model_id.startswith("A5") or model.model_id.startswith("A6"):
        return "PASSIVE_ADVECTION_FAILS"
    if model.model_id == "A2_CANON_CYCLE_LOCAL_ONLY":
        return "ATTACHMENT_REQUIRED"
    if model.model_id == "A1_FR_ONLY":
        return "FR_ODD_SELECTED_NO_SIGN"
    if model.model_id == "A0_FREE_NONE":
        return "BOSONIC_DEFAULT"
    if model.model_id.startswith("A7"):
        return "Q_DEPENDENT_DIAGNOSTIC"
    if model.model_id.startswith("A8"):
        return "NOISY_STABILITY_DIAGNOSTIC"
    return model.epistemic_status


# -----------------------------------------------------------------------------
# Output helpers
# -----------------------------------------------------------------------------

def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print(f"[write] {path}")


def md_table(rows: List[Dict[str, object]], fieldnames: Sequence[str], max_rows: Optional[int] = None) -> str:
    data = rows if max_rows is None else rows[:max_rows]
    lines = []
    lines.append("| " + " | ".join(fieldnames) + " |")
    lines.append("|" + "|".join(["---"] * len(fieldnames)) + "|")
    for row in data:
        vals = []
        for fn in fieldnames:
            v = row.get(fn, "")
            vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    if max_rows is not None and len(rows) > max_rows:
        lines.append(f"\n... {len(rows)-max_rows} additional rows omitted from markdown preview. See CSV for full table.\n")
    return "\n".join(lines)


def count_by(rows: Iterable[Dict[str, object]], key: str) -> Dict[str, int]:
    d: Dict[str, int] = {}
    for row in rows:
        k = str(row.get(key, ""))
        d[k] = d.get(k, 0) + 1
    return d


# -----------------------------------------------------------------------------
# Main audit
# -----------------------------------------------------------------------------

def run_attachment_audit(args) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]], str]:
    # Canon constants.
    omega_core = args.v_swirl / args.r_c
    t_core = TAU * args.r_c / args.v_swirl
    core_turns = omega_core * t_core / TAU
    vorticity_turns = (2.0 * omega_core) * t_core / TAU

    # Geometry rows.
    geometry_rows: List[GeometryRow]
    input_results = Path(args.input_results) if args.input_results else None
    if input_results and input_results.exists():
        geometry_rows = read_geometry_results(input_results, torus_only=not args.include_controls)
        print(f"[input] read geometry rows from {input_results}: {len(geometry_rows)}")
    else:
        if input_results:
            print(f"[warn] --input-results not found: {input_results}; falling back to analytic rows")
        q_list = [int(x.strip()) for x in args.q_list.split(",") if x.strip()]
        extra_torus = parse_extra_torus(args.extra_torus)
        geometry_rows = analytic_geometry_rows(args.p, q_list, extra_torus)
        print(f"[input] fallback analytic rows: {len(geometry_rows)}")

    if args.canonical_only:
        before = len(geometry_rows)
        geometry_rows = [r for r in geometry_rows if r.torus_status in ("PASS_DERIVED_PQ", "PASS_DERIVED_PQ_ANALYTIC_ASSUMED")]
        print(f"[filter] canonical-only retained {len(geometry_rows)} / {before}")

    models = default_models()
    if not args.include_perturbation_models:
        models = [m for m in models if not (m.model_id.startswith("A7") or m.model_id.startswith("A8"))]

    model_rows: List[Dict[str, object]] = []
    for m in models:
        model_rows.append({
            "model_id": m.model_id,
            "parity": m.parity,
            "connection": m.connection,
            "attachment": m.attachment,
            "chirality": m.chirality,
            "center_kind": m.center_kind,
            "epistemic_status": m.epistemic_status,
            "description": m.description,
        })

    result_rows: List[Dict[str, object]] = []
    lock_scan_rows: List[Dict[str, object]] = []

    for row in geometry_rows:
        target_abs = conditional_target_abs(row)
        for m in models:
            center = center_for_model(m, row, args)
            sel = select_n(center, m.parity, args.n_min, args.n_max, k_twist=args.k_twist, tol=args.degeneracy_tol)
            selected_str = ",".join(str(n) for n in sel.selected)
            selected_primary: Optional[int] = None
            if len(sel.selected) == 1:
                selected_primary = sel.selected[0]

            # If there is degeneracy, report all |SL| values.
            sl_abs_values: List[str] = []
            for n in sel.selected:
                v = abs_phys_sl(row, n)
                if v is not None:
                    sl_abs_values.append(str(v))
            sl_abs_str = ",".join(sl_abs_values)

            exact_pq_plus_1 = ""
            if target_abs is not None and sl_abs_values:
                exact_pq_plus_1 = "YES" if any(int(v) == int(target_abs) for v in sl_abs_values) else "NO"

            # Attachment theorem conditions.
            fr_gate = (m.parity == "odd")
            local_identity = (m.connection == "canon_core_cycle")
            global_attachment = (m.attachment == "global")
            energy_gate = args.k_twist > 0 and bool(sel.selected)
            load_bearing_open = "YES" if local_identity and not global_attachment else ""

            candidate = candidate_flag(m, sel, row)
            if row.torus_status not in ("PASS_DERIVED_PQ", "PASS_DERIVED_PQ_ANALYTIC_ASSUMED"):
                geometry_quality = "DIAGNOSTIC_SOURCE_NOT_CANONICAL"
            else:
                geometry_quality = "CANONICAL_GEOMETRY"

            result_rows.append({
                "curve": row.label,
                "source_type": row.source_type,
                "geometry_quality": geometry_quality,
                "torus_status": row.torus_status,
                "p": row.p if row.p is not None else "",
                "q": row.q if row.q is not None else "",
                "pq": row.expected_pq if row.expected_pq is not None else "",
                "target_pq_plus_1_abs": target_abs if target_abs is not None else "",
                "model_id": m.model_id,
                "parity": m.parity,
                "connection": m.connection,
                "attachment": m.attachment,
                "chirality": m.chirality,
                "center_turns": "" if center is None else f"{center:.12g}",
                "allowed_n": ",".join(str(n) for n in sel.allowed),
                "selected_n_core": selected_str,
                "min_energy": "" if sel.min_energy is None else f"{sel.min_energy:.12g}",
                "sl_phys_abs": sl_abs_str,
                "exact_pq_plus_1": exact_pq_plus_1,
                "fr_gate": "PASS" if fr_gate else "OFF",
                "local_identity": "YES" if local_identity else "NO",
                "global_attachment": "YES" if global_attachment else "NO",
                "energy_gate_ct_positive": "PASS" if energy_gate else "FAIL",
                "attachment_open_load_bearing": load_bearing_open,
                "status": candidate,
            })

        # Lock scan: what happens if the holonomy center is r in an interval?
        if row.expected_pq is not None:
            for r in [args.scan_min + i * args.scan_step for i in range(int(round((args.scan_max - args.scan_min) / args.scan_step)) + 1)]:
                sel_odd = select_n(r, "odd", args.n_min, args.n_max, args.k_twist, args.degeneracy_tol)
                sel_none = select_n(r, "none", args.n_min, args.n_max, args.k_twist, args.degeneracy_tol)
                odd_ns = ",".join(str(n) for n in sel_odd.selected)
                none_ns = ",".join(str(n) for n in sel_none.selected)
                exact_one = "YES" if sel_odd.selected == [1] else "NO"
                lock_scan_rows.append({
                    "curve": row.label,
                    "q": row.q if row.q is not None else "",
                    "pq": row.expected_pq,
                    "holonomy_turns_r": f"{r:.6g}",
                    "selected_n_odd_FR": odd_ns,
                    "selected_n_no_parity": none_ns,
                    "odd_selects_plus_one": exact_one,
                    "sl_abs_if_odd": ",".join(str(abs_phys_sl(row, n)) for n in sel_odd.selected if abs_phys_sl(row, n) is not None),
                })

    # Compose summary.
    counts_status = count_by(result_rows, "status")
    counts_model = count_by(result_rows, "model_id")
    counts_geom = count_by(result_rows, "geometry_quality")

    summary_lines: List[str] = []
    summary_lines.append("# Attachment Lemma audit summary")
    summary_lines.append("")
    summary_lines.append("## Purpose")
    summary_lines.append("")
    summary_lines.append("This audit asks whether a local SST core cycle can be promoted to a global closed-knot framing holonomy.")
    summary_lines.append("")
    summary_lines.append("```text")
    summary_lines.append("[TARGET]  Hol(A_core)/(2π) = chi = ±1")
    summary_lines.append("[OPEN]    The equality between local core period and global ribbon holonomy is the Attachment Lemma.")
    summary_lines.append("```")
    summary_lines.append("")
    summary_lines.append("## Canonical core constants")
    summary_lines.append("")
    summary_lines.append("| quantity | value |")
    summary_lines.append("|---|---:|")
    summary_lines.append(f"| `||v_swirl||` | {args.v_swirl:.12e} m/s |")
    summary_lines.append(f"| `r_c` | {args.r_c:.12e} m |")
    summary_lines.append(f"| `Omega_core = ||v_swirl||/r_c` | {omega_core:.12e} s^-1 |")
    summary_lines.append(f"| `T_core = 2π r_c/||v_swirl||` | {t_core:.12e} s |")
    summary_lines.append(f"| `Omega_core*T_core/(2π)` | {core_turns:.12f} turns |")
    summary_lines.append(f"| `omega_vorticity*T_core/(2π)` | {vorticity_turns:.12f} vorticity-turns |")
    summary_lines.append("")
    summary_lines.append("The framing angle integrates angular velocity, not vorticity: `dtheta_frame = Omega_core dt = 0.5 omega_core dt`.")
    summary_lines.append("")
    summary_lines.append("## Proof-stack status")
    summary_lines.append("")
    summary_lines.append("```text")
    summary_lines.append("[DERIVED]              Canonical torus-surface framing: |SL_torus(T(p,q))| = p q.")
    summary_lines.append("[FR-GATE / CONDITIONAL] Core-frame winding must represent the nontrivial FR loop to force odd n_core.")
    summary_lines.append("[KINEMATIC IDENTITY]   Omega_core*T_core = 2π locally.")
    summary_lines.append("[ATTACHMENT / OPEN]    Local core cycle must attach globally as framed-knot holonomy.")
    summary_lines.append("[ENERGY / CONDITIONAL] Given global attachment and C_T>0, n_core=chi is selected.")
    summary_lines.append("[CONDITIONAL]          SL_phys(T(p,q)) = SL_torus(T(p,q)) + chi.")
    summary_lines.append("```")
    summary_lines.append("")
    summary_lines.append("## Row counts")
    summary_lines.append("")
    summary_lines.append(f"Geometry rows: **{len(geometry_rows)}**")
    summary_lines.append(f"Attachment result rows: **{len(result_rows)}**")
    summary_lines.append(f"Model counts: `{counts_model}`")
    summary_lines.append(f"Status counts: `{counts_status}`")
    summary_lines.append(f"Geometry-quality counts: `{counts_geom}`")
    summary_lines.append("")
    summary_lines.append("## Model catalogue")
    summary_lines.append("")
    summary_lines.append(md_table(model_rows, ["model_id", "parity", "connection", "attachment", "chirality", "center_kind", "epistemic_status"], max_rows=None))
    summary_lines.append("")
    summary_lines.append("## Preview: canonical analytic/torus rows")
    summary_lines.append("")
    preview = [r for r in result_rows if str(r["curve"]).startswith("analytic:T(2,") and r["model_id"] in ("A0_FREE_NONE", "A1_FR_ONLY", "A2_CANON_CYCLE_LOCAL_ONLY", "A3_CANON_ATTACHED_MATTER", "A4_CANON_ATTACHED_ANTIMATTER", "A5_PASSIVE_TRANSIT_NONE")]
    if not preview:
        preview = result_rows[:36]
    summary_lines.append(md_table(preview, ["curve", "model_id", "center_turns", "selected_n_core", "sl_phys_abs", "exact_pq_plus_1", "status"], max_rows=36))
    summary_lines.append("")
    summary_lines.append("## Interpretation")
    summary_lines.append("")
    summary_lines.append("```text")
    summary_lines.append("A0_FREE_NONE: no FR and no attachment -> n_core=0, default/bosonic sector.")
    summary_lines.append("A1_FR_ONLY: FR odd parity -> n_core=±1, but no matter/antimatter sign or global holonomy theorem.")
    summary_lines.append("A2_CANON_CYCLE_LOCAL_ONLY: Omega*T=2π is local only; attachment is still required.")
    summary_lines.append("A3_CANON_ATTACHED_MATTER: FR + attachment + C_T>0 + chi=+1 -> n_core=+1.")
    summary_lines.append("A4_CANON_ATTACHED_ANTIMATTER: FR + attachment + C_T>0 + chi=-1 -> n_core=-1.")
    summary_lines.append("A5/A6_PASSIVE_TRANSIT: passive non-integer transit selects the wrong integer sector; it is not the pq+1 mechanism.")
    summary_lines.append("A7/A8 perturbation models, when enabled, are stability diagnostics only; exact Canon requires r(q)=chi, not merely near chi.")
    summary_lines.append("```")
    summary_lines.append("")
    summary_lines.append("## Audit conclusion")
    summary_lines.append("")
    summary_lines.append("The Attachment Lemma remains the load-bearing open step.  The candidate mechanism is not 'more pq+1 fitting'; it is the construction of a physical U(1) core-phase connection whose closed-knot holonomy is exactly `2π chi`.")

    return model_rows, result_rows, lock_scan_rows, geometry_rows_to_dicts(geometry_rows), "\n".join(summary_lines) + "\n"


def geometry_rows_to_dicts(rows: List[GeometryRow]) -> List[Dict[str, object]]:
    return [{
        "label": r.label,
        "source_type": r.source_type,
        "family": r.family,
        "p": r.p if r.p is not None else "",
        "q": r.q if r.q is not None else "",
        "expected_pq": r.expected_pq if r.expected_pq is not None else "",
        "torus_status": r.torus_status,
        "torus_sl_abs": "" if r.torus_sl_abs is None else f"{r.torus_sl_abs:.12g}",
        "torus_sl_round": "" if r.torus_sl_round is None else r.torus_sl_round,
        "notes": r.notes,
    } for r in rows]


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Audit Core-Cycle Attachment Lemma models for SST core twist.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--input-results", default="core_holonomy_v2_results.csv", help="Prior fs_core_twist_audit_v2 results CSV. If absent, use analytic fallback rows.")
    p.add_argument("--out-prefix", default="attachment_lemma_audit", help="Prefix for output files.")
    p.add_argument("--q-list", default="3,5,7,9,11", help="Fallback analytic q-list for T(p,q).")
    p.add_argument("--p", type=int, default=2, help="Fallback analytic torus p.")
    p.add_argument("--extra-torus", default="3:2,3:4", help="Fallback analytic controls, e.g. 3:2,3:4.")
    p.add_argument("--include-controls", action="store_true", help="Include non-torus controls from input CSV if present.")
    p.add_argument("--canonical-only", action="store_true", help="Keep only PASS_DERIVED_PQ rows from input geometry.")
    p.add_argument("--include-perturbation-models", action="store_true", help="Include A7 q-dependent and A8 noisy-lock diagnostics.")

    p.add_argument("--v-swirl", type=float, default=DEFAULT_V_SWIRL, help="Canonical swirl speed norm in m/s.")
    p.add_argument("--r-c", type=float, default=DEFAULT_R_C, help="Canonical core radius in m.")
    p.add_argument("--passive-turns", type=float, default=2.501, help="Passive transit holonomy center in turns for failure diagnostic.")
    p.add_argument("--k-twist", type=float, default=1.0, help="Positive twist stiffness scale used for dimensionless energy ranking.")
    p.add_argument("--n-min", type=int, default=-5, help="Minimum integer n_core to scan.")
    p.add_argument("--n-max", type=int, default=5, help="Maximum integer n_core to scan.")
    p.add_argument("--degeneracy-tol", type=float, default=1e-12, help="Tolerance for reporting degenerate minima.")

    p.add_argument("--q-ref", type=float, default=3.0, help="Reference q for q-dependent perturbation model.")
    p.add_argument("--q-slope", type=float, default=0.02, help="Slope for q-dependent diagnostic center=1+slope*(q-q_ref).")
    p.add_argument("--noise-amp", type=float, default=0.1, help="Amplitude for deterministic noisy-lock diagnostic.")

    p.add_argument("--scan-min", type=float, default=-0.5, help="Minimum holonomy-turn center for lock scan.")
    p.add_argument("--scan-max", type=float, default=3.5, help="Maximum holonomy-turn center for lock scan.")
    p.add_argument("--scan-step", type=float, default=0.25, help="Step for lock scan.")
    p.add_argument("--log-file", default="fs_attachment_lemma_audit_outputlog.txt", help="Console log path.")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.k_twist <= 0:
        raise SystemExit("--k-twist must be positive for the Energy Gate audit")
    if args.n_min > args.n_max:
        raise SystemExit("--n-min must be <= --n-max")
    if args.scan_step <= 0:
        raise SystemExit("--scan-step must be positive")

    out_prefix = Path(args.out_prefix)
    log_path = Path(args.log_file)
    if not log_path.is_absolute():
        log_path = out_prefix.parent / log_path

    log_f, old_stdout, old_stderr = install_tee(log_path)
    try:
        print(f"[config] input_results={args.input_results}")
        print(f"[config] out_prefix={args.out_prefix}")
        print(f"[config] n_range={args.n_min}:{args.n_max}, passive_turns={args.passive_turns}")
        print(f"[scope] Attachment Lemma audit: U(1) connection holonomy -> n_core selection")

        model_rows, result_rows, lock_scan_rows, geometry_rows, summary = run_attachment_audit(args)

        model_fields = ["model_id", "parity", "connection", "attachment", "chirality", "center_kind", "epistemic_status", "description"]
        result_fields = [
            "curve", "source_type", "geometry_quality", "torus_status", "p", "q", "pq", "target_pq_plus_1_abs",
            "model_id", "parity", "connection", "attachment", "chirality", "center_turns", "allowed_n", "selected_n_core",
            "min_energy", "sl_phys_abs", "exact_pq_plus_1", "fr_gate", "local_identity", "global_attachment",
            "energy_gate_ct_positive", "attachment_open_load_bearing", "status",
        ]
        scan_fields = ["curve", "q", "pq", "holonomy_turns_r", "selected_n_odd_FR", "selected_n_no_parity", "odd_selects_plus_one", "sl_abs_if_odd"]
        geom_fields = ["label", "source_type", "family", "p", "q", "expected_pq", "torus_status", "torus_sl_abs", "torus_sl_round", "notes"]

        write_csv(out_prefix.with_name(out_prefix.name + "_models.csv"), model_rows, model_fields)
        write_csv(out_prefix.with_name(out_prefix.name + "_results.csv"), result_rows, result_fields)
        write_csv(out_prefix.with_name(out_prefix.name + "_lock_scan.csv"), lock_scan_rows, scan_fields)
        write_csv(out_prefix.with_name(out_prefix.name + "_geometry_rows.csv"), geometry_rows, geom_fields)

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
