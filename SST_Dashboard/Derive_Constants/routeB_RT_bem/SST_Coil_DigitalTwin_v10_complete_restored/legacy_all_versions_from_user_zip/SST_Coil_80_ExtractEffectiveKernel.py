from __future__ import annotations
import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from SST_Coil_00_common import CoilConfig, CircuitConfig, SweepConfig, ensure_run_dirs, normalize_response, find_zero_crossings, local_extrema, save_json, V_SWIRL
from SST_Coil_40_BiotSavartDigitalTwin import field_harmonic_observable


def run_effective_kernel_sweep(radii, f_min, f_max, samples, duty, harmonics, observable, grid, export_root):
    dirs = ensure_run_dirs(export_root)
    freqs = np.geomspace(f_min, f_max, samples)
    response_rows = []
    feature_rows = []
    for R in radii:
        cfg = CoilConfig(radius_m=float(R), samples_per_segment=3, turns_pairs=40, path_mode="chord")
        circ = CircuitConfig(duty=duty)
        vals = []
        for f0 in freqs:
            obs = field_harmonic_observable(float(f0), cfg, circ, harmonics=harmonics, grid=grid, z_probe=max(0.012, 0.25*R), softening=max(1e-4, 0.004*R))
            vals.append(float(obs[observable]))
        vals = np.array(vals, dtype=float)
        norm = normalize_response(vals)
        for f0, v, vn in zip(freqs, vals, norm):
            response_rows.append({"R_m": R, "f0_hz": f0, "fR_Hz_m": f0*R, "observable": observable, "response_raw": v, "response_norm": vn})
        zeros = find_zero_crossings(freqs, norm)
        for j, z in enumerate(zeros[:10]):
            feature_rows.append({"R_m": R, "feature": "zero", "index": j+1, "f0_hz": z, "fR_Hz_m": z*R, "invR_m^-1": 1/R, "value": 0.0})
        for kind, xf, yf in local_extrema(freqs, norm, min_separation=max(3, samples//80))[:12]:
            feature_rows.append({"R_m": R, "feature": kind, "index": 0, "f0_hz": xf, "fR_Hz_m": xf*R, "invR_m^-1": 1/R, "value": yf})
    df = pd.DataFrame(response_rows)
    ff = pd.DataFrame(feature_rows)
    df.to_csv(dirs["csv"] / "SST-Coil_effective_kernel_response.csv", index=False)
    ff.to_csv(dirs["csv"] / "SST-Coil_effective_kernel_features.csv", index=False)

    fig, ax = plt.subplots(figsize=(11,6))
    for R, g in df.groupby("R_m"):
        ax.semilogx(g["f0_hz"], g["response_norm"], label=f"R={R:.3f} m")
    ax.axhline(0, lw=0.8)
    ax.set_xlabel("base frequency f0 [Hz]"); ax.set_ylabel("normalized extracted response")
    ax.set_title(f"Digital-twin extracted observable vs absolute frequency — {observable}")
    ax.legend(); fig.tight_layout(); fig.savefig(dirs["figures"] / "SST-Coil_effective_kernel_vs_frequency.png", dpi=180)

    fig, ax = plt.subplots(figsize=(11,6))
    for R, g in df.groupby("R_m"):
        ax.semilogx(g["fR_Hz_m"], g["response_norm"], label=f"R={R:.3f} m")
    ax.axhline(0, lw=0.8)
    ax.set_xlabel("f0 R [Hz m]"); ax.set_ylabel("normalized extracted response")
    ax.set_title("Effective-kernel collapse test from digital twin output")
    ax.legend(); fig.tight_layout(); fig.savefig(dirs["figures"] / "SST-Coil_effective_kernel_fR_collapse.png", dpi=180)

    # simple quality metric: interpolate all curves onto common fR overlap and compute RMS spread
    fR_min = max(df[df.R_m==R]["fR_Hz_m"].min() for R in radii)
    fR_max = min(df[df.R_m==R]["fR_Hz_m"].max() for R in radii)
    common = np.geomspace(fR_min, fR_max, 300)
    curves = []
    for R, g in df.groupby("R_m"):
        curves.append(np.interp(np.log(common), np.log(g["fR_Hz_m"].values), g["response_norm"].values))
    curves = np.array(curves)
    collapse_rms = float(np.sqrt(np.mean((curves - curves.mean(axis=0))**2)))
    save_json(dirs["reports"] / "effective_kernel_summary.json", {
        "observable": observable,
        "radii_m": list(map(float, radii)),
        "f_min_hz": f_min,
        "f_max_hz": f_max,
        "samples": samples,
        "harmonics": harmonics,
        "grid": grid,
        "duty": duty,
        "collapse_rms_in_fR": collapse_rms,
        "interpretation": "Small collapse_rms means curves align when plotted against f0*R. This is necessary but not sufficient evidence for a geometric kernel; compare against absolute-frequency resonance and measured data."
    })
    return dirs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", type=float, nargs="+", default=[0.03,0.05,0.10])
    ap.add_argument("--f-min", type=float, default=1e5)
    ap.add_argument("--f-max", type=float, default=8e6)
    ap.add_argument("--samples", type=int, default=70)
    ap.add_argument("--duty", type=float, default=0.382)
    ap.add_argument("--harmonics", type=int, default=9)
    ap.add_argument("--observable", choices=["weighted_gradB2", "axis_B2", "asymmetry_Bz", "signed_Bz_proxy"], default="weighted_gradB2")
    ap.add_argument("--grid", type=int, default=13)
    ap.add_argument("--export-root", default="exports/SST-Coil")
    args = ap.parse_args()
    dirs = run_effective_kernel_sweep(args.radii, args.f_min, args.f_max, args.samples, args.duty, args.harmonics, args.observable, args.grid, args.export_root)
    print(dirs["base"])

if __name__ == "__main__":
    main()
