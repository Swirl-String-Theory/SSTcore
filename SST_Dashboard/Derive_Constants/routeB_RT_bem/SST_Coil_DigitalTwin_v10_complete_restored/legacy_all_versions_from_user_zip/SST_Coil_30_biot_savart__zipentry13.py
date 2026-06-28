#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import numpy as np
MU0_4PI=1e-7

def biot_savart_wire_grid(X,Y,Z,polyline,current,r_softening=1e-6, chunk=256):
    Bx=np.zeros_like(X,dtype=float); By=np.zeros_like(Y,dtype=float); Bz=np.zeros_like(Z,dtype=float)
    pts=np.asarray(polyline,dtype=float)
    p0=pts[:-1]; p1=pts[1:]
    dl=p1-p0; mid=0.5*(p0+p1)
    target=np.stack([X.ravel(),Y.ravel(),Z.ravel()],axis=1)
    for s in range(0,len(dl),chunk):
        dls=dl[s:s+chunk]; mids=mid[s:s+chunk]
        for dL,m in zip(dls,mids):
            r_vec=target-m
            r_sq=np.sum(r_vec*r_vec,axis=1)+r_softening**2
            r_cubed=r_sq*np.sqrt(r_sq)
            cross=np.cross(np.broadcast_to(dL,r_vec.shape),r_vec)
            Bseg=cross*((MU0_4PI*current)/r_cubed)[:,None]
            Bx+=Bseg[:,0].reshape(X.shape); By+=Bseg[:,1].reshape(Y.shape); Bz+=Bseg[:,2].reshape(Z.shape)
    return Bx,By,Bz

def grid_from_bounds(bounds=0.06,res=21):
    x=np.linspace(-bounds,bounds,res); y=np.linspace(-bounds,bounds,res); z=np.linspace(-bounds,bounds,res)
    return np.meshgrid(x,y,z,indexing='ij')
