from __future__ import annotations
import argparse
import numpy as np
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_run_paths, frequency_for_x, write_csv, save_json, V_SWIRL

# First zeros of J0 and J1-like kernels. These are candidates, not assumptions.
DEFAULT_X_NODES = [2.4048255577, 3.8317059702, 5.5200781103, 7.0155866698]


def run(radii=(0.03, 0.05, 0.10), harmonics=(1, 3, 5, 7), x_nodes=DEFAULT_X_NODES,
        export_base="exports/SST-Coil", run_name=None):
    paths = make_run_paths(export_base, run_name)
    rows = []
    for R in radii:
        for n in harmonics:
            for idx, x in enumerate(x_nodes, start=1):
                f = frequency_for_x(x, n, R, V_SWIRL)
                rows.append([R, n, idx, x, f, f * R])
    write_csv(paths.csv / "SST-Coil_fR_node_predictions.csv",
              ["R_m", "harmonic_n", "node_index", "x_node", "f0_Hz", "f0_times_R_Hz_m"], rows)

    plt.figure(figsize=(8, 5))
    for n in harmonics:
        fs = [frequency_for_x(x_nodes[0], n, R, V_SWIRL) for R in radii]
        plt.plot(radii, np.array(fs) / 1e6, marker="o", label=f"n={n}, x={x_nodes[0]:.3f}")
    plt.xlabel("coil radius R [m]")
    plt.ylabel("base frequency f0 [MHz]")
    plt.title("fR scaling: first candidate node")
    plt.legend()
    plt.tight_layout()
    plt.savefig(paths.figures / "SST-Coil_fR_first_node.png", dpi=180)
    plt.close()
    save_json(paths.reports / "SST-Coil_fR_parameters.json", {
        "radii_m": list(radii), "harmonics": list(harmonics), "x_nodes": list(x_nodes), "v_swirl_m_s": V_SWIRL
    })
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", type=float, nargs="+", default=[0.03, 0.05, 0.10])
    ap.add_argument("--harmonics", type=int, nargs="+", default=[1, 3, 5, 7])
    ap.add_argument("--export-base", default="exports/SST-Coil")
    args = ap.parse_args()
    print(run(args.radii, args.harmonics, export_base=args.export_base).root)
