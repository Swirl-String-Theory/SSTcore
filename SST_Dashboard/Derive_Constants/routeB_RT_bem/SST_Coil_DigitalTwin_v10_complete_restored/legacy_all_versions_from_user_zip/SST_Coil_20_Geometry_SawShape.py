from __future__ import annotations
import argparse
from dataclasses import asdict
import matplotlib.pyplot as plt
from SST_Coil_00_common import SawShapeParams, build_three_phase_sawshape, make_run_paths, write_csv, save_json, polyline_length


def run(radius=0.05, height=0.0, n_pairs=20, profile="linear", samples=16,
        path_mode="chord", export_base="exports/SST-Coil", run_name=None):
    paths = make_run_paths(export_base, run_name)
    params = SawShapeParams(radius_bottom=radius, radius_top=radius, height=height,
                            n_pairs=n_pairs, profile=profile, samples_per_segment=samples, path_mode=path_mode)
    coils = build_three_phase_sawshape(params)
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    colors = ["tab:red", "tab:green", "tab:blue"]
    rows_summary = []
    for i, pts in enumerate(coils):
        ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=colors[i], lw=1.3, label=f"Phase {i+1}")
        write_csv(paths.csv / f"SST-Coil_geometry_phase_{i+1}.csv", ["x_m", "y_m", "z_m"], pts)
        rows_summary.append([i + 1, len(pts), polyline_length(pts)])
    lim = max(radius * 1.25, abs(height) * 0.6, 1e-3)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_zlabel("z [m]")
    ax.legend()
    ax.set_title("SST-Coil SawShape 3-phase geometry")
    plt.tight_layout()
    plt.savefig(paths.figures / "SST-Coil_geometry_3phase.png", dpi=180)
    plt.close(fig)
    write_csv(paths.csv / "SST-Coil_geometry_summary.csv", ["phase", "points", "polyline_length_m"], rows_summary)
    save_json(paths.reports / "SST-Coil_geometry_parameters.json", asdict(params))
    return paths, params, coils


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--radius", type=float, default=0.05)
    ap.add_argument("--height", type=float, default=0.0)
    ap.add_argument("--pairs", type=int, default=20)
    ap.add_argument("--profile", default="linear", choices=["linear", "exponential", "inverse_exponential"])
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--path-mode", default="chord", choices=["chord", "arc"])
    ap.add_argument("--export-base", default="exports/SST-Coil")
    args = ap.parse_args()
    p, *_ = run(args.radius, args.height, args.pairs, args.profile, args.samples, args.path_mode, args.export_base)
    print(p.root)
