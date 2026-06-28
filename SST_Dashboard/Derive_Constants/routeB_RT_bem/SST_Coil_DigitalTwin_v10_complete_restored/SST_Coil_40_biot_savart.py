#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import numpy as np
from SST_Coil_00_common import MU0_4PI


def grid_from_bounds(bounds: float = 0.06, res: int = 17):
    x = np.linspace(-bounds, bounds, int(res))
    y = np.linspace(-bounds, bounds, int(res))
    z = np.linspace(-bounds, bounds, int(res))
    return np.meshgrid(x, y, z, indexing='ij')


def biot_savart_wire_grid(X, Y, Z, polyline: np.ndarray, current: float | complex,
                          r_softening: float = 1e-6):
    pts = np.asarray(polyline, dtype=float)
    Bx = np.zeros_like(X, dtype=np.complex128 if np.iscomplexobj(current) else np.float64)
    By = np.zeros_like(Y, dtype=Bx.dtype)
    Bz = np.zeros_like(Z, dtype=Bx.dtype)
    p0 = pts[:-1]; p1 = pts[1:]
    dl = p1-p0; mid = 0.5*(p0+p1)
    target = np.stack([X.ravel(),Y.ravel(),Z.ravel()],axis=1)
    for dL, m in zip(dl, mid):
        r_vec = target-m
        r_sq = np.sum(r_vec*r_vec,axis=1)+r_softening**2
        r_cubed = r_sq*np.sqrt(r_sq)
        cross = np.cross(np.broadcast_to(dL,r_vec.shape),r_vec)
        Bseg = cross*((MU0_4PI*current)/r_cubed)[:,None] if np.ndim(current)>0 else cross*((MU0_4PI*current)/r_cubed)[:,None]
        Bx += Bseg[:,0].reshape(X.shape); By += Bseg[:,1].reshape(Y.shape); Bz += Bseg[:,2].reshape(Z.shape)
    return Bx,By,Bz


def field_for_lanes(lanes: list[dict], currents, X, Y, Z, r_softening=1e-5):
    Bx=np.zeros_like(X,dtype=np.complex128); By=np.zeros_like(X,dtype=np.complex128); Bz=np.zeros_like(X,dtype=np.complex128)
    if np.isscalar(currents):
        currents=[currents]*len(lanes)
    for lane,I in zip(lanes,currents):
        bx,by,bz=biot_savart_wire_grid(X,Y,Z,lane['points'],I,r_softening=r_softening)
        Bx+=bx; By+=by; Bz+=bz
    return Bx,By,Bz
