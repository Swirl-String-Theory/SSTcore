"""Biot-Savart segment-midpoint solver derived from rodin_GUI.py, without GUI."""
from __future__ import annotations
import numpy as np
from SST_Coil_00_common import MU0_4PI


def biot_savart_wire_grid(X,Y,Z,polyline,current,r_softening=1e-6, chunk_segments=None):
    Bx=np.zeros_like(X,dtype=float); By=np.zeros_like(Y,dtype=float); Bz=np.zeros_like(Z,dtype=float)
    p0=polyline[:-1]; p1=polyline[1:]; dl=p1-p0; mid=0.5*(p0+p1)
    target=np.stack([X.ravel(),Y.ravel(),Z.ravel()],axis=1)
    seg_indices = range(len(dl)) if chunk_segments is None else range(len(dl))
    for i in seg_indices:
        dL=dl[i]
        r_vec=target-mid[i]
        r_sq=np.sum(r_vec*r_vec,axis=1)+r_softening**2
        r_cubed=r_sq*np.sqrt(r_sq)
        cross=np.cross(np.broadcast_to(dL,r_vec.shape),r_vec)
        Bseg=cross*((MU0_4PI*current)/r_cubed)[:,None]
        Bx += Bseg[:,0].reshape(X.shape); By += Bseg[:,1].reshape(Y.shape); Bz += Bseg[:,2].reshape(Z.shape)
    return Bx,By,Bz


def field_from_coils(X,Y,Z,coil_items,current_map=None,default_current=1.0,r_softening=1e-6):
    Bx=np.zeros_like(X,dtype=float); By=np.zeros_like(Y,dtype=float); Bz=np.zeros_like(Z,dtype=float)
    for idx,c in enumerate(coil_items):
        name = c.get("name", str(idx)) if isinstance(c, dict) else str(idx)
        pts = c["points"] if isinstance(c, dict) else c
        I = default_current if current_map is None else current_map.get(name, current_map.get(idx, default_current))
        bx,by,bz=biot_savart_wire_grid(X,Y,Z,pts,I,r_softening)
        Bx+=bx; By+=by; Bz+=bz
    return Bx,By,Bz


def field_observables(Bx,By,Bz, spacing):
    B2=Bx*Bx+By*By+Bz*Bz
    Bmag=np.sqrt(B2)
    gx,gy,gz=np.gradient(B2, spacing, spacing, spacing, edge_order=1)
    gradB2=np.sqrt(gx*gx+gy*gy+gz*gz)
    return {"B2":B2,"Bmag":Bmag,"gradB2":gradB2,"gradB2_z":gz}
