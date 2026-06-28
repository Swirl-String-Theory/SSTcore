#!/usr/bin/env python3
r"""
fs_core_twist_audit_v2.py
========================

Non-circular SST core-twist + Core-Holonomy v2 audit for torus-knot swirl strings.

This script is intentionally an AUDIT runner, not a proof machine.  It separates
three different statements that were previously easy to mix:

  A. Target-free torus-surface framing:

       SL_torus(T(p,q)) = +/- p q       (orientation sign is convention)

     This is the non-circular part.  The script verifies it numerically on
     analytic torus knots, and optionally checks whether source curves from
     ideal.txt / .fseries are close to the same fitted torus framing.

  B. Core-twist hypothesis:

       SL_phys = SL_torus + sign(SL_torus) * n_core

     The SST lepton-ladder target |SL_phys| = p q + 1 follows only if
     n_core = +1.  This script reports that requirement explicitly; it does not
     hide it inside a target-injected ribbon.

  C. Energy-selection audit:

       E_null(n)  = k_null (n - 0)^2
       E_model(n) = k_core (n - n0)^2

     If n0=1, the +1 is a MODEL INPUT / POSIT, not a derived result.  The audit
     table makes that explicit.  A future physical background-vorticity model
     must derive n0=1 independently from, e.g., one intrinsic 2*pi core rotation.

It also includes a "circularity trap" diagnostic: inject an arbitrary target
(e.g. 25 or 99) via extra integer ribbon twists and show that it can pass.  This proves
that target-injection tests confirm Calugareanu only, not pq+1.

Folder-first input discovery, like the v4 pipeline:

  - ideal.txt
  - Knots_FourierSeries/**/*.fseries
  - knotplot/**/*.fseries

Optional zip fallback is included for ChatGPT/container testing:

  - Fseries.zip
  - Knotplot_outputs_fseries.zip

Default run:

    python fs_core_twist_audit.py --q-list 3,5,7,9,11 --samples 1024

Outputs:

    core_twist_audit_results.csv
    core_twist_energy_landscape.csv
    core_twist_audit_summary.md
    fs_core_twist_audit_outputlog.txt

Dependencies: numpy only.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import re
import sys
import time
import traceback
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

TAU = 2.0 * math.pi
FOUR_PI = 4.0 * math.pi


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
# Data model and labels
# -----------------------------------------------------------------------------

@dataclass
class CurveEntry:
    source_type: str                 # ideal | fseries | analytic
    label: str
    path: str
    coeffs: Optional[np.ndarray] = None
    coeff_indices: Optional[np.ndarray] = None
    p: int = 2
    q: Optional[int] = None
    family: str = "torus"            # torus | control_twist | unknown
    canonical_label: str = ""
    notes: str = ""
    control_for_q: Optional[int] = None


# Brian Gilbert / ideal.txt and Knot Atlas mappings.
# User-validated labels:
#   3:1:1    = 3_1 trefoil = T(2,3)
#   5:1:2    = 5_2 twist control
#   K11a367  = 11_1 = T(2,11)
#   K11a247  = 11_2 twist control
IDEAL_ID_Q = {
    "3:1:1": 3,
    "5:1:1": 5,
    "7:1:1": 7,
    "9:1:1": 9,
    "11:1:1": 11,
    "K11a367": 11,
}

IDEAL_CONTROL_INFO = {
    "5:1:2": {
        "canonical_label": "5_2_twist_control",
        "family": "control_twist",
        "control_for_q": 5,
        "notes": "Brian Gilbert ideal id 5:1:2 / user-labelled 5_2 twist control; torus pq rule not applied",
    },
    "K11a247": {
        "canonical_label": "11_2_twist_control",
        "family": "control_twist",
        "control_for_q": 11,
        "notes": "Knot Atlas K11a247 / user-labelled 11_2 twist control; torus pq rule not applied",
    },
}

CONTROL_LABEL_INFO = [
    (re.compile(r'(^|[/\\._-])(?:knot[._-]?)?5[._]2(?:[A-Za-z0-9]*|$)', re.I), {
        "canonical_label": "5_2_twist_control",
        "family": "control_twist",
        "control_for_q": 5,
        "notes": "fseries label matched 5_2 twist control; torus pq rule not applied",
    }),
    (re.compile(r'(^|[/\\._-])(?:knot[._-]?)?11[._]2(?:[A-Za-z0-9]*|$)', re.I), {
        "canonical_label": "11_2_twist_control",
        "family": "control_twist",
        "control_for_q": 11,
        "notes": "fseries label matched 11_2 twist control; torus pq rule not applied",
    }),
    (re.compile(r'K11a247', re.I), {
        "canonical_label": "11_2_twist_control",
        "family": "control_twist",
        "control_for_q": 11,
        "notes": "label matched K11a247 / 11_2 twist control; torus pq rule not applied",
    }),
]


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


def unique_existing(paths: Iterable[Path]) -> List[Path]:
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


def base_dirs() -> List[Path]:
    dirs: List[Path] = []
    try:
        dirs += parent_chain(Path.cwd())
    except Exception:
        pass
    try:
        dirs += parent_chain(Path(__file__).resolve().parent)
    except Exception:
        pass
    return dirs


def discover_folder_roots(names=("Knots_FourierSeries", "knotplot")) -> List[Path]:
    candidates: List[Path] = []
    env = os.environ.get("SST_FSERIES_DIRS", "").strip()
    if env:
        sep = ";" if ";" in env else os.pathsep
        for item in env.split(sep):
            item = item.strip().strip('"')
            if item:
                candidates.append(Path(item))
    for base in base_dirs():
        for name in names:
            candidates.append(base / name)
    return unique_existing(candidates)


def discover_ideal_paths() -> List[Path]:
    candidates: List[Path] = []
    env = os.environ.get("SST_IDEAL_TXT", "").strip().strip('"')
    if env:
        candidates.append(Path(env))
    for base in base_dirs():
        candidates.append(base / "ideal.txt")
    return unique_existing(candidates)


def discover_zip_roots(cache_dir: Path, enabled: bool = True) -> List[Path]:
    """Optional convenience fallback: extract Fseries.zip / Knotplot_outputs_fseries.zip.

    This is not needed on the user's normal machine if folders already exist.
    """
    if not enabled:
        return []
    zip_names = ["Fseries.zip", "Knotplot_outputs_fseries.zip", "fseries_batch_results.zip"]
    roots: List[Path] = []
    candidates: List[Path] = []
    for base in base_dirs():
        for zn in zip_names:
            candidates.append(base / zn)
    for zpath in unique_existing(candidates):
        out = cache_dir / zpath.stem
        sentinel = out / ".extracted.ok"
        try:
            if not sentinel.exists():
                out.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zpath, "r") as zf:
                    zf.extractall(out)
                sentinel.write_text(time.strftime("%Y-%m-%d %H:%M:%S"), encoding="utf-8")
            roots.append(out)
        except Exception as e:
            print(f"[WARN] failed zip fallback extraction {zpath}: {e}")
    return unique_existing(roots)


# -----------------------------------------------------------------------------
# Fourier parsing/evaluation
# -----------------------------------------------------------------------------

def parse_fseries_file(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Parse .fseries rows: ax bx ay by az bz. j starts at 1."""
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
        if "<Component" in body:
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
        ctrl = IDEAL_CONTROL_INFO.get(ideal_id)
        if ctrl is not None:
            entries.append(CurveEntry(
                source_type="ideal",
                label=f"ideal:{ideal_id} ({ctrl['canonical_label']})",
                path=str(ideal_path),
                coeffs=coeffs,
                coeff_indices=idx,
                q=None,
                family=str(ctrl["family"]),
                canonical_label=str(ctrl["canonical_label"]),
                notes=str(ctrl["notes"]),
                control_for_q=int(ctrl.get("control_for_q") or 0) or None,
            ))
        else:
            entries.append(CurveEntry(
                source_type="ideal",
                label=f"ideal:{ideal_id}",
                path=str(ideal_path),
                coeffs=coeffs,
                coeff_indices=idx,
                q=q,
                family="torus" if q else "unknown",
                canonical_label=f"T(2,{q})" if q else "",
            ))
        if max_ideal and len(entries) >= max_ideal:
            break
    return entries


