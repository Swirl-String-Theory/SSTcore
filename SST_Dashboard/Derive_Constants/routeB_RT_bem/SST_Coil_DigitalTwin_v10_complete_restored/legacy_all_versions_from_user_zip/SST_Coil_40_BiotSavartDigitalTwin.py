from __future__ import annotations
import argparse
import math
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from SST_Coil_00_common import CoilConfig, CircuitConfig, ensure_run_dirs, MU0_4PI, save_json
from SST_Coil_20_Geometry_SawShape import build_all_phases
from SST_Coil_30_CircuitModel import harmonic_phase_currents


def biot_savart_points(targets: np.ndarray, polyline: np.ndarray, current: complex, softening: float = 1e-5) -> np.ndarray:
    """Complex B for complex current, midpoint segment approximation."""
    B = np.zeros((targets.shape[0], 3), dtype=complex)
    p0 = polyline[:-1]; p1 = polyline[1:]
    dl = p1 - p0
    mid = 0.5*(p0+p1)
    for dL, m in zip(dl, mid):
        r = targets - m[None, :]
        r2 = np.sum(r*r, axis=1) + softening*softening
        r3 = r2*np.sqrt(r2)
        cross = np.cross(np.broadcast_to(dL, r.shape), r)
        B += (MU0_4PI * current) * cross / r3[:, None]
    return B


def make_probe_grid(radius_m: float, grid: int = 25, z_probe: float = 0.015) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lim = radius_m * 1.35
    x = np.linspace(-lim, lim, grid)
    y = np.linspace(-lim, lim, grid)
    X, Y = np.meshgrid(x, y, indexing="ij")
    Z = np.zeros_like(X) + z_probe
    targets = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    return X, Y, targets


def field_harmonic_observable(f0_hz: float, cfg: CoilConfig, circ: CircuitConfig, harmonics: int = 21, grid: int = 21, z_probe: float = 0.015, softening: float = 2e-4) -> Dict[str, float]:
    coils = build_all_phases(cfg)
    currents = harmonic_phase_currents(f0_hz, cfg, circ, harmonics)
    X, Y, targets = make_probe_grid(cfg.radius_m, grid, z_probe)
    dx = float(abs(X[1,0]-X[0,0])) if grid > 1 else cfg.radius_m
    total_axis_B2 = 0.0
    total_gradB2 = 0.0
    total_asym_Bz = 0.0
    total_signed = 0.0
    per_rows = []
    for n, Iph in currents.items():
        Bn = np.zeros((targets.shape[0], 3), dtype=complex)
        for pi, li, pts in coils:
            Bn += biot_savart_points(targets, pts, Iph[pi], softening=softening)
        # time-average B^2 for harmonic complex amplitude: 0.5 |B|^2
        B2 = 0.5*np.sum(np.abs(Bn)**2, axis=1).reshape(X.shape)
        Bz = Bn[:,2].reshape(X.shape)
        center = grid//2
        axis_B2 = float(B2[center, center])
        gy, gx = np.gradient(B2, dx, dx)  # approximate
        gradB2 = float(np.nanmean(np.sqrt(gx*gx + gy*gy)))
        left = np.nanmean(np.real(Bz[:center, :])) if center > 0 else 0.0
        right = np.nanmean(np.real(Bz[center+1:, :])) if center+1 < grid else 0.0
        asym = float(right-left)
        # sign-sensitive proxy: phase-weighted real axial field at off-axis probes
        signed = float(np.nanmean(np.real(Bz) * np.sign(X + 1e-30)))
        total_axis_B2 += axis_B2
        total_gradB2 += gradB2
        total_asym_Bz += asym
        total_signed += signed
        per_rows.append((n, n*f0_hz, axis_B2, gradB2, asym, signed, float(np.max(B2))))
    return {
        "f0_hz": float(f0_hz),
        "R_m": float(cfg.radius_m),
        "axis_B2": total_axis_B2,
        "weighted_gradB2": total_gradB2,
        "asymmetry_Bz": total_asym_Bz,
        "signed_Bz_proxy": total_signed,
        "per_harmonic": per_rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f0", type=float, default=1e6)
    ap.add_argument("--radius", type=float, default=0.05)
    ap.add_argument("--height", type=float, default=0.0)
    ap.add_argument("--duty", type=float, default=0.382)
    ap.add_argument("--harmonics", type=int, default=15)
    ap.add_argument("--grid", type=int, default=21)
    ap.add_argument("--export-root", default="exports/SST-Coil")
    args = ap.parse_args()
    dirs = ensure_run_dirs(args.export_root)
    cfg = CoilConfig(radius_m=args.radius, height_m=args.height)
    circ = CircuitConfig(duty=args.duty)
    out = field_harmonic_observable(args.f0, cfg, circ, args.harmonics, args.grid)
    rows = [{"n": r[0], "f_hz": r[1], "axis_B2": r[2], "gradB2": r[3], "asym_Bz": r[4], "signed_Bz_proxy": r[5], "max_B2": r[6]} for r in out.pop("per_harmonic")]
    pd.DataFrame(rows).to_csv(dirs["csv"] / "SST-Coil_digital_twin_per_harmonic.csv", index=False)
    save_json(dirs["reports"] / "digital_twin_observable_summary.json", {"summary": out, "coil": cfg, "circuit": circ})
    print(dirs["base"])

if __name__ == "__main__":
    main()
