#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_run_dirs, save_json, set_axes_equal
from SST_Coil_11_geometry_rodin_6lane_exact import build_rodin_6lane, geometry_summary
from SST_Coil_12_geometry_sawbowl_exact import build_sawbowl_3phase
from SST_Coil_30_biot_savart import biot_savart_wire_grid, grid_from_bounds

def plot_lanes(lanes, out, title, units='m'):
    fig=plt.figure(figsize=(9,8)); ax=fig.add_subplot(111,projection='3d')
    colors=['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown']
    allpts=[]
    scale=1000.0 if units=='mm' else 1.0
    for i,l in enumerate(lanes):
        pts=l['points']*scale
        allpts.append(pts)
        ls='--' if l.get('mirror') else '-'
        ax.plot(pts[:,0],pts[:,1],pts[:,2],lw=1.4,ls=ls,color=colors[i%len(colors)],label=l['name'])
    allpts=np.vstack(allpts)
    set_axes_equal(ax, allpts)
    label='mm' if units=='mm' else 'm'
    ax.set_xlabel(f'x [{label}]'); ax.set_ylabel(f'y [{label}]'); ax.set_zlabel(f'z [{label}]')
    ax.set_title(title); ax.legend(fontsize=7,loc='upper left')
    fig.tight_layout(); fig.savefig(out,dpi=180); plt.close(fig)

def diagnostic_field(lanes, outdir, name, current=5.0, bounds=0.06, res=17, soft=1e-5):
    X,Y,Z=grid_from_bounds(bounds,res)
    Bx=np.zeros_like(X); By=np.zeros_like(X); Bz=np.zeros_like(X)
    # static diagnostic: all lanes equal current, mirror lanes can be signed later; here geometry sanity only
    for l in lanes:
        bx,by,bz=biot_savart_wire_grid(X,Y,Z,l['points'],current,r_softening=soft)
        Bx+=bx; By+=by; Bz+=bz
    Bmag=np.sqrt(Bx*Bx+By*By+Bz*Bz)
    k=Z.shape[2]//2
    fig,ax=plt.subplots(figsize=(7,6))
    im=ax.imshow(Bmag[:,:,k].T,origin='lower',extent=[-bounds,bounds,-bounds,bounds],aspect='equal')
    ax.set_title(f'{name}: |B| midplane, static equal-current diagnostic')
    ax.set_xlabel('x [m]'); ax.set_ylabel('y [m]')
    fig.colorbar(im,ax=ax,label='T')
    fig.tight_layout(); fig.savefig(outdir/f'{name}_Bmag_midplane.png',dpi=170); plt.close(fig)
    return dict(Bmax=float(Bmag.max()), Bmean=float(Bmag.mean()), Brms=float(np.sqrt(np.mean(Bmag*Bmag))))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out-base',default='exports/SST-Coil')
    ap.add_argument('--no-field',action='store_true')
    args=ap.parse_args()
    run=make_run_dirs(args.out_base)
    figdir=run/'figures'; csvdir=run/'csv'; repdir=run/'reports'

    saw=build_sawbowl_3phase(Rb=0.025,Rt=0.030,height=0.006,n_pairs=20,profile='Exponential',mode='curved',samples_per_seg=24)
    rod=build_rodin_6lane(R_major_mm=33.40,R_tube_mm=9.0,p=5,q=12,n_path=6000,include_mirror=True,units='m')

    plot_lanes(saw, figdir/'SST-Coil_v8_geometry_sawbowl.png','SST-Coil v8 SawBowl: exact GUI-SawBowl logic', units='m')
    plot_lanes(rod, figdir/'SST-Coil_v8_geometry_rodin_6lane_exact.png','SST-Coil v8 Rodin: exact 6-lane guide script logic', units='mm')

    summaries={'sawbowl': {'n_lanes':len(saw), 'points_per_lane':len(saw[0]['points'])}, 'rodin': geometry_summary(rod)}
    if not args.no_field:
        summaries['field_sawbowl']=diagnostic_field(saw, figdir, 'SST-Coil_v8_sawbowl')
        summaries['field_rodin']=diagnostic_field(rod, figdir, 'SST-Coil_v8_rodin')

    with open(csvdir/'SST-Coil_v8_lane_summary.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['geometry','lane','phase','mirror','n_points','length_m'])
        for geom,lanes in [('sawbowl',saw),('rodin',rod)]:
            for i,l in enumerate(lanes):
                pts=l['points']; length=float(np.sum(np.linalg.norm(np.diff(pts,axis=0),axis=1)))
                w.writerow([geom,l['name'],l.get('phase'),l.get('mirror',False),len(pts),length])
    save_json(repdir/'SST-Coil_v8_summary.json',summaries)
    print('Wrote run:', run)
    print('Rodin extent [m]:', summaries['rodin']['extent_m'])

if __name__=='__main__':
    main()
