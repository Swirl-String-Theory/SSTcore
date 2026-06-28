#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, shutil, json
import numpy as np
import pandas as pd

from geometry.sawbowl import build_sawbowl_3phase
from geometry.rodin6lane import build_rodin6lane
from geometry.validators import validate_geometry
from experiments.common import new_run_dir, write_json, write_csv
from experiments.geometry_compare import geometry_compare
from experiments.frequency_sweep import frequency_sweep
from experiments.radius_sweep import radius_sweep
from experiments.pwm_compare import pwm_compare
from experiments.kernel_extract import summarize_kernel_like
from physics.current_model import current_model_summary
from experiments.mutual_current_sweep import mutual_frequency_sweep


def build_default_geometries(quick: bool):
    samples = 4 if quick else 16
    rodin_pts = 360 if quick else 1600
    return [
        build_sawbowl_3phase(Rb=0.025, Rt=0.030, height=0.006, pairs=20, mode='curved', samples_per_seg=samples),
        build_sawbowl_3phase(Rb=0.025, Rt=0.030, height=0.006, pairs=20, mode='chord', samples_per_seg=samples),
        build_rodin6lane(R_major=0.03340, R_tube=0.0090, n_path=rodin_pts),
    ]


def main():
    ap=argparse.ArgumentParser(description='SST_CoilLab_v2 mutual-current research runner')
    ap.add_argument('--quick', action='store_true', help='faster/smaller grid and fewer frequency samples')
    ap.add_argument('--out-base', default='exports/SST-CoilLab')
    ap.add_argument('--grid', type=int, default=None)
    ap.add_argument('--bounds', type=float, default=0.08)
    ap.add_argument('--harmonics', type=int, default=None)
    ap.add_argument('--skip-mutual', action='store_true', help='skip slower 3-phase RL mutual-current sweep')
    args=ap.parse_args()

    run_dir=new_run_dir(args.out_base)
    quick=bool(args.quick)
    grid=args.grid if args.grid is not None else (5 if quick else 11)
    harmonics=args.harmonics if args.harmonics is not None else (3 if quick else 9)
    f0_values=np.geomspace(1e5, 3e6 if quick else 8e6, 5 if quick else 18)

    coils=build_default_geometries(quick)
    write_json(os.path.join(run_dir,'reports','run_config.json'),{
        'quick':quick,'grid':grid,'bounds_m':args.bounds,'harmonics':harmonics,'f0_values_hz':f0_values.tolist(),
        'hard_rule':'all observables are computed from Biot-Savart B fields; no imposed sinc/exp kernel is used for geometry comparison.'
    })

    # copy original sources for traceability if present
    os.makedirs(os.path.join(run_dir,'reports'), exist_ok=True)

    val_rows=[]
    for c in coils:
        rep=validate_geometry(c)
        write_json(os.path.join(run_dir,'reports',f'geometry_validation_{c.name}.json'),rep)
        val_rows.append({k:v for k,v in rep.items() if k not in ('lane_lengths_m','metadata')})
    write_csv(os.path.join(run_dir,'csv','geometry_validation.csv'), val_rows)

    geo_rows=geometry_compare(coils, run_dir, grid=grid, bounds_m=args.bounds, current_a=1.0)
    write_csv(os.path.join(run_dir,'csv','geometry_compare_static_field.csv'), geo_rows)

    pwm_rows=pwm_compare(run_dir, duties=(0.382,0.5), harmonics=40)
    write_csv(os.path.join(run_dir,'csv','pwm_harmonics_compare.csv'), pwm_rows)

    freq_rows,current_rows=frequency_sweep(coils, run_dir, f0_values, harmonics=harmonics, grid=grid, bounds_m=args.bounds, duty=0.382, observable='gradB2_mean')
    write_csv(os.path.join(run_dir,'csv','frequency_sweep_field_observable.csv'), freq_rows)
    write_csv(os.path.join(run_dir,'csv','current_spectrum_by_geometry.csv'), current_rows)


    if not args.skip_mutual:
        mutual_rows, mutual_current_rows, mutual_L_rows = mutual_frequency_sweep(
            coils, run_dir, f0_values, harmonics=max(3, min(harmonics, 7)),
            grid=max(5, grid-2), bounds_m=args.bounds, duty=0.382,
            observable='gradB2_mean', max_segments_per_lane=(50 if quick else 100))
        write_csv(os.path.join(run_dir,'csv','mutual_frequency_sweep_field_observable.csv'), mutual_rows)
        write_csv(os.path.join(run_dir,'csv','mutual_phase_currents.csv'), mutual_current_rows)
        write_csv(os.path.join(run_dir,'csv','mutual_L_matrix.csv'), mutual_L_rows)

    # current model summaries
    current_summ=[{'geometry':c.name, **current_model_summary(c.total_length, f0_hz=1e6)} for c in coils]
    write_csv(os.path.join(run_dir,'csv','current_model_summary.csv'), current_summ)

    # radius sweeps per geometry; quick uses fewer radii/frequencies
    radii=[0.03,0.05,0.10]
    fr_values=np.geomspace(1e5, 3e6 if quick else 8e6, 4 if quick else 14)
    all_rad=[]; all_rad_cur=[]
    for c in coils:
        rrows,crows=radius_sweep(c, run_dir, radii, fr_values, harmonics=max(3,harmonics//2), grid=max(7,grid-2), duty=0.382, observable='gradB2_mean')
        all_rad.extend(rrows); all_rad_cur.extend(crows)
    write_csv(os.path.join(run_dir,'csv','radius_sweep_field_observable.csv'), all_rad)
    write_csv(os.path.join(run_dir,'csv','radius_sweep_current_samples.csv'), all_rad_cur)

    krows=summarize_kernel_like(all_rad, run_dir)
    write_csv(os.path.join(run_dir,'csv','kernel_like_extracted_from_field_output.csv'), krows)

    print('SST_CoilLab_v2 run complete:')
    print(run_dir)
    print(f'files: {sum(len(files) for _,_,files in os.walk(run_dir))}')

if __name__=='__main__':
    main()
