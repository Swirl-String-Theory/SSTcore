"""SawBowl/SawShape geometry extracted from GUI-SawBowl.py logic.
Strictly separate from Rodin torus geometry.
"""
from __future__ import annotations
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_export_paths, save_csv, write_json

S_DEFAULT = 40
STEP_FWD_DEFAULT = 11
STEP_BWD_DEFAULT = -9
POWER_DEFAULT = 2.2
PHASE_OFFSETS_3 = [0.0, 2*np.pi/3, 4*np.pi/3]


def alternating_skip_indices(S=40, step_fwd=11, step_bwd=-9, n_pairs=20, start=1):
    idx = int(start)
    seq = [idx]
    for k in range(2*int(n_pairs)):
        if k % 2 == 0:
            idx = (idx + step_fwd - 1) % S + 1
        else:
            idx = (idx + step_bwd - 1) % S + 1
        seq.append(idx)
    return np.array(seq, dtype=int)


def r_profile(s, Rb, Rt, profile="Exponential", power=POWER_DEFAULT):
    s = np.asarray(s, dtype=float)
    if profile.lower().startswith("exp"):
        return Rb + (Rt - Rb)*(s**power)
    if profile.lower().startswith("inverse"):
        return Rt - (Rt - Rb)*(s**power)
    return Rb + (Rt - Rb)*s


def build_sawbowl_phase(S=40, step_fwd=11, step_bwd=-9, pairs=20,
                        Rb=0.05, Rt=0.05, height=0.006, angle_offset=0.0,
                        profile="Exponential", power=POWER_DEFAULT,
                        samples_per_seg=24, start=1, mode="curved"):
    seq = alternating_skip_indices(S, step_fwd, step_bwd, pairs, start=start)
    slot_angles = np.linspace(0, 2*np.pi, S, endpoint=False) - np.pi/2.0
    N = len(seq) - 1
    s_nodes = np.linspace(0, 1, N+1)
    r_nodes = r_profile(s_nodes, Rb, Rt, profile, power)
    z_nodes = s_nodes * height
    if mode == "straight":
        pts = []
        for k in range(N+1):
            a = slot_angles[seq[k]-1] + angle_offset
            pts.append([r_nodes[k]*np.cos(a), r_nodes[k]*np.sin(a), z_nodes[k]])
        return np.asarray(pts), seq
    xs, ys, zs = [], [], []
    for k in range(N):
        i0, i1 = seq[k]-1, seq[k+1]-1
        a0 = slot_angles[i0] + angle_offset
        a1 = slot_angles[i1] + angle_offset
        # shortest angular interpolation, exactly as original curved phase logic
        da = (a1 - a0 + np.pi) % (2*np.pi) - np.pi
        t = np.linspace(0, 1, samples_per_seg, endpoint=False)
        a_line = a0 + t*da
        r_line = r_nodes[k] + t*(r_nodes[k+1]-r_nodes[k])
        z_line = z_nodes[k] + t*(z_nodes[k+1]-z_nodes[k])
        xs.append(r_line*np.cos(a_line)); ys.append(r_line*np.sin(a_line)); zs.append(z_line)
    # append final node
    a = slot_angles[seq[-1]-1] + angle_offset
    xs.append(np.array([r_nodes[-1]*np.cos(a)])); ys.append(np.array([r_nodes[-1]*np.sin(a)])); zs.append(np.array([z_nodes[-1]]))
    return np.column_stack([np.concatenate(xs), np.concatenate(ys), np.concatenate(zs)]), seq


def build_sawbowl_3phase(**kwargs):
    phases = []
    for i, off in enumerate(PHASE_OFFSETS_3):
        pts, seq = build_sawbowl_phase(angle_offset=off, **kwargs)
        phases.append({"name": f"Phase {i+1}", "points": pts, "seq": seq, "phase_offset": off})
    return phases


def plot_geometry(phases, out_path):
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection="3d")
    for ph in phases:
        p = ph["points"]
        ax.plot(p[:,0], p[:,1], p[:,2], lw=1.1, label=ph["name"])
    ax.set_title("SST-Coil v7 SawBowl: S=40, +11,-9, continuous z")
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_zlabel("z [m]")
    ax.legend()
    lim = max(np.max(np.abs(ph["points"][:,:2])) for ph in phases)*1.15
    zmax = max(np.max(ph["points"][:,2]) for ph in phases)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(0, max(zmax, 1e-6))
    fig.tight_layout(); fig.savefig(out_path, dpi=180); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=20)
    ap.add_argument("--Rb", type=float, default=0.05)
    ap.add_argument("--Rt", type=float, default=0.05)
    ap.add_argument("--height", type=float, default=0.006)
    ap.add_argument("--samples-per-seg", type=int, default=24)
    ap.add_argument("--mode", choices=["curved","straight"], default="curved")
    ap.add_argument("--export", default="exports/SST-Coil")
    args = ap.parse_args()
    ex = make_export_paths(args.export)
    phases = build_sawbowl_3phase(pairs=args.pairs, Rb=args.Rb, Rt=args.Rt, height=args.height,
                                  samples_per_seg=args.samples_per_seg, mode=args.mode)
    plot_geometry(phases, ex.figures/"SST-Coil_v7_geometry_sawbowl.png")
    rows = []
    for ph in phases:
        for j, (x,y,z) in enumerate(ph["points"]):
            rows.append({"phase": ph["name"], "j": j, "x_m": x, "y_m": y, "z_m": z})
    save_csv(ex.csv/"SST-Coil_v7_geometry_sawbowl_points.csv", rows)
    write_json(ex.reports/"sawbowl_geometry_summary.json", {"pairs":args.pairs,"Rb":args.Rb,"Rt":args.Rt,"height":args.height,"mode":args.mode,"n_points_per_phase":len(phases[0]["points"])})
    print(ex.root)

if __name__ == "__main__":
    main()
