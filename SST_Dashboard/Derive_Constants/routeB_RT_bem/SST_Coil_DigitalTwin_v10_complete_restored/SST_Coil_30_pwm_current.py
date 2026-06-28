#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PWM and first-order copper/RL current model.

This is still a lumped first-pass model, not a full distributed transmission-line solver.
It is kept explicit so future measurements can replace R,L,C estimates.
"""
from __future__ import annotations
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_run_dirs, write_csv_dicts, save_json, skin_depth_cu, CU_RHO_20C


def pwm_harmonic_complex(n: int, duty: float, v_bus: float = 24.0, bipolar: bool = True) -> complex:
    """Complex nth Fourier coefficient for rectangular PWM centered at phase zero.
    Magnitude is adequate for harmonic weighting; phase is retained for later use.
    """
    n=int(n)
    if n == 0:
        return v_bus*(2*duty-1 if bipolar else duty)
    amp = v_bus * (2.0 if bipolar else 1.0) * np.sin(np.pi*n*duty)/(np.pi*n)
    phase = -np.pi*n*duty
    return amp*np.exp(1j*phase)


def estimate_wire_ac_resistance(length_m: float, wire_diameter_m: float, f_hz: float, rho: float = CU_RHO_20C) -> float:
    radius = 0.5*wire_diameter_m
    area_dc = np.pi*radius*radius
    delta = float(skin_depth_cu(f_hz, rho))
    if delta >= radius:
        area_eff = area_dc
    else:
        area_eff = 2*np.pi*radius*delta
    return rho*length_m/max(area_eff, 1e-18)


def estimate_loop_inductance(length_m: float, wire_radius_m: float) -> float:
    # Conservative crude wire-loop self-inductance scale; replace with PEEC later.
    return 2e-7*length_m*(np.log(max(2*length_m/wire_radius_m, 1.1))-1.0)


def harmonic_current(f0_hz: float, n: int, duty: float, length_m: float, wire_diameter_m: float,
                     v_bus: float = 24.0, series_R_extra: float = 0.05, L_h: float | None = None,
                     C_parallel_f: float = 0.0) -> complex:
    f = float(f0_hz)*int(n)
    Vn = pwm_harmonic_complex(n, duty, v_bus=v_bus, bipolar=True)
    R = estimate_wire_ac_resistance(length_m, wire_diameter_m, f) + series_R_extra
    if L_h is None:
        L_h = estimate_loop_inductance(length_m, 0.5*wire_diameter_m)
    omega = 2*np.pi*f
    Z = R + 1j*omega*L_h
    if C_parallel_f and C_parallel_f > 0:
        Y = 1/Z + 1j*omega*C_parallel_f
        Z = 1/Y
    return Vn/Z


def current_spectrum(f0_hz: float, max_harmonic: int, duty: float, length_m: float, wire_diameter_m: float,
                     **kwargs) -> list[dict]:
    rows=[]
    for n in range(1, max_harmonic+1):
        I = harmonic_current(f0_hz, n, duty, length_m, wire_diameter_m, **kwargs)
        rows.append(dict(n=n, f_hz=float(f0_hz*n), I_abs_A=float(abs(I)), I_phase_rad=float(np.angle(I)),
                         skin_depth_m=float(skin_depth_cu(f0_hz*n))))
    return rows


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out-base',default='exports/SST-Coil')
    ap.add_argument('--f0',type=float,default=1e6); ap.add_argument('--duty',type=float,default=0.382)
    ap.add_argument('--length',type=float,default=2.5); ap.add_argument('--wire-diameter',type=float,default=0.0012)
    ap.add_argument('--harmonics',type=int,default=25)
    args=ap.parse_args(); run=make_run_dirs(args.out_base)
    rows=current_spectrum(args.f0,args.harmonics,args.duty,args.length,args.wire_diameter)
    write_csv_dicts(run/'csv'/'SST-Coil_current_spectrum.csv', rows)
    fig,ax=plt.subplots(figsize=(8,5)); ax.stem([r['n'] for r in rows],[r['I_abs_A'] for r in rows])
    ax.set_xlabel('harmonic n'); ax.set_ylabel('|I_n| [A]'); ax.set_title('PWM→copper/RL current spectrum')
    fig.tight_layout(); fig.savefig(run/'figures'/'SST-Coil_current_spectrum.png',dpi=170); plt.close(fig)
    save_json(run/'reports'/'SST-Coil_current_summary.json', {'f0_hz':args.f0,'duty':args.duty,'length_m':args.length})
    print('Wrote run:',run)
if __name__=='__main__': main()
