#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import numpy as np
from SST_Coil_00_common import MU0


def bmag(Bx,By,Bz):
    return np.sqrt(np.real(Bx*np.conjugate(Bx)+By*np.conjugate(By)+Bz*np.conjugate(Bz)))


def field_observables(Bx,By,Bz,X=None,Y=None,Z=None) -> dict:
    B = bmag(Bx,By,Bz)
    obs = {
        'B_max_T': float(np.nanmax(B)),
        'B_mean_T': float(np.nanmean(B)),
        'B_rms_T': float(np.sqrt(np.nanmean(B*B))),
        'mag_pressure_mean_Pa': float(np.nanmean(B*B/(2*MU0))),
        'mag_pressure_max_Pa': float(np.nanmax(B*B/(2*MU0))),
    }
    if X is not None and B.shape[0] > 2:
        # Central numerical gradient of B^2 over regular grid.
        dx=float(X[1,0,0]-X[0,0,0]); dy=float(Y[0,1,0]-Y[0,0,0]); dz=float(Z[0,0,1]-Z[0,0,0])
        g=np.gradient(B*B, dx, dy, dz, edge_order=1)
        grad_norm=np.sqrt(g[0]*g[0]+g[1]*g[1]+g[2]*g[2])
        obs['gradB2_mean_T2_per_m']=float(np.nanmean(grad_norm))
        obs['gradB2_max_T2_per_m']=float(np.nanmax(grad_norm))
    return obs


def phase_currents(base_complex_current: complex, phases=3, mirror_sign=-1.0):
    vals=[]
    for i in range(phases):
        vals.append(base_complex_current*np.exp(1j*2*np.pi*i/phases))
    return vals + [mirror_sign*v for v in vals]
