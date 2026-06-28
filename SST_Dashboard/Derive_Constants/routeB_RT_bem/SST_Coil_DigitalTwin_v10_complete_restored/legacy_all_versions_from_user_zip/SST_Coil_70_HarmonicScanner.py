from __future__ import annotations
import argparse
import numpy as np
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_run_paths, pwm_real_harmonic_amplitude, kernel_x, write_csv, save_json


def kernel_candidate(x: np.ndarray) -> np.ndarray:
    """Simple oscillatory candidate kernel. Use only as a diagnostic placeholder.

    sinc-like kernel: sin(x)/x. Replace with measured or simulated G_m when known.
    """
    return np.sinc(np.asarray(x) / np.pi)


def run(radius=0.05, duty=0.382, f_min=1e4, f_max=5e6, samples=500, n_harmonics=15,
        export_base="exports/SST-Coil", run_name=None):
    paths = make_run_paths(export_base, run_name)
    freqs = np.geomspace(f_min, f_max, samples)
    total = np.zeros_like(freqs, dtype=float)
    rows = []
    for n in range(1, n_harmonics + 1):
        amp = pwm_real_harmonic_amplitude(duty, n, 1.0)
        xs = np.array([kernel_x(n, f, radius) for f in freqs])
        g = kernel_candidate(xs)
        contribution = amp * g
        total += contribution
        for f, x, gi, ci in zip(freqs, xs, g, contribution):
            rows.append([f, radius, duty, n, amp, x, gi, ci])
    write_csv(paths.csv / "SST-Coil_harmonic_scanner.csv",
              ["f0_Hz", "R_m", "duty", "n", "PWM_amp", "x_knR", "G_candidate", "weighted_contribution"], rows)
    plt.figure(figsize=(9, 5))
    plt.semilogx(freqs, total)
    plt.axhline(0, lw=0.8)
    plt.xlabel("base frequency f0 [Hz]")
    plt.ylabel("Σ PWM_n G(n f0 R) [arb]")
    plt.title("Harmonic scanner with placeholder sinc kernel")
    plt.tight_layout()
    plt.savefig(paths.figures / "SST-Coil_harmonic_scanner_total.png", dpi=180)
    plt.close()
    save_json(paths.reports / "SST-Coil_harmonic_scanner_report.json", {
        "radius_m": radius, "duty": duty, "f_min_Hz": f_min, "f_max_Hz": f_max,
        "samples": samples, "n_harmonics": n_harmonics,
        "warning": "G is placeholder sinc. Use measured/simulated kernel when available."
    })
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--radius", type=float, default=0.05)
    ap.add_argument("--duty", type=float, default=0.382)
    ap.add_argument("--f-min", type=float, default=1e4)
    ap.add_argument("--f-max", type=float, default=5e6)
    ap.add_argument("--samples", type=int, default=500)
    ap.add_argument("--n-harmonics", type=int, default=15)
    ap.add_argument("--export-base", default="exports/SST-Coil")
    args = ap.parse_args()
    print(run(args.radius, args.duty, args.f_min, args.f_max, args.samples, args.n_harmonics, args.export_base).root)
