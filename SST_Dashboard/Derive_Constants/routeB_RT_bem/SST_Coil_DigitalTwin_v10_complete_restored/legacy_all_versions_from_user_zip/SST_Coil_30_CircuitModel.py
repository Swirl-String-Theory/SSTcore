from __future__ import annotations
import argparse
import math
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from SST_Coil_00_common import CircuitConfig, CoilConfig, ensure_run_dirs, pwm_harmonic_complex, ac_resistance_factor_round_wire, RHO_CU_20C, MU0, save_json
from SST_Coil_20_Geometry_SawShape import build_sawshape_phase, estimate_wire_length


def estimate_phase_resistance(cfg: CoilConfig, circ: CircuitConfig, f_hz: float) -> float:
    pts = build_sawshape_phase(cfg, 0, 0)
    Lwire = estimate_wire_length(pts) * max(1, cfg.layer_count)
    area = math.pi * (0.5*circ.wire_diameter_m)**2
    rdc = RHO_CU_20C * Lwire / max(area, 1e-30)
    fac = ac_resistance_factor_round_wire(f_hz, circ.wire_diameter_m) if circ.include_skin else 1.0
    return rdc * fac + circ.mosfet_rds_on_ohm + circ.phase_resistance_extra_ohm


def estimate_phase_inductance(cfg: CoilConfig, circ: CircuitConfig) -> float:
    # crude single-layer loop/star equivalent: L ~ mu0 R [ln(8R/a)-2] times effective turns^2 reduction.
    R = cfg.radius_m
    a = max(0.5*circ.wire_diameter_m, 1e-9)
    base = MU0 * R * max(math.log(8*R/a) - 2.0, 0.1)
    # SawShape path has many chords but not coherent turns; use layer_count^2 and mild path factor.
    path_factor = min(6.0, 1.0 + 0.025*cfg.turns_pairs)
    return circ.inductance_scale * base * path_factor * max(cfg.layer_count, 1)**2


def harmonic_phase_currents(f0_hz: float, cfg: CoilConfig, circ: CircuitConfig, harmonics: int = 25) -> Dict[int, np.ndarray]:
    """Return complex current coefficients [phase] for harmonic n.
    Includes PWM amplitude, RL low-pass, current limit, and 120 degree phase offsets.
    """
    L = estimate_phase_inductance(cfg, circ)
    currents = {}
    bipolar = circ.waveform == "bipolar_pwm"
    for n in range(1, harmonics+1):
        f = n * f0_hz
        omega = 2*math.pi*f
        R = estimate_phase_resistance(cfg, circ, f)
        Z = R + 1j*omega*L
        Vn = circ.v_bus * pwm_harmonic_complex(n, circ.duty, amplitude=1.0, bipolar=bipolar)
        In_base = Vn / Z
        # soft current limiter on harmonic magnitude
        mag = abs(In_base)
        if mag > circ.current_limit_A:
            In_base *= circ.current_limit_A / mag
        arr = np.zeros(cfg.phases, dtype=complex)
        for p in range(cfg.phases):
            arr[p] = In_base * np.exp(-1j*n*2*math.pi*p/cfg.phases)
        currents[n] = arr
    return currents


def summarize_circuit(f0_hz: float, cfg: CoilConfig, circ: CircuitConfig, harmonics: int = 25) -> pd.DataFrame:
    L = estimate_phase_inductance(cfg, circ)
    rows = []
    currents = harmonic_phase_currents(f0_hz, cfg, circ, harmonics)
    for n, arr in currents.items():
        f = n*f0_hz
        R = estimate_phase_resistance(cfg, circ, f)
        rows.append({
            "n": n, "f_hz": f, "R_ohm": R, "L_H": L, "XL_ohm": 2*math.pi*f*L,
            "I_phase1_mag_A": abs(arr[0]), "I_phase1_phase_rad": np.angle(arr[0]),
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f0", type=float, default=1e6)
    ap.add_argument("--radius", type=float, default=0.05)
    ap.add_argument("--duty", type=float, default=0.382)
    ap.add_argument("--harmonics", type=int, default=25)
    ap.add_argument("--export-root", default="exports/SST-Coil")
    args = ap.parse_args()
    dirs = ensure_run_dirs(args.export_root)
    cfg = CoilConfig(radius_m=args.radius)
    circ = CircuitConfig(duty=args.duty)
    df = summarize_circuit(args.f0, cfg, circ, args.harmonics)
    df.to_csv(dirs["csv"] / "SST-Coil_circuit_harmonics.csv", index=False)
    fig, ax = plt.subplots(figsize=(9,5))
    ax.loglog(df["f_hz"], df["I_phase1_mag_A"], marker="o")
    ax.set_xlabel("harmonic frequency [Hz]"); ax.set_ylabel("|I_n| [A]")
    ax.set_title("Digital-twin circuit harmonic current")
    fig.tight_layout(); fig.savefig(dirs["figures"] / "SST-Coil_circuit_harmonic_current.png", dpi=180)
    save_json(dirs["reports"] / "circuit_parameters.json", {"coil": cfg, "circuit": circ})
    print(dirs["base"])

if __name__ == "__main__":
    main()
