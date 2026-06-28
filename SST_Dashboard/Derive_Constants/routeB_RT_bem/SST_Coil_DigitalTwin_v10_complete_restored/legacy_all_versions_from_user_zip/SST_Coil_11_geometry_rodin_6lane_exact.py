#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exact Rodin 6-lane geometry from user script rodin_6lane_channel_guide_knot512.py.

Key point: this is NOT an overlaid reverse path and NOT a z-gap stack.
It is:
  - 3 phase lanes via cell phase offsets [0, 1/3, 2/3] of one q=12 sector
  - mirrored counterpart by z -> -z
  - total 6 continuous lanes on the same torus guide envelope.
"""
from __future__ import annotations
import numpy as np

# Defaults copied from user script
R_MAJOR_MM = 33.40
R_TUBE_MM = 9.0
P = 5
Q = 12
CELL_PHASES = (0.0, 1.0/3.0, 2.0/3.0)
N_PATH = 6000


def rodin_torus_knot(t: np.ndarray, *, R_major: float=R_MAJOR_MM, R_tube: float=R_TUBE_MM,
                     p: int=P, q: int=Q, cell_phase: float=0.0,
                     mirror_z: bool=False, units: str='m') -> np.ndarray:
    """Rodin (p,q) torus knot with per-cell phase offset and optional z mirror.

    Formula follows the uploaded guide script:
        dt = cell_phase * (2*pi/q)
        tp = t + dt
        theta = p*tp
        phi = q*tp
        x = (R + r*cos(phi))*cos(theta)
        y = (R + r*cos(phi))*sin(theta)
        z = r*sin(phi)
        mirror: z -> -z
    """
    dt = float(cell_phase) * (2.0*np.pi/float(q))
    tp = np.asarray(t, dtype=float) + dt
    theta = int(p) * tp
    phi = int(q) * tp
    x = (R_major + R_tube*np.cos(phi)) * np.cos(theta)
    y = (R_major + R_tube*np.cos(phi)) * np.sin(theta)
    z = R_tube*np.sin(phi)
    if mirror_z:
        z = -z
    pts = np.column_stack([x, y, z])
    if units == 'm':
        pts = pts * 1e-3
    elif units != 'mm':
        raise ValueError("units must be 'm' or 'mm'")
    return pts


def build_rodin_6lane(*, R_major_mm: float=R_MAJOR_MM, R_tube_mm: float=R_TUBE_MM,
                      p: int=P, q: int=Q, n_path: int=N_PATH,
                      cell_phases=CELL_PHASES, include_mirror: bool=True,
                      units: str='m'):
    """Return list of lane dicts: name, phase_index, mirror, cell_phase, points."""
    t = np.linspace(0.0, 2*np.pi, int(n_path), endpoint=True)
    lanes = []
    for i, cp in enumerate(cell_phases):
        pts = rodin_torus_knot(t, R_major=R_major_mm, R_tube=R_tube_mm,
                               p=p, q=q, cell_phase=cp, mirror_z=False, units=units)
        lanes.append(dict(name=f"CW phase {i+1} (cp={cp:.2f})", phase=i, mirror=False, cell_phase=cp, points=pts))
    if include_mirror:
        for i, cp in enumerate(cell_phases):
            pts = rodin_torus_knot(t, R_major=R_major_mm, R_tube=R_tube_mm,
                                   p=p, q=q, cell_phase=cp, mirror_z=True, units=units)
            lanes.append(dict(name=f"CCW phase {i+1} (cp={cp:.2f})", phase=i, mirror=True, cell_phase=cp, points=pts))
    return lanes


def geometry_summary(lanes):
    allpts = np.vstack([l['points'] for l in lanes])
    return {
        'n_lanes': len(lanes),
        'points_per_lane': int(len(lanes[0]['points'])) if lanes else 0,
        'bounds_min_m': allpts.min(axis=0).tolist(),
        'bounds_max_m': allpts.max(axis=0).tolist(),
        'extent_m': (allpts.max(axis=0)-allpts.min(axis=0)).tolist(),
    }
