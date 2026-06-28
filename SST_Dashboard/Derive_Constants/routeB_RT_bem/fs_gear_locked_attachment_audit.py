#!/usr/bin/env python3
"""
fs_gear_locked_attachment_audit.py
===================================

Gear-locked framed-tube audit for SST Core-Cycle Attachment Lemma work.

Purpose
-------
This script analyses a 3D-printable gear/link assembly as a *mechanical
analogue* of a framed SST tube with global phase attachment.  It does not
claim to prove the Attachment Lemma.  It tests whether the geometry and a
minimal phase-lock model support the following structure:

    local ring phases + central helix/axle phase -> one collective phase
    central phase holonomy -> n_core = chi under positive twist stiffness

The script is designed as the first module of a broader future audit family:
- gear-locked STL assemblies (this file)
- multi-component link TXT/Fourier audits (future)
- twist-knot framed-tube controls (future)

Outputs
-------
<out_prefix>_mesh_summary.csv
<out_prefix>_components.csv
<out_prefix>_distance_matrix.csv
<out_prefix>_lock_scenarios.csv
<out_prefix>_helicity_bookkeeping.csv   (if a linking matrix is supplied)
<out_prefix>_summary.md

Dependencies
------------
Required: numpy
Optional but recommended for STL: trimesh

Example
-------
python fs_gear_locked_attachment_audit.py ^
  --gear-stl triple_gear_solid_with_mark.stl ^
  --axle-stl 30cm_axle.stl ^
  --linking-matrix-csv tl33_gear_link_audit_linking_matrix.csv ^
  --out-prefix gear_locked_attachment_audit

"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import os
import sys
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

try:
    import trimesh  # type: ignore
except Exception:  # pragma: no cover
    trimesh = None


# -----------------------------------------------------------------------------
# Basic helpers
# -----------------------------------------------------------------------------


def _fmt(x: object) -> str:
    if x is None:
        return ""
    if isinstance(x, float):
        if math.isnan(x):
            return ""
        return f"{x:.12g}"
    return str(x)


def write_csv(path: str, rows: List[Dict[str, object]], fieldnames: Optional[List[str]] = None) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    if fieldnames is None:
        keys: List[str] = []
        for row in rows:
            for k in row.keys():
                if k not in keys:
                    keys.append(k)
        fieldnames = keys
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: _fmt(row.get(k, "")) for k in fieldnames})


def parse_int_range(spec: str) -> List[int]:
    """Parse '-3:3' or comma-separated integers."""
    spec = spec.strip()
    if ":" in spec:
        a, b = spec.split(":", 1)
        lo, hi = int(a), int(b)
        step = 1 if hi >= lo else -1
        return list(range(lo, hi + step, step))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


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
    vals = vals[order]
    vecs = vecs[:, order]
    # columns are principal axes
    return vals, vecs


# -----------------------------------------------------------------------------
# Mesh loading and component analysis
# -----------------------------------------------------------------------------

@dataclass
class MeshInfo:
    label: str
    path: str
    file_size_bytes: int
    vertices: int
    faces: int
    watertight: str
    euler_number: int
    body_count: int
    volume: float
    surface_area: float
    xmin: float
    ymin: float
    zmin: float
    xmax: float
    ymax: float
    zmax: float
    extent_x: float
    extent_y: float
    extent_z: float


@dataclass
class ComponentInfo:
    mesh_label: str
    component_id: int
    vertices: int
    faces: int
    watertight: str
    volume: float
    surface_area: float
    center_x: float
    center_y: float
    center_z: float
    extent_x: float
    extent_y: float
    extent_z: float
    pca_val_1: float
    pca_val_2: float
    pca_val_3: float
    normal_x: float
    normal_y: float
    normal_z: float
    normal_dot_axle_axis: float
    normal_angle_to_axle_deg: float


def load_mesh(path: str):
    if trimesh is None:
        raise RuntimeError("trimesh is required for STL mesh analysis. Install with: pip install trimesh")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    mesh = trimesh.load(path, force="mesh")
    if mesh.is_empty:
        raise RuntimeError(f"Loaded empty mesh: {path}")
    return mesh


def mesh_info(label: str, path: str, mesh) -> MeshInfo:
    bounds = np.asarray(mesh.bounds, dtype=float)
    ext = bounds[1] - bounds[0]
    body_count = int(getattr(mesh, "body_count", 1))
    return MeshInfo(
        label=label,
        path=os.path.abspath(path),
        file_size_bytes=int(os.path.getsize(path)),
        vertices=int(len(mesh.vertices)),
        faces=int(len(mesh.faces)),
        watertight="YES" if bool(mesh.is_watertight) else "NO",
        euler_number=int(mesh.euler_number),
        body_count=body_count,
        volume=float(mesh.volume),
        surface_area=float(mesh.area),
        xmin=float(bounds[0, 0]),
        ymin=float(bounds[0, 1]),
        zmin=float(bounds[0, 2]),
        xmax=float(bounds[1, 0]),
        ymax=float(bounds[1, 1]),
        zmax=float(bounds[1, 2]),
        extent_x=float(ext[0]),
        extent_y=float(ext[1]),
        extent_z=float(ext[2]),
    )


def infer_axle_axis(axle_mesh) -> np.ndarray:
    vals, vecs = pca_axes(np.asarray(axle_mesh.vertices, dtype=float))
    # first PCA axis is the long axis
    axis = unit(vecs[:, 0])
    # Prefer positive z for stable reports
    if axis[2] < 0:
        axis = -axis
    return axis


def split_components(mesh) -> List[object]:
    try:
        parts = list(mesh.split(only_watertight=False))
    except Exception:
        parts = [mesh]
    # Sort by center angle / x/y for reproducibility
    def sort_key(p):
        c = np.asarray(p.center_mass if p.is_watertight else p.centroid, dtype=float)
        return (math.atan2(c[1], c[0]), c[0], c[1], c[2])
    return sorted(parts, key=sort_key)


def component_infos(label: str, mesh, axle_axis: Optional[np.ndarray] = None) -> List[ComponentInfo]:
    if axle_axis is None:
        axle_axis = np.array([0.0, 0.0, 1.0])
    parts = split_components(mesh)
    rows: List[ComponentInfo] = []
    for idx, p in enumerate(parts, start=1):
        bounds = np.asarray(p.bounds, dtype=float)
        ext = bounds[1] - bounds[0]
        center = np.asarray(p.center_mass if p.is_watertight else p.centroid, dtype=float)
        vals, vecs = pca_axes(np.asarray(p.vertices, dtype=float))
        # For ring-like bodies, smallest PCA axis approximates tube/ring plane normal.
        normal = unit(vecs[:, 2])
        if np.dot(normal, axle_axis) < 0:
            normal = -normal
        dot = float(np.clip(np.dot(normal, axle_axis), -1.0, 1.0))
        angle = math.degrees(math.acos(abs(dot)))
        rows.append(ComponentInfo(
            mesh_label=label,
            component_id=idx,
            vertices=int(len(p.vertices)),
            faces=int(len(p.faces)),
            watertight="YES" if bool(p.is_watertight) else "NO",
            volume=float(p.volume),
            surface_area=float(p.area),
            center_x=float(center[0]),
            center_y=float(center[1]),
            center_z=float(center[2]),
            extent_x=float(ext[0]),
            extent_y=float(ext[1]),
            extent_z=float(ext[2]),
            pca_val_1=float(vals[0]),
            pca_val_2=float(vals[1]),
            pca_val_3=float(vals[2]),
            normal_x=float(normal[0]),
            normal_y=float(normal[1]),
            normal_z=float(normal[2]),
            normal_dot_axle_axis=dot,
            normal_angle_to_axle_deg=float(angle),
        ))
    return rows


def distance_matrix(component_rows: List[ComponentInfo]) -> List[Dict[str, object]]:
    rows = []
    for a, b in itertools.combinations(component_rows, 2):
        ca = np.array([a.center_x, a.center_y, a.center_z], dtype=float)
        cb = np.array([b.center_x, b.center_y, b.center_z], dtype=float)
        d = cb - ca
        rows.append({
            "component_i": a.component_id,
            "component_j": b.component_id,
            "distance": float(np.linalg.norm(d)),
            "dx": float(d[0]),
            "dy": float(d[1]),
            "dz": float(d[2]),
        })
    return rows


# -----------------------------------------------------------------------------
# Phase-lock model
# -----------------------------------------------------------------------------

@dataclass
class LockScenario:
    scenario_id: str
    s12: int
    s13: int
    s23: int
    cycle_product: int
    ring_constraint_rank: int
    ring_nullity: int
    full_constraint_rank: int
    full_nullity: int
    status: str
    collective_vector_theta1: float
    collective_vector_theta2: float
    collective_vector_theta3: float
    collective_vector_psi: float
    helix_ratio_m: float
    helix_turns_per_theta1_turn: float
    chi_target: int
    allowed_sector: str
    selected_n_core: int
    exact_holonomy_chi: str
    integer_selection_chi: str
    twist_energy_min: float
    interpretation: str


def matrix_rank(A: np.ndarray, tol: float = 1e-10) -> int:
    if A.size == 0:
        return 0
    s = np.linalg.svd(A, compute_uv=False)
    return int(np.sum(s > tol))


def nullspace(A: np.ndarray, tol: float = 1e-10) -> np.ndarray:
    if A.size == 0:
        return np.eye(A.shape[1])
    u, s, vh = np.linalg.svd(A)
    rank = int(np.sum(s > tol))
    return vh[rank:].T.copy()


def choose_n_core(center: float, allowed: Sequence[int], odd_only: bool = True) -> Tuple[int, float]:
    candidates = [n for n in allowed if ((n % 2) != 0 if odd_only else True)]
    if not candidates:
        candidates = list(allowed)
    # tie-break toward sign of center, then lower abs
    def key(n: int):
        return ((n - center) ** 2, abs(n), -math.copysign(1, n) * math.copysign(1, center) if center != 0 and n != 0 else 0)
    nsel = min(candidates, key=key)
    return nsel, float((nsel - center) ** 2)


def lock_scenarios(
    helix_ratio_m: float = 1.0,
    chi_target: int = 1,
    n_range: Sequence[int] = tuple(range(-5, 6)),
    signs_mode: str = "all",
    tol: float = 1e-9,
) -> List[LockScenario]:
    """Enumerate ring sign-lock scenarios.

    Variables are x = [theta1, theta2, theta3, psi] in turns.

    Ring lock edge convention:
        theta_i - s_ij theta_j = 0
    s=+1 means co-rotating/same phase; s=-1 means counter-rotating.

    Helix lock:
        psi - m theta1 = 0

    A nonzero collective locked mode requires full nullity = 1.
    For the triangular ring graph, ring cycle product s12*s23*s13 must be +1
    for an unfrustrated one-dimensional ring mode. Product -1 is frustrated.
    """
    sign_sets = []
    for s12, s13, s23 in itertools.product([+1, -1], repeat=3):
        if signs_mode == "unfrustrated" and (s12 * s13 * s23) != +1:
            continue
        if signs_mode == "frustrated" and (s12 * s13 * s23) != -1:
            continue
        sign_sets.append((s12, s13, s23))

    rows: List[LockScenario] = []
    for k, (s12, s13, s23) in enumerate(sign_sets, start=1):
        # ring variables only [theta1, theta2, theta3]
        Ar = np.array([
            [1.0, -float(s12), 0.0],
            [1.0, 0.0, -float(s13)],
            [0.0, 1.0, -float(s23)],
        ])
        r_rank = matrix_rank(Ar, tol)
        r_nullity = 3 - r_rank

        # full variables [theta1, theta2, theta3, psi]
        A = np.array([
            [1.0, -float(s12), 0.0, 0.0],
            [1.0, 0.0, -float(s13), 0.0],
            [0.0, 1.0, -float(s23), 0.0],
            [-float(helix_ratio_m), 0.0, 0.0, 1.0],
        ])
        f_rank = matrix_rank(A, tol)
        f_nullity = 4 - f_rank
        cycle_product = int(s12 * s13 * s23)
        ns = nullspace(A, tol)

        if f_nullity == 1:
            v = ns[:, 0]
            # Normalize to theta1 = +1 where possible.
            if abs(v[0]) > tol:
                v = v / v[0]
            else:
                v = v / np.linalg.norm(v)
            center = float(v[3])  # psi turns per theta1 turn
            nsel, emin = choose_n_core(center, n_range, odd_only=True)
            exact = "YES" if abs(center - chi_target) <= tol else "NO"
            integer_ok = "YES" if nsel == chi_target else "NO"
            if cycle_product == +1 and exact == "YES":
                status = "FULLY_LOCKED_ATTACHMENT_ANALOG"
                interpretation = "Unfrustrated ring gear graph plus helix lock leaves one collective mode and matches chi."
            elif cycle_product == +1:
                status = "FULLY_LOCKED_BUT_HELIX_RATIO_NOT_CHI"
                interpretation = "Unfrustrated collective mode exists, but helix holonomy does not exactly match chi."
            else:
                status = "UNEXPECTED_NONZERO_MODE_WITH_FRUSTRATED_SIGNS"
                interpretation = "Check sign conventions; triangular product is frustrated but a mode survived numerically."
        else:
            v = np.array([float("nan")] * 4)
            center = float("nan")
            nsel, emin = choose_n_core(float("nan") if False else 0.0, n_range, odd_only=True)
            exact = "NO"
            integer_ok = "NO"
            if f_nullity == 0:
                status = "FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION"
                interpretation = "No nonzero collective phase remains; all external-gear triangle signs can overconstrain rotation."
            else:
                status = "UNDERLOCKED_MULTIPLE_PHASE_MODES"
                interpretation = "More than one independent phase remains; attachment is not globally locked."

        rows.append(LockScenario(
            scenario_id=f"S{k:02d}_s12{s12:+d}_s13{s13:+d}_s23{s23:+d}",
            s12=s12,
            s13=s13,
            s23=s23,
            cycle_product=cycle_product,
            ring_constraint_rank=r_rank,
            ring_nullity=r_nullity,
            full_constraint_rank=f_rank,
            full_nullity=f_nullity,
            status=status,
            collective_vector_theta1=float(v[0]),
            collective_vector_theta2=float(v[1]),
            collective_vector_theta3=float(v[2]),
            collective_vector_psi=float(v[3]),
            helix_ratio_m=float(helix_ratio_m),
            helix_turns_per_theta1_turn=center,
            chi_target=int(chi_target),
            allowed_sector="odd_FR_sector",
            selected_n_core=int(nsel),
            exact_holonomy_chi=exact,
            integer_selection_chi=integer_ok,
            twist_energy_min=float(emin),
            interpretation=interpretation,
        ))
    return rows


# -----------------------------------------------------------------------------
# Link/helicity bookkeeping, optional
# -----------------------------------------------------------------------------


def read_linking_matrix_csv(path: str) -> Optional[np.ndarray]:
    if not path or not os.path.exists(path):
        return None
    # Try general CSV with columns i,j,lk or matrix-like CSV.
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None
    keys = {k.lower(): k for k in rows[0].keys()}
    # Pairwise row format
    if any(k in keys for k in ["component_i", "i"]) and any(k in keys for k in ["component_j", "j"]):
        ik = keys.get("component_i", keys.get("i"))
        jk = keys.get("component_j", keys.get("j"))
        lk = None
        for cand in ["lk_round", "linking_number_round", "lk", "linking_number", "gauss_lk"]:
            if cand in keys:
                lk = keys[cand]
                break
        if lk is None:
            # Try any column containing lk/link
            for key in rows[0].keys():
                if "lk" in key.lower() or "link" in key.lower():
                    lk = key
                    break
        if lk is None:
            return None
        pairs = []
        maxidx = 0
        for r in rows:
            try:
                i = int(float(r[ik]))
                j = int(float(r[jk]))
                val = float(r[lk])
            except Exception:
                continue
            maxidx = max(maxidx, i, j)
            pairs.append((i - 1, j - 1, val))
        if maxidx <= 0:
            return None
        M = np.zeros((maxidx, maxidx), dtype=float)
        for i, j, val in pairs:
            M[i, j] = M[j, i] = val
        return M

    # Matrix-like format: numeric columns except first label.
    numeric_rows = []
    for r in rows:
        vals = []
        for k, v in r.items():
            try:
                vals.append(float(v))
            except Exception:
                pass
        if vals:
            numeric_rows.append(vals)
    if numeric_rows:
        n = min(len(numeric_rows), min(len(r) for r in numeric_rows))
        return np.array([r[:n] for r in numeric_rows[:n]], dtype=float)
    return None


def helicity_bookkeeping_rows(M: Optional[np.ndarray], chi_values: Sequence[int]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    if M is None:
        return rows
    n = M.shape[0]
    if len(chi_values) != n:
        # Broadcast first chi if needed.
        if len(chi_values) == 1:
            chi_values = [int(chi_values[0])] * n
        else:
            chi_values = list(chi_values[:n]) + [1] * max(0, n - len(chi_values))
    chi = np.array(chi_values, dtype=float)
    pair_sum = 0.0
    abs_pair_sum = 0.0
    pair_rows = []
    for i in range(n):
        for j in range(i + 1, n):
            lk = float(M[i, j])
            pair_sum += lk
            abs_pair_sum += abs(lk)
            pair_rows.append(f"Lk{i+1}{j+1}={lk:.6g}")
    self_attachment = float(np.sum(chi))
    signed_pair_term = float(2.0 * pair_sum)
    abs_pair_term = float(2.0 * abs_pair_sum)
    rows.append({
        "case": "supplied_orientation",
        "n_components": n,
        "chi_values": ";".join(str(int(x)) for x in chi),
        "pairwise_lk": ";".join(pair_rows),
        "sum_chi_i": self_attachment,
        "sum_lk_ij": pair_sum,
        "2_sum_lk_ij": signed_pair_term,
        "index_pairwise_only": self_attachment + signed_pair_term,
        "sum_abs_lk_ij": abs_pair_sum,
        "2_sum_abs_lk_ij": abs_pair_term,
        "unoriented_index_abs_pairwise": self_attachment + abs_pair_term,
        "interpretation": "Self attachment per component plus pairwise link helicity; higher Milnor/triple terms not included.",
    })
    # Orientation scenarios: flip component signs; Lk_ij -> o_i o_j Lk_ij, chi_i -> o_i chi_i if chirality follows orientation.
    for signs in itertools.product([+1, -1], repeat=n):
        orient = np.array(signs, dtype=float)
        oriented_chi = orient * chi
        pair = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                pair += orient[i] * orient[j] * M[i, j]
        rows.append({
            "case": "orientation_" + "".join("+" if s > 0 else "-" for s in signs),
            "n_components": n,
            "chi_values": ";".join(str(int(x)) for x in oriented_chi),
            "pairwise_lk": "orientation-applied",
            "sum_chi_i": float(np.sum(oriented_chi)),
            "sum_lk_ij": float(pair),
            "2_sum_lk_ij": float(2 * pair),
            "index_pairwise_only": float(np.sum(oriented_chi) + 2 * pair),
            "sum_abs_lk_ij": abs_pair_sum,
            "2_sum_abs_lk_ij": abs_pair_term,
            "unoriented_index_abs_pairwise": float(np.sum(np.abs(chi)) + abs_pair_term),
            "interpretation": "Orientation scenario; use only if component orientation is tied to chirality assignment.",
        })
    return rows


# -----------------------------------------------------------------------------
# Summary writer
# -----------------------------------------------------------------------------


def write_summary(
    path: str,
    mesh_rows: List[MeshInfo],
    comp_rows: List[ComponentInfo],
    dist_rows: List[Dict[str, object]],
    lock_rows: List[LockScenario],
    helicity_rows: List[Dict[str, object]],
    args: argparse.Namespace,
) -> None:
    def table(headers: List[str], rows: Iterable[Sequence[object]]) -> str:
        out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        for r in rows:
            out.append("| " + " | ".join(_fmt(x) for x in r) + " |")
        return "\n".join(out)

    status_counts: Dict[str, int] = {}
    for r in lock_rows:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1

    exact_rows = [r for r in lock_rows if r.exact_holonomy_chi == "YES" and r.full_nullity == 1]
    fully_locked = [r for r in lock_rows if r.full_nullity == 1]

    lines: List[str] = []
    lines.append("# Gear-Locked Attachment Lemma audit summary\n")
    lines.append("## Purpose\n")
    lines.append("This audit treats the 3D print as a mechanical analogue of a closed framed SST tube with gear-locked phases. It tests whether the assembly admits one collective phase and whether a central helix/axle phase can represent a global attachment holonomy.\n")
    lines.append("```text\n[SUPPORTING MECHANICAL MODEL] not a proof of physical SST dynamics.\nThe core question is whether local ring/core rotations are globally locked to a central phase.\n```\n")

    lines.append("## Mesh inventory\n")
    lines.append(table(
        ["label", "vertices", "faces", "watertight", "body_count", "extents", "volume"],
        ([m.label, m.vertices, m.faces, m.watertight, m.body_count, f"{m.extent_x:.3f} x {m.extent_y:.3f} x {m.extent_z:.3f}", m.volume] for m in mesh_rows)
    ))
    lines.append("")

    lines.append("## Gear components\n")
    lines.append(table(
        ["id", "center", "volume", "normal", "angle_to_axle_deg"],
        ([c.component_id, f"({c.center_x:.3f},{c.center_y:.3f},{c.center_z:.3f})", c.volume, f"({c.normal_x:.3f},{c.normal_y:.3f},{c.normal_z:.3f})", c.normal_angle_to_axle_deg] for c in comp_rows if c.mesh_label == "gear")
    ))
    lines.append("")

    if dist_rows:
        lines.append("## Component center distances\n")
        lines.append(table(
            ["i", "j", "distance", "dx", "dy", "dz"],
            ([r["component_i"], r["component_j"], r["distance"], r["dx"], r["dy"], r["dz"]] for r in dist_rows)
        ))
        lines.append("")

    lines.append("## Phase-lock scenarios\n")
    lines.append(f"Sign mode: `{args.signs_mode}`; helix ratio `m={args.helix_ratio}`; chi target `{args.chi}`.\n")
    lines.append(f"Status counts: `{status_counts}`\n")
    lines.append(table(
        ["scenario", "s12", "s13", "s23", "cycle", "nullity", "psi/theta1", "n_core", "exact", "status"],
        ([r.scenario_id, r.s12, r.s13, r.s23, r.cycle_product, r.full_nullity, r.helix_turns_per_theta1_turn, r.selected_n_core, r.exact_holonomy_chi, r.status] for r in lock_rows)
    ))
    lines.append("")

    lines.append("## Interpretation\n")
    lines.append("```text\n")
    lines.append("FULLY_LOCKED_ATTACHMENT_ANALOG:\n  The gear sign graph is unfrustrated, the helix/axle is locked to one collective phase, and the helix holonomy matches chi.\n")
    lines.append("FULLY_LOCKED_BUT_HELIX_RATIO_NOT_CHI:\n  A collective mode exists, but the chosen helix gear ratio does not produce exact chi.\n")
    lines.append("FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION:\n  The sign constraints eliminate nonzero collective rotation; a simple all-external triangular gear graph has this problem.\n")
    lines.append("UNDERLOCKED_MULTIPLE_PHASE_MODES:\n  More than one phase remains, so the assembly is not globally attached.\n")
    lines.append("```\n")

    if helicity_rows:
        lines.append("## Optional link/helicity bookkeeping\n")
        h0 = helicity_rows[0]
        lines.append("For a supplied linking matrix, the pairwise-only normalized index is\n")
        lines.append("\\[\nH/\\Gamma^2=\\sum_i\\chi_i+2\\sum_{i<j}\\mathrm{Lk}_{ij}.\n\\]\n")
        lines.append(table(
            ["case", "sum_chi", "sum_lk", "2sum_lk", "index", "abs_pair_index"],
            ([r["case"], r["sum_chi_i"], r["sum_lk_ij"], r["2_sum_lk_ij"], r["index_pairwise_only"], r["unoriented_index_abs_pairwise"]] for r in helicity_rows[:9])
        ))
        lines.append("")

    lines.append("## Canon status\n")
    lines.append("```text\n")
    if exact_rows:
        lines.append("[KEEP / SUPPORTING MODEL]\n  At least one lock scenario supports a single collective phase with exact chi holonomy.\n")
    elif fully_locked:
        lines.append("[PARTIAL SUPPORT]\n  A collective phase exists, but exact chi holonomy depends on helix ratio/sign choices.\n")
    else:
        lines.append("[NOT SUPPORTED BY THIS SIGN MODEL]\n  No single collective phase appears for the selected sign assumptions. Try different gear signs or helix ratio.\n")
    lines.append("[NOT A PROOF]\n  The script is a mechanical analogy/audit. It does not prove the physical SST Attachment Lemma.\n")
    lines.append("[NEXT MODULES]\n  Reuse the bookkeeping for Hopf, Solomon, Borromean, TL3.3 Gear and twist-knot framed-tube controls.\n")
    lines.append("```\n")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Gear-locked framed-tube Attachment Lemma audit")
    ap.add_argument("--gear-stl", default="triple_gear_solid_with_mark.stl", help="STL of the gear ring assembly")
    ap.add_argument("--axle-stl", default="30cm_axle.stl", help="STL of central axle/helix proxy")
    ap.add_argument("--linking-matrix-csv", default="", help="Optional CSV from link audit with pairwise Lk values")
    ap.add_argument("--out-prefix", default="gear_locked_attachment_audit", help="Output prefix")
    ap.add_argument("--helix-ratio", type=float, default=1.0, help="m in psi = m theta1, in turns/turn")
    ap.add_argument("--chi", type=int, default=1, help="Target matter/mirror holonomy chi (+1 or -1)")
    ap.add_argument("--n-core-range", default="-5:5", help="Integer n_core search range, e.g. -5:5")
    ap.add_argument("--signs-mode", choices=["all", "unfrustrated", "frustrated"], default="all", help="Which ring gear sign scenarios to enumerate")
    ap.add_argument("--chi-values", default="1,1,1", help="Comma list of chi_i for optional helicity bookkeeping")
    ap.add_argument("--tol", type=float, default=1e-9, help="Numerical tolerance")
    args = ap.parse_args(argv)

    out_dir = os.path.dirname(os.path.abspath(args.out_prefix)) or "."
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    gear_mesh = load_mesh(args.gear_stl)
    axle_mesh = load_mesh(args.axle_stl) if args.axle_stl else None
    axle_axis = infer_axle_axis(axle_mesh) if axle_mesh is not None else np.array([0.0, 0.0, 1.0])

    mesh_rows: List[MeshInfo] = [mesh_info("gear", args.gear_stl, gear_mesh)]
    if axle_mesh is not None:
        mesh_rows.append(mesh_info("axle", args.axle_stl, axle_mesh))

    comp_rows = component_infos("gear", gear_mesh, axle_axis=axle_axis)
    if axle_mesh is not None:
        comp_rows += component_infos("axle", axle_mesh, axle_axis=axle_axis)
    dist_rows = distance_matrix([c for c in comp_rows if c.mesh_label == "gear"])

    n_range = parse_int_range(args.n_core_range)
    lock_rows = lock_scenarios(
        helix_ratio_m=float(args.helix_ratio),
        chi_target=int(args.chi),
        n_range=n_range,
        signs_mode=args.signs_mode,
        tol=float(args.tol),
    )

    M = read_linking_matrix_csv(args.linking_matrix_csv) if args.linking_matrix_csv else None
    chi_values = [int(float(x.strip())) for x in args.chi_values.split(",") if x.strip()]
    helicity_rows = helicity_bookkeeping_rows(M, chi_values)

    write_csv(args.out_prefix + "_mesh_summary.csv", [asdict(r) for r in mesh_rows])
    write_csv(args.out_prefix + "_components.csv", [asdict(r) for r in comp_rows])
    write_csv(args.out_prefix + "_distance_matrix.csv", dist_rows)
    write_csv(args.out_prefix + "_lock_scenarios.csv", [asdict(r) for r in lock_rows])
    if helicity_rows:
        write_csv(args.out_prefix + "_helicity_bookkeeping.csv", helicity_rows)
    write_summary(args.out_prefix + "_summary.md", mesh_rows, comp_rows, dist_rows, lock_rows, helicity_rows, args)

    print(f"[write] {args.out_prefix}_mesh_summary.csv")
    print(f"[write] {args.out_prefix}_components.csv")
    print(f"[write] {args.out_prefix}_distance_matrix.csv")
    print(f"[write] {args.out_prefix}_lock_scenarios.csv")
    if helicity_rows:
        print(f"[write] {args.out_prefix}_helicity_bookkeeping.csv")
    print(f"[write] {args.out_prefix}_summary.md")
    print("[done]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
