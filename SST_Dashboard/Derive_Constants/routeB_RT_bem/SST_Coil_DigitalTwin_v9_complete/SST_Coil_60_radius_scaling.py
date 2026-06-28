#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_run_dirs, write_csv_dicts, save_json, scale_lanes, path_length
from SST_Coil_10_geometry_sawbowl import build_sawbowl_3phase
from SST_Coil_11_geometry_rodin6lane import build_rodin_6lane
from SST_Coil_30_pwm_current import harmonic_current
from SST_Coil_40_biot_savart import grid_from_bounds, field_for_lanes
from SST_Coil_50_observables import field_observables, phase_currents


def build_geom(name):
    if name=='sawbowl': return build_sawbowl_3phase(Rb=0.025,Rt=0.030,height=0.006,n_pairs=20,mode='curved')
    if name=='rodin': return build_rodin_6lane(units='m', n_path=900)  # decimated for sweeps; high-res geometry remains in compare script
    raise ValueError('geometry must be sawbowl or rodin')


def run_sweep(geometry='sawbowl', radii=(0.03,0.05,0.10), f_min=1e5, f_max=5e6, samples=30, harmonics=5, grid=9, duty=0.382):
    base=build_geom(geometry)
    # Normalize xy radius to about 0.05 m before scaling to requested R.
    allpts=np.vstack([l['points'] for l in base]); base_R=float(np.max(np.sqrt(allpts[:,0]**2+allpts[:,1]**2)))
    freqs=np.geomspace(f_min,f_max,int(samples)); rows=[]
    for R in radii:
        lanes=scale_lanes(base, float(R)/base_R)
        length=max(path_length(l['points']) for l in lanes)
        bounds=max(2.0*R,0.08)
        X,Y,Z=grid_from_bounds(bounds=bounds,res=grid)
        # precompute per-phase geometry fields for unit current? simple direct loop per frequency/harmonic here.
        for f0 in freqs:
            Bx=0j*np.zeros_like(X); By=0j*np.zeros_like(X); Bz=0j*np.zeros_like(X)
            for n in range(1,harmonics+1):
                I=harmonic_current(f0,n,duty,length,wire_diameter_m=0.0012)
                curr=phase_currents(I, phases=3, mirror_sign=-1.0 if len(lanes)==6 else 1.0)
                curr=curr[:len(lanes)]
                bx,by,bz=field_for_lanes(lanes,curr,X,Y,Z,r_softening=2e-4)
                Bx+=bx; By+=by; Bz+=bz
            obs=field_observables(Bx,By,Bz,X,Y,Z)
            rows.append(dict(geometry=geometry,R_m=float(R),f0_hz=float(f0),f0R_Hz_m=float(f0*R),**obs))
    return rows


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--geometry',choices=['sawbowl','rodin'],default='sawbowl')
    ap.add_argument('--out-base',default='exports/SST-Coil'); ap.add_argument('--samples',type=int,default=28)
    ap.add_argument('--grid',type=int,default=7); ap.add_argument('--harmonics',type=int,default=3)
    ap.add_argument('--f-min',type=float,default=1e5); ap.add_argument('--f-max',type=float,default=5e6)
    args=ap.parse_args(); run=make_run_dirs(args.out_base)
    rows=run_sweep(args.geometry,f_min=args.f_min,f_max=args.f_max,samples=args.samples,harmonics=args.harmonics,grid=args.grid)
    write_csv_dicts(run/'csv'/f'SST-Coil_{args.geometry}_radius_scaling.csv', rows)
    fig,ax=plt.subplots(figsize=(9,5.5))
    for R in sorted({r['R_m'] for r in rows}):
        rr=[r for r in rows if r['R_m']==R]
        y=np.array([r['gradB2_mean_T2_per_m'] for r in rr]); y=y/max(y.max(),1e-30)
        ax.plot([r['f0_hz'] for r in rr],y,label=f'R={R:.3f} m')
    ax.set_xscale('log'); ax.set_xlabel('f0 [Hz]'); ax.set_ylabel('normalized gradB2 mean'); ax.set_title(f'{args.geometry}: extracted observable vs absolute frequency')
    ax.legend(); fig.tight_layout(); fig.savefig(run/'figures'/f'SST-Coil_{args.geometry}_radius_scaling_freq.png',dpi=170); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5.5))
    for R in sorted({r['R_m'] for r in rows}):
        rr=[r for r in rows if r['R_m']==R]
        y=np.array([r['gradB2_mean_T2_per_m'] for r in rr]); y=y/max(y.max(),1e-30)
        ax.plot([r['f0R_Hz_m'] for r in rr],y,label=f'R={R:.3f} m')
    ax.set_xscale('log'); ax.set_xlabel('f0 R [Hz m]'); ax.set_ylabel('normalized gradB2 mean'); ax.set_title(f'{args.geometry}: fR collapse check from digital twin')
    ax.legend(); fig.tight_layout(); fig.savefig(run/'figures'/f'SST-Coil_{args.geometry}_radius_scaling_fR.png',dpi=170); plt.close(fig)
    save_json(run/'reports'/f'SST-Coil_{args.geometry}_radius_scaling_summary.json', {'rows':len(rows),'samples':args.samples,'harmonics':args.harmonics,'grid':args.grid})
    print('Wrote run:',run)
if __name__=='__main__': main()
