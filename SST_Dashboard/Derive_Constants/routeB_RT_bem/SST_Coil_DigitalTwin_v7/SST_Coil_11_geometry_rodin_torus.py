"""Rodin / torus-knot 3-phase geometry extracted from rodin_GUI.py logic.
Strictly separate from SawBowl geometry.
"""
from __future__ import annotations
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_export_paths, save_csv, write_json


def torus_knot_cellphase_polyline(R_major, r_minor, p, q, n_points=1200, turns=1,
                                  cell_phase_frac=0.0, mirror=False, z_offset=0.0,
                                  theta_offset=0.0):
    p = int(max(1,p)); q = int(max(1,q)); turns = int(max(1,turns))
    t = np.linspace(0, 2*np.pi*turns, int(max(120,n_points)))
    dt_cell = float(cell_phase_frac) * (2*np.pi/q)
    tp = t + dt_cell
    theta = p*tp + float(theta_offset)
    phi_t = q*tp
    if mirror:
        phi_t = -phi_t
    x = (R_major + r_minor*np.cos(phi_t))*np.cos(theta)
    y = (R_major + r_minor*np.cos(phi_t))*np.sin(theta)
    z = r_minor*np.sin(phi_t) + z_offset
    return np.stack([x,y,z], axis=1)


def build_rodin_torus_coils(R_major=0.049, r_minor=0.012, p=5, q=12, phases=3, turns=1,
                            points=900, separate_families=False, gap=0.0,
                            ccw_start_mode="Same", ccw_mode="overlay_reversed"):
    """Build Rodin / torus-knot coils.

    ccw_mode:
      - "overlay_reversed" (default): CCW occupies the exact same spatial curve and z-coordinates
        as CW, but the point order is reversed to represent opposite winding/current direction.
      - "mirror_phi": legacy rodin_GUI mirror, phi -> -phi. This mirrors z and is NOT co-located.
    separate_families:
      legacy vertical split. Keep False for the intended physical co-located CW/CCW geometry.
    """
    phases = int(max(1, phases)); q = int(max(1,q))
    cell_fracs = np.arange(phases, dtype=float)/phases
    z_cw = -gap/2 if separate_families else 0.0
    z_ccw = +gap/2 if separate_families else 0.0
    theta_offset_ccw = np.pi if str(ccw_start_mode).startswith("Opposite") else 0.0
    coils=[]
    cw_points=[]
    for i, cf in enumerate(cell_fracs):
        pts = torus_knot_cellphase_polyline(R_major,r_minor,p,q,points,turns,cf,False,z_cw,0.0)
        cw_points.append(pts)
        coils.append({"name":f"CW Phase {i+1}","points":pts,"family":"CW","phase_index":i})
    for i, cf in enumerate(cell_fracs):
        if ccw_mode == "overlay_reversed":
            pts = cw_points[i][::-1].copy()
            if separate_families:
                pts[:,2] += (z_ccw - z_cw)
        elif ccw_mode == "mirror_phi":
            pts = torus_knot_cellphase_polyline(R_major,r_minor,p,q,points,turns,cf,True,z_ccw,theta_offset_ccw)
        else:
            raise ValueError(f"Unknown ccw_mode={ccw_mode!r}")
        coils.append({"name":f"CCW Phase {i+1}","points":pts,"family":"CCW","phase_index":i})
    return coils


def plot_geometry(coils, out_path):
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection="3d")
    for c in coils:
        p = c["points"]
        ax.plot(p[:,0],p[:,1],p[:,2],lw=1.05, linestyle="--" if c["family"]=="CCW" else "-", label=c["name"])
    ax.set_title("SST-Coil v7 Rodin torus-knot geometry")
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_zlabel("z [m]")
    ax.legend(fontsize=8)
    allp = np.concatenate([c["points"] for c in coils], axis=0)
    lim = np.max(np.abs(allp))*1.12
    ax.set_xlim(-lim,lim); ax.set_ylim(-lim,lim); ax.set_zlim(np.min(allp[:,2])*1.12, np.max(allp[:,2])*1.12)
    fig.tight_layout(); fig.savefig(out_path, dpi=180); plt.close(fig)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--R-major", type=float, default=0.049)
    ap.add_argument("--r-minor", type=float, default=0.012)
    ap.add_argument("--p", type=int, default=5)
    ap.add_argument("--q", type=int, default=12)
    ap.add_argument("--phases", type=int, default=3)
    ap.add_argument("--turns", type=int, default=1)
    ap.add_argument("--points", type=int, default=900)
    ap.add_argument("--gap", type=float, default=0.0)
    ap.add_argument("--ccw-mode", default="overlay_reversed", choices=["overlay_reversed","mirror_phi"])
    ap.add_argument("--separate-families", action="store_true")
    ap.add_argument("--export", default="exports/SST-Coil")
    args=ap.parse_args()
    ex=make_export_paths(args.export)
    coils=build_rodin_torus_coils(args.R_major,args.r_minor,args.p,args.q,args.phases,args.turns,args.points,args.separate_families,args.gap, ccw_mode=args.ccw_mode)
    plot_geometry(coils, ex.figures/"SST-Coil_v7_geometry_rodin_torus.png")
    rows=[]
    for c in coils:
        for j,(x,y,z) in enumerate(c["points"]): rows.append({"coil":c["name"],"family":c["family"],"phase_index":c["phase_index"],"j":j,"x_m":x,"y_m":y,"z_m":z})
    save_csv(ex.csv/"SST-Coil_v7_geometry_rodin_points.csv", rows)
    write_json(ex.reports/"rodin_geometry_summary.json", vars(args)|{"n_coils":len(coils)})
    print(ex.root)

if __name__=="__main__": main()
