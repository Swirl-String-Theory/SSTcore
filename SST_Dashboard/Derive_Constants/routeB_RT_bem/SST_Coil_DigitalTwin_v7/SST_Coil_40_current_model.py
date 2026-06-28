"""PWM + crude R/L copper current model."""
from __future__ import annotations
import argparse
import numpy as np
from SST_Coil_00_common import make_export_paths, save_csv, write_json, phase_current_coeffs, skin_depth, RHO_CU


def estimate_wire_RL(length_m, wire_radius_m=0.0005, f_ref=1e6, turns_factor=1.0):
    A=np.pi*wire_radius_m**2
    Rdc=RHO_CU*length_m/A
    delta=skin_depth(f_ref)
    Rac_factor=max(1.0, wire_radius_m/(2*delta))
    # crude loop inductance scale, intentionally conservative
    L=1e-6*max(length_m,1e-9)*turns_factor
    return Rdc, Rac_factor, L


def three_phase_current_harmonics(f0=1e6,duty=0.382,harmonics=9,v_bus=24.0,R=1.0,L=1e-6,C=None):
    offs=[0.0,2*np.pi/3,4*np.pi/3]
    return [phase_current_coeffs(f0,duty,harmonics,v_bus,R,L,C,off) for off in offs]


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--f0",type=float,default=1e6); ap.add_argument("--duty",type=float,default=0.382); ap.add_argument("--harmonics",type=int,default=20); ap.add_argument("--R",type=float,default=1.0); ap.add_argument("--L",type=float,default=1e-6); ap.add_argument("--export",default="exports/SST-Coil")
    args=ap.parse_args(); ex=make_export_paths(args.export)
    coeffs=three_phase_current_harmonics(args.f0,args.duty,args.harmonics,R=args.R,L=args.L)
    rows=[]
    for ph, d in enumerate(coeffs):
        for n,c in d.items(): rows.append({"phase":ph+1,"n":n,"f_hz":n*args.f0,"I_abs_A":abs(c),"I_phase_rad":np.angle(c)})
    save_csv(ex.csv/"SST-Coil_v7_current_harmonics.csv", rows)
    write_json(ex.reports/"current_model_summary.json", vars(args))
    print(ex.root)
if __name__=="__main__": main()
