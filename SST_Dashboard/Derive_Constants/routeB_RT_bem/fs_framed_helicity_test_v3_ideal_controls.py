#!/usr/bin/env python3
r"""
fs_framed_helicity_test.py
====================================
Folder-first framed-helicity / self-linking test for SST torus-ladder knots.

Purpose
-------
This script tests the SST-native framed-helicity statement

    H / Gamma^2 = SL = Wr + Tw

on curve data from three sources:

  1. ideal.txt                    (Brian Gilbert ideal-knot Fourier database)
  2. Knots_FourierSeries/*.fseries
  3. knotplot/*.fseries           (KnotPlot-generated Fourier series)

It does NOT perform Faddeev-Skyrme relaxation and does NOT claim to prove the
lattice Hopf charge Q_H.  It is a separate diagnostic for the framed-knot
helicity route: measure Wr, build a closed ribbon framing, measure its linking
number, and report the twist required for the torus-ladder target

    SL_target(T(2,q)) = 2 q + 1.

Default Windows-friendly usage from your project folder:

    python fs_framed_helicity_test.py

It will look for:

    ideal.txt
    Knots_FourierSeries
    knotplot

in the current folder, the script folder, and parent folders. You can override:

    set SST_FSERIES_DIRS=C:\path\to\Knots_FourierSeries;C:\path\to\knotplot
    set SST_IDEAL_TXT=C:\path\to\ideal.txt
    python fs_framed_helicity_test.py --q-list 3,5,7,9,11 --samples 1024

Outputs:

    framed_helicity_results.csv
    framed_helicity_summary.md
    fs_framed_helicity_test_outputlog.txt

Dependencies: numpy only.
"""

from __future__ import annotations

import argparse
import csv
import io
import math
import os
import re
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

TAU = 2.0 * math.pi
FOUR_PI = 4.0 * math.pi


# -----------------------------------------------------------------------------
# Logging / tee
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
# Data model
# -----------------------------------------------------------------------------

@dataclass
class CurveEntry:
    source_type: str       # ideal | fseries | analytic
    label: str             # friendly label
    path: str              # file path or source id
    coeffs: Optional[np.ndarray] = None  # rows [ax,bx,ay,by,az,bz], j starts at 0 or 1 by convention below
    coeff_indices: Optional[np.ndarray] = None
    q: Optional[int] = None
    target_sl: Optional[int] = None
    family: str = "torus"
    canonical_label: str = ""
    notes: str = ""
    control_for_q: Optional[int] = None


# -----------------------------------------------------------------------------
# Discovery
# -----------------------------------------------------------------------------

def parent_chain(start: Path, max_depth: int = 8) -> List[Path]:
    out = []
    p = start.resolve()
    for _ in range(max_depth + 1):
        out.append(p)
        if p.parent == p:
            break
        p = p.parent
    return out


def unique_paths(paths: Iterable[Path]) -> List[Path]:
    seen = set()
    out = []
    for p in paths:
        try:
            key = str(p.resolve())
        except Exception:
            key = str(p)
        if key not in seen and p.exists():
            seen.add(key)
            out.append(p)
    return out


def discover_folder_roots(names=("Knots_FourierSeries", "knotplot")) -> List[Path]:
    candidates: List[Path] = []

    env = os.environ.get("SST_FSERIES_DIRS", "").strip()
    if env:
        sep = ";" if ";" in env else os.pathsep
        for item in env.split(sep):
            item = item.strip().strip('"')
            if item:
                candidates.append(Path(item))

    base_dirs: List[Path] = []
    try:
        base_dirs += parent_chain(Path.cwd())
    except Exception:
        pass
    try:
        base_dirs += parent_chain(Path(__file__).resolve().parent)
    except Exception:
        pass

    for base in base_dirs:
        for name in names:
            candidates.append(base / name)

    return unique_paths(candidates)


def discover_ideal_paths() -> List[Path]:
    candidates: List[Path] = []
    env = os.environ.get("SST_IDEAL_TXT", "").strip().strip('"')
    if env:
        candidates.append(Path(env))

    base_dirs: List[Path] = []
    try:
        base_dirs += parent_chain(Path.cwd())
    except Exception:
        pass
    try:
        base_dirs += parent_chain(Path(__file__).resolve().parent)
    except Exception:
        pass
    for base in base_dirs:
        candidates.append(base / "ideal.txt")
    return unique_paths(candidates)


