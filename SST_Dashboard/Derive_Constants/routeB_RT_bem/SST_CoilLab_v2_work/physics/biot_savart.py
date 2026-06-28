from __future__ import annotations
import numpy as np
from geometry.base import CoilGeometry
MU0_4PI = 1e-7


def make_grid(bounds_m: float = 0.08, grid: int = 17, z_span_m: float | None = None):
    b = float(bounds_m)
    z_b = b if z_span_m is None else float(z_span_m)
    x = np.linspace(-b, b, int(grid))
    y = np.linspace(-b, b, int(grid))
    z = np.linspace(-z_b, z_b, int(grid))
    return np.meshgrid(x, y, z, indexing="ij"), (x, y, z)


def biot_savart_polyline_grid(X, Y, Z, polyline: np.ndarray, current: complex | float, r_softening: float = 1e-5):
    dtype = np.complex128 if np.iscomplexobj(current) else np.float64
    Bx = np.zeros_like(X, dtype=dtype); By = np.zeros_like(Y, dtype=dtype); Bz = np.zeros_like(Z, dtype=dtype)
    pts = np.asarray(polyline, dtype=float)
    if len(pts) < 2:
        return Bx, By, Bz
    p0 = pts[:-1]; p1 = pts[1:]
    dl = p1 - p0
    mid = 0.5*(p0+p1)
    target = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    for dL, m in zip(dl, mid):
        r_vec = target - m
        r_sq = np.sum(r_vec*r_vec, axis=1) + r_softening*r_softening
        r_cubed = r_sq*np.sqrt(r_sq)
        cross = np.cross(np.broadcast_to(dL, r_vec.shape), r_vec)
        Bseg = cross * ((MU0_4PI*current)/r_cubed)[:, None] if hasattr((MU0_4PI*current)/r_cubed, '__len__') else cross * ((MU0_4PI*current)/r_cubed)[:, None]
        Bx += Bseg[:,0].reshape(X.shape); By += Bseg[:,1].reshape(Y.shape); Bz += Bseg[:,2].reshape(Z.shape)
    return Bx, By, Bz


def biot_savart_coil_grid(coil: CoilGeometry, X, Y, Z, lane_currents=None, r_softening: float = 1e-5):
    if lane_currents is None:
        lane_currents = [1.0] * coil.lane_count
    dtype = np.complex128 if np.iscomplexobj(np.asarray(lane_currents)) else np.float64
    Bx = np.zeros_like(X, dtype=dtype); By = np.zeros_like(Y, dtype=dtype); Bz = np.zeros_like(Z, dtype=dtype)
    for lane, I in zip(coil.lanes, lane_currents):
        bx, by, bz = biot_savart_polyline_grid(X, Y, Z, lane.points, I, r_softening=r_softening)
        Bx += bx; By += by; Bz += bz
    return Bx, By, Bz
