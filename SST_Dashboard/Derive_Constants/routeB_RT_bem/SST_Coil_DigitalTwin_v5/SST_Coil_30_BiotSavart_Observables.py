from __future__ import annotations
import numpy as np, math
from SST_Coil_00_common import MU0_4PI
from SST_Coil_10_Geometry_FromUserScripts import build_all_phases, GeometryConfig
from SST_Coil_20_Circuit_DistributedLite import harmonic_phase_currents
from SST_Coil_00_common import CircuitConfig

def biot_savart_points(obs, polyline, current_complex, softening=1e-4):
    obs=np.asarray(obs,float); p=np.asarray(polyline,float)
    B=np.zeros((len(obs),3),dtype=np.complex128)
    p0=p[:-1]; p1=p[1:]; dl=p1-p0; mid=0.5*(p0+p1)
    for dL, m in zip(dl, mid):
        r=obs-m; rsq=np.sum(r*r,axis=1)+softening**2; rcub=rsq*np.sqrt(rsq)
        B += MU0_4PI*current_complex*np.cross(np.broadcast_to(dL,r.shape),r)/rcub[:,None]
    return B

def probe_grid(radius_m, grid=11, z_probe=None):
    span=1.35*radius_m; z=0.25*radius_m if z_probe is None else z_probe
    x=np.linspace(-span,span,grid); y=np.linspace(-span,span,grid)
    X,Y=np.meshgrid(x,y,indexing='ij')
    obs=np.column_stack([X.ravel(),Y.ravel(),np.full(X.size,z)])
    return obs,X,Y

def observable_for_frequency(f0_hz, geom:GeometryConfig, circ:CircuitConfig, harmonics=9, grid=11, softening=None):
    coils=build_all_phases(geom)
    currents, meta=harmonic_phase_currents(f0_hz,coils,circ,harmonics,geom.radius_m)
    obs,X,Y=probe_grid(geom.radius_m,grid)
    soft= max(5e-5, 0.002*geom.radius_m) if softening is None else softening
    # map phase to all layer coils
    Bn={}
    for n,ph,I in currents:
        B=np.zeros((len(obs),3),dtype=np.complex128)
        for c in coils:
            if c['phase']==ph:
                B += biot_savart_points(obs,c['points'],I,soft)
        Bn[n]=Bn.get(n,0)+B
    # time-average B^2 = sum 1/2 |B_n|^2 for harmonic phasors
    B2=np.zeros(len(obs),float); signedBz=0.0
    for n,B in Bn.items():
        B2 += 0.5*np.sum(np.abs(B)**2,axis=1)
        signedBz += float(np.mean(np.real(B[:,2])))
    B2grid=B2.reshape(X.shape)
    dx=(X[1,0]-X[0,0]) if X.shape[0]>1 else 1.0
    dy=(Y[0,1]-Y[0,0]) if Y.shape[1]>1 else 1.0
    gx,gy=np.gradient(B2grid,dx,dy,edge_order=1)
    gradmag=np.sqrt(gx*gx+gy*gy)
    # observables
    axis_i=grid//2
    axis_B2=float(B2grid[axis_i,axis_i])
    weighted_gradB2=float(np.mean(gradmag/(np.sqrt(X*X+Y*Y)+0.1*geom.radius_m)))
    asymmetry_B2=float(np.mean(B2grid[X>0])-np.mean(B2grid[X<0])) if np.any(X>0) and np.any(X<0) else 0.0
    return {'axis_B2':axis_B2,'weighted_gradB2':weighted_gradB2,'asymmetry_B2':asymmetry_B2,'signed_Bz_proxy':signedBz,'meta':meta}
