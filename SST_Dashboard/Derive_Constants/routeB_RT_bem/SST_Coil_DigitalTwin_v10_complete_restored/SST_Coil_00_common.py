#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SST-Coil Digital Twin v9: common constants, exports, and numeric helpers."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import numpy as np

MU0 = 4.0*np.pi*1e-7
MU0_4PI = 1e-7
EPS0 = 8.8541878128e-12
C0 = 299792458.0
V_SWIRL = 1.09384563e6
RHO_F = 7.0e-7
CU_RHO_20C = 1.724e-8       # ohm m
CU_TEMP_COEFF = 0.00393     # 1/K near room temperature


def make_run_dirs(base: str | Path = 'exports/SST-Coil') -> Path:
    run = Path(base) / ('run_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    for sub in ['figures', 'csv', 'npz', 'reports', 'logs']:
        (run / sub).mkdir(parents=True, exist_ok=True)
    return run


def save_json(path: str | Path, data) -> None:
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True))


def write_csv_dicts(path: str | Path, rows: list[dict]) -> None:
    import csv
    path = Path(path)
    if not rows:
        path.write_text('')
        return
    keys = list(rows[0].keys())
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)


def path_length(points: np.ndarray) -> float:
    pts = np.asarray(points, dtype=float)
    if len(pts) < 2:
        return 0.0
    return float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))


def lane_lengths(lanes: list[dict]) -> list[float]:
    return [path_length(l['points']) for l in lanes]


def scale_lanes(lanes: list[dict], factor: float) -> list[dict]:
    out = []
    for l in lanes:
        d = dict(l)
        d['points'] = np.asarray(l['points'], dtype=float) * factor
        out.append(d)
    return out


def set_axes_equal(ax, pts: np.ndarray, pad: float = 0.08) -> None:
    pts = np.asarray(pts, dtype=float)
    mins = pts.min(axis=0); maxs = pts.max(axis=0)
    span = float(np.max(maxs-mins))*(1.0+pad)
    if span <= 0:
        span = 1.0
    mid = 0.5*(mins+maxs)
    ax.set_xlim(mid[0]-span/2, mid[0]+span/2)
    ax.set_ylim(mid[1]-span/2, mid[1]+span/2)
    ax.set_zlim(mid[2]-span/2, mid[2]+span/2)


def summarize_lanes(lanes: list[dict]) -> dict:
    allpts = np.vstack([l['points'] for l in lanes]) if lanes else np.zeros((1,3))
    return {
        'n_lanes': len(lanes),
        'points_per_lane_min': int(min(len(l['points']) for l in lanes)) if lanes else 0,
        'points_per_lane_max': int(max(len(l['points']) for l in lanes)) if lanes else 0,
        'lengths_m': lane_lengths(lanes),
        'bounds_min_m': allpts.min(axis=0).tolist(),
        'bounds_max_m': allpts.max(axis=0).tolist(),
        'extent_m': (allpts.max(axis=0)-allpts.min(axis=0)).tolist(),
    }


def skin_depth_cu(f_hz: np.ndarray | float, rho: float = CU_RHO_20C) -> np.ndarray:
    f = np.asarray(f_hz, dtype=float)
    omega = 2*np.pi*np.maximum(f, 1e-30)
    return np.sqrt(2*rho/(MU0*omega))