def eval_fourier_curve(coeffs: np.ndarray, idx: np.ndarray, samples: int) -> np.ndarray:
    theta = np.linspace(0.0, TAU, samples, endpoint=False, dtype=np.float64)
    curve = np.zeros((samples, 3), dtype=np.float64)
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
    rms = math.sqrt(float(np.mean(np.sum(c * c, axis=1))))
    if rms > 0:
        c /= rms
    return c


def analytic_torus_knot(p: int, q: int, samples: int,
                        R: float = 2.0, r: float = 0.65) -> Tuple[np.ndarray, np.ndarray]:
    """Return normalized analytic T(p,q) curve and its target-free torus normal.

    Convention: x=(R+r cos(qt))cos(pt), y=(R+r cos(qt))sin(pt), z=r sin(qt).
    This gives a signed SL whose sign depends on orientation; |SL| should be pq.
    """
    t = np.linspace(0.0, TAU, samples, endpoint=False, dtype=np.float64)
    curve = np.column_stack([
        (R + r * np.cos(q * t)) * np.cos(p * t),
        (R + r * np.cos(q * t)) * np.sin(p * t),
        r * np.sin(q * t),
    ])
    normal = np.column_stack([
        np.cos(q * t) * np.cos(p * t),
        np.cos(q * t) * np.sin(p * t),
        np.sin(q * t),
    ])
    normal /= np.maximum(np.linalg.norm(normal, axis=1), 1e-15)[:, None]
    return normalize_curve(curve), normal


# -----------------------------------------------------------------------------
# Label identification
# -----------------------------------------------------------------------------

def control_info_from_label(label: str) -> Optional[Dict[str, object]]:
    s = (label or "").replace("\\", "/")
    for pat, info in CONTROL_LABEL_INFO:
        if pat.search(s):
            return dict(info)
    return None


def q_from_label_or_ideal(label: str = "", ideal_id: str = "") -> Optional[int]:
    s = (label or ideal_id or "").replace("\\", "/")
    if ideal_id in IDEAL_ID_Q:
        return IDEAL_ID_Q[ideal_id]
    if label in IDEAL_ID_Q:
        return IDEAL_ID_Q[label]
    for atlas_id, qval in IDEAL_ID_Q.items():
        if atlas_id.startswith("K") and atlas_id.lower() in s.lower():
            return qval

    m = re.search(r'T\s*2[._:-]?(\d+)', s, re.I)
    if m:
        q = int(m.group(1))
        if q % 2 == 1:
            return q

    parts = re.split(r'[/\\]+', s)
    for part in parts:
        stem = part[:-8] if part.lower().endswith('.fseries') else part
        m = re.match(r'^(?:knot[._-]?)?(3|5|7|9|11)[._]1(?:[A-Za-z]*|$)', stem, re.I)
        if m:
            return int(m.group(1))
    return None


def collect_fseries_entries(roots: Sequence[Path], q_list: Sequence[int], include_all_fseries: bool = False,
                            max_fseries: int = 0, include_twist_controls: bool = True) -> List[CurveEntry]:
    entries: List[CurveEntry] = []
    qset = set(q_list)
    seen_paths = set()
    for root in roots:
        for path in sorted(root.rglob("*.fseries")):
            try:
                real_key = str(path.resolve())
            except Exception:
                real_key = str(path)
            if real_key in seen_paths:
                continue
            seen_paths.add(real_key)

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
                entries.append(CurveEntry(
                    source_type="fseries",
                    label=f"{root.name}/{rel}",
                    path=str(path),
                    coeffs=coeffs,
                    coeff_indices=idx,
                    q=None,
                    family=str(ctrl["family"]),
                    canonical_label=str(ctrl["canonical_label"]),
                    notes=str(ctrl["notes"]),
                    control_for_q=int(ctrl.get("control_for_q") or 0) or None,
                ))
            else:
                entries.append(CurveEntry(
                    source_type="fseries",
                    label=f"{root.name}/{rel}",
                    path=str(path),
                    coeffs=coeffs,
                    coeff_indices=idx,
                    q=q,
                    family="torus" if q else "unknown",
                    canonical_label=f"T(2,{q})" if q else "",
                ))
            if max_fseries and len(entries) >= max_fseries:
                return entries
    return entries


def collect_analytic_entries(q_list: Sequence[int], p: int = 2, extra_pq: Sequence[Tuple[int, int]] = ()) -> List[CurveEntry]:
    out = []
    for q in q_list:
        out.append(CurveEntry(
            source_type="analytic",
            label=f"analytic:T({p},{q})",
            path="analytic",
            p=p,
            q=q,
            family="torus",
            canonical_label=f"T({p},{q})",
        ))
    for pp, qq in extra_pq:
        out.append(CurveEntry(
            source_type="analytic",
            label=f"analytic:T({pp},{qq})",
            path="analytic",
            p=pp,
            q=qq,
            family="torus",
            canonical_label=f"T({pp},{qq})",
        ))
    return out


# -----------------------------------------------------------------------------
# Geometry: Gauss integrals, frames, fitted torus surface normal
# -----------------------------------------------------------------------------

