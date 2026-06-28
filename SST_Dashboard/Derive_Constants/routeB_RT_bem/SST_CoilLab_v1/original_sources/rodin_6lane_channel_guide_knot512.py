#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rodin_6lane_channel_guide_knot512.py

Purpose
-------
Generate a "mold-like" winding guide (torus + channel fences) for the *Rodin-style*
(5,12) torus-knot wiring with:
  - 3-phase interleaving via per-cell phase offsets: [0, 1/3, 2/3] of one q=12 sector
  - mirrored counterpart (bidirectional / opposite side): z -> -z
=> total 6 continuous lanes.

This matches the logic in your rodin_double.py:
    dt = cell_phase * (2*pi/q);  tp = t + dt;  theta = p*tp; phi = q*tp
and mirror flips z.

We avoid mesh booleans; channels are formed by two thin **fences** per lane,
creating a valley that holds the wire (similar to grooved donut examples).

Outputs (mm)
------------
- rodin_6lane_channel_guide_knot512_90mm.stl
- rodin_6lane_channel_guide_knot512_preview.png

Dependencies
------------
pip install trimesh numpy matplotlib
"""

import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# =========================
# Size envelope (mm)
# =========================
MAX_XY = 90.0
MAX_Z  = 90.0

# Base torus geometry
R_MAJOR = 33.40     # mm
R_TUBE  = 9.0       # mm
TORUS_PROFILE_SAMPLES = 180
TORUS_SECTIONS = 240

# Rodin knot parameters
P, Q = 5, 12
CELL_PHASES = [0.0, 1.0/3.0, 2.0/3.0]  # fractions of one q-sector
MIRROR = True

# Curve sampling
N_PATH = 6000

# Channel sizing (choose before buying wire; safe default)
WIRE_DIAMETER = 1.2      # mm (gives room; good "unknown wire" choice)
WIRE_CLEARANCE = 0.4     # mm (FDM tolerance)

# Fence geometry (channel walls)
FENCE_THICKNESS = 0.85   # mm
FENCE_HEIGHT = 2.3       # mm
FENCE_SEGMENTS = 520     # more = smoother but heavier STL
FENCE_BOX_MINLEN = 0.55  # mm

BASE_LIFT = 0.15         # mm lift fences off surface to slice cleanly

# Outputs
OUT_STL = "rodin_6lane_channel_guide_knot512_89p9mm.stl"
OUT_PNG = "rodin_6lane_channel_guide_knot512_preview_89p9mm.png"


# =========================
# Geometry core
# =========================
def torus_knot_5_12(t: np.ndarray, cell_phase: float = 0.0, mirror: bool = False) -> np.ndarray:
    """
    (p,q)=(5,12) torus knot with per-cell phase offset:
      dt = cell_phase * (2*pi/q)
      tp = t + dt
      theta = p*tp
      phi   = q*tp
    """
    dt = cell_phase * (2.0*np.pi / Q)
    tp = t + dt

    theta = P * tp
    phi   = Q * tp

    x = (R_MAJOR + R_TUBE*np.cos(phi)) * np.cos(theta)
    y = (R_MAJOR + R_TUBE*np.cos(phi)) * np.sin(theta)
    z = R_TUBE * np.sin(phi)

    if mirror:
        z = -z
    return np.column_stack([x, y, z])


def torus_frame(pt: np.ndarray, tangent: np.ndarray):
    """
    Return unit vectors (t_hat, n_hat, l_hat) at point on torus surface.
      t_hat: tangent along lane
      n_hat: outward normal of torus surface
      l_hat: lateral direction in surface tangent plane, perpendicular to t_hat
    """
    t_hat = tangent / max(np.linalg.norm(tangent), 1e-12)

    x, y, _ = pt
    theta = np.arctan2(y, x)
    center = np.array([R_MAJOR*np.cos(theta), R_MAJOR*np.sin(theta), 0.0])
    n = pt - center
    n_hat = n / max(np.linalg.norm(n), 1e-12)

    l = np.cross(n_hat, t_hat)
    l_hat = l / max(np.linalg.norm(l), 1e-12)
    return t_hat, n_hat, l_hat


def make_oriented_box(center: np.ndarray, t_hat: np.ndarray, n_hat: np.ndarray, l_hat: np.ndarray,
                      length: float, thickness: float, height: float) -> trimesh.Trimesh:
    """
    Local axes:
      x -> l_hat (thickness)
      y -> n_hat (height)
      z -> t_hat (length)
    """
    box = trimesh.creation.box(extents=[thickness, height, length])

    T = np.eye(4)
    T[:3, 0] = l_hat
    T[:3, 1] = n_hat
    T[:3, 2] = t_hat
    box.apply_transform(T)
    box.apply_translation(center)
    return box


def build_base_torus_revolve() -> trimesh.Trimesh:
    """
    Watertight torus via revolve of an offset circle about the Y-axis.
    """
    phi = np.linspace(0.0, 2*np.pi, TORUS_PROFILE_SAMPLES, endpoint=True)
    linestring = np.column_stack([R_MAJOR + R_TUBE*np.cos(phi), R_TUBE*np.sin(phi)])  # 2D
    torus = trimesh.creation.revolve(linestring, sections=TORUS_SECTIONS)
    torus.remove_duplicate_faces()
    torus.remove_degenerate_faces()
    torus.merge_vertices()
    return torus


def build_lane_fences(path_pts: np.ndarray) -> list:
    """
    Two fences around the lane centerline: channel width ~= wire_d + clearance.
    """
    half_gap = 0.5 * (WIRE_DIAMETER + WIRE_CLEARANCE)
    fence_center_offset = half_gap + 0.5*FENCE_THICKNESS

    idx = np.linspace(0, len(path_pts)-1, FENCE_SEGMENTS, dtype=int)

    fences = []
    for i0, i1 in zip(idx[:-1], idx[1:]):
        a = path_pts[i0]
        b = path_pts[i1]
        seg = b - a
        L = float(np.linalg.norm(seg))
        if L < FENCE_BOX_MINLEN:
            continue

        mid = 0.5*(a+b)
        t_hat, n_hat, l_hat = torus_frame(mid, seg)

        mid_lifted = mid + n_hat * BASE_LIFT

        cL = mid_lifted + l_hat * fence_center_offset + n_hat * (0.5*FENCE_HEIGHT)
        cR = mid_lifted - l_hat * fence_center_offset + n_hat * (0.5*FENCE_HEIGHT)

        fences.append(make_oriented_box(cL, t_hat, n_hat, l_hat, length=L,
                                        thickness=FENCE_THICKNESS, height=FENCE_HEIGHT))
        fences.append(make_oriented_box(cR, t_hat, n_hat, l_hat, length=L,
                                        thickness=FENCE_THICKNESS, height=FENCE_HEIGHT))
    return fences


def preview(lanes: list, out_png: str):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")

    for name, pts in lanes:
        ax.plot(pts[:,0], pts[:,1], pts[:,2], linewidth=2, alpha=0.9, label=name)

    all_pts = np.vstack([pts for _, pts in lanes])
    mins, maxs = all_pts.min(axis=0), all_pts.max(axis=0)
    span = float(np.max(maxs - mins))
    mid = 0.5*(mins + maxs)
    ax.set_xlim(mid[0]-span/2, mid[0]+span/2)
    ax.set_ylim(mid[1]-span/2, mid[1]+span/2)
    ax.set_zlim(mid[2]-span/2, mid[2]+span/2)

    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title("(5,12) Rodin knot lanes: 3-phase + mirrored (6 lanes)")
    ax.legend(loc="upper left", fontsize=7)
    plt.tight_layout()
    plt.savefig(out_png, dpi=170)
    plt.close(fig)


def main():
    base = build_base_torus_revolve()

    t = np.linspace(0.0, 2*np.pi, N_PATH, endpoint=True)
    lanes = []

    # 3-phase, one direction
    for i, cp in enumerate(CELL_PHASES):
        pts = torus_knot_5_12(t, cell_phase=cp, mirror=False)
        lanes.append((f"CW phase {i+1} (cp={cp:.2f})", pts))

    # mirrored (bidirectional)
    if MIRROR:
        for i, cp in enumerate(CELL_PHASES):
            pts = torus_knot_5_12(t, cell_phase=cp, mirror=True)
            lanes.append((f"CCW phase {i+1} (cp={cp:.2f})", pts))

    parts = [base]
    for _, pts in lanes:
        parts.extend(build_lane_fences(pts))

    mesh = trimesh.util.concatenate(parts)
    mesh.remove_duplicate_faces()
    mesh.remove_degenerate_faces()
    mesh.merge_vertices()

    # center at origin
    mesh.apply_translation(-mesh.centroid)

    ext = mesh.bounds[1] - mesh.bounds[0]
    print("Bounding box extents (mm):", ext)

    if ext[0] > MAX_XY + 1e-6 or ext[1] > MAX_XY + 1e-6:
        print("WARNING: exceeds XY limit; reduce R_MAJOR/R_TUBE/FENCE_HEIGHT.")
    if ext[2] > MAX_Z + 1e-6:
        print("WARNING: exceeds Z limit; reduce FENCE_HEIGHT.")

    mesh.export(OUT_STL)
    print("Wrote:", OUT_STL)

    preview(lanes, OUT_PNG)
    print("Wrote:", OUT_PNG)


if __name__ == "__main__":
    main()