from __future__ import annotations
import argparse
import itertools
from SST_Coil_00_common import make_run_paths, pwm_real_harmonic_amplitude, kernel_x, write_csv, save_json
from SST_Coil_70_HarmonicScanner import kernel_candidate


def run(radii=(0.03, 0.05, 0.10), duties=(0.382, 0.5), freqs=(1e5, 3e5, 1e6, 3e6), harmonics=(1,3,5,7),
        export_base="exports/SST-Coil", run_name=None):
    paths = make_run_paths(export_base, run_name)
    rows = []
    for R, d, f in itertools.product(radii, duties, freqs):
        score = 0.0
        for n in harmonics:
            amp = pwm_real_harmonic_amplitude(d, n, 1.0)
            x = kernel_x(n, f, R)
            g = float(kernel_candidate(x))
            c = amp * g
            score += c
            rows.append([R, d, f, n, amp, x, g, c, score])
    write_csv(paths.csv / "SST-Coil_param_sweep.csv",
              ["R_m", "duty", "f0_Hz", "n", "PWM_amp", "x", "G_candidate", "contribution", "running_score"], rows)
    save_json(paths.reports / "SST-Coil_param_sweep_report.json", {
        "radii_m": list(radii), "duties": list(duties), "freqs_Hz": list(freqs), "harmonics": list(harmonics),
        "warning": "Uses placeholder kernel; intended for ranking candidate tests, not proof."
    })
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-base", default="exports/SST-Coil")
    args = ap.parse_args()
    print(run(export_base=args.export_base).root)
