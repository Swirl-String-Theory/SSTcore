#!/usr/bin/env python3
r"""
fs_unified_attachment_audit.py
==============================

Unified SST Attachment-Lemma audit harness.

Purpose
-------
This script unifies the earlier audit directions into one reproducible runner:

  1. single-component torus knots
     - canonical base rule: |SL_torus(T(p,q))| = p q
     - attachment test: SL_phys = SL_base + chi

  2. single-component twist/general knots
     - no pq rule is imposed
     - if no canonical framed self-linking is known, PT_Lk0_round is used only as
       a diagnostic framing proxy
     - attachment test: SL_phys = SL_geom_proxy + chi

  3. multi-component links
     - parses blank-line-separated coordinate blocks from .txt or .zip files
     - estimates pairwise Gauss linking numbers Lk_ij
     - bookkeeping: H/Gamma^2 = sum_i(SL_i + chi_i) + 2 sum_{i<j} Lk_ij + higher

  4. gear-locked STL analogs
     - splits a gear STL into connected bodies
     - estimates body centers/normals and axle axis
     - scans sign-lock scenarios for theta_i - s_ij theta_j = 0
     - tests whether a central helix/axle phase psi = m Theta gives n_core=chi

Every object class uses the same compensated swirl-clock / entanglement attachment
kernel:

    chi_total = chi_local + chi_attachment.

The Canon-candidate compensated neutral mode enforces:

    chi_local      = chi/(1 + sigma * epsilon_SE)
    chi_attachment = chi - chi_local
    chi_total      = chi
    charge_leak    = 0

Important audit distinction:

  - integer_selection_chi can survive approximate holonomy errors;
  - exact_holonomy_chi is required for exact Canon status.

Outputs
-------
By default exports are written to a folder with the same name as --out-prefix:

  <out-prefix>/<out-prefix>_objects.csv
  <out-prefix>/<out-prefix>_single_attachment_results.csv
  <out-prefix>/<out-prefix>_link_components.csv
  <out-prefix>/<out-prefix>_linking_matrices.csv
  <out-prefix>/<out-prefix>_link_attachment_results.csv
  <out-prefix>/<out-prefix>_gear_mesh_summary.csv
  <out-prefix>/<out-prefix>_gear_components.csv
  <out-prefix>/<out-prefix>_gear_lock_scenarios.csv
  <out-prefix>/<out-prefix>_gear_helicity_bookkeeping.csv
  <out-prefix>/<out-prefix>_summary.md
  <out-prefix>/<out-prefix>_runlog.txt

Typical runs
------------
Torus/twist from previous v2 geometry audit:

    python fs_unified_attachment_audit.py \
      --input-results core_holonomy_v2_results.csv \
      --include-controls \
      --out-prefix unified_attachment_audit

Add a multicomponent link zip:

    python fs_unified_attachment_audit.py \
      --input-results core_holonomy_v2_results.csv \
      --include-controls \
      --link-file knot_TL3.3_Gear.zip \
      --out-prefix unified_attachment_audit

Add STL gear analog:

    python fs_unified_attachment_audit.py \
      --input-results core_holonomy_v2_results.csv \
      --include-controls \
      --link-file knot_TL3.3_Gear.zip \
      --gear-stl triple_gear_solid_with_mark.stl \
      --axle-stl 30cm_axle.stl \
      --out-prefix unified_attachment_audit

Dependencies
------------
Required: Python 3.9+, numpy.
Optional for STL gear module: trimesh.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import os
import re
import sys
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

try:
    import trimesh  # type: ignore
except Exception:  # pragma: no cover
    trimesh = None

TAU = 2.0 * math.pi
DEFAULT_V_SWIRL = 1.09384563e6
DEFAULT_R_C = 1.40897017e-15


# -----------------------------------------------------------------------------
# General utilities
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


def fmt(x: object) -> str:
    if x is None:
        return ""
    if isinstance(x, float):
        if math.isnan(x):
            return ""
        return f"{x:.12g}"
    return str(x)


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: Optional[List[str]] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for k in row.keys():
                if k not in fieldnames:
                    fieldnames.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: fmt(row.get(k, "")) for k in fieldnames})


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


def parse_int_or_none(x: object) -> Optional[int]:
    y = parse_float_or_none(x)
    if y is None:
        return None
    try:
        return int(round(y))
    except Exception:
        return None


def parse_num_list(s: str, typ=float) -> List:
    out = []
    for p in s.split(','):
        p = p.strip()
        if p:
            out.append(typ(p))
    return out


def parse_int_range(spec: str) -> Tuple[int, int]:
    spec = spec.strip()
    if ":" in spec:
        a, b = spec.split(":", 1)
        return int(a), int(b)
    vals = [int(x.strip()) for x in spec.split(',') if x.strip()]
    if not vals:
        raise ValueError("empty integer range")
    return min(vals), max(vals)


def parse_q_list(s: str) -> List[int]:
    return [int(x.strip()) for x in s.split(',') if x.strip()]


def parse_extra_torus(s: str) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    if not s.strip():
        return out
    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        if ':' in part:
            a, b = part.split(':', 1)
        elif 'x' in part.lower():
            a, b = part.lower().split('x', 1)
        else:
            raise ValueError(f"cannot parse extra torus entry: {part!r}")
        out.append((int(a), int(b)))
    return out


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n == 0:
        return v
    return v / n


def pca_axes(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    X = np.asarray(points, dtype=float)
    c = X.mean(axis=0)
    Y = X - c
    cov = np.cov(Y.T)
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    return vals[order], vecs[:, order]


def output_paths(out_prefix: str, out_dir_arg: Optional[str]) -> Tuple[Path, str]:
    p = Path(out_prefix)
    base = p.name
    if out_dir_arg:
        out_dir = Path(out_dir_arg)
    else:
        parent = p.parent if str(p.parent) not in ('', '.') else Path('.')
        out_dir = parent / base
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir, base


# -----------------------------------------------------------------------------
# Attachment kernel
# -----------------------------------------------------------------------------

@dataclass
class AttachmentModel:
    model_id: str
    description: str
    parity: str              # none | odd | even
    chi_kind: str            # matter | antimatter
    local_kind: str          # canon | renormalized | q_renormalized | passive | decohered
    attachment_kind: str     # exact_compensated | none | partial | charge_leak | residual
    status_label: str


def attachment_models(include_diagnostics: bool = True) -> List[AttachmentModel]:
    models = [
        AttachmentModel("C0_CANON_ATTACHED_BASELINE", "Baseline exact attachment: local=chi, attachment=0.", "odd", "matter", "canon", "exact_compensated", "BASELINE_EXACT_ATTACHMENT"),
        AttachmentModel("C1_COMPENSATED_NEUTRAL_MATTER", "Matter-sector exact neutral compensation.", "odd", "matter", "renormalized", "exact_compensated", "CANON_CANDIDATE_COMPENSATED"),
        AttachmentModel("C2_COMPENSATED_NEUTRAL_ANTIMATTER", "Antimatter/mirror exact neutral compensation.", "odd", "antimatter", "renormalized", "exact_compensated", "CANON_CANDIDATE_MIRROR_COMPENSATED"),
    ]
    if include_diagnostics:
        models.extend([
            AttachmentModel("C3_UNCOMPENSATED_LOCAL_ONLY", "Local swirl-clock renormalization without attachment compensation.", "odd", "matter", "renormalized", "none", "FAILS_EXACT_HOLONOMY_UNLESS_EPS_ZERO"),
            AttachmentModel("C4_PARTIAL_COMPENSATION", "Diagnostic partial compensation; tests exactness failure.", "odd", "matter", "renormalized", "partial", "PARTIAL_COMPENSATION_DIAGNOSTIC"),
            AttachmentModel("C5_CHARGE_LEAK", "Compensation partly leaks into charge/spectral sector.", "odd", "matter", "renormalized", "charge_leak", "CHARGE_LEAK_CONSTRAINED"),
            AttachmentModel("C6_DECOHERED_RESIDUAL", "Residual/decohered attachment; selection may survive but exactness fails.", "odd", "matter", "decohered", "residual", "DECOHERENCE_RESIDUAL_DIAGNOSTIC"),
            AttachmentModel("C7_Q_DEP_COMPENSATED", "q-dependent local contribution but total exact; diagnostic for universality.", "odd", "matter", "q_renormalized", "exact_compensated", "Q_DEP_LOCAL_BUT_TOTAL_EXACT"),
            AttachmentModel("C8_PASSIVE_TRANSIT_COMPENSATED_TEST", "Rejected passive transit center; not an Attachment mechanism.", "none", "matter", "passive", "none", "PASSIVE_TRANSIT_REJECTED"),
        ])
    return models


def chi_sign(kind: str) -> int:
    return -1 if kind.lower().startswith('anti') else 1


def allowed_ns(parity: str, n_min: int, n_max: int) -> List[int]:
    vals = list(range(n_min, n_max + 1))
    if parity == 'none':
        return vals
    if parity == 'odd':
        return [n for n in vals if n % 2 != 0]
    if parity == 'even':
        return [n for n in vals if n % 2 == 0]
    raise ValueError(f"unknown parity {parity!r}")


def select_n(center: Optional[float], parity: str, n_min: int, n_max: int, tol: float = 1e-12) -> Tuple[List[int], Optional[float], List[int]]:
    allowed = allowed_ns(parity, n_min, n_max)
    if center is None:
        return [], None, allowed
    energies = [(n, (n - center) ** 2) for n in allowed]
    e_min = min(e for _, e in energies)
    selected = [n for n, e in energies if abs(e - e_min) <= tol]
    return selected, e_min, allowed


def attachment_turns_for(model: AttachmentModel, epsilon: float, sigma: float, chi: int, q: Optional[int], q_ref: int, q_slope: float, passive_center: float, partial_fraction: float, charge_leak_fraction: float, decoherence_residual: float) -> Dict[str, float]:
    # local contribution
    if model.local_kind == 'canon':
        local = float(chi)
    elif model.local_kind == 'renormalized':
        local = float(chi) / (1.0 + sigma * epsilon)
    elif model.local_kind == 'q_renormalized':
        q_term = 0.0 if q is None else q_slope * (float(q) - float(q_ref))
        local = float(chi) / (1.0 + sigma * epsilon + q_term)
    elif model.local_kind == 'passive':
        local = passive_center
    elif model.local_kind == 'decohered':
        local = float(chi) / (1.0 + sigma * epsilon)
    else:
        raise ValueError(f"unknown local kind {model.local_kind}")

    missing = float(chi) - local
    charge_leak = 0.0
    residual = 0.0

    if model.attachment_kind == 'exact_compensated':
        attachment = missing
    elif model.attachment_kind == 'none':
        attachment = 0.0
    elif model.attachment_kind == 'partial':
        attachment = partial_fraction * missing
    elif model.attachment_kind == 'charge_leak':
        charge_leak = charge_leak_fraction * missing
        attachment = missing - charge_leak
    elif model.attachment_kind == 'residual':
        residual = decoherence_residual
        attachment = missing - residual
    else:
        raise ValueError(f"unknown attachment kind {model.attachment_kind}")

    total = local + attachment
    return dict(local_turns=local, attachment_turns=attachment, total_turns=total, charge_leak_turns=charge_leak, decoherence_residual=residual)


def audit_status(model: AttachmentModel, total: float, chi: int, selected: List[int], charge_leak: float, exact_tol: float, charge_tol: float) -> Tuple[str, str, str, str]:
    exact = abs(total - chi) <= exact_tol
    integer = (len(selected) == 1 and selected[0] == chi)
    charge_safe = abs(charge_leak) <= charge_tol
    if model.model_id == 'C8_PASSIVE_TRANSIT_COMPENSATED_TEST':
        status = 'PASSIVE_TRANSIT_REJECTED'
    elif not charge_safe:
        status = 'CHARGE_LEAK_REJECT_OR_CONSTRAIN'
    elif exact and model.attachment_kind == 'exact_compensated' and model.model_id.startswith(('C1', 'C2', 'C7')):
        status = 'CANON_CANDIDATE_EXACT_COMPENSATED'
    elif exact and model.model_id == 'C0_CANON_ATTACHED_BASELINE':
        status = 'BASELINE_EXACT_ATTACHMENT'
    elif exact and model.model_id == 'C3_UNCOMPENSATED_LOCAL_ONLY':
        status = 'LOCAL_ONLY_TRIVIAL_EPS0'
    elif not exact and integer:
        if model.model_id == 'C4_PARTIAL_COMPENSATION':
            status = 'PARTIAL_SELECTION_STABLE_NOT_EXACT'
        elif model.model_id == 'C6_DECOHERED_RESIDUAL':
            status = 'DECOHERED_SELECTION_STABLE_NOT_EXACT'
        else:
            status = 'SELECTION_STABLE_BUT_HOLONOMY_NOT_EXACT'
    elif not exact and model.model_id == 'C4_PARTIAL_COMPENSATION':
        status = 'PARTIAL_COMPENSATION_FAILS_EXACTNESS'
    else:
        status = 'FAILS_ATTACHMENT_AUDIT'
    return ('YES' if exact else 'NO', 'YES' if integer else 'NO', 'YES' if charge_safe else 'NO', status)


# -----------------------------------------------------------------------------
# Single-object loading from core_holonomy_v2_results or fallback analytic torus
# -----------------------------------------------------------------------------

@dataclass
class SingleObject:
    object_id: str
    object_type: str        # single_torus | single_twist | single_general
    source_type: str
    family: str
    p: Optional[int]
    q: Optional[int]
    base_rule: str
    base_sl_abs: Optional[int]
    base_sl_signed: Optional[int]
    expected_pq: Optional[int]
    torus_status: str
    canon_status: str
    notes: str


def read_single_objects(path: Path, include_controls: bool, canonical_only: bool, include_noncanonical: bool) -> List[SingleObject]:
    objs: List[SingleObject] = []
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for raw in reader:
            family = (raw.get('family') or 'unknown').strip()
            if family != 'torus' and not include_controls:
                continue
            label = (raw.get('label') or raw.get('canonical_label') or 'object').strip()
            p = parse_int_or_none(raw.get('p'))
            q = parse_int_or_none(raw.get('q'))
            expected_pq = parse_int_or_none(raw.get('expected_pq') or raw.get('pq'))
            torus_status = (raw.get('torus_status') or '').strip()
            source_type = (raw.get('source_type') or 'csv').strip()
            base_signed: Optional[int] = None
            base_abs: Optional[int] = None
            base_rule = ''
            canon_status = ''
            object_type = 'single_general'
            notes: List[str] = []

            if family == 'torus':
                object_type = 'single_torus'
                if torus_status == 'PASS_DERIVED_PQ' and expected_pq is not None:
                    base_abs = expected_pq
                    base_signed = parse_int_or_none(raw.get('torus_SL_round'))
                    base_rule = 'torus_surface_pq'
                    canon_status = 'CANONICAL_TORUS_BASE'
                else:
                    if canonical_only and not include_noncanonical:
                        continue
                    tsl = parse_int_or_none(raw.get('torus_SL_round'))
                    if tsl is None:
                        continue
                    base_signed = tsl
                    base_abs = abs(tsl)
                    base_rule = 'fitted_torus_proxy_noncanonical'
                    canon_status = 'DIAGNOSTIC_NONCANONICAL_TORUS_FIT'
                    notes.append('Source/framing does not pass canonical pq check; retained only as diagnostic.')
            else:
                # twist/general control: no pq target. Use PT_Lk0_round if present as a framing proxy.
                if family == 'control_twist' or re.search(r'(^|[^0-9])(?:5_2|6_1|7_2|8_1|9_2|10_1|11_2)', label):
                    object_type = 'single_twist'
                pt = parse_int_or_none(raw.get('PT_Lk0_round') or raw.get('PT_Lk0'))
                if pt is None:
                    continue
                base_signed = pt
                base_abs = abs(pt)
                base_rule = 'PT_Lk0_round_proxy_no_pq_rule'
                canon_status = 'DIAGNOSTIC_TWIST_OR_GENERAL_PROXY'
                notes.append('No torus pq rule applied. PT_Lk0 is a framing proxy, not a canonical SL theorem.')

            if base_abs is None:
                continue
            objs.append(SingleObject(
                object_id=label,
                object_type=object_type,
                source_type=source_type,
                family=family,
                p=p,
                q=q,
                base_rule=base_rule,
                base_sl_abs=base_abs,
                base_sl_signed=base_signed,
                expected_pq=expected_pq,
                torus_status=torus_status,
                canon_status=canon_status,
                notes=' '.join(notes),
            ))
    return objs


def fallback_torus_objects(q_list: List[int], p: int, extra: List[Tuple[int, int]]) -> List[SingleObject]:
    objs: List[SingleObject] = []
    pairs = [(p, q) for q in q_list] + extra
    seen = set()
    for pp, qq in pairs:
        if (pp, qq) in seen:
            continue
        seen.add((pp, qq))
        pq = pp * qq
        objs.append(SingleObject(
            object_id=f'analytic:T({pp},{qq})',
            object_type='single_torus',
            source_type='analytic_fallback',
            family='torus',
            p=pp,
            q=qq,
            base_rule='torus_surface_pq_assumed',
            base_sl_abs=pq,
            base_sl_signed=-pq,
            expected_pq=pq,
            torus_status='PASS_DERIVED_PQ_ANALYTIC_ASSUMED',
            canon_status='CANONICAL_TORUS_BASE_ASSUMED',
            notes='Analytic fallback row; no numerical geometry audit performed in this script.',
        ))
    return objs


def run_single_attachment(objs: List[SingleObject], models: List[AttachmentModel], eps_list: List[float], args) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for obj in objs:
        for eps in eps_list:
            for model in models:
                chi = chi_sign(model.chi_kind)
                t = attachment_turns_for(model, eps, args.sigma, chi, obj.q, args.q_ref, args.q_slope, args.passive_center, args.partial_fraction, args.charge_leak_fraction, args.decoherence_residual)
                selected, e_min, allowed = select_n(t['total_turns'], model.parity, args.n_min, args.n_max, args.energy_tol)
                exact, integer, charge_safe, status = audit_status(model, t['total_turns'], chi, selected, t['charge_leak_turns'], args.exact_tol, args.charge_tol)
                selected_str = ','.join(str(n) for n in selected)
                if selected:
                    # Co-oriented absolute convention: attachment adds |n| to |base|.
                    sl_phys_abs = (obj.base_sl_abs or 0) + abs(selected[0])
                else:
                    sl_phys_abs = None
                exact_pq_plus_1 = ''
                if obj.object_type == 'single_torus' and obj.expected_pq is not None and sl_phys_abs is not None:
                    exact_pq_plus_1 = 'YES' if sl_phys_abs == obj.expected_pq + 1 and integer == 'YES' else 'NO'
                rows.append({
                    'object_id': obj.object_id,
                    'object_type': obj.object_type,
                    'source_type': obj.source_type,
                    'family': obj.family,
                    'p': obj.p,
                    'q': obj.q,
                    'base_rule': obj.base_rule,
                    'base_sl_abs': obj.base_sl_abs,
                    'base_sl_signed': obj.base_sl_signed,
                    'expected_pq': obj.expected_pq,
                    'torus_status': obj.torus_status,
                    'canon_status': obj.canon_status,
                    'epsilon_SE': eps,
                    'sigma': args.sigma,
                    'model_id': model.model_id,
                    'chi': chi,
                    'local_turns': t['local_turns'],
                    'attachment_turns': t['attachment_turns'],
                    'total_turns': t['total_turns'],
                    'residual_to_chi': t['total_turns'] - chi,
                    'charge_leak_turns': t['charge_leak_turns'],
                    'decoherence_residual': t['decoherence_residual'],
                    'allowed_n': ','.join(str(n) for n in allowed),
                    'selected_n_core': selected_str,
                    'min_energy': e_min,
                    'sl_phys_abs': sl_phys_abs,
                    'exact_holonomy_chi': exact,
                    'integer_selection_chi': integer,
                    'exact_pq_plus_1': exact_pq_plus_1,
                    'charge_safe': charge_safe,
                    'audit_status': status,
                    'notes': obj.notes,
                })
    return rows


# -----------------------------------------------------------------------------
# Multi-component link parsing and Gauss linking
# -----------------------------------------------------------------------------

@dataclass
class LinkObject:
    object_id: str
    source_path: str
    member: str
    components: List[np.ndarray]
    notes: str


def read_link_text(path: Path, member: Optional[str] = None) -> Tuple[str, str]:
    if path.suffix.lower() == '.zip':
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if member is None:
                txts = [n for n in names if n.lower().endswith('.txt') and not n.lower().endswith('_report.txt') and 'ideal' not in n.lower() and 'monopole' not in n.lower()]
                if not txts:
                    raise FileNotFoundError(f'No coordinate .txt member found in {path}')
                member = txts[0]
            return z.read(member).decode('utf-8', errors='replace'), member
    return path.read_text(encoding='utf-8', errors='replace'), path.name


def parse_components_from_text(text: str) -> List[np.ndarray]:
    comps: List[np.ndarray] = []
    for block in re.split(r'\n\s*\n', text.strip()):
        pts = []
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('%'):
                continue
            vals = re.split(r'[\s,]+', line)
            if len(vals) >= 3:
                try:
                    pts.append([float(vals[0]), float(vals[1]), float(vals[2])])
                except ValueError:
                    pass
        if pts:
            comps.append(np.asarray(pts, dtype=float))
    return comps


def load_link_object(path: Path, member: Optional[str] = None) -> LinkObject:
    text, used_member = read_link_text(path, member)
    comps = parse_components_from_text(text)
    if len(comps) < 2:
        raise RuntimeError(f'Expected a multi-component link from {path}; found {len(comps)} component(s).')
    return LinkObject(object_id=path.stem, source_path=str(path), member=used_member, components=comps, notes='blank-line-separated coordinate blocks')


def component_stats(P: np.ndarray) -> Dict[str, object]:
    n = len(P)
    closure_gap = float(np.linalg.norm(P[0] - P[-1]))
    length = float(sum(np.linalg.norm(P[(i + 1) % n] - P[i]) for i in range(n)))
    mn = P.min(axis=0)
    mx = P.max(axis=0)
    return {
        'points': n,
        'closure_gap': closure_gap,
        'closed_polygon_length': length,
        'bbox_x_min': float(mn[0]), 'bbox_x_max': float(mx[0]),
        'bbox_y_min': float(mn[1]), 'bbox_y_max': float(mx[1]),
        'bbox_z_min': float(mn[2]), 'bbox_z_max': float(mx[2]),
    }


def subdivide_closed_polygon(P: np.ndarray, sub: int) -> np.ndarray:
    pts = []
    n = len(P)
    for i in range(n):
        a = P[i]
        b = P[(i + 1) % n]
        for k in range(sub):
            pts.append(a + (b - a) * (k / sub))
    return np.asarray(pts, dtype=float)


def gauss_lk_midpoint(P: np.ndarray, Q: np.ndarray, sub: int = 32) -> float:
    P2 = subdivide_closed_polygon(P, sub)
    Q2 = subdivide_closed_polygon(Q, sub)
    Ps = P2
    Pe = np.roll(P2, -1, axis=0)
    dP = Pe - Ps
    mP = 0.5 * (Ps + Pe)
    Qs = Q2
    Qe = np.roll(Q2, -1, axis=0)
    dQ = Qe - Qs
    mQ = 0.5 * (Qs + Qe)
    total = 0.0
    for i in range(len(P2)):
        r = mP[i] - mQ
        cr = np.cross(dP[i], dQ)
        num = np.einsum('ij,ij->i', r, cr)
        den = np.linalg.norm(r, axis=1) ** 3
        total += float(np.sum(num / den))
    return total / (4.0 * math.pi)


def compute_linking_matrix(comps: List[np.ndarray], sub: int) -> np.ndarray:
    n = len(comps)
    L = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            val = gauss_lk_midpoint(comps[i], comps[j], sub=sub)
            L[i, j] = L[j, i] = val
    return L


def run_link_attachment(link: LinkObject, L: np.ndarray, models: List[AttachmentModel], eps_list: List[float], args) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    comp_rows: List[Dict[str, object]] = []
    matrix_rows: List[Dict[str, object]] = []
    result_rows: List[Dict[str, object]] = []
    n = len(link.components)
    for idx, P in enumerate(link.components, start=1):
        st = component_stats(P)
        row = {'object_id': link.object_id, 'source_path': link.source_path, 'member': link.member, 'component': idx}
        row.update(st)
        comp_rows.append(row)
    for i in range(n):
        for j in range(i + 1, n):
            v = float(L[i, j])
            r = int(round(v))
            matrix_rows.append({
                'object_id': link.object_id,
                'i': i + 1,
                'j': j + 1,
                'lk_estimate': v,
                'lk_integer': r,
                'abs_error_to_integer': abs(v - r),
            })
    sum_lk = float(sum(L[i, j] for i in range(n) for j in range(i + 1, n)))
    sum_lk_int = int(round(sum_lk))
    sum_lk_abs_int = int(round(sum(abs(L[i, j]) for i in range(n) for j in range(i + 1, n))))
    pair_cross_signed = 2 * sum_lk_int
    pair_cross_abs = 2 * sum_lk_abs_int
    for eps in eps_list:
        for model in models:
            # Use same model/chi on every component by default.
            chi = chi_sign(model.chi_kind)
            per = []
            charge_leaks = []
            selected_ns = []
            exacts = []
            integers = []
            charge_safes = []
            statuses = []
            for comp_i in range(1, n + 1):
                t = attachment_turns_for(model, eps, args.sigma, chi, None, args.q_ref, args.q_slope, args.passive_center, args.partial_fraction, args.charge_leak_fraction, args.decoherence_residual)
                selected, e_min, allowed = select_n(t['total_turns'], model.parity, args.n_min, args.n_max, args.energy_tol)
                exact, integer, charge_safe, status = audit_status(model, t['total_turns'], chi, selected, t['charge_leak_turns'], args.exact_tol, args.charge_tol)
                per.append(t)
                charge_leaks.append(t['charge_leak_turns'])
                selected_ns.append(selected[0] if len(selected) == 1 else None)
                exacts.append(exact == 'YES')
                integers.append(integer == 'YES')
                charge_safes.append(charge_safe == 'YES')
                statuses.append(status)
            self_attachment = sum((abs(x) if x is not None else 0) for x in selected_ns)
            helicity_signed = self_attachment + pair_cross_signed
            helicity_abs_pair = self_attachment + pair_cross_abs
            if all(exacts) and all(integers) and all(charge_safes) and model.model_id.startswith(('C0', 'C1', 'C2', 'C7')):
                link_status = 'LINK_CANON_CANDIDATE_EXACT_COMPENSATED'
            elif model.model_id == 'C8_PASSIVE_TRANSIT_COMPENSATED_TEST':
                link_status = 'LINK_PASSIVE_TRANSIT_REJECTED'
            elif not all(charge_safes):
                link_status = 'LINK_CHARGE_LEAK_REJECT_OR_CONSTRAIN'
            elif all(integers) and not all(exacts):
                link_status = 'LINK_SELECTION_STABLE_BUT_HOLONOMY_NOT_EXACT'
            else:
                link_status = 'LINK_DIAGNOSTIC_FAIL_OR_PARTIAL'
            result_rows.append({
                'object_id': link.object_id,
                'object_type': 'multicomponent_link',
                'component_count': n,
                'epsilon_SE': eps,
                'model_id': model.model_id,
                'chi_each': chi,
                'chi_total_per_component': ';'.join(fmt(p['total_turns']) for p in per),
                'selected_n_per_component': ';'.join('' if x is None else str(x) for x in selected_ns),
                'exact_holonomy_all_components': 'YES' if all(exacts) else 'NO',
                'integer_selection_all_components': 'YES' if all(integers) else 'NO',
                'charge_safe_all_components': 'YES' if all(charge_safes) else 'NO',
                'sum_lk_signed_estimate': sum_lk,
                'sum_lk_signed_integer': sum_lk_int,
                'pairwise_cross_signed': pair_cross_signed,
                'sum_abs_lk_integer': sum_lk_abs_int,
                'pairwise_cross_abs': pair_cross_abs,
                'self_attachment_sum_abs': self_attachment,
                'helicity_index_signed_pairwise_only': helicity_signed,
                'helicity_index_unoriented_abs_pairwise_only': helicity_abs_pair,
                'higher_linking_term': '',
                'audit_status': link_status,
                'notes': 'H/Gamma^2 = sum_i SL_i + 2 sum_ij Lk_ij + higher. Self SL_i here is attachment-only unless component SL_geom is supplied.',
            })
    return comp_rows, matrix_rows, result_rows


# -----------------------------------------------------------------------------
# Gear STL module
# -----------------------------------------------------------------------------

@dataclass
class MeshSummary:
    mesh_label: str
    path: str
    file_size_bytes: int
    vertices: int
    faces: int
    watertight: str
    euler_number: int
    body_count: int
    volume: float
    surface_area: float
    extent_x: float
    extent_y: float
    extent_z: float


def load_mesh(path: Path):
    if trimesh is None:
        raise RuntimeError('trimesh is required for STL gear module. Install trimesh or omit --gear-stl.')
    mesh = trimesh.load(str(path), force='mesh')
    if mesh is None or getattr(mesh, 'vertices', None) is None:
        raise RuntimeError(f'Could not load mesh: {path}')
    return mesh


def mesh_summary(mesh, path: Path, label: str) -> MeshSummary:
    ext = mesh.extents if hasattr(mesh, 'extents') else (mesh.bounds[1] - mesh.bounds[0])
    try:
        bodies = mesh.split(only_watertight=False)
        body_count = len(bodies)
    except Exception:
        body_count = 1
    return MeshSummary(
        mesh_label=label,
        path=str(path),
        file_size_bytes=int(path.stat().st_size),
        vertices=int(len(mesh.vertices)),
        faces=int(len(mesh.faces)),
        watertight='YES' if bool(mesh.is_watertight) else 'NO',
        euler_number=int(getattr(mesh, 'euler_number', 0)),
        body_count=int(body_count),
        volume=float(mesh.volume),
        surface_area=float(mesh.area),
        extent_x=float(ext[0]),
        extent_y=float(ext[1]),
        extent_z=float(ext[2]),
    )


def component_info_rows(mesh, mesh_label: str, axle_axis: Optional[np.ndarray]) -> List[Dict[str, object]]:
    bodies = mesh.split(only_watertight=False)
    rows: List[Dict[str, object]] = []
    for idx, body in enumerate(bodies, start=1):
        pts = np.asarray(body.vertices, dtype=float)
        vals, vecs = pca_axes(pts)
        # For ring/flat-ish gear body, smallest PCA axis is an approximate normal.
        normal = unit(vecs[:, -1])
        if axle_axis is not None and np.dot(normal, axle_axis) < 0:
            normal = -normal
        dot = float(np.dot(normal, axle_axis)) if axle_axis is not None else float('nan')
        dot_clamped = max(-1.0, min(1.0, dot)) if axle_axis is not None else float('nan')
        angle = math.degrees(math.acos(abs(dot_clamped))) if axle_axis is not None else float('nan')
        c = body.centroid if hasattr(body, 'centroid') else pts.mean(axis=0)
        ext = body.extents if hasattr(body, 'extents') else (body.bounds[1] - body.bounds[0])
        rows.append({
            'mesh_label': mesh_label,
            'component_id': idx,
            'vertices': int(len(body.vertices)),
            'faces': int(len(body.faces)),
            'watertight': 'YES' if bool(body.is_watertight) else 'NO',
            'volume': float(body.volume),
            'surface_area': float(body.area),
            'center_x': float(c[0]), 'center_y': float(c[1]), 'center_z': float(c[2]),
            'extent_x': float(ext[0]), 'extent_y': float(ext[1]), 'extent_z': float(ext[2]),
            'pca_val_1': float(vals[0]), 'pca_val_2': float(vals[1]), 'pca_val_3': float(vals[2]),
            'normal_x': float(normal[0]), 'normal_y': float(normal[1]), 'normal_z': float(normal[2]),
            'normal_dot_axle_axis': dot,
            'normal_angle_to_axle_deg': angle,
        })
    return rows


def distance_matrix_rows(component_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    centers = []
    for r in component_rows:
        centers.append(np.array([float(r['center_x']), float(r['center_y']), float(r['center_z'])], dtype=float))
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            rows.append({
                'i': i + 1,
                'j': j + 1,
                'center_distance': float(np.linalg.norm(centers[i] - centers[j])),
            })
    return rows


def gear_lock_scenarios(n_gears: int, helix_ratio: float, n_min: int, n_max: int, tol: float = 1e-12) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    if n_gears < 2:
        return rows
    # Complete graph sign assignments for up to 3 gears; for larger, use cycle edges plus all edges.
    pairs = [(i, j) for i in range(n_gears) for j in range(i + 1, n_gears)]
    for signs in itertools.product([-1, 1], repeat=len(pairs)):
        sign_map = {pair: s for pair, s in zip(pairs, signs)}
        # Build linear equations theta_i - s_ij theta_j = 0.
        A = []
        for (i, j), s in sign_map.items():
            row = np.zeros(n_gears)
            row[i] = 1.0
            row[j] = -float(s)
            A.append(row)
        A_np = np.vstack(A) if A else np.zeros((0, n_gears))
        # Nullspace dimension.
        _, sv, vh = np.linalg.svd(A_np)
        rank = int(np.sum(sv > 1e-10))
        null_dim = n_gears - rank
        if null_dim > 0:
            basis = vh[rank:].T[:, 0]
            if abs(basis[0]) > 1e-12:
                basis = basis / basis[0]
            collective = 'YES'
        else:
            basis = np.zeros(n_gears)
            collective = 'NO'
        center = helix_ratio if collective == 'YES' else None
        selected, e_min, allowed = select_n(center, 'odd', n_min, n_max, tol)
        exact = center is not None and abs(center - 1.0) <= 1e-12 and selected == [1]
        product_cycle = None
        if n_gears == 3:
            product_cycle = sign_map[(0, 1)] * sign_map[(0, 2)] * sign_map[(1, 2)]
        status = 'FULLY_LOCKED_ATTACHMENT_ANALOG' if exact else ('FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION' if collective == 'NO' else 'COLLECTIVE_LOCK_BUT_NONCANONICAL_HELIX_RATIO')
        rows.append({
            'n_gears': n_gears,
            'signs': ';'.join(f's{a+1}{b+1}={s:+d}' for (a, b), s in sign_map.items()),
            'cycle_sign_product': product_cycle,
            'rank': rank,
            'null_dim': null_dim,
            'collective_mode_exists': collective,
            'collective_basis_theta': ','.join(fmt(float(x)) for x in basis),
            'helix_ratio': helix_ratio,
            'psi_center_turns': center,
            'selected_n_core': ','.join(str(n) for n in selected),
            'exact_holonomy_chi': 'YES' if exact else 'NO',
            'audit_status': status,
        })
    return rows


def read_linking_matrix_csv(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for raw in reader:
            if 'i' in raw and 'j' in raw:
                i = parse_int_or_none(raw.get('i'))
                j = parse_int_or_none(raw.get('j'))
                lk = parse_float_or_none(raw.get('lk_integer') or raw.get('lk_estimate'))
                if i is not None and j is not None and lk is not None:
                    rows.append({'i': i, 'j': j, 'lk': lk})
    return rows


def gear_helicity_rows(linking_matrix_csv: Optional[Path], component_count: int) -> List[Dict[str, object]]:
    if not linking_matrix_csv or not linking_matrix_csv.exists():
        return []
    matrix = read_linking_matrix_csv(linking_matrix_csv)
    if not matrix:
        return []
    sum_lk = sum(float(r['lk']) for r in matrix)
    sum_lk_int = int(round(sum_lk))
    sum_abs = sum(abs(float(r['lk'])) for r in matrix)
    sum_abs_int = int(round(sum_abs))
    self_attach = component_count
    return [{
        'component_count': component_count,
        'source_linking_matrix_csv': str(linking_matrix_csv),
        'sum_lk_signed': sum_lk,
        'sum_lk_signed_integer': sum_lk_int,
        'pairwise_cross_signed': 2 * sum_lk_int,
        'sum_abs_lk_integer': sum_abs_int,
        'pairwise_cross_abs': 2 * sum_abs_int,
        'self_attachment_sum_chi_all_matter': self_attach,
        'helicity_index_signed_pairwise_only': self_attach + 2 * sum_lk_int,
        'helicity_index_unoriented_abs_pairwise_only': self_attach + 2 * sum_abs_int,
        'notes': 'Gear STL mechanical phase-lock bookkeeping combined with supplied link matrix. No higher Milnor term included.',
    }]


def run_gear_module(args, out_dir: Path, base: str) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    mesh_summary_rows: List[Dict[str, object]] = []
    comp_rows: List[Dict[str, object]] = []
    dist_rows: List[Dict[str, object]] = []
    lock_rows: List[Dict[str, object]] = []
    helicity_rows: List[Dict[str, object]] = []
    if not args.gear_stl:
        return mesh_summary_rows, comp_rows, dist_rows, lock_rows, helicity_rows
    gear_path = Path(args.gear_stl)
    gear_mesh = load_mesh(gear_path)
    mesh_summary_rows.append(asdict(mesh_summary(gear_mesh, gear_path, 'gear_stl')))
    axle_axis: Optional[np.ndarray] = None
    if args.axle_stl:
        axle_path = Path(args.axle_stl)
        axle_mesh = load_mesh(axle_path)
        mesh_summary_rows.append(asdict(mesh_summary(axle_mesh, axle_path, 'axle_stl')))
        vals, vecs = pca_axes(np.asarray(axle_mesh.vertices, dtype=float))
        axle_axis = unit(vecs[:, 0])
    comp_rows = component_info_rows(gear_mesh, 'gear_stl', axle_axis)
    dist_rows = distance_matrix_rows(comp_rows)
    n_gears = len(comp_rows)
    lock_rows = gear_lock_scenarios(n_gears, args.helix_ratio, args.n_min, args.n_max, args.energy_tol)
    link_csv = Path(args.gear_linking_matrix_csv) if args.gear_linking_matrix_csv else None
    helicity_rows = gear_helicity_rows(link_csv, n_gears)
    return mesh_summary_rows, comp_rows, dist_rows, lock_rows, helicity_rows


# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------


def count_by(rows: List[Dict[str, object]], key: str) -> Dict[str, int]:
    d: Dict[str, int] = {}
    for r in rows:
        k = str(r.get(key, ''))
        d[k] = d.get(k, 0) + 1
    return d


def write_summary(path: Path, args, single_objs: List[SingleObject], single_rows: List[Dict[str, object]], link_objects: List[LinkObject], link_result_rows: List[Dict[str, object]], gear_rows: Dict[str, List[Dict[str, object]]]) -> None:
    lines: List[str] = []
    Omega = args.v_swirl / args.r_c
    T_core = TAU * args.r_c / args.v_swirl
    lines.append('# Unified Compensated Attachment Audit Summary\n\n')
    lines.append('## Purpose\n\n')
    lines.append('This audit tests compensated swirl-clock / entanglement attachment across single torus knots, twist/general single-component controls, multicomponent links, and optional gear-locked STL analogs.\n\n')
    lines.append('```text\n')
    lines.append('chi_total = chi_local + chi_attachment\n')
    lines.append('Canon-safe mode: chi_total = chi, charge_leak = 0, FR odd parity active\n')
    lines.append('Important distinction: integer selection may survive approximate holonomy, but exact Canon requires exact holonomy.\n')
    lines.append('```\n\n')
    lines.append('## Canonical constants\n\n')
    lines.append('| quantity | value |\n|---|---:|\n')
    lines.append(f'| `||v_swirl||` | {args.v_swirl:.12e} m/s |\n')
    lines.append(f'| `r_c` | {args.r_c:.12e} m |\n')
    lines.append(f'| `Omega_core` | {Omega:.12e} s^-1 |\n')
    lines.append(f'| `T_core` | {T_core:.12e} s |\n')
    lines.append(f'| `Omega_core*T_core/(2π)` | {Omega*T_core/TAU:.12f} turns |\n')
    lines.append(f'| `omega_vorticity*T_core/(2π)` | {2*Omega*T_core/TAU:.12f} vorticity-turns |\n')
    lines.append('\n')
    lines.append('## Inputs and row counts\n\n')
    lines.append(f'- single objects: **{len(single_objs)}**\n')
    lines.append(f'- single attachment result rows: **{len(single_rows)}**\n')
    lines.append(f'- multicomponent links parsed: **{len(link_objects)}**\n')
    lines.append(f'- link attachment result rows: **{len(link_result_rows)}**\n')
    lines.append(f'- gear mesh rows: **{len(gear_rows.get("mesh", []))}**\n')
    lines.append(f'- gear lock scenarios: **{len(gear_rows.get("lock", []))}**\n')
    lines.append('\n')
    if single_objs:
        lines.append('## Single-object classes\n\n')
        cls_counts: Dict[str, int] = {}
        for o in single_objs:
            cls_counts[o.object_type] = cls_counts.get(o.object_type, 0) + 1
        lines.append(f'Class counts: `{cls_counts}`\n\n')
        lines.append('| object | type | base rule | base | status |\n|---|---|---|---:|---|\n')
        for o in single_objs[:30]:
            lines.append(f'| `{o.object_id}` | `{o.object_type}` | `{o.base_rule}` | {o.base_sl_abs} | `{o.canon_status}` |\n')
        if len(single_objs) > 30:
            lines.append(f'| ... | ... | ... | ... | {len(single_objs)-30} more rows in CSV |\n')
        lines.append('\n')
    if single_rows:
        lines.append('## Single attachment audit status counts\n\n')
        lines.append(f'`{count_by(single_rows, "audit_status")}`\n\n')
    if link_objects:
        lines.append('## Link objects\n\n')
        lines.append('| object | components | source | member |\n|---|---:|---|---|\n')
        for lo in link_objects:
            lines.append(f'| `{lo.object_id}` | {len(lo.components)} | `{lo.source_path}` | `{lo.member}` |\n')
        lines.append('\n')
    if link_result_rows:
        lines.append('## Link attachment audit status counts\n\n')
        lines.append(f'`{count_by(link_result_rows, "audit_status")}`\n\n')
    if gear_rows.get('mesh'):
        lines.append('## Gear/STL module\n\n')
        lines.append('| mesh | bodies | extents | watertight |\n|---|---:|---|---|\n')
        for r in gear_rows['mesh']:
            lines.append(f"| `{r.get('mesh_label')}` | {r.get('body_count')} | {fmt(r.get('extent_x'))} x {fmt(r.get('extent_y'))} x {fmt(r.get('extent_z'))} | `{r.get('watertight')}` |\n")
        lines.append('\n')
    if gear_rows.get('lock'):
        lines.append('## Gear lock scenario counts\n\n')
        lines.append(f'`{count_by(gear_rows["lock"], "audit_status")}`\n\n')
    lines.append('## Canon-candidate statement\n\n')
    lines.append('```text\n')
    lines.append('[CONDITIONAL CANON-CANDIDATE]\n')
    lines.append('If a compensated neutral core/framing connection exists such that\n')
    lines.append('Hol(A_core)/(2π) = chi_local + chi_attachment = chi,\n')
    lines.append('with charge_leak = 0 and FR odd parity active, then positive twist stiffness selects\n')
    lines.append('n_core = chi.\n\n')
    lines.append('For torus knots:        SL_phys(T(p,q)) = pq + chi.\n')
    lines.append('For twist/general knots: SL_phys(K) = SL_geom_proxy(K) + chi, with proxy status explicit.\n')
    lines.append('For multicomponent links: H/Gamma^2 = sum_i(SL_i + chi_i) + 2 sum_ij Lk_ij + higher.\n')
    lines.append('For gear STL analogs: fully locked sign sectors support a mechanical global-attachment analog.\n')
    lines.append('```\n\n')
    lines.append('## Audit warning\n\n')
    lines.append('This script is an audit harness and model classifier, not a proof machine. Exact neutral compensation remains the physical load-bearing gate.\n')
    path.write_text(''.join(lines), encoding='utf-8')


# -----------------------------------------------------------------------------
# CLI / main
# -----------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description='Unified compensated Attachment-Lemma audit for torus/twist knots, multicomponent links, and gear STL analogs.')
    ap.add_argument('--out-prefix', default='unified_attachment_audit', help='Base name. By default exports go to a folder with this same name.')
    ap.add_argument('--out-dir', default=None, help='Override output folder. If omitted, uses ./<out-prefix>/')

    # single objects
    ap.add_argument('--input-results', default=None, help='Optional core_holonomy_v2_results.csv or compatible CSV.')
    ap.add_argument('--include-controls', action='store_true', help='Include non-torus control/twist rows from --input-results.')
    ap.add_argument('--canonical-only', action='store_true', help='Keep only PASS_DERIVED_PQ torus rows unless --include-noncanonical is set.')
    ap.add_argument('--include-noncanonical', action='store_true', help='Include noncanonical fitted torus diagnostics from input CSV.')
    ap.add_argument('--q-list', default='3,5,7,9,11', help='Fallback analytic torus q-list.')
    ap.add_argument('--p', type=int, default=2, help='Fallback analytic torus p.')
    ap.add_argument('--extra-torus', default='3:2,3:4', help='Fallback extra torus pairs, e.g. 3:2,3:4')

    # link files
    ap.add_argument('--link-file', action='append', default=[], help='Multicomponent link .txt or .zip. Can be repeated.')
    ap.add_argument('--link-member', default=None, help='Optional member name for all link zips.')
    ap.add_argument('--link-sub', type=int, default=32, help='Gauss midpoint subdivision per original segment.')

    # gear module
    ap.add_argument('--gear-stl', default=None, help='Optional gear STL assembly file.')
    ap.add_argument('--axle-stl', default=None, help='Optional axle STL file.')
    ap.add_argument('--gear-linking-matrix-csv', default=None, help='Optional linking matrix CSV to combine with gear module.')
    ap.add_argument('--helix-ratio', type=float, default=1.0, help='psi/Theta ratio for central helix/axle lock model.')

    # attachment kernel
    ap.add_argument('--eps-list', default='0,0.01,0.1,1.0', help='epsilon_SE values.')
    ap.add_argument('--sigma', type=float, default=1.0)
    ap.add_argument('--n-range', default='-5:5', help='Core integer range, e.g. -5:5')
    ap.add_argument('--q-ref', type=int, default=3)
    ap.add_argument('--q-slope', type=float, default=0.01)
    ap.add_argument('--passive-center', type=float, default=2.501)
    ap.add_argument('--partial-fraction', type=float, default=0.5)
    ap.add_argument('--charge-leak-fraction', type=float, default=0.01)
    ap.add_argument('--decoherence-residual', type=float, default=0.005)
    ap.add_argument('--exact-tol', type=float, default=1e-12)
    ap.add_argument('--charge-tol', type=float, default=1e-12)
    ap.add_argument('--energy-tol', type=float, default=1e-12)
    ap.add_argument('--core-models', choices=['canon', 'full'], default='full', help='canon=C0-C2 only; full=C0-C8 diagnostics.')

    # constants
    ap.add_argument('--v-swirl', type=float, default=DEFAULT_V_SWIRL)
    ap.add_argument('--r-c', type=float, default=DEFAULT_R_C)
    return ap


def main() -> None:
    ap = build_arg_parser()
    args = ap.parse_args()
    args.n_min, args.n_max = parse_int_range(args.n_range)

    out_dir, base = output_paths(args.out_prefix, args.out_dir)
    log_file, old_stdout, old_stderr = install_tee(out_dir / f'{base}_runlog.txt')
    try:
        print(f'[config] out_dir={out_dir}')
        print(f'[config] out_base={base}')
        print(f'[config] input_results={args.input_results}')
        print(f'[config] link_files={args.link_file}')
        print(f'[config] gear_stl={args.gear_stl}')
        print(f'[scope] unified compensated swirl-clock / entanglement attachment audit')

        models = attachment_models(include_diagnostics=(args.core_models == 'full'))
        eps_list = parse_num_list(args.eps_list, float)

        # single objects
        single_objs: List[SingleObject] = []
        if args.input_results and Path(args.input_results).exists():
            single_objs = read_single_objects(Path(args.input_results), args.include_controls, args.canonical_only, args.include_noncanonical)
            print(f'[input] read {len(single_objs)} single objects from {args.input_results}')
        if not single_objs:
            single_objs = fallback_torus_objects(parse_q_list(args.q_list), args.p, parse_extra_torus(args.extra_torus))
            print(f'[fallback] generated {len(single_objs)} analytic torus rows')
        single_rows = run_single_attachment(single_objs, models, eps_list, args)

        object_rows = [asdict(o) for o in single_objs]
        model_rows = [asdict(m) for m in models]

        # links
        link_objects: List[LinkObject] = []
        link_comp_rows: List[Dict[str, object]] = []
        link_matrix_rows: List[Dict[str, object]] = []
        link_result_rows: List[Dict[str, object]] = []
        for lf in args.link_file:
            try:
                lo = load_link_object(Path(lf), args.link_member)
                link_objects.append(lo)
                print(f'[link] {lo.object_id}: components={len(lo.components)} from {lf} member={lo.member}')
                L = compute_linking_matrix(lo.components, args.link_sub)
                crows, mrows, rrows = run_link_attachment(lo, L, models, eps_list, args)
                link_comp_rows.extend(crows)
                link_matrix_rows.extend(mrows)
                link_result_rows.extend(rrows)
            except Exception as e:
                print(f'[link][ERROR] {lf}: {e}')

        # gear
        gear_mesh_rows: List[Dict[str, object]] = []
        gear_comp_rows: List[Dict[str, object]] = []
        gear_dist_rows: List[Dict[str, object]] = []
        gear_lock_rows: List[Dict[str, object]] = []
        gear_helicity_rows: List[Dict[str, object]] = []
        if args.gear_stl:
            try:
                gear_mesh_rows, gear_comp_rows, gear_dist_rows, gear_lock_rows, gear_helicity_rows = run_gear_module(args, out_dir, base)
                print(f'[gear] mesh_rows={len(gear_mesh_rows)} components={len(gear_comp_rows)} lock_scenarios={len(gear_lock_rows)}')
            except Exception as e:
                print(f'[gear][ERROR] {e}')

        # writes
        paths = {
            'objects': out_dir / f'{base}_objects.csv',
            'models': out_dir / f'{base}_models.csv',
            'single': out_dir / f'{base}_single_attachment_results.csv',
            'link_components': out_dir / f'{base}_link_components.csv',
            'link_matrix': out_dir / f'{base}_linking_matrices.csv',
            'link_results': out_dir / f'{base}_link_attachment_results.csv',
            'gear_mesh': out_dir / f'{base}_gear_mesh_summary.csv',
            'gear_components': out_dir / f'{base}_gear_components.csv',
            'gear_dist': out_dir / f'{base}_gear_distance_matrix.csv',
            'gear_lock': out_dir / f'{base}_gear_lock_scenarios.csv',
            'gear_helicity': out_dir / f'{base}_gear_helicity_bookkeeping.csv',
            'summary': out_dir / f'{base}_summary.md',
        }
        write_csv(paths['objects'], object_rows)
        write_csv(paths['models'], model_rows)
        write_csv(paths['single'], single_rows)
        write_csv(paths['link_components'], link_comp_rows)
        write_csv(paths['link_matrix'], link_matrix_rows)
        write_csv(paths['link_results'], link_result_rows)
        write_csv(paths['gear_mesh'], gear_mesh_rows)
        write_csv(paths['gear_components'], gear_comp_rows)
        write_csv(paths['gear_dist'], gear_dist_rows)
        write_csv(paths['gear_lock'], gear_lock_rows)
        write_csv(paths['gear_helicity'], gear_helicity_rows)
        write_summary(paths['summary'], args, single_objs, single_rows, link_objects, link_result_rows, {
            'mesh': gear_mesh_rows,
            'components': gear_comp_rows,
            'distance': gear_dist_rows,
            'lock': gear_lock_rows,
            'helicity': gear_helicity_rows,
        })
        for name, p in paths.items():
            print(f'[write] {p}')
        print('[done]')
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        log_file.close()


if __name__ == '__main__':
    main()
