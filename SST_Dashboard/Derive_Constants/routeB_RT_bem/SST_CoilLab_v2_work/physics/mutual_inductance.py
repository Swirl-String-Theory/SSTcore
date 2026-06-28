from __future__ import annotations

import numpy as np
from geometry.base import CoilGeometry, Lane

MU0_OVER_4PI = 1e-7


def _sample_polyline(points: np.ndarray, max_segments: int = 180):
    """Return midpoint/dl arrays for a polyline, deterministically downsampled.

    This is a Neumann-style engineering estimate, not a high-accuracy PEEC solver.
    It is intended to expose geometry-dependent L/M trends for sweeps.
    """
    pts = np.asarray(points, dtype=float)
    if len(pts) < 2:
        return np.zeros((0, 3)), np.zeros((0, 3))
    p0 = pts[:-1]
    p1 = pts[1:]
    dl = p1 - p0
    mid = 0.5 * (p0 + p1)
    if len(dl) > max_segments:
        idx = np.linspace(0, len(dl) - 1, max_segments, dtype=int)
        dl = dl[idx]
        mid = mid[idx]
    return mid, dl


def _lane_pair_neumann(lane_a: Lane, lane_b: Lane, wire_radius: float = 0.0005,
                       max_segments: int = 180) -> float:
    ma, dla = _sample_polyline(lane_a.points, max_segments=max_segments)
    mb, dlb = _sample_polyline(lane_b.points, max_segments=max_segments)
    if len(dla) == 0 or len(dlb) == 0:
        return 0.0
    # scale correction for deterministic segment downsampling
    scale_a = max(1.0, (len(lane_a.points) - 1) / max(1, len(dla)))
    scale_b = max(1.0, (len(lane_b.points) - 1) / max(1, len(dlb)))
    dla_eff = dla * scale_a
    dlb_eff = dlb * scale_b
    r = ma[:, None, :] - mb[None, :, :]
    d = np.sqrt(np.sum(r * r, axis=2) + wire_radius * wire_radius)
    dot = np.einsum('ik,jk->ij', dla_eff, dlb_eff)
    return float(MU0_OVER_4PI * np.sum(dot / d))


def phase_lanes(coil: CoilGeometry, phase_count: int = 3) -> list[list[Lane]]:
    grouped = [[] for _ in range(phase_count)]
    for lane in coil.lanes:
        grouped[int(lane.phase_index) % phase_count].append(lane)
    return grouped


def estimate_phase_inductance_matrix(coil: CoilGeometry, wire_radius: float = 0.0005,
                                      max_segments_per_lane: int = 120,
                                      phase_count: int = 3) -> np.ndarray:
    """Estimate a 3x3 phase inductance matrix from geometry.

    Diagonal terms include all self and same-phase lane interactions. Off-diagonal
    terms include mutual interactions between phase groups. The sign is inherited
    from the actual lane direction in the geometry. Mirrored lanes therefore affect
    the result through their point order and shape rather than through a fake kernel.
    """
    groups = phase_lanes(coil, phase_count=phase_count)
    L = np.zeros((phase_count, phase_count), dtype=float)
    for i in range(phase_count):
        for j in range(i, phase_count):
            total = 0.0
            for lane_a in groups[i]:
                for lane_b in groups[j]:
                    total += _lane_pair_neumann(lane_a, lane_b, wire_radius=wire_radius,
                                                max_segments=max_segments_per_lane)
            L[i, j] = L[j, i] = total
    # Numerical Neumann estimates can be slightly non-positive on diagonals for
    # complex closed paths. Clamp to a small physically sane floor based on length.
    for i, lanes in enumerate(groups):
        length = sum(l.length for l in lanes)
        floor = 1e-7 * max(length, 1e-9)
        if not np.isfinite(L[i, i]) or L[i, i] < floor:
            L[i, i] = floor
    return L


def inductance_matrix_rows(coil: CoilGeometry, L: np.ndarray) -> list[dict]:
    rows = []
    for i in range(L.shape[0]):
        for j in range(L.shape[1]):
            rows.append({
                'geometry': coil.name,
                'phase_i': i,
                'phase_j': j,
                'L_or_M_H': float(L[i, j]),
                'kind': 'self' if i == j else 'mutual',
            })
    return rows
