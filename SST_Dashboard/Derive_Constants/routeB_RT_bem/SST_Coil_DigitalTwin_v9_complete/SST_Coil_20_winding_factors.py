#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analytic S=40 double-star/Rodin winding factors retained from double-starshaped_coil40.py."""
from __future__ import annotations
import argparse
import numpy as np
from math import pi
from SST_Coil_00_common import make_run_dirs, write_csv_dicts, save_json


def winding_rows(S=40, p=4, m=3, y=2, delta_e_deg=30.0, harmonics=(1,5,7)):
    alpha_e = pi * p / S
    gamma = y * alpha_e
    q = S/(p*m)
    rows=[]
    for nu in harmonics:
        den = q*np.sin(0.5*nu*alpha_e)
        kd = np.sin(0.5*q*nu*alpha_e)/den if abs(den) > 1e-15 else 1.0
        kp = np.cos(0.5*nu*gamma)
        kw = kp*kd
        dbl_factor = 2*np.cos(0.5*np.deg2rad(delta_e_deg)*nu)
        rows.append(dict(nu=int(nu), k_p=float(kp), k_d=float(kd), k_w=float(kw),
                         dbl_factor=float(dbl_factor), k_w_dbl=float(dbl_factor*kw)))
    return rows


def phase_table_rows(S=40, p=4, delta_e_deg=30.0):
    alpha_e = pi*p/S
    rows=[]
    for slot in range(S):
        angle_elec_deg = float(np.rad2deg(slot*alpha_e) % 360.0)
        phase_a = ['A','B','C'][int(np.floor(angle_elec_deg/120.0))]
        phase_b = ['A','B','C'][int(np.floor(((angle_elec_deg+delta_e_deg)%360.0)/120.0))]
        rows.append(dict(slot=slot, angle_elec_deg=round(angle_elec_deg,3), phase_star_A=phase_a, phase_star_B=phase_b))
    return rows


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out-base', default='exports/SST-Coil')
    args=ap.parse_args(); run=make_run_dirs(args.out_base)
    rows=winding_rows(harmonics=range(1,16)); phase=phase_table_rows()
    write_csv_dicts(run/'csv'/'SST-Coil_winding_factors.csv', rows)
    write_csv_dicts(run/'csv'/'SST-Coil_phase_table.csv', phase)
    save_json(run/'reports'/'SST-Coil_winding_summary.json', {'n_harmonics':len(rows), 'n_slots':len(phase)})
    print('Wrote run:', run)
if __name__=='__main__': main()
