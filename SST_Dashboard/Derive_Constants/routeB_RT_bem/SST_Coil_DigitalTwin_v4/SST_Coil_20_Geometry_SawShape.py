from __future__ import annotations
import argparse
import math
from pathlib import Path
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt

from SST_Coil_00_common import CoilConfig, ensure_run_dirs, save_json


def alternating_skip_indices(S: int, step_fwd: int, step_bwd: int, n_pairs: int, start: int = 0) -> np.ndarray:
    idx = int(start) % S
    seq = [idx]
    for k in range(2 * int(n_pairs)):
        if k % 2 == 0:
            idx = (idx + step_fwd) % S
        else:
            idx = (idx + step_bwd) % S
        seq.append(idx)
    return np.array(seq, dtype=int)


def interpolate_segment(a0: float, a1: float, r0: float, r1: float, z0: float, z1: float, samples: int, mode: str) -> np.ndarray:
    samples = max(2, int(samples))
    if mode == "arc":
        da = (a1 - a0 + math.pi) % (2*math.pi) - math.pi
        t = np.linspace(0, 1, samples, endpoint=False)
        a = a0 + t * da
        r = r0 + t * (r1-r0)
        z = z0 + t * (z1-z0)
        return np.stack([r*np.cos(a), r*np.sin(a), z], axis=1)
    # chord mode: straight 3D line between slot points
    p0 = np.array([r0*math.cos(a0), r0*math.sin(a0), z0], dtype=float)
    p1 = np.array([r1*math.cos(a1), r1*math.sin(a1), z1], dtype=float)
    t = np.linspace(0, 1, samples, endpoint=False)
    return p0[None, :] + t[:, None]*(p1-p0)[None, :]


def build_sawshape_phase(cfg: CoilConfig, phase_index: int = 0, layer_index: int = 0) -> np.ndarray:
    S = cfg.S
    phase_offset = 2.0 * math.pi * phase_index / cfg.phases
    layer_z = (layer_index - 0.5*(cfg.layer_count-1)) * cfg.layer_spacing_m
    seq = alternating_skip_indices(S, cfg.step_fwd, cfg.step_bwd, cfg.turns_pairs, start=phase_index)
    slot_angles = np.linspace(0, 2*math.pi, S, endpoint=False) - math.pi/2 + phase_offset

    pts = []
    N = len(seq)-1
    for k in range(N):
        i0, i1 = seq[k], seq[k+1]
        # optional slow z progression over path plus layer offset
        z0 = cfg.height_m * (k / max(N,1) - 0.5) + layer_z
        z1 = cfg.height_m * ((k+1) / max(N,1) - 0.5) + layer_z
        seg = interpolate_segment(slot_angles[i0], slot_angles[i1], cfg.radius_m, cfg.radius_m, z0, z1, cfg.samples_per_segment, cfg.path_mode)
        pts.append(seg)
    pts.append(np.array([[cfg.radius_m*math.cos(slot_angles[seq[-1]]), cfg.radius_m*math.sin(slot_angles[seq[-1]]), cfg.height_m*0.5 + layer_z]]))
    return np.concatenate(pts, axis=0)


def build_all_phases(cfg: CoilConfig) -> List[Tuple[int, int, np.ndarray]]:
    out = []
    for li in range(cfg.layer_count):
        for pi in range(cfg.phases):
            out.append((pi, li, build_sawshape_phase(cfg, pi, li)))
    return out


def estimate_wire_length(polyline: np.ndarray) -> float:
    return float(np.sum(np.linalg.norm(np.diff(polyline, axis=0), axis=1)))


def plot_geometry(cfg: CoilConfig, out_path: Path | None = None):
    coils = build_all_phases(cfg)
    colors = ["tab:red", "tab:green", "tab:blue", "tab:purple", "tab:orange", "tab:cyan"]
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    for pi, li, pts in coils:
        ax.plot(pts[:,0], pts[:,1], pts[:,2], color=colors[pi % len(colors)], lw=1.2, alpha=0.85, label=f"Phase {pi+1}" if li == 0 else None)
    lim = cfg.radius_m * 1.25
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    zlim = max(abs(cfg.height_m)*0.75 + cfg.layer_spacing_m*cfg.layer_count, cfg.radius_m*0.2)
    ax.set_zlim(-zlim, zlim)
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_zlabel("z [m]")
    ax.set_title(f"SST-Coil SawShape S={cfg.S}, steps=({cfg.step_fwd},{cfg.step_bwd}), mode={cfg.path_mode}")
    ax.legend()
    fig.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=180)
    return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--radius", type=float, default=0.05)
    ap.add_argument("--height", type=float, default=0.0)
    ap.add_argument("--layers", type=int, default=1)
    ap.add_argument("--path-mode", choices=["chord", "arc"], default="chord")
    ap.add_argument("--export-root", default="exports/SST-Coil")
    args = ap.parse_args()
    dirs = ensure_run_dirs(args.export_root)
    cfg = CoilConfig(radius_m=args.radius, height_m=args.height, layer_count=args.layers, path_mode=args.path_mode)
    plot_geometry(cfg, dirs["figures"] / "SST-Coil_geometry_3phase.png")
    lengths = {f"phase_{pi+1}_layer_{li+1}": estimate_wire_length(pts) for pi,li,pts in build_all_phases(cfg)}
    save_json(dirs["reports"] / "geometry_parameters.json", {"config": cfg, "wire_lengths_m": lengths})
    print(dirs["base"])

if __name__ == "__main__":
    main()
