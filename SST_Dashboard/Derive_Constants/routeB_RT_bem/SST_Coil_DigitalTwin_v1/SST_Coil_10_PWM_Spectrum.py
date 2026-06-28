from __future__ import annotations
import argparse
import numpy as np
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_run_paths, pwm_fourier_unipolar, write_csv, save_json


def run(duties=(0.382, 0.5), n_harmonics=40, amplitude=1.0, export_base="exports/SST-Coil", run_name=None):
    paths = make_run_paths(export_base, run_name)
    for duty in duties:
        c = pwm_fourier_unipolar(duty, n_harmonics, amplitude)
        rows = []
        for n in range(n_harmonics + 1):
            real_amp = abs(c[0]) if n == 0 else 2.0 * abs(c[n])
            rows.append([n, c[n].real, c[n].imag, abs(c[n]), real_amp, np.angle(c[n])])
        write_csv(paths.csv / f"SST-Coil_PWM_spectrum_d{duty:.4f}.csv",
                  ["n", "c_real", "c_imag", "abs_c", "real_sinusoid_amplitude", "phase_rad"], rows)

        ns = np.arange(1, n_harmonics + 1)
        amps = [2.0 * abs(c[n]) for n in ns]
        plt.figure(figsize=(9, 4.8))
        plt.stem(ns, amps)
        plt.xlabel("harmonic n")
        plt.ylabel("real sinusoid amplitude")
        plt.title(f"PWM harmonic spectrum, duty={duty:.4f}")
        plt.tight_layout()
        plt.savefig(paths.figures / f"SST-Coil_PWM_spectrum_d{duty:.4f}.png", dpi=180)
        plt.close()
    save_json(paths.reports / "SST-Coil_PWM_parameters.json", {
        "duties": list(duties), "n_harmonics": n_harmonics, "amplitude": amplitude
    })
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--duties", type=float, nargs="+", default=[0.382, 0.5])
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--amplitude", type=float, default=1.0)
    ap.add_argument("--export-base", default="exports/SST-Coil")
    args = ap.parse_args()
    p = run(tuple(args.duties), args.n, args.amplitude, args.export_base)
    print(p.root)