def polygon_segments(curve: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    p0 = curve
    p1 = np.roll(curve, -1, axis=0)
    return 0.5 * (p0 + p1), p1 - p0


def gauss_linking_midpoint(curve_a: np.ndarray, curve_b: np.ndarray, chunk: int = 256,
                           same_curve: bool = False) -> float:
    ma, da = polygon_segments(curve_a)
    mb, db = polygon_segments(curve_b)
    n = ma.shape[0]
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
    return {
        "seg_min": float(np.min(seg)),
        "seg_mean": float(np.mean(seg)),
        "seg_max": float(np.max(seg)),
        "bbox_diag": float(np.linalg.norm(bbox)),
        "rms_radius": math.sqrt(float(np.mean(np.sum((curve - curve.mean(axis=0)) ** 2, axis=1)))),
    }


def rotate_about_axis(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    an = float(np.linalg.norm(axis))
    if an < 1e-15 or abs(angle) < 1e-15:
        return v.copy()
    k = axis / an
    return v * math.cos(angle) + np.cross(k, v) * math.sin(angle) + k * float(np.dot(k, v)) * (1.0 - math.cos(angle))


def point_tangents(curve: np.ndarray) -> np.ndarray:
    t = np.roll(curve, -1, axis=0) - np.roll(curve, 1, axis=0)
    norm = np.linalg.norm(t, axis=1)
    norm[norm < 1e-15] = 1.0
    return t / norm[:, None]


def signed_angle_in_plane(a: np.ndarray, b: np.ndarray, normal: np.ndarray) -> float:
    a = a / max(np.linalg.norm(a), 1e-15)
    b = b / max(np.linalg.norm(b), 1e-15)
    n = normal / max(np.linalg.norm(normal), 1e-15)
    return math.atan2(float(np.dot(n, np.cross(a, b))), float(np.dot(a, b)))


def closed_parallel_frame(curve: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    T = point_tangents(curve)
    n = len(curve)
    U = np.zeros_like(curve)
    axes = np.eye(3)
    dots = np.abs(axes @ T[0])
    u0 = axes[int(np.argmin(dots))]
    u0 = u0 - np.dot(u0, T[0]) * T[0]
    u0 = u0 / max(np.linalg.norm(u0), 1e-15)
    U[0] = u0

    for i in range(1, n):
        prev = T[i - 1]
        cur = T[i]
        axis = np.cross(prev, cur)
        angle = math.atan2(float(np.linalg.norm(axis)), float(np.dot(prev, cur)))
        ui = rotate_about_axis(U[i - 1], axis, angle)
        ui = ui - np.dot(ui, cur) * cur
        ui = ui / max(np.linalg.norm(ui), 1e-15)
        U[i] = ui

    axis = np.cross(T[-1], T[0])
    angle = math.atan2(float(np.linalg.norm(axis)), float(np.dot(T[-1], T[0])))
    u_end = rotate_about_axis(U[-1], axis, angle)
    u_end = u_end - np.dot(u_end, T[0]) * T[0]
    u_end = u_end / max(np.linalg.norm(u_end), 1e-15)
    hol = signed_angle_in_plane(u_end, U[0], T[0])

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


def offset_curve(curve: np.ndarray, normal: np.ndarray, eps: float) -> np.ndarray:
    return curve + eps * normal


def fit_torus_surface_normal(curve: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
    """Best-effort target-free fitted torus normal for source curves.

    This is not a proof for arbitrary ideal curves.  It is a diagnostic: if a source
    is already close to a standard torus embedding, the fitted normal should give
    |SL| close to pq.  If not, the source framing is not canonical torus-surface.
    """
    c = normalize_curve(curve)
    X = c - c.mean(axis=0)
    cov = (X.T @ X) / max(len(X), 1)
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    e1, e2, e3 = vecs[:, order[0]], vecs[:, order[1]], vecs[:, order[2]]
    x = X @ e1
    y = X @ e2
    z = X @ e3
    rho = np.sqrt(x * x + y * y)
    R = float(np.mean(rho))
    radial = np.zeros_like(c)
    mask = rho > 1e-12
    radial[mask] = np.outer(x[mask] / rho[mask], e1) + np.outer(y[mask] / rho[mask], e2)
    radial[~mask] = e1
    normal = (rho - R)[:, None] * radial + z[:, None] * e3
    nn = np.linalg.norm(normal, axis=1)
    fallback = nn < 1e-12
    if np.any(fallback):
        normal[fallback] = radial[fallback]
        nn = np.linalg.norm(normal, axis=1)
    normal = normal / np.maximum(nn, 1e-15)[:, None]

    # Quality hints. These do not certify topology; they flag fit plausibility.
    torus_radius_std = float(np.std(np.sqrt((rho - R) ** 2 + z ** 2)))
    minor_radius_mean = float(np.mean(np.sqrt((rho - R) ** 2 + z ** 2)))
    qual = {
        "fit_R_major": R,
        "fit_minor_mean": minor_radius_mean,
        "fit_minor_std": torus_radius_std,
        "fit_minor_cv": torus_radius_std / max(minor_radius_mean, 1e-15),
        "pca_eval_1": float(vals[order[0]]),
        "pca_eval_2": float(vals[order[1]]),
        "pca_eval_3": float(vals[order[2]]),
    }
    return c, normal, qual


# -----------------------------------------------------------------------------
# Core audit and analysis
# -----------------------------------------------------------------------------

def sgn(x: float) -> int:
    return 1 if x >= 0 else -1


def parse_range(s: str) -> List[int]:
    s = s.strip()
    if ":" in s:
        a, b = [int(x.strip()) for x in s.split(":", 1)]
        step = 1 if b >= a else -1
        return list(range(a, b + step, step))
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def parse_extra_torus(s: str) -> List[Tuple[int, int]]:
    if not s.strip():
        return []
    out = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            p, q = part.split(":", 1)
        elif "/" in part:
            p, q = part.split("/", 1)
        else:
            raise ValueError(f"bad --extra-torus item {part!r}; use p:q")
        out.append((int(p), int(q)))
    return out


def core_sl_from_base(base_round_signed: int, n_core_abs: int, mode: str = "follow") -> int:
    """Return signed SL after adding an intrinsic core twist.

    mode='follow': core sign follows the base torus chirality, so |SL|=|base|+n for n>0.
    mode='absolute_positive': always add +n in signed coordinates.
    mode='absolute_negative': always add -n in signed coordinates.
    """
    if mode == "follow":
        return int(base_round_signed + sgn(base_round_signed) * n_core_abs)
    if mode == "absolute_positive":
        return int(base_round_signed + n_core_abs)
    if mode == "absolute_negative":
        return int(base_round_signed - n_core_abs)
    raise ValueError(f"unknown core sign mode {mode}")


def analyze_entry(entry: CurveEntry, args) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    if entry.source_type == "analytic":
        assert entry.q is not None
        curve, surface_normal = analytic_torus_knot(entry.p, int(entry.q), args.samples,
                                                    R=args.torus_R, r=args.torus_r)
        c = curve
        torus_normal_kind = "analytic_surface_normal"
        fit_qual: Dict[str, float] = {}
    else:
        assert entry.coeffs is not None and entry.coeff_indices is not None
        raw = eval_fourier_curve(entry.coeffs, entry.coeff_indices, args.samples)
        c = normalize_curve(raw)
        surface_normal = None
        torus_normal_kind = "not_available"
        fit_qual = {}
        if args.source_torus_fit and entry.q is not None:
            c, surface_normal, fit_qual = fit_torus_surface_normal(raw)
            torus_normal_kind = "pca_fit_surface_normal"

    diag = curve_diagnostics(c)
    eps = args.ribbon_eps_frac * diag["bbox_diag"]
    if eps <= 0:
        eps = 1e-3

    wr = gauss_linking_midpoint(c, c, chunk=args.chunk, same_curve=True)

    # Parallel-transport/closed frame baseline: useful to demonstrate conformation dependence,
    # not a canonical torus-surface proof.
    T, U_pt = closed_parallel_frame(c)
    c_pt = offset_curve(c, U_pt, eps)
    lk_pt = gauss_linking_midpoint(c, c_pt, chunk=args.chunk, same_curve=False)
    lk_pt_round = int(round(lk_pt))

    p = int(entry.p)
    q = entry.q
    expected_pq = p * int(q) if q is not None else None
    expected_pq_plus_1 = expected_pq + 1 if expected_pq is not None else None

    torus_lk = None
    torus_round = None
    torus_abs_err_pq = None
    torus_status = "NO_TORUS_TARGET"
    torus_sign = None
    if surface_normal is not None and expected_pq is not None and entry.family == "torus":
        ct = offset_curve(c, surface_normal, eps)
        torus_lk = gauss_linking_midpoint(c, ct, chunk=args.chunk, same_curve=False)
        torus_round = int(round(torus_lk))
        torus_sign = sgn(torus_lk)
        torus_abs_err_pq = abs(abs(float(torus_lk)) - float(expected_pq))
        if torus_abs_err_pq <= args.pq_abs_tol:
            torus_status = "PASS_DERIVED_PQ"
        elif entry.source_type == "analytic":
            torus_status = "CHECK_ANALYTIC_PQ"
        else:
            torus_status = "SOURCE_FIT_NOT_CANONICAL"

    # Required core twist to move from target-free torus framing to pq+1.
    core_required_abs = None
    if torus_round is not None and expected_pq_plus_1 is not None:
        core_required_abs = int(expected_pq_plus_1 - abs(torus_round))

    # Null and +/-1 consequences.
    sl_null_signed = torus_round
    sl_core_plus1_signed = None if torus_round is None else core_sl_from_base(torus_round, 1, args.core_sign_mode)
    sl_core_minus1_signed = None if torus_round is None else core_sl_from_base(torus_round, -1, args.core_sign_mode)

    # Energy selection model. This does not derive n0; it audits what a posited n0 would select.
    n_values = parse_range(args.n_core_range)
    e_null_vals = {n: args.k_null * (n - 0.0) ** 2 for n in n_values}
    e_model_vals = {n: args.k_core * (n - float(args.core_n0)) ** 2 for n in n_values}
    n_selected_null = min(e_null_vals, key=e_null_vals.get) if n_values else None
    n_selected_model = min(e_model_vals, key=e_model_vals.get) if n_values else None

    energy_status = "NO_TORUS_FRAMING"
    if torus_round is not None:
        if abs(float(args.core_n0) - 1.0) < 1e-12:
            energy_status = "MODEL_INPUT_SELECTS_PLUS_ONE"
        elif abs(float(args.core_n0)) < 1e-12:
            energy_status = "NULL_MODEL_SELECTS_ZERO"
        else:
            energy_status = "MODEL_INPUT_SELECTS_OTHER"

    # Circularity trap: can an arbitrary target be manufactured by integer twisting a closed frame?
    trap_target = args.trap_target
    trap_lk = None
    trap_err = None
    trap_status = "SKIPPED"
    if args.circularity_trap and entry.family == "torus" and trap_target is not None:
        k_trap = int(trap_target - lk_pt_round)
        U_trap = add_integer_twist(U_pt, T, k_trap)
        c_trap = offset_curve(c, U_trap, eps)
        trap_lk = gauss_linking_midpoint(c, c_trap, chunk=args.chunk, same_curve=False)
        trap_err = float(trap_lk - trap_target)
        trap_status = "PASS_ANY_TARGET" if abs(trap_err) <= args.trap_tol else "CHECK_TRAP"

    row: Dict[str, object] = {
        "source_type": entry.source_type,
        "family": entry.family,
        "canonical_label": entry.canonical_label,
        "label": entry.label,
        "path": entry.path,
        "p": p,
        "q": q,
        "control_for_q": entry.control_for_q,
        "expected_pq": expected_pq,
        "expected_pq_plus_1": expected_pq_plus_1,
        "samples": args.samples,
        "Wr": float(wr),
        "PT_Lk0": float(lk_pt),
        "PT_Lk0_round": lk_pt_round,
        "PT_Tw0_est": float(lk_pt - wr),
        "torus_normal_kind": torus_normal_kind,
        "torus_SL": None if torus_lk is None else float(torus_lk),
        "torus_SL_round": torus_round,
        "torus_SL_abs": None if torus_lk is None else abs(float(torus_lk)),
        "torus_SL_abs_err_vs_pq": torus_abs_err_pq,
        "torus_status": torus_status,
        "core_required_abs_to_pq_plus_1": core_required_abs,
        "SL_null_n0_signed": sl_null_signed,
        "SL_null_n0_abs": None if sl_null_signed is None else abs(int(sl_null_signed)),
        "SL_core_plus1_signed": sl_core_plus1_signed,
        "SL_core_plus1_abs": None if sl_core_plus1_signed is None else abs(int(sl_core_plus1_signed)),
        "SL_core_minus1_signed": sl_core_minus1_signed,
        "SL_core_minus1_abs": None if sl_core_minus1_signed is None else abs(int(sl_core_minus1_signed)),
        "n_selected_null": n_selected_null,
        "n_selected_model": n_selected_model,
        "core_n0_model_input": float(args.core_n0),
        "energy_status": energy_status,
        "trap_target": trap_target if args.circularity_trap else None,
        "trap_Lk": None if trap_lk is None else float(trap_lk),
        "trap_error": trap_err,
        "trap_status": trap_status,
        "ribbon_eps": float(eps),
        "seg_min": diag["seg_min"],
        "seg_mean": diag["seg_mean"],
        "seg_max": diag["seg_max"],
        "bbox_diag": diag["bbox_diag"],
        "fit_R_major": fit_qual.get("fit_R_major"),
        "fit_minor_mean": fit_qual.get("fit_minor_mean"),
        "fit_minor_cv": fit_qual.get("fit_minor_cv"),
        "notes": entry.notes,
    }

    landscapes: List[Dict[str, object]] = []
    if torus_round is not None and expected_pq is not None:
        for n in n_values:
            sl_signed = core_sl_from_base(int(torus_round), int(n), args.core_sign_mode)
            landscapes.append({
                "source_type": entry.source_type,
                "label": entry.label,
                "p": p,
                "q": q,
                "expected_pq": expected_pq,
                "torus_SL_round": torus_round,
                "n_core": n,
                "SL_phys_signed": sl_signed,
                "SL_phys_abs": abs(sl_signed),
                "matches_pq": abs(sl_signed) == expected_pq,
                "matches_pq_plus_1": abs(sl_signed) == expected_pq_plus_1,
                "E_null": e_null_vals[n],
                "E_model": e_model_vals[n],
                "selected_by_null": n == n_selected_null,
                "selected_by_model": n == n_selected_model,
                "core_n0_model_input": float(args.core_n0),
                "status": torus_status,
            })
    return row, landscapes


# -----------------------------------------------------------------------------
# Reporting
# -----------------------------------------------------------------------------

RESULT_FIELDS = [
    "source_type", "family", "canonical_label", "label", "path", "p", "q", "control_for_q",
    "expected_pq", "expected_pq_plus_1", "samples",
    "Wr", "PT_Lk0", "PT_Lk0_round", "PT_Tw0_est",
    "torus_normal_kind", "torus_SL", "torus_SL_round", "torus_SL_abs", "torus_SL_abs_err_vs_pq", "torus_status",
    "core_required_abs_to_pq_plus_1", "SL_null_n0_signed", "SL_null_n0_abs",
    "SL_core_plus1_signed", "SL_core_plus1_abs", "SL_core_minus1_signed", "SL_core_minus1_abs",
    "n_selected_null", "n_selected_model", "core_n0_model_input", "energy_status",
    "trap_target", "trap_Lk", "trap_error", "trap_status",
    "ribbon_eps", "seg_min", "seg_mean", "seg_max", "bbox_diag",
    "fit_R_major", "fit_minor_mean", "fit_minor_cv", "notes",
]

LANDSCAPE_FIELDS = [
    "source_type", "label", "p", "q", "expected_pq", "torus_SL_round", "n_core",
    "SL_phys_signed", "SL_phys_abs", "matches_pq", "matches_pq_plus_1",
    "E_null", "E_model", "selected_by_null", "selected_by_model", "core_n0_model_input", "status",
]


def write_csv(rows: List[Dict[str, object]], path: Path, fields: Sequence[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields))
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


def fmt(x, nd=6):
    if x is None:
        return ""
    if isinstance(x, float):
        return f"{x:.{nd}g}"
    return str(x)


def status_counts(rows: List[Dict[str, object]], key: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in rows:
        k = str(r.get(key))
        out[k] = out.get(k, 0) + 1
    return out


def write_markdown(rows: List[Dict[str, object]], landscapes: List[Dict[str, object]], path: Path, args):
    analytic = [r for r in rows if r.get("source_type") == "analytic" and r.get("expected_pq") is not None]
    source_torus = [r for r in rows if r.get("source_type") in ("ideal", "fseries") and r.get("expected_pq") is not None]
    controls = [r for r in rows if str(r.get("family", "")).startswith("control")]
    traps = [r for r in rows if r.get("trap_status") in ("PASS_ANY_TARGET", "CHECK_TRAP")]

    lines: List[str] = []
    lines.append("# Core-twist audit summary")
    lines.append("")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This audit separates three statements that must not be conflated:")
    lines.append("")
    lines.append("```text")
    lines.append("[DERIVED CHECK]    torus-surface framing: |SL_torus(T(p,q))| = p q")
    lines.append("[POSITED CHECK]    physical SST core adds n_core = +1")
    lines.append("[CONDITIONAL]      |SL_phys| = p q + 1 iff n_core = +1")
    lines.append("[CIRCULARITY TRAP] arbitrary target injection can PASS any integer target")
    lines.append("```")
    lines.append("")
    lines.append(f"Curves analysed: **{len(rows)}**; energy landscape rows: **{len(landscapes)}**")
    lines.append(f"Samples: **{args.samples}**; q-list: `{args.q_list}`; n-core range: `{args.n_core_range}`")
    lines.append("")

    lines.append("## A. Target-free analytic torus-surface framing")
    lines.append("")
    lines.append("These rows are the non-circular check. No `2q+1` target is injected; the offset direction is the analytic torus surface normal.")
    lines.append("")
    if analytic:
        lines.append("| curve | expected pq | measured SL | |SL|-pq err | status | n needed for pq+1 |")
        lines.append("|---|---:|---:|---:|---|---:|")
        for r in sorted(analytic, key=lambda x: (int(x.get("p") or 0), int(x.get("q") or 0))):
            lines.append(
                f"| `{r['label']}` | {fmt(r['expected_pq'])} | {fmt(r['torus_SL'])} | "
                f"{fmt(r['torus_SL_abs_err_vs_pq'])} | {r['torus_status']} | {fmt(r['core_required_abs_to_pq_plus_1'])} |"
            )
    else:
        lines.append("No analytic torus rows were included.")
    lines.append("")

    lines.append("## B. Source curves: fitted torus-framing diagnostic")
    lines.append("")
    lines.append("For ideal/fseries curves the fitted torus normal is diagnostic only. A mismatch means the source conformation/framing is not the canonical torus-surface embedding; it does not falsify the analytic theorem.")
    lines.append("")
    if source_torus:
        lines.append("| source | expected pq | fitted SL | abs err | PT Lk0 | status |")
        lines.append("|---|---:|---:|---:|---:|---|")
        items = sorted(source_torus, key=lambda r: (int(r.get("q") or 0), str(r.get("label") or "")))
        for r in items[:80]:
            lines.append(
                f"| `{r['label']}` | {fmt(r['expected_pq'])} | {fmt(r['torus_SL'])} | "
                f"{fmt(r['torus_SL_abs_err_vs_pq'])} | {fmt(r['PT_Lk0'])} | {r['torus_status']} |"
            )
        if len(items) > 80:
            lines.append(f"\n... {len(items)-80} more source rows omitted. See CSV.")
    else:
        lines.append("No source torus rows were included or `--source-torus-fit` was disabled.")
    lines.append("")

    lines.append("## C. Core-twist audit")
    lines.append("")
    lines.append("For every row with a target-free torus framing, the lepton-ladder value `pq+1` requires exactly:")
    lines.append("")
    lines.append("```text")
    lines.append("n_core_required = (pq + 1) - |round(SL_torus)|")
    lines.append("```")
    lines.append("")
    lines.append("If `n_core_required = 1`, the old `pq+1` rule has been reduced to the single open rule `n_core=+1`.")
    lines.append("")
    core_rows = [r for r in rows if r.get("core_required_abs_to_pq_plus_1") is not None]
    if core_rows:
        lines.append("| source | pq | |SL(n=0)| | |SL(n=+1)| | required n | selected by null | selected by model | model status |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
        for r in sorted(core_rows, key=lambda x: (str(x.get("source_type")), int(x.get("q") or 0), str(x.get("label"))))[:80]:
            lines.append(
                f"| `{r['label']}` | {fmt(r['expected_pq'])} | {fmt(r['SL_null_n0_abs'])} | "
                f"{fmt(r['SL_core_plus1_abs'])} | {fmt(r['core_required_abs_to_pq_plus_1'])} | "
                f"{fmt(r['n_selected_null'])} | {fmt(r['n_selected_model'])} | {r['energy_status']} |"
            )
    lines.append("")
    lines.append("Energy note: `E_model` uses `core_n0` as an explicit model input. With the default `core_n0=1`, the script reports `MODEL_INPUT_SELECTS_PLUS_ONE`, not `[DERIVED]`.")
    lines.append("")

    if controls:
        lines.append("## D. Twist / non-torus controls")
        lines.append("")
        lines.append("These are intentionally not tested against the torus pq or pq+1 rule.")
        lines.append("")
        lines.append("| control | for q | Wr | PT Lk0 | status | notes |")
        lines.append("|---|---:|---:|---:|---|---|")
        for r in sorted(controls, key=lambda x: str(x.get("label") or "")):
            lines.append(
                f"| `{r['label']}` | {fmt(r.get('control_for_q'))} | {fmt(r.get('Wr'))} | "
                f"{fmt(r.get('PT_Lk0'))} | {r.get('family')} | {r.get('notes','')} |"
            )
        lines.append("")

    lines.append("## E. Circularity trap")
    lines.append("")
    if traps:
        counts = status_counts(traps, "trap_status")
        lines.append(f"Trap target: `{args.trap_target}`. Status counts: `{counts}`")
        lines.append("")
        lines.append("If these pass, that proves integer target-injection is circular: the same method can manufacture an arbitrary self-linking target.")
        lines.append("")
        lines.append("| source | trap target | trap Lk | err | status |")
        lines.append("|---|---:|---:|---:|---|")
        for r in sorted(traps, key=lambda x: str(x.get("label")))[:30]:
            lines.append(f"| `{r['label']}` | {fmt(r['trap_target'])} | {fmt(r['trap_Lk'])} | {fmt(r['trap_error'])} | {r['trap_status']} |")
    else:
        lines.append("Circularity trap disabled.")
    lines.append("")

    lines.append("## Audit labels")
    lines.append("")
    lines.append("```text")
    lines.append("[DERIVED]      |SL_torus(T(p,q))| = p q for target-free torus-surface framing, if analytic rows pass.")
    lines.append("[POSITED]      n_core = +1 unless an independent background/core model derives core_n0=1.")
    lines.append("[CONDITIONAL]  |SL_phys| = p q + 1 iff n_core=+1.")
    lines.append("[CIRCULAR]     Any test that sets extra_k = target - round(Lk0) and then confirms target.")
    lines.append("[CONTROL]      5_2 / 11_2 twist knots are non-torus controls, not falsifiers of the T(2,q) rule.")
    lines.append("```")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")




# -----------------------------------------------------------------------------
# Core Holonomy Audit v2: FR parity + attachment + twist-energy gates
# -----------------------------------------------------------------------------

V_SWIRL_CANON = 1.09384563e6       # m/s, ||v_{swirl}||
R_C_CANON = 1.40897017e-15         # m

GATE_SCENARIO_FIELDS = [
    "source_type", "family", "label", "p", "q", "expected_pq", "torus_status",
    "scenario", "scenario_status", "epistemic_label",
    "parity", "allowed_n", "holonomy_model", "attachment", "chirality",
    "phi_turns", "phi_integer_error", "center_n0", "selected_n_core", "selected_degenerate",
    "E_selected", "C_T", "L_est", "energy_prefactor", "SL_torus_round",
    "SL_phys_signed", "SL_phys_abs", "matches_pq", "matches_pq_plus_1",
    "gate_pass_FR", "gate_pass_attachment", "gate_pass_energy", "gate_pass_integer_holonomy",
    "notes",
]


def integer_distance(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    return abs(float(x) - round(float(x)))


def allowed_by_parity(n_values: Sequence[int], parity: str) -> List[int]:
    if parity == "none":
        return list(n_values)
    if parity == "odd":
        return [n for n in n_values if n % 2 != 0]
    if parity == "even":
        return [n for n in n_values if n % 2 == 0]
    raise ValueError(f"unknown parity {parity!r}")


def select_minima(n_values: Sequence[int], center: float, prefactor: float, tol: float = 1e-12):
    if not n_values:
        return [], None, {}
    energies = {int(n): float(prefactor) * (float(n) - float(center)) ** 2 for n in n_values}
    emin = min(energies.values())
    mins = [n for n, e in energies.items() if abs(e - emin) <= tol * max(1.0, abs(emin))]
    return mins, emin, energies


def sl_from_n_signed(sl_torus_round: Optional[int], n_core: Optional[int], chirality: str = "follow") -> Optional[int]:
    if sl_torus_round is None or n_core is None:
        return None
    if chirality == "follow":
        return int(sl_torus_round + sgn(sl_torus_round) * abs(int(n_core)))
    return int(sl_torus_round + int(n_core))


def row_line_length_est(row: Dict[str, object]) -> Optional[float]:
    try:
        seg_mean = float(row.get("seg_mean"))
        samples = int(row.get("samples"))
        if seg_mean > 0 and samples > 0:
            return seg_mean * samples
    except Exception:
        pass
    return None


def core_cycle_numbers(args) -> Dict[str, float]:
    v = float(getattr(args, "v_swirl", V_SWIRL_CANON))
    rc = float(getattr(args, "r_c", R_C_CANON))
    omega = v / rc
    T = TAU * rc / v
    return {
        "v_swirl": v,
        "r_c": rc,
        "Omega_core": omega,
        "T_core": T,
        "Omega_T": omega * T,
        "Omega_T_turns": omega * T / TAU,
        "omega_vorticity_T_turns": 2.0 * omega * T / TAU,
    }


def make_gate_scenario_rows(rows: List[Dict[str, object]], args) -> List[Dict[str, object]]:
    """Build M0--M5 audit rows.

    This is the v2 layer. It does not change the geometric measurement. It audits
    which extra assumptions are needed to select n_core=chi.
    """
    n_values = parse_range(args.n_core_range)
    C_T = float(getattr(args, "C_T", 1.0))
    chi_matter = int(getattr(args, "matter_chi", 1))
    chi_anti = -chi_matter
    passive_turns = float(getattr(args, "twoomega_transit_turns", 2.501))
    hol = core_cycle_numbers(args)
    canon_turns = hol["Omega_T_turns"]  # exactly 1 within roundoff
    int_tol = float(getattr(args, "holonomy_integer_tol", 1e-9))

    scenario_defs = [
        {
            "scenario": "M0_NONE",
            "status": "BOSONIC_DEFAULT",
            "epistemic": "CONTROL",
            "parity": "none",
            "holonomy_model": "none",
            "attachment": "none",
            "chirality": "unsigned",
            "phi_turns": 0.0,
            "center": 0.0,
            "notes": "No FR parity and no holonomy attachment: default twist stiffness selects n_core=0.",
        },
        {
            "scenario": "M1_FR_ONLY",
            "status": "LOWEST_ODD_SELECTED",
            "epistemic": "DERIVED_CONDITIONAL_GIVEN_FR",
            "parity": "odd",
            "holonomy_model": "none",
            "attachment": "none",
            "chirality": "unsigned",
            "phi_turns": 0.0,
            "center": 0.0,
            "notes": "FR odd-sector constraint plus positive twist stiffness selects the degenerate pair n_core=±1.",
        },
        {
            "scenario": "M2_CANON_CYCLE_LOCAL_ONLY",
            "status": "LOCAL_IDENTITY_ONLY",
            "epistemic": "KINEMATIC_ONLY_ATTACHMENT_REQUIRED",
            "parity": "none",
            "holonomy_model": "canon_core_cycle",
            "attachment": "none",
            "chirality": "unsigned",
            "phi_turns": canon_turns,
            "center": None,
            "notes": "Omega_core*T_core=2π is local/kinematic only; without global attachment it does not select a closed-knot n_core.",
        },
        {
            "scenario": "M3_CANON_CYCLE_ATTACHED_MATTER",
            "status": "CONDITIONAL_CANON_CANDIDATE",
            "epistemic": "DERIVED_CONDITIONAL_FR_ATTACHMENT_CT_POSITIVE",
            "parity": "odd",
            "holonomy_model": "canon_core_cycle",
            "attachment": "global",
            "chirality": "matter",
            "phi_turns": float(chi_matter) * canon_turns,
            "center": float(chi_matter) * canon_turns,
            "notes": "FR odd-sector + global core-cycle attachment + C_T>0 selects n_core=+1 for matter.",
        },
        {
            "scenario": "M4_CANON_CYCLE_ATTACHED_ANTIMATTER",
            "status": "CONDITIONAL_MIRROR_SECTOR",
            "epistemic": "DERIVED_CONDITIONAL_FR_ATTACHMENT_CT_POSITIVE",
            "parity": "odd",
            "holonomy_model": "canon_core_cycle",
            "attachment": "global",
            "chirality": "antimatter",
            "phi_turns": float(chi_anti) * canon_turns,
            "center": float(chi_anti) * canon_turns,
            "notes": "FR odd-sector + global core-cycle attachment + C_T>0 selects n_core=-1 for antimatter.",
        },
        {
            "scenario": "M5_TWOOMEGA_TRANSIT",
            "status": "PASSIVE_ADVECTION_FAILS",
            "epistemic": "NEGATIVE_CONTROL",
            "parity": "none",
            "holonomy_model": "twoomega_transit",
            "attachment": "passive_transit",
            "chirality": "unsigned",
            "phi_turns": passive_turns,
            "center": passive_turns,
            "notes": "Passive two-omega transit is a non-integer holonomy center by default; it cannot by itself define an integer core twist sector.",
        },
    ]

    out: List[Dict[str, object]] = []
    for row in rows:
        if row.get("expected_pq") is None or row.get("torus_SL_round") is None:
            continue
        sl0 = int(row.get("torus_SL_round"))
        expected_pq = int(row.get("expected_pq"))
        expected_pq_plus_1 = int(row.get("expected_pq_plus_1"))
        L_est = row_line_length_est(row)
        pref = (2.0 * math.pi * math.pi * C_T / L_est) if (L_est and L_est > 0) else C_T
        for sd in scenario_defs:
            allowed = allowed_by_parity(n_values, sd["parity"])
            phi_turns = sd["phi_turns"]
            center = sd["center"]
            phi_err = integer_distance(phi_turns)
            selected = None
            degenerate = ""
            E_selected = None
            if center is not None and allowed:
                mins, E_selected, energies = select_minima(allowed, center, pref)
                if mins:
                    if len(mins) == 1:
                        selected = int(mins[0])
                    else:
                        selected = None
                        degenerate = ",".join(str(m) for m in mins)
            # Scenario M2 deliberately avoids selection, even though local center is 1.
            if sd["scenario"] == "M2_CANON_CYCLE_LOCAL_ONLY":
                selected = None
                degenerate = ""
                E_selected = None
            # Signed convention note:
            # The measured torus SL may be negative depending on orientation.  For the
            # attached canon-cycle matter/antimatter branches, the local core twist
            # n_core=±1 is reported as selected_n_core, but the global co-oriented
            # self-linking magnitude must increase by one: |SL_phys|=|SL_torus|+1.
            # Matter keeps the measured orientation; antimatter is reported as the
            # mirror signed sector.  Negative-control scenarios use direct signed
            # addition and are not used as pq+1 proofs.
            sl_phys = None
            if selected is not None:
                if sd["scenario"] == "M3_CANON_CYCLE_ATTACHED_MATTER":
                    sl_phys = int(sgn(sl0) * (abs(sl0) + abs(int(selected))))
                elif sd["scenario"] == "M4_CANON_CYCLE_ATTACHED_ANTIMATTER":
                    sl_phys = int(-sgn(sl0) * (abs(sl0) + abs(int(selected))))
                else:
                    sl_phys = int(sl0 + int(selected))
            # For M1 degenerate ±1, no single matter/antimatter sign is selected.
            if degenerate:
                sl_phys = None
            out.append({
                "source_type": row.get("source_type"),
                "family": row.get("family"),
                "label": row.get("label"),
                "p": row.get("p"),
                "q": row.get("q"),
                "expected_pq": expected_pq,
                "torus_status": row.get("torus_status"),
                "scenario": sd["scenario"],
                "scenario_status": sd["status"],
                "epistemic_label": sd["epistemic"],
                "parity": sd["parity"],
                "allowed_n": " ".join(str(n) for n in allowed),
                "holonomy_model": sd["holonomy_model"],
                "attachment": sd["attachment"],
                "chirality": sd["chirality"],
                "phi_turns": float(phi_turns) if phi_turns is not None else None,
                "phi_integer_error": phi_err,
                "center_n0": center,
                "selected_n_core": selected,
                "selected_degenerate": degenerate,
                "E_selected": E_selected,
                "C_T": C_T,
                "L_est": L_est,
                "energy_prefactor": pref,
                "SL_torus_round": sl0,
                "SL_phys_signed": sl_phys,
                "SL_phys_abs": None if sl_phys is None else abs(int(sl_phys)),
                "matches_pq": None if sl_phys is None else abs(int(sl_phys)) == expected_pq,
                "matches_pq_plus_1": None if sl_phys is None else abs(int(sl_phys)) == expected_pq_plus_1,
                "gate_pass_FR": (sd["parity"] == "odd"),
                "gate_pass_attachment": (sd["attachment"] == "global"),
                "gate_pass_energy": (C_T > 0 and selected is not None),
                "gate_pass_integer_holonomy": (phi_err is not None and phi_err <= int_tol),
                "notes": sd["notes"],
            })
    return out


def write_gate_markdown(rows: List[Dict[str, object]], gate_rows: List[Dict[str, object]], path: Path, args):
    hol = core_cycle_numbers(args)
    lines: List[str] = []
    lines.append("# Core-Holonomy v2 audit summary")
    lines.append("")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Canon-candidate proof stack")
    lines.append("")
    lines.append("```text")
    lines.append("[DERIVED]              |SL_torus(T(p,q))| = p q for canonical torus-surface framing.")
    lines.append("[FR-GATE / CONDITIONAL] If core-frame winding realizes the nontrivial FR loop, n_core is odd.")
    lines.append("[KINEMATIC IDENTITY]   Omega_core*T_core = 2π by SST core definitions.")
    lines.append("[ATTACHMENT / OPEN]    Local core cycle must attach globally as closed-knot framing holonomy.")
    lines.append("[ENERGY / CONDITIONAL] Given attachment and C_T>0, E_twist selects n_core=chi.")
    lines.append("[CONDITIONAL]          SL_phys(T(p,q)) = SL_torus(T(p,q)) + chi.")
    lines.append("```")
    lines.append("")
    lines.append("## Canonical core-cycle constants")
    lines.append("")
    lines.append("The local core cycle is kinematic, not by itself a global holonomy theorem.")
    lines.append("")
    lines.append("| quantity | value |")
    lines.append("|---|---:|")
    lines.append(f"| `||v_swirl||` | {hol['v_swirl']:.12e} m/s |")
    lines.append(f"| `r_c` | {hol['r_c']:.12e} m |")
    lines.append(f"| `Omega_core = ||v_swirl||/r_c` | {hol['Omega_core']:.12e} s^-1 |")
    lines.append(f"| `T_core = 2π r_c/||v_swirl||` | {hol['T_core']:.12e} s |")
    lines.append(f"| `Omega_core*T_core/(2π)` | {hol['Omega_T_turns']:.12f} turns |")
    lines.append(f"| `omega_vorticity*T_core/(2π)` | {hol['omega_vorticity_T_turns']:.12f} vorticity-turns |")
    lines.append("")
    lines.append("Important: the framing angle integrates angular velocity `Omega_core`, not vorticity `omega_core=2 Omega_core`; equivalently `dtheta_frame = 0.5 omega_core dt`.")
    lines.append("")
    lines.append("## M0--M5 scenario matrix")
    lines.append("")
    # Count by scenario/status
    counts: Dict[str, int] = {}
    for gr in gate_rows:
        key = f"{gr.get('scenario')}:{gr.get('scenario_status')}"
        counts[key] = counts.get(key, 0) + 1
    lines.append(f"Gate rows: **{len(gate_rows)}**. Counts: `{counts}`")
    lines.append("")
    # Representative analytic rows only for readability
    rep = [gr for gr in gate_rows if gr.get("source_type") == "analytic" and gr.get("q") in (3,5,7,9,11)]
    lines.append("| curve | scenario | parity | holonomy | attachment | chi | center | selected n | degenerate | |SL_phys| | status |")
    lines.append("|---|---|---|---|---|---|---:|---:|---|---:|---|")
    for gr in rep[:60]:
        lines.append(
            f"| `{gr.get('label')}` | `{gr.get('scenario')}` | {gr.get('parity')} | {gr.get('holonomy_model')} | "
            f"{gr.get('attachment')} | {gr.get('chirality')} | {fmt(gr.get('center_n0'))} | {fmt(gr.get('selected_n_core'))} | "
            f"{gr.get('selected_degenerate') or ''} | {fmt(gr.get('SL_phys_abs'))} | {gr.get('scenario_status')} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("```text")
    lines.append("M0_NONE: no FR and no holonomy -> n_core=0, bosonic/default sector.")
    lines.append("M1_FR_ONLY: odd FR sector -> lowest odd pair n_core=±1, but no matter/antimatter sign.")
    lines.append("M2_CANON_CYCLE_LOCAL_ONLY: Omega*T=2π is local only; no global n_core selected.")
    lines.append("M3_CANON_CYCLE_ATTACHED_MATTER: with FR+attachment+C_T>0 -> n_core=+1.")
    lines.append("M4_CANON_CYCLE_ATTACHED_ANTIMATTER: with FR+attachment+C_T>0 -> n_core=-1.")
    lines.append("M5_TWOOMEGA_TRANSIT: passive transit noninteger center -> not a valid integer core-twist theorem.")
    lines.append("```")
    lines.append("")
    lines.append("## Audit conclusion")
    lines.append("")
    lines.append("The +1 core twist is not inserted as a target in M3. It is selected only after three explicit gates: FR parity identification, global core-cycle attachment, and positive twist stiffness. The attachment lemma remains the main open/load-bearing step.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")

# -----------------------------------------------------------------------------
# CLI
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
    ap = argparse.ArgumentParser(description="Non-circular SST core-twist audit: torus framing pq + posited core twist")
    ap.add_argument("--q-list", default="3,5,7,9,11", help="Comma-list q for T(2,q). Default 3,5,7,9,11")
    ap.add_argument("--p", type=int, default=2, help="Default p for torus ladder. Default 2")
    ap.add_argument("--extra-torus", default="3:2,3:4", help="Extra analytic torus checks as p:q list. Default 3:2,3:4")
    ap.add_argument("--samples", type=int, default=1024, help="Samples per curve. Default 1024")
    ap.add_argument("--chunk", type=int, default=256, help="Gauss integral chunk size. Default 256")
    ap.add_argument("--ribbon-eps-frac", type=float, default=0.008, help="Ribbon offset fraction of bbox diagonal. Default 0.008")
    ap.add_argument("--pq-abs-tol", type=float, default=0.25, help="Tolerance for |SL|-pq PASS. Default 0.25")
    ap.add_argument("--torus-R", type=float, default=2.0, help="Analytic torus major radius. Default 2.0")
    ap.add_argument("--torus-r", type=float, default=0.65, help="Analytic torus minor radius. Default 0.65")

    ap.add_argument("--include-analytic", action=argparse.BooleanOptionalAction, default=True,
                    help="Include analytic torus checks. Default true")
    ap.add_argument("--source-torus-fit", action=argparse.BooleanOptionalAction, default=True,
                    help="Try fitted torus surface normal for ideal/fseries. Default true")
    ap.add_argument("--include-all-fseries", action="store_true", help="Analyze every .fseries found")
    ap.add_argument("--include-all-ideal", action="store_true", help="Analyze all single-component ideal.txt entries")
    ap.add_argument("--no-twist-controls", action="store_true", help="Skip twist controls such as 5_2, 11_2")
    ap.add_argument("--no-zip-fallback", action="store_true", help="Do not auto-extract Fseries.zip/Knotplot zip fallback")
    ap.add_argument("--max-fseries", type=int, default=0, help="Limit fseries entries. 0=no limit")
    ap.add_argument("--max-ideal", type=int, default=0, help="Limit ideal entries. 0=no limit")

    ap.add_argument("--n-core-range", default="-3:3", help="Integer n_core range, e.g. -3:3 or -1,0,1. Default -3:3")
    ap.add_argument("--core-sign-mode", default="follow", choices=["follow", "absolute_positive", "absolute_negative"],
                    help="How core twist sign is applied to signed torus SL. Default follow")
    ap.add_argument("--core-n0", type=float, default=1.0,
                    help="Model input n0 for E_model=(n-n0)^2. Default 1.0 (explicitly posits +1)")
    ap.add_argument("--k-core", type=float, default=1.0, help="E_model stiffness. Default 1")
    ap.add_argument("--k-null", type=float, default=1.0, help="E_null stiffness. Default 1")

    ap.add_argument("--circularity-trap", action=argparse.BooleanOptionalAction, default=True,
                    help="Enable arbitrary-target injection trap. Default true")
    ap.add_argument("--trap-target", type=int, default=25, help="Arbitrary self-linking target for circularity trap. Default 25")
    ap.add_argument("--trap-tol", type=float, default=0.25, help="Trap PASS tolerance. Default 0.25")


    # Core-Holonomy v2 audit controls. These do not overwrite the geometric audit;
    # they build an explicit M0--M5 gate matrix on top of it.
    ap.add_argument("--v2-gates", action=argparse.BooleanOptionalAction, default=True,
                    help="Write Core-Holonomy v2 M0--M5 gate audit outputs. Default true")
    ap.add_argument("--C-T", dest="C_T", type=float, default=1.0,
                    help="Positive twist stiffness C_T for v2 gate energy. Default 1")
    ap.add_argument("--v-swirl", type=float, default=V_SWIRL_CANON,
                    help="Canonical ||v_swirl|| in m/s. Default SST value")
    ap.add_argument("--r-c", type=float, default=R_C_CANON,
                    help="Canonical r_c in m. Default SST value")
    ap.add_argument("--matter-chi", type=int, default=1, choices=[-1, 1],
                    help="Matter chirality sign chi. Antimatter uses -chi. Default +1")
    ap.add_argument("--twoomega-transit-turns", type=float, default=2.501,
                    help="Passive twoomega transit holonomy in turns for M5 negative control. Default 2.501")
    ap.add_argument("--holonomy-integer-tol", type=float, default=1e-9,
                    help="Tolerance for integer holonomy center. Default 1e-9")

    ap.add_argument("--out-prefix", default="core_twist_audit", help="Output prefix. Default core_twist_audit")
    ap.add_argument("--log", default=None, help="Log path. Default fs_core_twist_audit_outputlog.txt")
    args = ap.parse_args(argv)

    if args.samples < 64:
        raise SystemExit("--samples must be at least 64")

    log_path = Path(args.log) if args.log else Path(Path(sys.argv[0]).stem + "_outputlog.txt")
    log_file, old_stdout, old_stderr = install_tee(log_path)

    try:
        q_list = parse_q_list(args.q_list)
        qset = set(q_list)
        extra_torus = parse_extra_torus(args.extra_torus)
        print(f"[config] q_list={q_list}, p={args.p}, extra_torus={extra_torus}, samples={args.samples}")
        print(f"[config] core_n_range={args.n_core_range}, core_n0={args.core_n0}, core_sign_mode={args.core_sign_mode}")
        print("[scope] Non-circular audit: target-free torus pq + Core-Holonomy v2 gate matrix.")

        roots = discover_folder_roots()
        zip_roots = discover_zip_roots(Path(".fs_core_twist_audit_cache"), enabled=not args.no_zip_fallback)
        all_roots = unique_existing(list(roots) + list(zip_roots))
        print("[fseries] roots:")
        if all_roots:
            for r in all_roots:
                print(f"  - {r}")
        else:
            print("  - none")

        ideal_paths = discover_ideal_paths()
        print("[ideal] candidate ideal.txt paths:")
        if ideal_paths:
            for pth in ideal_paths:
                print(f"  - {pth}")
        else:
            print("  - none")

        entries: List[CurveEntry] = []
        if args.include_analytic:
            entries.extend(collect_analytic_entries(q_list, p=args.p, extra_pq=extra_torus))

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
            all_roots,
            q_list=q_list,
            include_all_fseries=args.include_all_fseries,
            max_fseries=args.max_fseries,
            include_twist_controls=(not args.no_twist_controls),
        ))

        if not args.include_all_fseries and not args.include_all_ideal:
            entries = [e for e in entries if (e.q in qset) or str(e.family).startswith("control") or e.source_type == "analytic"]

        print(f"[inventory] entries to analyze: {len(entries)}")
        for e in entries[:60]:
            ctrl = f" ctrl_q={e.control_for_q}" if e.control_for_q else ""
            print(f"  - {e.source_type:8s} {e.family:13s} p={e.p:<2d} q={e.q or '-':>2}{ctrl:>10s} {e.label}")
        if len(entries) > 60:
            print(f"  ... {len(entries)-60} more")

        rows: List[Dict[str, object]] = []
        landscapes: List[Dict[str, object]] = []
        for i, e in enumerate(entries, 1):
            try:
                row, land = analyze_entry(e, args)
                rows.append(row)
                landscapes.extend(land)
                print(
                    f"[RESULT {i:03d}/{len(entries):03d}] {e.label} "
                    f"p={row['p']} q={row['q']} pq={row['expected_pq']} "
                    f"Wr={row['Wr']:+.6f} PT_Lk0={row['PT_Lk0']:+.4f} "
                    f"SL_torus={fmt(row['torus_SL'])} abs_err={fmt(row['torus_SL_abs_err_vs_pq'])} "
                    f"n_req={row['core_required_abs_to_pq_plus_1']} "
                    f"SL+1_abs={row['SL_core_plus1_abs']} "
                    f"model_select={row['n_selected_model']} {row['torus_status']} trap={row['trap_status']}"
                )
            except KeyboardInterrupt:
                raise
            except Exception as ex:
                print(f"[ERROR] failed {e.label}: {ex}")
                traceback.print_exc()

        out_prefix = Path(args.out_prefix)
        out_csv = out_prefix.with_name(out_prefix.name + "_results.csv")
        out_land = out_prefix.with_name(out_prefix.name + "_energy_landscape.csv")
        out_md = out_prefix.with_name(out_prefix.name + "_summary.md")
        write_csv(rows, out_csv, RESULT_FIELDS)
        write_csv(landscapes, out_land, LANDSCAPE_FIELDS)
        write_markdown(rows, landscapes, out_md, args)
        if args.v2_gates:
            gate_rows = make_gate_scenario_rows(rows, args)
            out_gate = out_prefix.with_name(out_prefix.name + "_v2_gate_scenarios.csv")
            out_gate_md = out_prefix.with_name(out_prefix.name + "_v2_gate_summary.md")
            write_csv(gate_rows, out_gate, GATE_SCENARIO_FIELDS)
            write_gate_markdown(rows, gate_rows, out_gate_md, args)
        else:
            gate_rows = []
            out_gate = None
            out_gate_md = None
        print(f"[write] {out_csv.resolve()}")
        print(f"[write] {out_land.resolve()}")
        print(f"[write] {out_md.resolve()}")
        if args.v2_gates:
            print(f"[write] {out_gate.resolve()}")
            print(f"[write] {out_gate_md.resolve()}")
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
