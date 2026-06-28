"""Analytical winding-factor diagnostics from double-starshaped_coil40.py."""
from __future__ import annotations
import argparse
import numpy as np
from math import pi
from SST_Coil_00_common import make_export_paths, save_csv, write_json


def winding_rows(S=40, p=4, m=3, y=2, delta_e_deg=30.0, nus=range(1,21)):
    alpha_e = pi*p/S
    gamma = y*alpha_e
    q = S/(p*m)
    def kd(nu):
        den = q*np.sin(0.5*nu*alpha_e)
        if abs(den) < 1e-15:
            return np.nan
        return np.sin(0.5*q*nu*alpha_e)/den
    def kp(nu): return np.cos(0.5*nu*gamma)
    def kw(nu): return kp(nu)*kd(nu)
    def kw_dbl(nu): return 2*np.cos(0.5*np.deg2rad(delta_e_deg)*nu)*kw(nu)
    rows=[]
    for nu in nus:
        rows.append({"nu":nu,"k_p":kp(nu),"k_d":kd(nu),"k_w":kw(nu),"dbl_factor":2*np.cos(0.5*np.deg2rad(delta_e_deg)*nu),"k_w_dbl":kw_dbl(nu),"abs_k_w_dbl":abs(kw_dbl(nu))})
    return rows


def phase_table(S=40,p=4,delta_e_deg=30.0):
    angles_elec = np.arange(S) * (pi*p/S)
    def phase_from_angle_deg(theta_deg):
        t = theta_deg % 360.0
        return ["A","B","C"][int(np.floor(t/120.0))]
    rows=[]
    for s in range(S):
        rows.append({"slot":s,"angle_elec_deg":round(np.rad2deg(angles_elec[s]),3),"phase_star_A":phase_from_angle_deg(np.rad2deg(angles_elec[s])),"phase_star_B_30deg":phase_from_angle_deg(np.rad2deg(angles_elec[s])+delta_e_deg)})
    return rows


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--export", default="exports/SST-Coil"); ap.add_argument("--max-nu", type=int, default=40)
    args=ap.parse_args(); ex=make_export_paths(args.export)
    rows=winding_rows(nus=range(1,args.max_nu+1)); save_csv(ex.csv/"SST-Coil_v7_winding_factors.csv", rows)
    save_csv(ex.csv/"SST-Coil_v7_slot_phase_table.csv", phase_table())
    write_json(ex.reports/"winding_factor_summary.json", {"min_abs_harmonics": sorted(rows, key=lambda r:r["abs_k_w_dbl"])[:8]})
    print(ex.root)
if __name__=="__main__": main()
