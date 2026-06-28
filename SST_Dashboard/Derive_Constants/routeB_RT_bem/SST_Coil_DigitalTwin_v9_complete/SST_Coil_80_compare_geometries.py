#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_run_dirs, save_json, write_csv_dicts, summarize_lanes, path_length
from SST_Coil_01_plotting import plot_lanes_3d
from SST_Coil_10_geometry_sawbowl import build_sawbowl_3phase
from SST_Coil_11_geometry_rodin6lane import build_rodin_6lane
from SST_Coil_20_winding_factors import winding_rows, phase_table_rows
from SST_Coil_30_pwm_current import harmonic_current, current_spectrum
from SST_Coil_40_biot_savart import grid_from_bounds, field_for_lanes
from SST_Coil_50_observables import field_observables, phase_currents


def lane_summary_rows(geoms):
    rows=[]
    for geom,lanes in geoms.items():
        for l in lanes:
            rows.append(dict(geometry=geom, lane=l['name'], phase=l.get('phase'), mirror=l.get('mirror',False),
                             n_points=len(l['points']), length_m=path_length(l['points'])))
    return rows


def diagnostic_field(lanes, name, current=5.0, bounds=0.08, res=13, soft=2e-4):
    X,Y,Z=grid_from_bounds(bounds,res)
    if len(lanes)==6:
        curr=phase_currents(current+0j,phases=3,mirror_sign=-1.0)
    else:
        curr=[current]*len(lanes)
    Bx,By,Bz=field_for_lanes(lanes,curr[:len(lanes)],X,Y,Z,r_softening=soft)
    obs=field_observables(Bx,By,Bz,X,Y,Z)
    B=np.sqrt(np.real(Bx*np.conjugate(Bx)+By*np.conjugate(By)+Bz*np.conjugate(Bz)))
    return obs,B,X,Y,Z


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out-base',default='exports/SST-Coil')
    ap.add_argument('--grid',type=int,default=13); ap.add_argument('--no-field',action='store_true')
    args=ap.parse_args(); run=make_run_dirs(args.out_base)
    figdir=run/'figures'; csvdir=run/'csv'; repdir=run/'reports'

    geoms={
        'sawbowl_curved': build_sawbowl_3phase(Rb=0.025,Rt=0.030,height=0.006,n_pairs=20,mode='curved',profile='Exponential'),
        'sawbowl_chord': build_sawbowl_3phase(Rb=0.025,Rt=0.030,height=0.006,n_pairs=20,mode='chord',profile='Exponential'),
        'rodin6lane': build_rodin_6lane(units='m'),
    }
    plot_lanes_3d(geoms['sawbowl_curved'], figdir/'SST-Coil_v9_geometry_sawbowl_curved.png', 'SST-Coil v9 SawBowl curved: original continuous z/r logic')
    plot_lanes_3d(geoms['sawbowl_chord'], figdir/'SST-Coil_v9_geometry_sawbowl_chord.png', 'SST-Coil v9 SawBowl chord: slot-to-slot version')
    plot_lanes_3d(geoms['rodin6lane'], figdir/'SST-Coil_v9_geometry_rodin6lane.png', 'SST-Coil v9 Rodin (5,12): exact 6-lane z-mirror guide', units='mm')

    write_csv_dicts(csvdir/'SST-Coil_v9_lane_summary.csv', lane_summary_rows(geoms))
    write_csv_dicts(csvdir/'SST-Coil_v9_winding_factors.csv', winding_rows(harmonics=range(1,16)))
    write_csv_dicts(csvdir/'SST-Coil_v9_phase_table.csv', phase_table_rows())

    report={'geometries':{k:summarize_lanes(v) for k,v in geoms.items()}}
    if not args.no_field:
        field_rows=[]
        for name,lanes in geoms.items():
            obs,B,X,Y,Z=diagnostic_field(lanes,name,res=args.grid)
            report[f'field_{name}']=obs
            field_rows.append(dict(geometry=name,**obs))
            k=Z.shape[2]//2
            fig,ax=plt.subplots(figsize=(7,6))
            im=ax.imshow(B[:,:,k].T,origin='lower',extent=[X.min(),X.max(),Y.min(),Y.max()],aspect='equal')
            ax.set_title(f'{name}: |B| midplane static diagnostic')
            ax.set_xlabel('x [m]'); ax.set_ylabel('y [m]')
            fig.colorbar(im,ax=ax,label='T'); fig.tight_layout(); fig.savefig(figdir/f'SST-Coil_v9_{name}_Bmag_midplane.png',dpi=170); plt.close(fig)
        write_csv_dicts(csvdir/'SST-Coil_v9_field_diagnostics.csv', field_rows)

    # one current spectrum using representative Rodin lane length
    length=path_length(geoms['rodin6lane'][0]['points'])
    write_csv_dicts(csvdir/'SST-Coil_v9_current_spectrum_1MHz.csv', current_spectrum(1e6,25,0.382,length,0.0012))
    save_json(repdir/'SST-Coil_v9_summary.json', report)
    print('Wrote run:',run)

if __name__=='__main__': main()