# -----------------------------------------------------------------------------
# Fourier parsing/evaluation
# -----------------------------------------------------------------------------

def parse_fseries_file(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Parse simple .fseries rows: ax bx ay by az bz. j starts at 1."""
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("%") or s.startswith("#"):
            continue
        parts = s.replace(",", " ").split()
        vals = []
        for p in parts[:6]:
            try:
                vals.append(float(p))
            except ValueError:
                vals = []
                break
        if len(vals) == 6:
            rows.append(vals)
    if not rows:
        raise ValueError(f"no Fourier coefficient rows found in {path}")
    coeffs = np.asarray(rows, dtype=np.float64)
    idx = np.arange(1, coeffs.shape[0] + 1, dtype=np.float64)
    return coeffs, idx


def parse_vec3(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in s.split(",")]
    if len(parts) != 3:
        raise ValueError(f"bad vec3: {s}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def parse_ideal_ab_blocks(ideal_path: Path, include_ids: Optional[set] = None,
                          include_all_single_component: bool = False,
                          max_ideal: int = 0) -> List[CurveEntry]:
    """Parse AB blocks from ideal.txt.

    For single-component knots, coefficients are direct children of AB. Links with
    Component subblocks are skipped by default. Fourier convention is exactly the
    I-index in ideal.txt, including possible I=0 constants.
    """
    text = ideal_path.read_text(encoding="utf-8", errors="ignore")
    block_re = re.compile(r'<AB\s+([^>]*)>(.*?)</AB>', re.S)
    coeff_re = re.compile(
        r'<Coeff\s+[^>]*I="\s*([0-9]+)"\s+A="([^"]+)"\s+B="([^"]+)"\s*/?>',
        re.S,
    )
    id_re = re.compile(r'Id="([^"]+)"')
    entries: List[CurveEntry] = []

    for m in block_re.finditer(text):
        attrs = m.group(1)
        body = m.group(2)
        mid = id_re.search(attrs)
        if not mid:
            continue
        ideal_id = mid.group(1)
        is_multi = "<Component" in body
        if is_multi:
            continue
        if include_ids is not None and ideal_id not in include_ids:
            continue
        if include_ids is None and not include_all_single_component:
            continue

        coeff_rows = []
        indices = []
        for cm in coeff_re.finditer(body):
            i = int(cm.group(1))
            avec = parse_vec3(cm.group(2))
            bvec = parse_vec3(cm.group(3))
            coeff_rows.append([avec[0], bvec[0], avec[1], bvec[1], avec[2], bvec[2]])
            indices.append(float(i))
        if not coeff_rows:
            continue
        coeffs = np.asarray(coeff_rows, dtype=np.float64)
        idx = np.asarray(indices, dtype=np.float64)
        q = q_from_label_or_ideal(ideal_id=ideal_id)
        control_info = IDEAL_CONTROL_INFO.get(ideal_id)
        if control_info is not None:
            family = str(control_info["family"])
            canonical_label = str(control_info["canonical_label"])
            notes = str(control_info["notes"])
            control_for_q = int(control_info.get("control_for_q") or 0) or None
            label = f"ideal:{ideal_id} ({canonical_label})"
            target_sl = None
            q = None
        else:
            family = "torus" if q else "unknown"
            canonical_label = f"T(2,{q})" if q else ""
            notes = ""
            control_for_q = None
            label = f"ideal:{ideal_id}"
            target_sl = (2 * q + 1 if q else None)

        entries.append(CurveEntry(
            source_type="ideal",
            label=label,
            path=str(ideal_path),
            coeffs=coeffs,
            coeff_indices=idx,
            q=q,
            target_sl=target_sl,
            family=family,
            canonical_label=canonical_label,
            notes=notes,
            control_for_q=control_for_q,
        ))
        if max_ideal and len(entries) >= max_ideal:
            break
    return entries


def eval_fourier_curve(coeffs: np.ndarray, idx: np.ndarray, samples: int) -> np.ndarray:
    theta = np.linspace(0.0, TAU, samples, endpoint=False, dtype=np.float64)
    curve = np.zeros((samples, 3), dtype=np.float64)
    # rows: ax bx ay by az bz; x=sum ax cos(jt)+bx sin(jt)
    for row, j in zip(coeffs, idx):
        c = np.cos(j * theta)
        s = np.sin(j * theta)
        curve[:, 0] += row[0] * c + row[1] * s
        curve[:, 1] += row[2] * c + row[3] * s
        curve[:, 2] += row[4] * c + row[5] * s
    return curve


def normalize_curve(curve: np.ndarray) -> np.ndarray:
    c = np.asarray(curve, dtype=np.float64).copy()
    c -= c.mean(axis=0, keepdims=True)
    # normalize RMS radius for comparable epsilon/diagnostics
    rms = math.sqrt(float(np.mean(np.sum(c * c, axis=1))))
    if rms > 0:
        c /= rms
    return c


def analytic_torus_knot(p: int, q: int, samples: int, R: float = 2.0, r: float = 0.65) -> np.ndarray:
    # Standard T(p,q) curve on a torus. For T(2,q), p=2, q odd.
    t = np.linspace(0.0, TAU, samples, endpoint=False, dtype=np.float64)
    x = (R + r * np.cos(q * t)) * np.cos(p * t)
    y = (R + r * np.cos(q * t)) * np.sin(p * t)
    z = r * np.sin(q * t)
    return normalize_curve(np.column_stack([x, y, z]))


# -----------------------------------------------------------------------------
# Target identification
# -----------------------------------------------------------------------------

TORUS_INDEX_Q = {"3_1": 3, "5_1": 5, "7_1": 7, "9_1": 9, "11_1": 11}

# Brian Gilbert / ideal.txt and Knot Atlas alternate ids.
# K11a367 is the 11-crossing member of the T(2,q) torus ladder
# (Knot Atlas notes it as the next knot after trefoil/cinquefoil/septafoil/nonafoil; T(11,2)).
IDEAL_ID_Q = {
    "3:1:1": 3,
    "5:1:1": 5,
    "7:1:1": 7,
    "9:1:1": 9,
    "11:1:1": 11,      # accepted if present in other ideal databases
    "K11a367": 11,     # Knot Atlas alternate for 11_1 = T(2,11) / T(11,2)
}

# Non-torus / twist controls. These are analysed when their parent crossing/
# ladder level is requested, but pq+1 is deliberately NOT applied to them.
# User-supplied identifications:
#   5:1:2   = 5_2 twist knot
#   K11a247 = 11_2 twist knot
IDEAL_CONTROL_INFO = {
    "5:1:2": {
        "canonical_label": "5_2_twist_control",
        "family": "control_twist",
        "control_for_q": 5,
        "notes": "Brian Gilbert ideal id 5:1:2 / user-labelled 5_2 twist control; pq+1 torus target not applied",
    },
    "K11a247": {
        "canonical_label": "11_2_twist_control",
        "family": "control_twist",
        "control_for_q": 11,
        "notes": "Knot Atlas K11a247 / user-labelled 11_2 twist control; pq+1 torus target not applied",
    },
}

# fseries/KnotPlot controls by label. These are included by default when the
# corresponding q appears in --q-list, but they remain controls with no pq+1 target.
CONTROL_LABEL_INFO = [
    (re.compile(r'(^|[/\\._-])(?:knot[._-]?)?5[._]2(?:[A-Za-z]*|$)', re.I), {
        "canonical_label": "5_2_twist_control",
        "family": "control_twist",
        "control_for_q": 5,
        "notes": "fseries label matched 5_2 twist control; pq+1 torus target not applied",
    }),
    (re.compile(r'(^|[/\\._-])(?:knot[._-]?)?11[._]2(?:[A-Za-z]*|$)', re.I), {
        "canonical_label": "11_2_twist_control",
        "family": "control_twist",
        "control_for_q": 11,
        "notes": "fseries label matched 11_2 twist control; pq+1 torus target not applied",
    }),
    (re.compile(r'K11a247', re.I), {
        "canonical_label": "11_2_twist_control",
        "family": "control_twist",
        "control_for_q": 11,
        "notes": "fseries/KnotPlot label matched K11a247 / 11_2 twist control; pq+1 torus target not applied",
    }),
]


def control_info_from_label(label: str) -> Optional[Dict[str, object]]:
    s = (label or "").replace("\\", "/")
    for pat, info in CONTROL_LABEL_INFO:
        if pat.search(s):
            return dict(info)
    return None


def q_from_label_or_ideal(label: str = "", ideal_id: str = "") -> Optional[int]:
    s = (label or ideal_id or "").replace("\\", "/")
    # ideal ids: 3:1:1, 5:1:1, ...
    if ideal_id in IDEAL_ID_Q:
        return IDEAL_ID_Q[ideal_id]
    if label in IDEAL_ID_Q:
        return IDEAL_ID_Q[label]
    # Knot Atlas alternate ids embedded in paths/filenames.
    for atlas_id, qval in IDEAL_ID_Q.items():
        if atlas_id.startswith("K") and atlas_id.lower() in s.lower():
            return qval

    # Explicit torus labels: knot_T2.3, knot_T2_5, T2-7
    m = re.search(r'T\s*2[._:-]?(\d+)', s, re.I)
    if m:
        q = int(m.group(1))
        if q % 2 == 1:
            return q

    # Standard knot labels only when a path component or file stem begins with
    # exactly 3_1, knot.3_1, knot_3.1, etc.  This deliberately avoids false
    # positives like knot_0.3.1 or knot_6.3.1.
    parts = re.split(r'[/\\]+', s)
    candidates = []
    for part in parts:
        stem = part[:-8] if part.lower().endswith('.fseries') else part
        candidates.append(stem)
    for c in candidates:
        m = re.match(r'^(?:knot[._-]?)?(3|5|7|9|11)[._]1(?:[A-Za-z]*|$)', c, re.I)
        if m:
            return int(m.group(1))
    return None


def collect_fseries_entries(roots: Sequence[Path], q_list: Sequence[int], include_all_fseries: bool = False,
                            max_fseries: int = 0, include_twist_controls: bool = True) -> List[CurveEntry]:
    entries: List[CurveEntry] = []
    qset = set(q_list)
    for root in roots:
        for path in sorted(root.rglob("*.fseries")):
            rel = str(path.relative_to(root)).replace("\\", "/")
            q = q_from_label_or_ideal(rel)
            ctrl = control_info_from_label(rel) if include_twist_controls else None

            is_requested_torus = (q is not None and q in qset)
            is_requested_control = bool(ctrl and int(ctrl.get("control_for_q") or -1) in qset)

            if not include_all_fseries and not (is_requested_torus or is_requested_control):
                continue
            try:
                coeffs, idx = parse_fseries_file(path)
            except Exception as e:
                print(f"[WARN] failed to parse fseries {path}: {e}")
                continue

            if ctrl:
                family = str(ctrl["family"])
                canonical_label = str(ctrl["canonical_label"])
                notes = str(ctrl["notes"])
                control_for_q = int(ctrl.get("control_for_q") or 0) or None
                q_out = None
                target_sl = None
            else:
                family = "torus" if q else "unknown"
                canonical_label = f"T(2,{q})" if q else ""
                notes = ""
                control_for_q = None
                q_out = q
                target_sl = (2 * q + 1 if q else None)

            entries.append(CurveEntry(
                source_type="fseries",
                label=f"{root.name}/{rel}",
                path=str(path),
                coeffs=coeffs,
                coeff_indices=idx,
                q=q_out,
                target_sl=target_sl,
                family=family,
                canonical_label=canonical_label,
                notes=notes,
                control_for_q=control_for_q,
            ))
            if max_fseries and len(entries) >= max_fseries:
                return entries
    return entries

def collect_analytic_entries(q_list: Sequence[int]) -> List[CurveEntry]:
    out = []
    for q in q_list:
        out.append(CurveEntry(
            source_type="analytic",
            label=f"analytic:T(2,{q})",
            path="analytic",
            q=q,
            target_sl=2 * q + 1,
            family="torus",
            canonical_label=f"T(2,{q})",
        ))
    return out


# -----------------------------------------------------------------------------
# Geometry: writhe/linking/framing
# -----------------------------------------------------------------------------

def polygon_segments(curve: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    p0 = curve
    p1 = np.roll(curve, -1, axis=0)
    d = p1 - p0
    mid = 0.5 * (p0 + p1)
    return mid, d


def gauss_linking_midpoint(curve_a: np.ndarray, curve_b: np.ndarray, chunk: int = 256,
                           same_curve: bool = False) -> float:
    """Midpoint-rule Gauss linking integral for polygonal closed curves.

    For same_curve=True this estimates writhe. This is a numerical diagnostic,
    not the exact segment-pair formula.
    """
    ma, da = polygon_segments(curve_a)
    mb, db = polygon_segments(curve_b)
    n = ma.shape[0]
    m = mb.shape[0]
    total = 0.0
    eps2 = 1e-30
    for i0 in range(0, n, chunk):
        i1 = min(i0 + chunk, n)
        M = ma[i0:i1, None, :] - mb[None, :, :]
        C = np.cross(da[i0:i1, None, :], db[None, :, :])
        r2 = np.einsum("ijk,ijk->ij", M, M)
        denom = np.power(np.maximum(r2, eps2), 1.5)
        num = np.einsum("ijk,ijk->ij", M, C)
        term = num / denom
        if same_curve and curve_a is curve_b:
            rows = np.arange(i0, i1)
            term[np.arange(i1 - i0), rows] = 0.0
        total += float(np.sum(term))
    return total / FOUR_PI


def curve_diagnostics(curve: np.ndarray) -> Dict[str, float]:
    p0 = curve
    p1 = np.roll(curve, -1, axis=0)
    seg = np.linalg.norm(p1 - p0, axis=1)
    bbox = np.max(curve, axis=0) - np.min(curve, axis=0)
    bbox_diag = float(np.linalg.norm(bbox))
    rms = math.sqrt(float(np.mean(np.sum((curve - curve.mean(axis=0)) ** 2, axis=1))))
    return {
        "seg_min": float(np.min(seg)),
        "seg_mean": float(np.mean(seg)),
        "seg_max": float(np.max(seg)),
        "bbox_diag": bbox_diag,
        "rms_radius": rms,
    }


def rotate_about_axis(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    axis = np.asarray(axis, dtype=np.float64)
    an = float(np.linalg.norm(axis))
    if an < 1e-15 or abs(angle) < 1e-15:
        return v.copy()
    k = axis / an
    v = np.asarray(v, dtype=np.float64)
    return v * math.cos(angle) + np.cross(k, v) * math.sin(angle) + k * float(np.dot(k, v)) * (1.0 - math.cos(angle))


def point_tangents(curve: np.ndarray) -> np.ndarray:
    # centered finite difference tangent at vertices
    t = np.roll(curve, -1, axis=0) - np.roll(curve, 1, axis=0)
    norm = np.linalg.norm(t, axis=1)
    norm[norm < 1e-15] = 1.0
    return t / norm[:, None]


def signed_angle_in_plane(a: np.ndarray, b: np.ndarray, normal: np.ndarray) -> float:
    # signed angle rotating a -> b around normal
    a = a / max(np.linalg.norm(a), 1e-15)
    b = b / max(np.linalg.norm(b), 1e-15)
    n = normal / max(np.linalg.norm(normal), 1e-15)
    return math.atan2(float(np.dot(n, np.cross(a, b))), float(np.dot(a, b)))


def closed_parallel_frame(curve: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return tangents T and a closed approximately parallel normal frame U."""
    T = point_tangents(curve)
    n = len(curve)
    U = np.zeros_like(curve)
    # choose initial normal from least-aligned coordinate axis
    axes = np.eye(3)
    dots = np.abs(axes @ T[0])
    u0 = axes[int(np.argmin(dots))]
    u0 = u0 - np.dot(u0, T[0]) * T[0]
    u0 = u0 / max(np.linalg.norm(u0), 1e-15)
    U[0] = u0

    # transport forward
    for i in range(1, n):
        prev = T[i - 1]
        cur = T[i]
        axis = np.cross(prev, cur)
        angle = math.atan2(float(np.linalg.norm(axis)), float(np.dot(prev, cur)))
        ui = rotate_about_axis(U[i - 1], axis, angle)
        ui = ui - np.dot(ui, cur) * cur
        ui = ui / max(np.linalg.norm(ui), 1e-15)
        U[i] = ui

    # transport last tangent back to first to estimate holonomy
    axis = np.cross(T[-1], T[0])
    angle = math.atan2(float(np.linalg.norm(axis)), float(np.dot(T[-1], T[0])))
    u_end = rotate_about_axis(U[-1], axis, angle)
    u_end = u_end - np.dot(u_end, T[0]) * T[0]
    u_end = u_end / max(np.linalg.norm(u_end), 1e-15)
    hol = signed_angle_in_plane(u_end, U[0], T[0])  # correction needed at end

    # distribute closure correction along the curve
    for i in range(n):
        frac = i / float(n)
        U[i] = rotate_about_axis(U[i], T[i], frac * hol)
        U[i] = U[i] - np.dot(U[i], T[i]) * T[i]
        U[i] = U[i] / max(np.linalg.norm(U[i]), 1e-15)
    return T, U


def add_integer_twist(U: np.ndarray, T: np.ndarray, k: int) -> np.ndarray:
    n = len(U)
    out = np.zeros_like(U)
    for i in range(n):
        phi = TAU * k * (i / float(n))
        out[i] = rotate_about_axis(U[i], T[i], phi)
        out[i] = out[i] - np.dot(out[i], T[i]) * T[i]
        out[i] = out[i] / max(np.linalg.norm(out[i]), 1e-15)
    return out


def framed_offset_curve(curve: np.ndarray, U: np.ndarray, eps: float) -> np.ndarray:
    return curve + eps * U


def analyze_curve(curve: np.ndarray, entry: CurveEntry, samples: int, ribbon_eps_frac: float,
                  chunk: int, compute_target_link: bool = True) -> Dict[str, object]:
    c = normalize_curve(curve)
    diag = curve_diagnostics(c)
    eps = ribbon_eps_frac * diag["bbox_diag"]
    if eps <= 0:
        eps = 1e-3

    wr = gauss_linking_midpoint(c, c, chunk=chunk, same_curve=True)
    T, U0 = closed_parallel_frame(c)
    c0 = framed_offset_curve(c, U0, eps)
    lk0 = gauss_linking_midpoint(c, c0, chunk=chunk, same_curve=False)
    lk0_round = int(round(lk0))
    tw0_est = lk0 - wr
    tw0_round_est = lk0_round - wr

    target_sl = entry.target_sl
    q = entry.q
    extra_k = None
    lk_target = None
    lk_target_round = None
    lk_target_err = None
    tw_target = None
    status = "NO_TARGET"
    if target_sl is not None:
        extra_k = int(target_sl - lk0_round)
        tw_target = float(target_sl - wr)
        if compute_target_link:
            Utarget = add_integer_twist(U0, T, extra_k)
            ct = framed_offset_curve(c, Utarget, eps)
            lk_target = gauss_linking_midpoint(c, ct, chunk=chunk, same_curve=False)
            lk_target_round = int(round(lk_target))
            lk_target_err = float(lk_target - target_sl)
            status = "PASS" if abs(lk_target - target_sl) < 0.25 else "CHECK"
        else:
            status = "TARGET_COMPUTED"

    return {
        "source_type": entry.source_type,
        "family": entry.family,
        "canonical_label": entry.canonical_label,
        "label": entry.label,
        "path": entry.path,
        "q": q,
        "control_for_q": entry.control_for_q,
        "target_SL": target_sl,
        "samples": samples,
        "Wr": float(wr),
        "Lk0": float(lk0),
        "Lk0_round": lk0_round,
        "Tw0_est_Lk0_minus_Wr": float(tw0_est),
        "Tw0_round_est": float(tw0_round_est),
        "extra_integer_twists_to_target": extra_k,
        "Tw_target_targetSL_minus_Wr": tw_target,
        "Lk_target": None if lk_target is None else float(lk_target),
        "Lk_target_round": lk_target_round,
        "Lk_target_error": lk_target_err,
        "ribbon_eps": float(eps),
        "seg_min": diag["seg_min"],
        "seg_mean": diag["seg_mean"],
        "seg_max": diag["seg_max"],
        "bbox_diag": diag["bbox_diag"],
        "status": status,
        "notes": entry.notes,
    }


# -----------------------------------------------------------------------------
# Reporting
# -----------------------------------------------------------------------------

CSV_FIELDS = [
    "source_type", "family", "canonical_label", "label", "path", "q", "control_for_q", "target_SL", "samples",
    "Wr", "Lk0", "Lk0_round", "Tw0_est_Lk0_minus_Wr", "Tw0_round_est",
    "extra_integer_twists_to_target", "Tw_target_targetSL_minus_Wr",
    "Lk_target", "Lk_target_round", "Lk_target_error",
    "ribbon_eps", "seg_min", "seg_mean", "seg_max", "bbox_diag", "status", "notes",
]


def write_csv(rows: List[Dict[str, object]], path: Path):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in CSV_FIELDS})


