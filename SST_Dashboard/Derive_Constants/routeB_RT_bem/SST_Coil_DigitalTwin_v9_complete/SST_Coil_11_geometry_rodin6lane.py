#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rodin torus-knot 6-lane geometry sector, matching the uploaded
rodin_6lane_channel_guide_knot512.py guide script.

Correct Rodin interpretation for this project:
  - (p,q)=(5,12) torus-knot lanes on a torus guide.
  - 3 phase interleaving via cell_phase = [0, 1/3, 2/3] of one q-sector.
  - mirrored counterpart is z -> -z, giving six continuous lanes.
This is not the SawBowl geometry and not a reverse-overlaid path.
"""
from __future__ import annotations
import numpy as np

R_MAJOR_MM = 33.40
R_TUBE_MM = 9.0
P_DEFAULT = 5
Q_DEFAULT = 12
CELL_PHASES_DEFAULT = (0.0, 1.0/3.0, 2.0/3.0)
N_PATH_DEFAULT = 6000


def rodin_torus_knot(t: np.ndarray, *, R_major_mm: float = R_MAJOR_MM,
                     R_tube_mm: float = R_TUBE_MM, p: int = P_DEFAULT,
                     q: int = Q_DEFAULT, cell_phase: float = 0.0,
                     mirror_z: bool = False, units: str = 'm') -> np.ndarray:
    dt = float(cell_phase) * (2*np.pi / float(q))
    tp = np.asarray(t, dtype=float) + dt
    theta = int(p) * tp
    phi = int(q) * tp
    x = (R_major_mm + R_tube_mm*np.cos(phi))*np.cos(theta)
    y = (R_major_mm + R_tube_mm*np.cos(phi))*np.sin(theta)
    z = R_tube_mm*np.sin(phi)
    if mirror_z:
        z = -z
    pts = np.column_stack([x, y, z])
    if units == 'm':
        pts *= 1e-3
    elif units != 'mm':
        raise ValueError("units must be 'm' or 'mm'")
    return pts


def build_rodin_6lane(*, R_major_mm: float = R_MAJOR_MM, R_tube_mm: float = R_TUBE_MM,
                      p: int = P_DEFAULT, q: int = Q_DEFAULT,
                      n_path: int = N_PATH_DEFAULT,
                      cell_phases = CELL_PHASES_DEFAULT,
                      include_mirror: bool = True, units: str = 'm') -> list[dict]:
    t = np.linspace(0.0, 2*np.pi, int(n_path), endpoint=True)
    lanes = []
    for i, cp in enumerate(cell_phases):
        pts = rodin_torus_knot(t, R_major_mm=R_major_mm, R_tube_mm=R_tube_mm,
                               p=p, q=q, cell_phase=cp, mirror_z=False, units=units)
        lanes.append(dict(name=f'CW phase {i+1} (cp={cp:.2f})', geometry='rodin6lane',
                          phase=i, mirror=False, cell_phase=cp, points=pts))
    if include_mirror:
        for i, cp in enumerate(cell_phases):
            pts = rodin_torus_knot(t, R_major_mm=R_major_mm, R_tube_mm=R_tube_mm,
                                   p=p, q=q, cell_phase=cp, mirror_z=True, units=units)
            lanes.append(dict(name=f'CCW/mirror phase {i+1} (cp={cp:.2f})', geometry='rodin6lane',
                              phase=i, mirror=True, cell_phase=cp, points=pts))
    return lanes
