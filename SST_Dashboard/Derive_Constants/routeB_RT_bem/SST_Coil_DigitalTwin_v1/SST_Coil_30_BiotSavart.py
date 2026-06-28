from __future__ import annotations
import argparse
from dataclasses import asdict
import numpy as np
import matplotlib.pyplot as plt
from SST_Coil_00_common import (
    SawShapeParams, build_three_phase_sawshape, make_run_paths, biot_savart_points,
    make_grid, magnetic_pressure_proxy, write_csv, save_json, three_phase_currents_from_pwm,
    kernel_x, estimate_ac_resistance_round_wire, polyline_length
)


def compute_field(radius=0.05, current_peak=5.0, duty=0.382, f0=1e6, harmonic=1,
                  grid_res=51, bounds=0.10, softening=1e-4, height=0.0, n_pairs=20,
                  samples=10, wire_radius=0.0005, export_base="exports/SST-Coil", run_name=None):
    paths = make_run_paths(export_base, run_name)
    params = SawShapeParams(radius_bottom=radius, radius_top=radius, height=height,
                            n_pairs=n_pairs, samples_per_segment=samples)
    coils = build_three_phase_sawshape(params)
    points, (X, Y, Z) = make_grid(bounds=bounds, res=grid_res, z=0.0)
    Ih = three_phase_currents_from_pwm(duty, harmonic, current_peak)[:, harmonic]
    B = np.zeros((points.shape[0], 3), dtype=np.complex128)
    for phase_i, pts in enumerate(coils):
        B += biot_savart_points(points, pts, current=Ih[phase_i], softening=softening)
    Bmag = np.sqrt(np.real(np.sum(B * np.conjugate(B), axis=1)))
    pressure = magnetic_pressure_proxy(B)
    Bz_abs = np.abs(B[:, 2])

    np.savez_compressed(paths.npz / "SST-Coil_BiotSavart_midplane.npz",
                        points=points, B=B, Bmag=Bmag, pressure=pressure, X=X, Y=Y, Z=Z,
                        params=asdict(params), currents=Ih)

    write_csv(paths.csv / "SST-Coil_BiotSavart_midplane_sample.csv",
              ["x_m", "y_m", "z_m", "Bx_real_T", "By_real_T", "Bz_real_T", "Bmag_T", "Pmag_proxy_Pa"],
              [[*points[i], B[i,0].real, B[i,1].real, B[i,2].real, Bmag[i], pressure[i]] for i in range(points.shape[0])])

    extent = [-bounds, bounds, -bounds, bounds]
    plt.figure(figsize=(7, 6))
    plt.imshow(Bmag.reshape(X.shape).T, origin="lower", extent=extent, aspect="equal")
    plt.colorbar(label="|B_n| [T], harmonic phasor magnitude")
    plt.xlabel("x [m]"); plt.ylabel("y [m]")
    plt.title(f"B midplane | n={harmonic}, f0={f0:g} Hz, d={duty}")
    plt.tight_layout()
    plt.savefig(paths.figures / "SST-Coil_Bmag_midplane.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 6))
    plt.imshow(Bz_abs.reshape(X.shape).T, origin="lower", extent=extent, aspect="equal")
    plt.colorbar(label="|Bz_n| [T]")
    plt.xlabel("x [m]"); plt.ylabel("y [m]")
    plt.title("Axial field harmonic magnitude")
    plt.tight_layout()
    plt.savefig(paths.figures / "SST-Coil_Bz_midplane.png", dpi=180)
    plt.close()

    length_total = sum(polyline_length(c) for c in coils)
    ac = estimate_ac_resistance_round_wire(length_total, wire_radius, f0 * harmonic)
    report = {
        "radius_m": radius,
        "current_peak_A": current_peak,
        "duty": duty,
        "f0_Hz": f0,
        "harmonic": harmonic,
        "kernel_x": kernel_x(harmonic, f0, radius),
        "grid_res": grid_res,
        "bounds_m": bounds,
        "Bmag_max_T": float(np.max(Bmag)),
        "Bmag_mean_T": float(np.mean(Bmag)),
        "pressure_min_proxy_Pa": float(np.min(pressure)),
        "wire_length_total_m": length_total,
        "ac_copper_estimate": ac,
        "params": asdict(params)
    }
    save_json(paths.reports / "SST-Coil_BiotSavart_report.json", report)
    return paths, report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--radius", type=float, default=0.05)
    ap.add_argument("--current", type=float, default=5.0)
    ap.add_argument("--duty", type=float, default=0.382)
    ap.add_argument("--f0", type=float, default=1e6)
    ap.add_argument("--harmonic", type=int, default=1)
    ap.add_argument("--grid-res", type=int, default=51)
    ap.add_argument("--bounds", type=float, default=0.10)
    ap.add_argument("--softening", type=float, default=1e-4)
    ap.add_argument("--export-base", default="exports/SST-Coil")
    args = ap.parse_args()
    p, report = compute_field(args.radius, args.current, args.duty, args.f0, args.harmonic,
                              args.grid_res, args.bounds, args.softening, export_base=args.export_base)
    print(p.root)
    print(report)
