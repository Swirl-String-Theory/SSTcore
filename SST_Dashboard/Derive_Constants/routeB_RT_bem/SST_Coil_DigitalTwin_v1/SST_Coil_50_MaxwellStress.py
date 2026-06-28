from __future__ import annotations
import argparse
import numpy as np
from pathlib import Path
from SST_Coil_00_common import make_run_paths, MU0, write_csv, save_json


def maxwell_stress_tensor(B: np.ndarray) -> np.ndarray:
    """Return T_ij = (B_i B_j - 1/2 delta_ij B^2)/mu0 for real B vectors."""
    B = np.asarray(B, dtype=float)
    B2 = np.sum(B * B, axis=-1)
    T = np.zeros(B.shape[:-1] + (3, 3), dtype=float)
    for i in range(3):
        for j in range(3):
            T[..., i, j] = B[..., i] * B[..., j]
            if i == j:
                T[..., i, j] -= 0.5 * B2
    return T / MU0


def run(npz_path: str | Path, export_base="exports/SST-Coil", run_name=None):
    """Compute a conservative Maxwell-stress proxy from midplane data.

    This is not a full closed-surface force integral; it is a diagnostic tensor summary.
    A true force calculation needs B on all faces of a closed 3D control surface.
    """
    paths = make_run_paths(export_base, run_name)
    data = np.load(npz_path, allow_pickle=True)
    B = np.real(data["B"])
    T = maxwell_stress_tensor(B)
    means = np.mean(T, axis=0)
    maxabs = np.max(np.abs(T), axis=0)
    rows = []
    for i in range(3):
        for j in range(3):
            rows.append([i, j, means[i, j], maxabs[i, j]])
    write_csv(paths.csv / "SST-Coil_MaxwellStress_tensor_summary.csv",
              ["i", "j", "mean_Tij_Pa", "max_abs_Tij_Pa"], rows)
    save_json(paths.reports / "SST-Coil_MaxwellStress_report.json", {
        "source_npz": str(npz_path),
        "note": "midplane tensor diagnostic only; not a full closed-surface force integral",
        "mean_tensor_Pa": means.tolist(),
        "max_abs_tensor_Pa": maxabs.tolist()
    })
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("npz_path")
    ap.add_argument("--export-base", default="exports/SST-Coil")
    args = ap.parse_args()
    print(run(args.npz_path, args.export_base).root)
