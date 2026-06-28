#!/usr/bin/env python3
r"""
fs_core_holonomy_audit.py
=========================

Audit runner for the *single remaining* SST torus-ladder question:

    n_core = (1/2π) ∮_K dθ_core  ?=  1

This script deliberately does NOT prove pq+1 by injecting pq+1.  It consumes the
non-circular torus-framing audit from ``fs_core_twist_audit.py``:

    |SL_torus(T(p,q))| = p q

and then asks which independent core-holonomy models select the required
integer core winding

    n_required = (p q + 1) - |round(SL_torus)|.

For clean canonical torus-framing rows, n_required should be 1.  The script then
compares models for the background/core holonomy Φ_bg:

    E_core(n; Φ_bg) = K (2π n - Φ_bg)^2 + λ_abs n^2 + E_parity(n)

where n is an integer.  If a model selects n=1, the output states whether that
is a hypothesis/input or a consequence of the specified assumptions.

Why this exists
---------------
Earlier framed-helicity tests could always manufacture any target integer by
setting extra twists equal to target - Lk0.  That confirms Călugăreanu
(Lk=Wr+Tw), not pq+1.  This audit instead treats +1 as the only open physical
claim and makes all assumptions explicit.

Required companion file
-----------------------
Place this script in the same directory as:

    fs_core_twist_audit.py

The companion supplies parsers and the target-free torus-framing computation.

Example runs
------------

    python fs_core_holonomy_audit.py --q-list 3,5,7,9,11 --samples 1024

    python fs_core_holonomy_audit.py --models zero,unit,twoomega_cycle,twoomega_transit \
        --q-list 3,5,7,9,11 --samples 2048

Outputs
-------

    core_holonomy_audit_results.csv
    core_holonomy_energy_landscape.csv
    core_holonomy_audit_summary.md
    fs_core_holonomy_audit_outputlog.txt

Dependencies: numpy and fs_core_twist_audit.py.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

TAU = 2.0 * math.pi

# Canon/user constants used only for optional physical clock estimates.
R_C = 1.40897017e-15                      # m
V_SWIRL = 1.09384563e6                    # m/s
C_LIGHT = 2.99792458e8                    # m/s
OMEGA_CORE_DEFAULT = V_SWIRL / R_C        # rad/s, Ω_core such that v=Ω r_c


# -----------------------------------------------------------------------------
# Import companion audit code
# -----------------------------------------------------------------------------

try:
    import fs_core_twist_audit as cta
except Exception as exc:  # pragma: no cover
    print("[ERROR] Could not import fs_core_twist_audit.py")
    print("Place fs_core_holonomy_audit.py in the same folder as fs_core_twist_audit.py.")
    print(f"Original import error: {exc}")
    raise


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()

    def flush(self):
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
# Utility
# -----------------------------------------------------------------------------

def parse_q_list(s: str) -> List[int]:
    out: List[int] = []
    for part in str(s).split(','):
        part = part.strip()
        if not part:
            continue
        out.append(int(part))
    return out


def parse_models(s: str) -> List[str]:
    if str(s).lower().strip() == "all":
        return ["zero", "unit", "signed_unit", "twoomega_cycle", "twoomega_transit", "background"]
    out = []
    for part in str(s).split(','):
        part = part.strip().lower()
        if part:
            out.append(part)
    valid = {"zero", "unit", "signed_unit", "twoomega_cycle", "twoomega_transit", "background"}
    bad = [m for m in out if m not in valid]
    if bad:
        raise ValueError(f"unknown model(s): {bad}; valid={sorted(valid)}")
    return out


def parse_int_range(s: str) -> List[int]:
    s = str(s).strip()
    if ':' in s:
        a, b = [int(x.strip()) for x in s.split(':', 1)]
        step = 1 if b >= a else -1
        return list(range(a, b + step, step))
    return [int(x.strip()) for x in s.split(',') if x.strip()]


def fmt(x, nd=6) -> str:
    if x is None:
        return ""
    if isinstance(x, (float, np.floating)):
        return f"{float(x):.{nd}g}"
    return str(x)


def sgn(x: float) -> int:
    return 1 if float(x) >= 0.0 else -1


def polygon_length(curve: np.ndarray) -> float:
    d = np.roll(curve, -1, axis=0) - curve
    return float(np.sum(np.linalg.norm(d, axis=1)))


def curve_for_entry(entry: "cta.CurveEntry", samples: int, torus_R: float, torus_r: float) -> Optional[np.ndarray]:
    """Return the same normalized centerline class used by the companion, for diagnostics."""
    try:
        if entry.source_type == "analytic":
            if entry.q is None:
                return None
            curve, _ = cta.analytic_torus_knot(int(entry.p), int(entry.q), samples, R=torus_R, r=torus_r)
            return curve
        if entry.coeffs is not None and entry.coeff_indices is not None:
            raw = cta.eval_fourier_curve(entry.coeffs, entry.coeff_indices, samples)
            return cta.normalize_curve(raw)
    except Exception:
        return None
    return None


def build_companion_args(args: argparse.Namespace) -> SimpleNamespace:
    """Create an args namespace sufficient for cta.analyze_entry."""
    return SimpleNamespace(
        samples=args.samples,
        chunk=args.chunk,
        ribbon_eps_frac=args.ribbon_eps_frac,
        pq_abs_tol=args.pq_abs_tol,
        torus_R=args.torus_R,
        torus_r=args.torus_r,
        source_torus_fit=args.source_torus_fit,
        n_core_range=args.n_core_range,
        core_sign_mode=args.core_sign_mode,
        core_n0=1.0,             # companion model label only; this script does its own holonomy models
        k_core=1.0,
        k_null=1.0,
        circularity_trap=args.circularity_trap,
        trap_target=args.trap_target,
        trap_tol=args.trap_tol,
    )


# -----------------------------------------------------------------------------
# Holonomy models
# -----------------------------------------------------------------------------

@dataclass
class HolonomyModelResult:
    model: str
    phi_turns: float
    phi_rad: float
    status: str
    assumption: str


def phi_for_model(model: str, row: Dict[str, object], entry: "cta.CurveEntry", args: argparse.Namespace,
                  curve_length_dimless: Optional[float]) -> HolonomyModelResult:
    """Return Φ_bg in radians and a status label for each model."""
    # For signed SL rows, follow the measured torus orientation unless model explicitly says unsigned.
    torus_sl = row.get("torus_SL")
    chirality_sign = sgn(float(torus_sl)) if torus_sl is not None else 1

    if model == "zero":
        return HolonomyModelResult(
            model=model,
            phi_turns=0.0,
            phi_rad=0.0,
            status="NULL_BACKGROUND",
            assumption="Φ_bg=0; selects n=0 unless other terms intervene",
        )

    if model == "unit":
        return HolonomyModelResult(
            model=model,
            phi_turns=1.0,
            phi_rad=TAU,
            status="INPUT_UNIT_HOLONOMY",
            assumption="assumes one unsigned 2π core holonomy; tests consequences only",
        )

    if model == "signed_unit":
        turns = float(chirality_sign)
        return HolonomyModelResult(
            model=model,
            phi_turns=turns,
            phi_rad=TAU * turns,
            status="INPUT_SIGNED_UNIT_HOLONOMY",
            assumption="assumes one signed 2π core holonomy following torus chirality",
        )

    if model == "twoomega_cycle":
        # This is the clean closure hypothesis: Ω_core T_core = 2π.
        # Since ω_core=2Ω_core, the same condition is (1/4π)∫ω_core dt = 1.
        return HolonomyModelResult(
            model=model,
            phi_turns=1.0,
            phi_rad=TAU,
            status="CLOSURE_ASSUMPTION_SELECTS_PLUS_ONE",
            assumption="uses Ω_core T_cycle=2π (equivalently (1/4π)∫ω_core dt=1); closure assumption, not derived from curve length",
        )

    if model == "background":
        turns = float(args.phi_bg_turns)
        if args.background_sign_mode == "follow":
            turns *= chirality_sign
        return HolonomyModelResult(
            model=model,
            phi_turns=turns,
            phi_rad=TAU * turns,
            status="EXTERNAL_BACKGROUND_INPUT",
            assumption=f"uses user-specified Φ_bg/(2π)={turns:g} with sign_mode={args.background_sign_mode}",
        )

    if model == "twoomega_transit":
        # Diagnostic model: a material point traverses the centerline once.
        # This is NOT expected to be q-independent unless parameters conspire.
        # T = L_phys / v_transport, Φ=Ω_core T.
        if curve_length_dimless is None:
            return HolonomyModelResult(model, float('nan'), float('nan'), "NO_CURVE_LENGTH", "curve length unavailable")
        length_unit_m = float(args.length_unit_m)
        v_transport = float(args.v_transport)
        omega_core = float(args.omega_core)
        L_phys = curve_length_dimless * length_unit_m
        T = L_phys / max(abs(v_transport), 1e-300)
        phi = omega_core * T
        return HolonomyModelResult(
            model=model,
            phi_turns=phi / TAU,
            phi_rad=phi,
            status="DIAGNOSTIC_TRANSIT_MODEL",
            assumption=(
                f"Φ=Ω_core L/v with L_dimless={curve_length_dimless:.6g}, "
                f"length_unit={length_unit_m:.6g} m, Ω={omega_core:.6g} s^-1, v={v_transport:.6g} m/s"
            ),
        )

    raise ValueError(f"unknown model {model}")


def energy_landscape(phi_rad: float, n_values: Sequence[int], args: argparse.Namespace) -> Tuple[List[Dict[str, object]], int]:
    """Energy over integer n_core sectors."""
    rows: List[Dict[str, object]] = []
    best_n: Optional[int] = None
    best_e = float('inf')
    for n in n_values:
        # Basic holonomy spring; optional absolute winding penalty; optional odd-sector bonus.
        e_spring = float(args.k_holonomy) * (TAU * n - phi_rad) ** 2
        e_abs = float(args.k_abs) * (n ** 2)
        e_odd = -float(args.odd_bonus) if (abs(int(n)) % 2 == 1) else 0.0
        e_total = e_spring + e_abs + e_odd
        row = {
            "n_core": int(n),
            "E_spring": e_spring,
            "E_abs": e_abs,
            "E_odd_bonus": e_odd,
            "E_total": e_total,
        }
        rows.append(row)
        if e_total < best_e:
            best_e = e_total
            best_n = int(n)
    return rows, int(best_n if best_n is not None else 0)


def model_epistemic_status(model_name: str, selected_n: int, required_n: Optional[int], h: HolonomyModelResult) -> str:
    if required_n is None:
        return "NO_TORUS_REQUIREMENT"
    if selected_n != required_n:
        return "DOES_NOT_SELECT_REQUIRED_CORE_TWIST"
    if model_name in {"zero"}:
        return "UNEXPECTED_SELECTION_CHECK_INPUTS"
    if model_name in {"unit", "signed_unit", "background"}:
        return "SELECTS_REQUIRED_BY_INPUT_ASSUMPTION"
    if model_name == "twoomega_cycle":
        return "SELECTS_REQUIRED_BY_CLOSURE_ASSUMPTION"
    if model_name == "twoomega_transit":
        return "SELECTS_REQUIRED_IN_TRANSIT_MODEL"
    return "SELECTS_REQUIRED"


# -----------------------------------------------------------------------------
# Discovery/inventory
# -----------------------------------------------------------------------------

def collect_entries(args: argparse.Namespace) -> List["cta.CurveEntry"]:
    q_list = parse_q_list(args.q_list)
    qset = set(q_list)
    extra_torus = cta.parse_extra_torus(args.extra_torus)

    entries: List["cta.CurveEntry"] = []
    if args.include_analytic:
        entries.extend(cta.collect_analytic_entries(q_list, p=args.p, extra_pq=extra_torus))

    roots = cta.discover_folder_roots()
    zip_roots = cta.discover_zip_roots(Path(".fs_core_holonomy_cache"), enabled=not args.no_zip_fallback)
    all_roots = cta.unique_existing(list(roots) + list(zip_roots))
    print("[fseries] roots:")
    if all_roots:
        for r in all_roots:
            print(f"  - {r}")
    else:
        print("  - none")

    ideal_paths = cta.discover_ideal_paths()
    print("[ideal] candidate ideal.txt paths:")
    if ideal_paths:
        for pth in ideal_paths:
            print(f"  - {pth}")
    else:
        print("  - none")

    ideal_ids = {k for k, q in cta.IDEAL_ID_Q.items() if q in qset}
    if not args.no_twist_controls:
        for cid, info in cta.IDEAL_CONTROL_INFO.items():
            if int(info.get("control_for_q") or -1) in qset:
                ideal_ids.add(cid)
    for ip in ideal_paths[:1]:
        entries.extend(cta.parse_ideal_ab_blocks(
            ip,
            include_ids=None if args.include_all_ideal else ideal_ids,
            include_all_single_component=args.include_all_ideal,
            max_ideal=args.max_ideal,
        ))

    entries.extend(cta.collect_fseries_entries(
        all_roots,
        q_list=q_list,
        include_all_fseries=args.include_all_fseries,
        max_fseries=args.max_fseries,
        include_twist_controls=(not args.no_twist_controls),
    ))

    return entries


# -----------------------------------------------------------------------------
# Reporting
# -----------------------------------------------------------------------------

RESULT_FIELDS = [
    "source_type", "family", "label", "p", "q", "expected_pq", "expected_pq_plus_1",
    "torus_status", "torus_SL", "torus_SL_round", "torus_SL_abs_err_vs_pq",
    "core_required_abs_to_pq_plus_1", "curve_length_dimless",
    "model", "phi_turns", "phi_rad", "holonomy_status", "assumption",
    "n_selected", "selected_matches_required", "epistemic_status",
    "SL_phys_selected_signed", "SL_phys_selected_abs", "SL_phys_required_abs",
    "spin_half_compatible", "twoomega_integral_turns", "core_n_formula",
]

LANDSCAPE_FIELDS = [
    "label", "source_type", "p", "q", "expected_pq", "torus_SL_round",
    "model", "phi_turns", "n_core", "E_spring", "E_abs", "E_odd_bonus", "E_total",
    "selected", "matches_required",
]


def write_csv(path: Path, rows: Sequence[Dict[str, object]], fields: Sequence[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields))
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


def write_markdown(path: Path, rows: Sequence[Dict[str, object]], landscape: Sequence[Dict[str, object]], args: argparse.Namespace) -> None:
    clean = [r for r in rows if r.get("torus_status") == "PASS_DERIVED_PQ"]
    analytic = [r for r in clean if r.get("source_type") == "analytic"]
    plus = [r for r in rows if r.get("selected_matches_required") is True]
    rejects = [r for r in rows if r.get("selected_matches_required") is False and r.get("core_required_abs_to_pq_plus_1") is not None]

    by_model: Dict[str, List[Dict[str, object]]] = {}
    for r in rows:
        by_model.setdefault(str(r.get("model")), []).append(r)

    lines: List[str] = []
    lines.append("# Core-holonomy audit summary")
    lines.append("")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("```text")
    lines.append("n_core = (1/2π) ∮_K dθ_core  ?=  1")
    lines.append("SL_phys(T(p,q)) = SL_torus + n_core")
    lines.append("```")
    lines.append("")
    lines.append("The non-circular theorem checked upstream is `|SL_torus(T(p,q))| = p q`. This audit asks which physical/core-holonomy model selects the missing `+1` without injecting `pq+1` as a target.")
    lines.append("")
    lines.append(f"Curves/models analysed: **{len(rows)}** result rows; energy rows: **{len(landscape)}**.")
    lines.append(f"Models: `{args.models}`; n range: `{args.n_core_range}`; samples: **{args.samples}**.")
    lines.append("")

    lines.append("## A. Clean analytic theorem rows")
    lines.append("")
    if analytic:
        lines.append("| curve | pq | SL_torus | required n_core |")
        lines.append("|---|---:|---:|---:|")
        seen = set()
        for r in analytic:
            key = (r["label"], r["model"])
            # show only once per curve, independent of model
            if r["label"] in seen:
                continue
            seen.add(r["label"])
            lines.append(f"| `{r['label']}` | {fmt(r['expected_pq'])} | {fmt(r['torus_SL'])} | {fmt(r['core_required_abs_to_pq_plus_1'])} |")
    else:
        lines.append("No clean analytic rows found. Check `fs_core_twist_audit.py` and input settings.")
    lines.append("")

    lines.append("## B. Model selection overview")
    lines.append("")
    lines.append("| model | rows | selects required | rejects required | typical status |")
    lines.append("|---|---:|---:|---:|---|")
    for model, rs in sorted(by_model.items()):
        req_rows = [r for r in rs if r.get("core_required_abs_to_pq_plus_1") is not None]
        ok = sum(1 for r in req_rows if r.get("selected_matches_required") is True)
        no = sum(1 for r in req_rows if r.get("selected_matches_required") is False)
        statuses = sorted(set(str(r.get("epistemic_status")) for r in req_rows))
        lines.append(f"| `{model}` | {len(req_rows)} | {ok} | {no} | `{'; '.join(statuses[:3])}` |")
    lines.append("")

    lines.append("## C. Clean rows where required +1 is selected")
    lines.append("")
    ok_clean = [r for r in plus if r.get("torus_status") == "PASS_DERIVED_PQ"]
    if ok_clean:
        lines.append("| curve | model | Φ/(2π) | selected n | epistemic status |")
        lines.append("|---|---|---:|---:|---|")
        for r in ok_clean[:100]:
            lines.append(f"| `{r['label']}` | `{r['model']}` | {fmt(r['phi_turns'])} | {fmt(r['n_selected'])} | `{r['epistemic_status']}` |")
    else:
        lines.append("No clean rows selected the required +1 under the chosen models.")
    lines.append("")

    lines.append("## D. Clean rows rejecting +1")
    lines.append("")
    bad_clean = [r for r in rejects if r.get("torus_status") == "PASS_DERIVED_PQ"]
    if bad_clean:
        lines.append("| curve | model | Φ/(2π) | selected n | required n | status |")
        lines.append("|---|---|---:|---:|---:|---|")
        for r in bad_clean[:100]:
            lines.append(f"| `{r['label']}` | `{r['model']}` | {fmt(r['phi_turns'])} | {fmt(r['n_selected'])} | {fmt(r['core_required_abs_to_pq_plus_1'])} | `{r['epistemic_status']}` |")
    else:
        lines.append("No clean rows rejected +1 under the chosen models.")
    lines.append("")

    lines.append("## E. Interpretation labels")
    lines.append("")
    lines.append("```text")
    lines.append("[DERIVED]       |SL_torus(T(p,q))| = p q, from target-free torus-surface framing.")
    lines.append("[ISOLATED]      pq+1 reduces to n_core = 1 for clean torus rows.")
    lines.append("[INPUT]         unit/signed_unit/background models select +1 only because Φ_bg/(2π)=1 is supplied.")
    lines.append("[CLOSURE]       twoomega_cycle selects +1 if Ω_core T_cycle = 2π is accepted as a closure condition.")
    lines.append("[DIAGNOSTIC]    twoomega_transit tests a material transit model; it need not be q-independent.")
    lines.append("[OPEN]          derive Φ_bg = 2π from swirl-clock closure, quantized circulation, or FR/θ=π spinon topology.")
    lines.append("```")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Audit n_core=(1/2π)∮dθ_core selection for SST torus ladder")
    ap.add_argument("--q-list", default="3,5,7,9,11")
    ap.add_argument("--p", type=int, default=2)
    ap.add_argument("--extra-torus", default="3:2,3:4")
    ap.add_argument("--samples", type=int, default=1024)
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--ribbon-eps-frac", type=float, default=0.008)
    ap.add_argument("--pq-abs-tol", type=float, default=0.25)
    ap.add_argument("--torus-R", type=float, default=2.0)
    ap.add_argument("--torus-r", type=float, default=0.65)
    ap.add_argument("--source-torus-fit", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--include-analytic", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--include-all-fseries", action="store_true")
    ap.add_argument("--include-all-ideal", action="store_true")
    ap.add_argument("--no-twist-controls", action="store_true")
    ap.add_argument("--no-zip-fallback", action="store_true")
    ap.add_argument("--max-fseries", type=int, default=0)
    ap.add_argument("--max-ideal", type=int, default=0)

    ap.add_argument("--models", default="zero,unit,twoomega_cycle,twoomega_transit,background",
                    help="Comma list or 'all': zero,unit,signed_unit,twoomega_cycle,twoomega_transit,background")
    ap.add_argument("--n-core-range", default="-3:3")
    ap.add_argument("--k-holonomy", type=float, default=1.0)
    ap.add_argument("--k-abs", type=float, default=0.0, help="optional penalty λ_abs n^2; default 0")
    ap.add_argument("--odd-bonus", type=float, default=0.0, help="optional energy bonus for odd |n|; default 0")
    ap.add_argument("--core-sign-mode", default="follow", choices=["follow", "absolute_positive", "absolute_negative"])

    # Physical/diagnostic parameters for twoomega_transit.
    ap.add_argument("--omega-core", type=float, default=OMEGA_CORE_DEFAULT,
                    help=f"Ω_core in rad/s for transit model; default v_swirl/r_c={OMEGA_CORE_DEFAULT:.6g}")
    ap.add_argument("--v-transport", type=float, default=V_SWIRL,
                    help=f"transport speed along curve for transit model; default v_swirl={V_SWIRL:.6g} m/s")
    ap.add_argument("--length-unit-m", type=float, default=R_C,
                    help=f"physical meters per normalized curve unit for transit model; default r_c={R_C:.6g} m")
    ap.add_argument("--phi-bg-turns", type=float, default=1.0, help="Φ_bg/(2π) for background model; default 1")
    ap.add_argument("--background-sign-mode", default="unsigned", choices=["unsigned", "follow"])

    # Companion circularity trap settings, kept to compare upstream status.
    ap.add_argument("--circularity-trap", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--trap-target", type=int, default=25)
    ap.add_argument("--trap-tol", type=float, default=0.25)

    ap.add_argument("--only-clean", action=argparse.BooleanOptionalAction, default=False,
                    help="If true, write holonomy rows only for PASS_DERIVED_PQ torus rows")
    ap.add_argument("--out-prefix", default="core_holonomy_audit")
    ap.add_argument("--log", default=None)
    args = ap.parse_args(argv)

    log_path = Path(args.log) if args.log else Path(Path(sys.argv[0]).stem + "_outputlog.txt")
    log_file, old_stdout, old_stderr = install_tee(log_path)

    try:
        models = parse_models(args.models)
        n_values = parse_int_range(args.n_core_range)
        print(f"[config] q_list={parse_q_list(args.q_list)}, samples={args.samples}, models={models}")
        print(f"[config] n_range={n_values}, k_holonomy={args.k_holonomy}, k_abs={args.k_abs}, odd_bonus={args.odd_bonus}")
        print("[scope] Core-holonomy audit: test n_core=(1/2π)∮dθ_core selection without injecting pq+1.")

        entries = collect_entries(args)
        print(f"[inventory] entries to analyze: {len(entries)}")
        for e in entries:
            qtxt = str(e.q) if e.q is not None else "-"
            extra = f" ctrl_q={e.control_for_q}" if e.control_for_q else ""
            print(f"  - {e.source_type:8s} {e.family:13s} p={e.p:<2d} q={qtxt:>2s}{extra:>10s} {e.label}")

        comp_args = build_companion_args(args)
        result_rows: List[Dict[str, object]] = []
        landscape_rows: List[Dict[str, object]] = []

        for idx, entry in enumerate(entries, start=1):
            try:
                base_row, _ = cta.analyze_entry(entry, comp_args)
            except Exception as exc:
                print(f"[ERROR] analyze failed for {entry.label}: {exc}")
                continue

            curve = curve_for_entry(entry, args.samples, args.torus_R, args.torus_r)
            curve_len = polygon_length(curve) if curve is not None else None

            if args.only_clean and base_row.get("torus_status") != "PASS_DERIVED_PQ":
                continue

            required_n = base_row.get("core_required_abs_to_pq_plus_1")
            torus_round = base_row.get("torus_SL_round")
            expected_pq = base_row.get("expected_pq")
            expected_pq_plus_1 = base_row.get("expected_pq_plus_1")

            # Skip non-torus controls for holonomy-model selection, but still report a base row with NO_TORUS_REQUIREMENT if desired.
            if required_n is None or torus_round is None:
                for m in models:
                    h = HolonomyModelResult(m, float('nan'), float('nan'), "NO_TORUS_REQUIREMENT", "non-torus/control row; no pq+1 target")
                    result_rows.append({
                        **{k: base_row.get(k) for k in ["source_type", "family", "label", "p", "q", "expected_pq", "expected_pq_plus_1", "torus_status", "torus_SL", "torus_SL_round", "torus_SL_abs_err_vs_pq", "core_required_abs_to_pq_plus_1"]},
                        "curve_length_dimless": curve_len,
                        "model": m,
                        "phi_turns": h.phi_turns,
                        "phi_rad": h.phi_rad,
                        "holonomy_status": h.status,
                        "assumption": h.assumption,
                        "n_selected": None,
                        "selected_matches_required": None,
                        "epistemic_status": "NO_TORUS_REQUIREMENT",
                        "SL_phys_selected_signed": None,
                        "SL_phys_selected_abs": None,
                        "SL_phys_required_abs": None,
                        "spin_half_compatible": None,
                        "twoomega_integral_turns": None,
                        "core_n_formula": "n_core=(1/2π)∮dθ_core",
                    })
                continue

            for model in models:
                h = phi_for_model(model, base_row, entry, args, curve_len)
                e_rows, n_selected = energy_landscape(h.phi_rad, n_values, args)
                selected_matches = (int(n_selected) == int(required_n))
                ep_status = model_epistemic_status(model, int(n_selected), int(required_n), h)
                # Apply the selected n to the signed torus self-linking.
                try:
                    sl_phys_signed = cta.core_sl_from_base(int(torus_round), int(n_selected), args.core_sign_mode)
                    sl_phys_abs = abs(int(sl_phys_signed))
                except Exception:
                    sl_phys_signed = None
                    sl_phys_abs = None
                spin_half_compatible = (abs(int(n_selected)) % 2 == 1)  # odd core winding can carry fermionic Z2 sign in the FR/θ=π route.

                row = {
                    **{k: base_row.get(k) for k in ["source_type", "family", "label", "p", "q", "expected_pq", "expected_pq_plus_1", "torus_status", "torus_SL", "torus_SL_round", "torus_SL_abs_err_vs_pq", "core_required_abs_to_pq_plus_1"]},
                    "curve_length_dimless": curve_len,
                    "model": model,
                    "phi_turns": h.phi_turns,
                    "phi_rad": h.phi_rad,
                    "holonomy_status": h.status,
                    "assumption": h.assumption,
                    "n_selected": int(n_selected),
                    "selected_matches_required": bool(selected_matches),
                    "epistemic_status": ep_status,
                    "SL_phys_selected_signed": sl_phys_signed,
                    "SL_phys_selected_abs": sl_phys_abs,
                    "SL_phys_required_abs": expected_pq_plus_1,
                    "spin_half_compatible": spin_half_compatible,
                    "twoomega_integral_turns": h.phi_turns if model.startswith("twoomega") else None,
                    "core_n_formula": "n_core=(1/2π)∮dθ_core",
                }
                result_rows.append(row)

                for er in e_rows:
                    landscape_rows.append({
                        "label": entry.label,
                        "source_type": entry.source_type,
                        "p": base_row.get("p"),
                        "q": base_row.get("q"),
                        "expected_pq": expected_pq,
                        "torus_SL_round": torus_round,
                        "model": model,
                        "phi_turns": h.phi_turns,
                        **er,
                        "selected": int(er["n_core"]) == int(n_selected),
                        "matches_required": int(er["n_core"]) == int(required_n),
                    })

                print(
                    f"[RESULT {idx:03d}/{len(entries):03d}] {entry.label} model={model} "
                    f"pq={expected_pq} SL_torus={fmt(base_row.get('torus_SL'))} "
                    f"n_req={required_n} phi/2pi={fmt(h.phi_turns)} n_sel={n_selected} "
                    f"{ep_status}"
                )

        out_prefix = Path(args.out_prefix)
        results_csv = out_prefix.with_name(out_prefix.name + "_results.csv")
        landscape_csv = out_prefix.with_name(out_prefix.name + "_energy_landscape.csv")
        summary_md = out_prefix.with_name(out_prefix.name + "_summary.md")

        write_csv(results_csv, result_rows, RESULT_FIELDS)
        write_csv(landscape_csv, landscape_rows, LANDSCAPE_FIELDS)
        write_markdown(summary_md, result_rows, landscape_rows, args)
        print(f"[write] {results_csv}")
        print(f"[write] {landscape_csv}")
        print(f"[write] {summary_md}")
        print("[done]")
        return 0

    finally:
        try:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            log_file.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
