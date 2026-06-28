from __future__ import annotations
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from SST_Coil_00_common import make_run_paths, write_csv, save_json, MU0


def analyze(npz_path: str | Path, export_base="exports/SST-Coil", run_name=None):
    paths = make_run_paths(export_base, run_name)
    data = np.load(npz_path, allow_pickle=True)
    points = data["points"]
    B = data["B"]
    Bmag = data["Bmag"]
    pressure = data["pressure"]
    X, Y = data["X"], data["Y"]
    shape = X.shape
    B2 = Bmag.reshape(shape) ** 2
    P = pressure.reshape(shape)
    dx = float(np.mean(np.diff(X[:, 0]))) if shape[0] > 1 else 1.0
    dy = float(np.mean(np.diff(Y[0, :]))) if shape[1] > 1 else 1.0
    dB2_dx, dB2_dy = np.gradient(B2, dx, dy, edge_order=1)
    grad_mag = np.sqrt(dB2_dx**2 + dB2_dy**2)

    np.savez_compressed(paths.npz / "SST-Coil_FieldAnalysis.npz", B2=B2, P=P, dB2_dx=dB2_dx, dB2_dy=dB2_dy, grad_mag=grad_mag)
    write_csv(paths.csv / "SST-Coil_FieldAnalysis_summary.csv",
              ["metric", "value"],
              [["B2_max_T2", float(np.max(B2))], ["B2_mean_T2", float(np.mean(B2))],
               ["grad_B2_max_T2_per_m", float(np.max(grad_mag))],
               ["magnetic_energy_density_max_J_m3", float(np.max(B2)/(2*MU0))],
               ["pressure_proxy_min_Pa", float(np.min(P))]])

    extent = [float(X.min()), float(X.max()), float(Y.min()), float(Y.max())]
    plt.figure(figsize=(7, 6))
    plt.imshow(grad_mag.T, origin="lower", extent=extent, aspect="equal")
    plt.colorbar(label="|∇B²| [T²/m]")
    plt.xlabel("x [m]"); plt.ylabel("y [m]")
    plt.title("Field-gradient proxy")
    plt.tight_layout()
    plt.savefig(paths.figures / "SST-Coil_gradB2_midplane.png", dpi=180)
    plt.close()

    save_json(paths.reports / "SST-Coil_FieldAnalysis_report.json", {
        "source_npz": str(npz_path),
        "B2_max_T2": float(np.max(B2)),
        "grad_B2_max_T2_per_m": float(np.max(grad_mag))
    })
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("npz_path")
    ap.add_argument("--export-base", default="exports/SST-Coil")
    args = ap.parse_args()
    print(analyze(args.npz_path, args.export_base).root)
