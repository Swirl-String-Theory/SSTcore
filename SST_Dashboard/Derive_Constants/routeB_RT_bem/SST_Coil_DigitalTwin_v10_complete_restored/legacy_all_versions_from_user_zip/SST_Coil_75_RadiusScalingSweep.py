"""
SST_Coil_75_RadiusScalingSweep.py
Dense radius-scaling sweep for the SST SawShape coil suite.

Purpose
-------
Test the *mathematical diagnostic* for a geometry-kernel response:

    response(f0, R) = sum_n P_n(duty) * G(2*pi*n*f0*R/v_swirl)

If the response is controlled by x = k_n R, extracted nodes/peaks should obey

    f_feature * R ~= constant / n

for the same harmonic/kernel feature. If features remain at fixed absolute f0
when R changes, they are more likely electronics/parasitic resonances.

Important
---------
This script uses explicit candidate kernels. It does not claim anomalous gravity.
It supplies a falsifiable frequency-radius scaling diagnostic for later measured
observables such as force, phase, impedance, B^2, or pickup voltage.
"""
from __future__ import annotations

import argparse
import math
from typing import Iterable

import numpy as np
import matplotlib.pyplot as plt

from SST_Coil_00_common import (
    V_SWIRL,
    make_run_paths,
    pwm_real_harmonic_amplitude,
    kernel_x,
    write_csv,
    save_json,
)


def candidate_kernel(x: np.ndarray, kind: str = "sinc") -> np.ndarray:
    """Candidate geometry kernels G(x).

    Available kernels are intentionally simple and dependency-free:
    - sinc: sin(x)/x, zeros at pi, 2pi, ...
    - damped_sinc: sin(x)/x with weak exponential damping
    - cos_sinc: cos(x)*sin(x)/x, sign-changing lobes
    - j0_asymptotic: cos(x-pi/4)/sqrt(x+eps), large-x Bessel-like sign pattern

    Replace this with an experimentally calibrated G(x) when available.
    """
    x = np.asarray(x, dtype=float)
    eps = 1e-12
    if kind == "damped_sinc":
        return np.sinc(x / np.pi) * np.exp(-0.03 * x)
    if kind == "cos_sinc":
        return np.cos(x) * np.sinc(x / np.pi)
    if kind == "j0_asymptotic":
        return np.cos(x - np.pi / 4.0) / np.sqrt(np.maximum(x, eps) + 1.0)
    return np.sinc(x / np.pi)