def fmt(x, nd=6):
    if x is None:
        return ""
    if isinstance(x, float):
        return f"{x:.{nd}g}"
    return str(x)


def write_markdown(rows: List[Dict[str, object]], path: Path, args):
    targeted = [r for r in rows if r.get("target_SL") is not None]
    by_q: Dict[int, List[Dict[str, object]]] = {}
    for r in targeted:
        q = int(r["q"])
        by_q.setdefault(q, []).append(r)

    lines = []
    lines.append("# Framed-helicity test summary")
    lines.append("")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("Core diagnostic:")
    lines.append("")
    lines.append("```text")
    lines.append("H/Gamma^2 = SL = Wr + Tw")
    lines.append("SL_target(T(2,q)) = 2q + 1")
    lines.append("Tw_target = SL_target - Wr")
    lines.append("```")
    lines.append("")
    lines.append(f"Total curves analysed: **{len(rows)}**")
    lines.append(f"Targeted torus-ladder curves: **{len(targeted)}**")
    lines.append(f"Samples per curve: **{args.samples}**")
    lines.append("")

    for q in sorted(by_q):
        lines.append(f"## T(2,{q}) target SL = {2*q+1}")
        lines.append("")
        items = sorted(by_q[q], key=lambda r: abs(float(r.get("Lk_target_error") or 999)))
        lines.append("| source | Wr | Lk0 | extra k | Tw target | Lk target | err | status |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
        for r in items[:12]:
            lines.append(
                f"| `{r['label']}` | {fmt(r['Wr'])} | {fmt(r['Lk0'])} | "
                f"{fmt(r['extra_integer_twists_to_target'])} | {fmt(r['Tw_target_targetSL_minus_Wr'])} | "
                f"{fmt(r['Lk_target'])} | {fmt(r['Lk_target_error'])} | {r['status']} |"
            )
        lines.append("")

    controls = [r for r in rows if str(r.get("family", "")).startswith("control")]
    if controls:
        lines.append("## Twist / non-torus controls")
        lines.append("")
        controls_sorted = sorted(controls, key=lambda r: (str(r.get("canonical_label") or ""), str(r.get("label") or "")))
        lines.append("| control | for q | Wr | Lk0 | Tw0 est | status | notes |")
        lines.append("|---|---:|---:|---:|---:|---|---|")
        for r in controls_sorted[:24]:
            lines.append(
                f"| `{r['label']}` | {fmt(r.get('control_for_q'))} | {fmt(r['Wr'])} | "
                f"{fmt(r['Lk0'])} | {fmt(r['Tw0_est_Lk0_minus_Wr'])} | {r['status']} | {r.get('notes','')} |"
            )
        lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("`PASS` means the constructed framed ribbon numerically links near the target self-linking integer. It does **not** mean the Faddeev--Skyrme lattice relaxation is solved. This is the SST-native framed-helicity diagnostic, separated from the leaking Q_H relaxation pipeline.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def parse_q_list(s: str) -> List[int]:
    out = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        q = int(part)
        if q % 2 == 0:
            print(f"[WARN] q={q} is even; T(2,q) is a link, not a knot. Keeping only if requested.")
        out.append(q)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="SST framed-helicity/self-linking test for ideal.txt + fseries + knotplot curves")
    ap.add_argument("--q-list", default="3,5,7,9,11", help="Comma list of q for T(2,q), default 3,5,7,9,11")
    ap.add_argument("--samples", type=int, default=1024, help="Fourier samples per curve, default 1024")
    ap.add_argument("--chunk", type=int, default=256, help="Gauss integral chunk size, default 256")
    ap.add_argument("--ribbon-eps-frac", type=float, default=0.012, help="Ribbon offset as fraction of bbox diagonal, default 0.012")
    ap.add_argument("--include-analytic", action="store_true", help="Also include analytic T(2,q) controls")
    ap.add_argument("--include-all-fseries", action="store_true", help="Analyze every .fseries found, not only torus-ladder labels")
    ap.add_argument("--include-all-ideal", action="store_true", help="Analyze all single-component ideal.txt entries, not only torus-ladder ids")
    ap.add_argument("--no-twist-controls", action="store_true", help="Do not include explicit non-torus control ids such as K11a247")
    ap.add_argument("--max-fseries", type=int, default=0, help="Limit number of fseries curves, 0=no limit")
    ap.add_argument("--max-ideal", type=int, default=0, help="Limit number of ideal curves, 0=no limit")
    ap.add_argument("--no-target-link", action="store_true", help="Skip measuring target ribbon linking after adding integer twists")
    ap.add_argument("--out-csv", default="framed_helicity_results.csv")
    ap.add_argument("--out-md", default="framed_helicity_summary.md")
    ap.add_argument("--log", default=None, help="Log file. Default <script>_outputlog.txt")
    args = ap.parse_args(argv)

    if args.samples < 64:
        raise SystemExit("--samples must be at least 64")

    log_path = Path(args.log) if args.log else Path(Path(sys.argv[0]).stem + "_outputlog.txt")
    log_file, old_stdout, old_stderr = install_tee(log_path)

    try:
        q_list = parse_q_list(args.q_list)
        qset = set(q_list)
        print(f"[config] q_list={q_list}, samples={args.samples}, chunk={args.chunk}, eps_frac={args.ribbon_eps_frac}")
        print("[scope] This script tests framed helicity/self-linking: SL = Wr + Tw. It does not relax FS Hopfions.")

        roots = discover_folder_roots()
        print("[fseries] folder roots:")
        if roots:
            for r in roots:
                print(f"  - {r}")
        else:
            print("  - none found")

        ideal_paths = discover_ideal_paths()
        print("[ideal] candidate ideal.txt paths:")
        if ideal_paths:
            for p in ideal_paths:
                print(f"  - {p}")
        else:
            print("  - none found")

        entries: List[CurveEntry] = []

        # ideal torus IDs by default. Add explicit controls for q=11 unless disabled.
        ideal_ids = {k for k, q in IDEAL_ID_Q.items() if q in qset}
        if not args.no_twist_controls:
            for cid, info in IDEAL_CONTROL_INFO.items():
                if int(info.get("control_for_q") or -1) in qset:
                    ideal_ids.add(cid)
        for ip in ideal_paths[:1]:
            entries.extend(parse_ideal_ab_blocks(
                ip,
                include_ids=None if args.include_all_ideal else ideal_ids,
                include_all_single_component=args.include_all_ideal,
                max_ideal=args.max_ideal,
            ))

        entries.extend(collect_fseries_entries(
            roots,
            q_list=q_list,
            include_all_fseries=args.include_all_fseries,
            max_fseries=args.max_fseries,
            include_twist_controls=(not args.no_twist_controls),
        ))

        if args.include_analytic:
            entries.extend(collect_analytic_entries(q_list))

        # Drop targetless entries unless include-all flags were used.
        if not args.include_all_fseries and not args.include_all_ideal:
            entries = [e for e in entries if (e.q in qset) or e.family.startswith("control")]

        print(f"[inventory] entries to analyze: {len(entries)}")
        for e in entries[:40]:
            ctrl = f" ctrl_q={e.control_for_q}" if e.control_for_q else ""
            print(f"  - {e.source_type:8s} {e.family:13s} q={e.q or '-':>2}{ctrl:>10s} target={e.target_sl or '-':>3} {e.label}")
        if len(entries) > 40:
            print(f"  ... {len(entries)-40} more")

        rows: List[Dict[str, object]] = []
        for i, e in enumerate(entries, 1):
            try:
                if e.source_type == "analytic":
                    curve = analytic_torus_knot(2, int(e.q), args.samples)
                else:
                    assert e.coeffs is not None and e.coeff_indices is not None
                    curve = eval_fourier_curve(e.coeffs, e.coeff_indices, args.samples)
                row = analyze_curve(
                    curve,
                    e,
                    samples=args.samples,
                    ribbon_eps_frac=args.ribbon_eps_frac,
                    chunk=args.chunk,
                    compute_target_link=not args.no_target_link,
                )
                rows.append(row)
                print(
                    f"[RESULT {i:03d}/{len(entries):03d}] {e.label} "
                    f"q={row['q']} SL*={row['target_SL']} Wr={row['Wr']:+.6f} "
                    f"Lk0={row['Lk0']:+.4f} k={row['extra_integer_twists_to_target']} "
                    f"Tw*={fmt(row['Tw_target_targetSL_minus_Wr'])} "
                    f"Lk*={fmt(row['Lk_target'])} err={fmt(row['Lk_target_error'])} {row['status']}"
                )
            except KeyboardInterrupt:
                raise
            except Exception as ex:
                print(f"[ERROR] failed {e.label}: {ex}")
                traceback.print_exc()

        out_csv = Path(args.out_csv)
        out_md = Path(args.out_md)
        write_csv(rows, out_csv)
        write_markdown(rows, out_md, args)
        print(f"[write] {out_csv.resolve()}")
        print(f"[write] {out_md.resolve()}")
        print("[done]")
        return 0
    finally:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            log_file.flush()
            log_file.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
