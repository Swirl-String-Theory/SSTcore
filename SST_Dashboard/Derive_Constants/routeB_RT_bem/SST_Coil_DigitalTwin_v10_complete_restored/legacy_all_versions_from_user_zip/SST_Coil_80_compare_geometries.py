"""Compare SawBowl and Rodin-torus geometries under same simple current/field observable model."""
from __future__ import annotations
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_export_paths, make_grid, save_csv, write_json, normalize_response
from SST_Coil_10_geometry_sawbowl import build_sawbowl_3phase, plot_geometry as plot_sawbowl
from SST_Coil_11_geometry_rodin_torus import build_rodin_torus_coils, plot_geometry as plot_rodin
from SST_Coil_30_biot_savart import field_from_coils, field_observables
from SST_Coil_50_observables import reduce_observable
from SST_Coil_40_current_model import three_phase_current_harmonics


def phase_current_map(coils, coeffs, n=1, family_sign=True):
    m={}
    for c in coils:
        pi = c.get("phase_index", None)
        if pi is None:
            # SawBowl name Phase 1 etc.
            pi = int(c["name"].split()[-1])-1
        I = coeffs[pi][n]
        if family_sign and c.get("family","") == "CCW": I = -I
        m[c["name"]] = float(np.real(I))  # quasi-static snapshot at t=0
    return m


def evaluate_geometry(coils, f0s, radius_label, bounds, grid, duty, harmonics, mode, r_soft):
    x,X,Y,Z = make_grid(bounds, grid); spacing=x[1]-x[0]
    rows=[]
    # crude fixed R/L; intentionally same for both geometries except user can later replace with measured values.
    for f0 in f0s:
        coeffs=three_phase_current_harmonics(f0=f0,duty=duty,harmonics=harmonics,R=1.0,L=1e-6)
        total=0.0
        for n in range(1,harmonics+1):
            cmap=phase_current_map(coils, coeffs, n=n)
            Bx,By,Bz=field_from_coils(X,Y,Z,coils,current_map=cmap,r_softening=r_soft)
            obs=field_observables(Bx,By,Bz,spacing)
            total += reduce_observable(obs, mode=mode)
        rows.append({"geometry":radius_label,"f0_hz":float(f0),"observable":float(total)})
    return rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=int,default=24)
    ap.add_argument("--f-min",type=float,default=1e5)
    ap.add_argument("--f-max",type=float,default=5e6)
    ap.add_argument("--grid",type=int,default=9)
    ap.add_argument("--bounds",type=float,default=0.09)
    ap.add_argument("--duty",type=float,default=0.382)
    ap.add_argument("--harmonics",type=int,default=5)
    ap.add_argument("--observable",default="weighted_gradB2")
    ap.add_argument("--export",default="exports/SST-Coil")
    args=ap.parse_args(); ex=make_export_paths(args.export)
    f0s=np.geomspace(args.f_min,args.f_max,args.samples)
    saw=build_sawbowl_3phase(pairs=20,Rb=0.05,Rt=0.05,height=0.006,samples_per_seg=12,mode="curved")
    rod=build_rodin_torus_coils(R_major=0.049,r_minor=0.012,p=5,q=12,phases=3,turns=1,points=500,separate_families=True,gap=0.05)
    plot_sawbowl(saw, ex.figures/"SST-Coil_v7_geometry_sawbowl.png")
    plot_rodin(rod, ex.figures/"SST-Coil_v7_geometry_rodin_torus.png")
    rows=[]
    rows += evaluate_geometry(saw, f0s, "SawBowl_S40_11_-9", args.bounds,args.grid,args.duty,args.harmonics,args.observable,1e-4)
    rows += evaluate_geometry(rod, f0s, "Rodin_T5_12_CWCCW", args.bounds,args.grid,args.duty,args.harmonics,args.observable,1e-4)
    save_csv(ex.csv/"SST-Coil_v7_compare_geometries.csv", rows)
    fig,ax=plt.subplots(figsize=(9,5.5))
    for geom in sorted(set(r["geometry"] for r in rows)):
        sub=[r for r in rows if r["geometry"]==geom]
        f=np.array([r["f0_hz"] for r in sub]); y=normalize_response(np.array([r["observable"] for r in sub]))
        ax.plot(f,y,label=geom)
    ax.set_xscale("log"); ax.set_xlabel("base frequency f0 [Hz]"); ax.set_ylabel(f"normalized {args.observable}"); ax.set_title("v7 geometry comparison under same drive model")
    ax.legend(); fig.tight_layout(); fig.savefig(ex.figures/"SST-Coil_v7_compare_geometries_response.png",dpi=170); plt.close(fig)
    write_json(ex.reports/"v7_compare_summary.json", vars(args)|{"note":"SawBowl and Rodin are separate geometry sectors; current model remains first-order R/L."})
    print(ex.root)
if __name__=="__main__": main()