def normalize(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    m = np.nanmax(np.abs(y))
    if not np.isfinite(m) or m <= 0:
        return y.copy()
    return y / m


def detect_zero_crossings(freqs: np.ndarray, y: np.ndarray) -> list[dict[str, float]]:
    """Linear-interpolated zero crossings."""
    freqs = np.asarray(freqs, dtype=float)
    y = np.asarray(y, dtype=float)
    out: list[dict[str, float]] = []
    for i in range(len(y) - 1):
        y0, y1 = y[i], y[i + 1]
        if not (np.isfinite(y0) and np.isfinite(y1)):
            continue
        if y0 == 0.0:
            fz = freqs[i]
        elif y0 * y1 < 0.0:
            # interpolate in log-frequency for dense logarithmic sweeps
            lf0 = math.log(freqs[i])
            lf1 = math.log(freqs[i + 1])
            frac = abs(y0) / (abs(y0) + abs(y1))
            fz = math.exp(lf0 + frac * (lf1 - lf0))
        else:
            continue
        out.append({"kind": "zero", "index": float(i), "f_Hz": float(fz), "response": 0.0})
    return out


def detect_local_extrema(freqs: np.ndarray, y: np.ndarray, max_features: int = 12,
                         min_abs_fraction: float = 0.08) -> list[dict[str, float]]:
    """Detect local extrema and return strongest by |response|."""
    freqs = np.asarray(freqs, dtype=float)
    y = np.asarray(y, dtype=float)
    dy0 = y[1:-1] - y[:-2]
    dy1 = y[2:] - y[1:-1]
    idxs = np.where((dy0 * dy1) < 0.0)[0] + 1
    if idxs.size == 0:
        return []
    abs_y = np.abs(y[idxs])
    threshold = float(min_abs_fraction) * float(np.nanmax(np.abs(y)))
    keep = idxs[abs_y >= threshold]
    keep = sorted(keep, key=lambda i: abs(y[i]), reverse=True)[:max_features]
    keep = sorted(keep, key=lambda i: freqs[i])
    out = []
    for i in keep:
        kind = "peak" if y[i] > y[i - 1] and y[i] > y[i + 1] else "trough"
        out.append({"kind": kind, "index": float(i), "f_Hz": float(freqs[i]), "response": float(y[i])})
    return out


def weighted_response(freqs: np.ndarray, radius: float, duty: float, n_harmonics: int,
                      kernel_kind: str, include_skin_rolloff: bool = False,
                      skin_ref_hz: float = 1e6) -> tuple[np.ndarray, list[dict[str, float]]]:
    """Compute response(f, R) and per-harmonic rows."""
    freqs = np.asarray(freqs, dtype=float)
    total = np.zeros_like(freqs, dtype=float)
    rows: list[dict[str, float]] = []
    for n in range(1, int(n_harmonics) + 1):
        amp = pwm_real_harmonic_amplitude(duty, n, 1.0)
        x = 2.0 * np.pi * n * freqs * radius / V_SWIRL
        g = candidate_kernel(x, kernel_kind)
        # Optional crude electronics/current rolloff control: attenuate high n*f.
        # This is not a substitute for circuit simulation; it prevents false claims
        # that all high harmonics are equally drivable.
        if include_skin_rolloff:
            drive = 1.0 / np.sqrt(1.0 + (n * freqs / skin_ref_hz))
        else:
            drive = 1.0
        contrib = amp * drive * g
        total += contrib
        # Sparse per-harmonic rows only at every ~50th frequency to avoid giant CSV.
        stride = max(1, len(freqs) // 200)
        for j in range(0, len(freqs), stride):
            rows.append({
                "R_m": float(radius),
                "f0_Hz": float(freqs[j]),
                "n": int(n),
                "duty": float(duty),
                "PWM_amp": float(amp),
                "x_knR": float(x[j]),
                "G_candidate": float(g[j]),
                "weighted_contribution": float(contrib[j]),
            })
    return total, rows


def run(radii: Iterable[float] = (0.03, 0.05, 0.10), duty: float = 0.382,
        f_min: float = 1e5, f_max: float = 25e6, samples: int = 2500,
        n_harmonics: int = 15, kernel_kind: str = "sinc",
        include_skin_rolloff: bool = False,
        export_base: str = "exports/SST-Coil", run_name: str | None = None):
    paths = make_run_paths(export_base, run_name)
    radii = [float(r) for r in radii]
    freqs = np.geomspace(float(f_min), float(f_max), int(samples))

    all_feature_rows = []
    all_response_rows = []
    harmonic_rows = []
    response_by_radius = {}

    for R in radii:
        y, hrows = weighted_response(freqs, R, duty, n_harmonics, kernel_kind, include_skin_rolloff)
        yn = normalize(y)
        response_by_radius[R] = yn
        harmonic_rows.extend(hrows)

        zeros = detect_zero_crossings(freqs, yn)
        extrema = detect_local_extrema(freqs, yn)
        features = zeros[:20] + extrema
        features = sorted(features, key=lambda row: row["f_Hz"])
        for local_idx, feat in enumerate(features):
            all_feature_rows.append([
                R,
                local_idx,
                feat["kind"],
                feat["f_Hz"],
                feat["f_Hz"] * R,
                feat["response"],
                duty,
                n_harmonics,
                kernel_kind,
                int(include_skin_rolloff),
            ])

        stride = max(1, len(freqs) // 800)
        for f, val in zip(freqs[::stride], yn[::stride]):
            all_response_rows.append([R, f, f * R, val])

    write_csv(
        paths.csv / "SST-Coil_radius_scaling_response.csv",
        ["R_m", "f0_Hz", "f0_times_R_Hz_m", "normalized_response"],
        all_response_rows,
    )
    write_csv(
        paths.csv / "SST-Coil_radius_scaling_features.csv",
        ["R_m", "feature_index", "feature_kind", "f0_Hz", "f0_times_R_Hz_m", "response", "duty", "n_harmonics", "kernel", "skin_rolloff"],
        all_feature_rows,
    )
    write_csv(
        paths.csv / "SST-Coil_radius_scaling_harmonic_samples.csv",
        ["R_m", "f0_Hz", "n", "duty", "PWM_amp", "x_knR", "G_candidate", "weighted_contribution"],
        ([row[k] for k in ["R_m", "f0_Hz", "n", "duty", "PWM_amp", "x_knR", "G_candidate", "weighted_contribution"]] for row in harmonic_rows),
    )

    # Plot response vs absolute frequency.
    plt.figure(figsize=(10, 5.8))
    for R in radii:
        plt.semilogx(freqs, response_by_radius[R], label=f"R={R:.3f} m")
    plt.axhline(0, lw=0.8)
    plt.xlabel("base frequency f0 [Hz]")
    plt.ylabel("normalized response [arb]")
    plt.title(f"Radius sweep vs absolute frequency — kernel={kernel_kind}, duty={duty}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(paths.figures / "SST-Coil_radius_scaling_vs_frequency.png", dpi=180)
    plt.close()

    # Collapse plot vs fR.
    plt.figure(figsize=(10, 5.8))
    for R in radii:
        plt.semilogx(freqs * R, response_by_radius[R], label=f"R={R:.3f} m")
    plt.axhline(0, lw=0.8)
    plt.xlabel("f0 R [Hz m]")
    plt.ylabel("normalized response [arb]")
    plt.title("Kernel-collapse test: geometry-kernel response should align in fR")
    plt.legend()
    plt.tight_layout()
    plt.savefig(paths.figures / "SST-Coil_radius_scaling_fR_collapse.png", dpi=180)
    plt.close()

    # Feature f versus 1/R plot.
    feature_arr = np.asarray([[row[0], row[3], row[4]] for row in all_feature_rows if row[2] in ("zero", "peak", "trough")], dtype=float)
    plt.figure(figsize=(8, 5.8))
    if feature_arr.size:
        invR = 1.0 / feature_arr[:, 0]
        plt.scatter(invR, feature_arr[:, 1] / 1e6, s=18, alpha=0.70)
    plt.xlabel("1/R [m$^{-1}$]")
    plt.ylabel("feature frequency [MHz]")
    plt.title("Feature frequencies: geometry-kernel model predicts f ∝ 1/R")
    plt.tight_layout()
    plt.savefig(paths.figures / "SST-Coil_radius_scaling_features_vs_invR.png", dpi=180)
    plt.close()

    save_json(paths.reports / "SST-Coil_radius_scaling_report.json", {
        "radii_m": radii,
        "duty": duty,
        "f_min_Hz": f_min,
        "f_max_Hz": f_max,
        "samples": samples,
        "n_harmonics": n_harmonics,
        "kernel_kind": kernel_kind,
        "include_skin_rolloff": include_skin_rolloff,
        "interpretation": "If experimental features collapse in f0*R and shift as 1/R, this supports a geometry-kernel diagnostic. Fixed absolute frequencies indicate ordinary electronics/parasitics unless otherwise explained.",
        "warning": "This is a candidate-kernel mathematical test, not evidence for anomalous force or gravity control. Replace G_candidate with measured response kernel when available.",
    })
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", nargs="+", type=float, default=[0.03, 0.05, 0.10])
    ap.add_argument("--duty", type=float, default=0.382)
    ap.add_argument("--f-min", type=float, default=1e5)
    ap.add_argument("--f-max", type=float, default=25e6)
    ap.add_argument("--samples", type=int, default=2500)
    ap.add_argument("--n-harmonics", type=int, default=15)
    ap.add_argument("--kernel", choices=["sinc", "damped_sinc", "cos_sinc", "j0_asymptotic"], default="sinc")
    ap.add_argument("--skin-rolloff", action="store_true")
    ap.add_argument("--export-base", default="exports/SST-Coil")
    args = ap.parse_args()
    out = run(
        radii=args.radii,
        duty=args.duty,
        f_min=args.f_min,
        f_max=args.f_max,
        samples=args.samples,
        n_harmonics=args.n_harmonics,
        kernel_kind=args.kernel,
        include_skin_rolloff=args.skin_rolloff,
        export_base=args.export_base,
    )
    print(out.root)
