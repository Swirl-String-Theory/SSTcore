#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SST Coil Digital Twin v10 complete RunAll.

One timestamped run, broad artifact output. This intentionally restores the
larger output surface from earlier versions while keeping the corrected v9
geometry sectors.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from SST_Coil_00_common import (
    make_run_dirs, save_json, write_csv_dicts, summarize_lanes,
    path_length, scale_lanes, skin_depth_cu, V_SWIRL, MU0
)
from SST_Coil_01_plotting import plot_lanes_3d
from SST_Coil_10_geometry_sawbowl import build_sawbowl_3phase
from SST_Coil_11_geometry_rodin6lane import build_rodin_6lane
from SST_Coil_20_winding_factors import winding_rows, phase_table_rows
from SST_Coil_30_pwm_current import current_spectrum, harmonic_current
from SST_Coil_40_biot_savart import grid_from_bounds, field_for_lanes
from SST_Coil_50_observables import field_observables, phase_currents, bmag


def lane_summary_rows(geometries: dict[str, list[dict]]) -> list[dict]:
    rows = []
    for geom, lanes in geometries.items():
        for lane in lanes:
            pts = lane["points"]
            rows.append({
                "geometry": geom,
                "lane": lane.get("name", ""),
                "phase": lane.get("phase", ""),
                "mirror": lane.get("mirror", False),
                "n_points": len(pts),
                "length_m": path_length(pts),
                "x_min_m": float(np.min(pts[:,0])),
                "x_max_m": float(np.max(pts[:,0])),
                "y_min_m": float(np.min(pts[:,1])),
                "y_max_m": float(np.max(pts[:,1])),
                "z_min_m": float(np.min(pts[:,2])),
                "z_max_m": float(np.max(pts[:,2])),
            })
    return rows




def decimate_lanes(lanes: list[dict], max_points: int) -> list[dict]:
    """Return a lighter copy of lane polylines for expensive Biot-Savart sweeps."""
    out = []
    for lane in lanes:
        pts = np.asarray(lane["points"], dtype=float)
        if len(pts) > max_points:
            idx = np.linspace(0, len(pts)-1, int(max_points), dtype=int)
            pts = pts[idx]
        d = dict(lane)
        d["points"] = pts
        out.append(d)
    return out


def save_midplane_maps(run: Path, geometry_name: str, Bx, By, Bz, X, Y, Z) -> dict:
    figdir = run / "figures"
    npzdir = run / "npz"
    obs = field_observables(Bx, By, Bz, X, Y, Z)
    B = bmag(Bx, By, Bz)
    B2 = B * B
    k = Z.shape[2] // 2

    np.savez_compressed(
        npzdir / f"SST-Coil_v10_{geometry_name}_field_grid.npz",
        X=X, Y=Y, Z=Z, Bx=Bx, By=By, Bz=Bz, Bmag=B, B2=B2
    )

    def imshow_field(arr, title, fname, cbar):
        fig, ax = plt.subplots(figsize=(7.5, 6.5))
        im = ax.imshow(
            np.real(arr[:, :, k]).T, origin="lower",
            extent=[float(X.min()), float(X.max()), float(Y.min()), float(Y.max())],
            aspect="equal"
        )
        ax.set_title(title)
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        fig.colorbar(im, ax=ax, label=cbar)
        fig.tight_layout()
        fig.savefig(figdir / fname, dpi=170)
        plt.close(fig)

    imshow_field(B, f"{geometry_name}: |B| midplane", f"SST-Coil_v10_{geometry_name}_Bmag_midplane.png", "T")
    imshow_field(Bz, f"{geometry_name}: Bz midplane", f"SST-Coil_v10_{geometry_name}_Bz_midplane.png", "T")
    imshow_field(B2/(2*MU0), f"{geometry_name}: magnetic pressure proxy midplane", f"SST-Coil_v10_{geometry_name}_mag_pressure_midplane.png", "Pa")

    # Gradient magnitude midplane
    dx=float(X[1,0,0]-X[0,0,0]); dy=float(Y[0,1,0]-Y[0,0,0]); dz=float(Z[0,0,1]-Z[0,0,0])
    g=np.gradient(np.real(B2), dx, dy, dz, edge_order=1)
    grad=np.sqrt(g[0]*g[0]+g[1]*g[1]+g[2]*g[2])
    imshow_field(grad, f"{geometry_name}: |grad B²| midplane", f"SST-Coil_v10_{geometry_name}_gradB2_midplane.png", "T²/m")
    obs["gradB2_midplane_mean_T2_per_m"] = float(np.nanmean(grad[:,:,k]))
    obs["gradB2_midplane_max_T2_per_m"] = float(np.nanmax(grad[:,:,k]))
    return obs


def static_field_diagnostics(run: Path, geometries: dict[str, list[dict]], grid: int, current_a: float) -> list[dict]:
    rows = []
    for name, lanes0 in geometries.items():
        lanes = decimate_lanes(lanes0, max_points=450 if grid <= 7 else 700)
        allpts = np.vstack([l["points"] for l in lanes])
        Rxy = float(np.max(np.sqrt(allpts[:,0]**2 + allpts[:,1]**2)))
        bounds = max(2.2 * Rxy, 0.08)
        X, Y, Z = grid_from_bounds(bounds=bounds, res=grid)

        if len(lanes) == 6:
            currents = phase_currents(current_a + 0j, phases=3, mirror_sign=-1.0)[:len(lanes)]
        else:
            currents = [current_a + 0j] * len(lanes)

        Bx, By, Bz = field_for_lanes(lanes, currents, X, Y, Z, r_softening=max(bounds/grid * 0.15, 1e-4))
        obs = save_midplane_maps(run, name, Bx, By, Bz, X, Y, Z)
        rows.append({"geometry": name, "current_A": current_a, "grid": grid, "bounds_m": bounds, **obs})
    return rows


def radius_scaling_sweep(
    run: Path,
    geometry_name: str,
    base_lanes: list[dict],
    radii=(0.03,0.05,0.10),
    f_min=1e5,
    f_max=5e6,
    samples=28,
    harmonics=3,
    grid=7,
    duty=0.382,
    wire_diameter=0.0012,
) -> list[dict]:
    rows = []
    base_lanes = decimate_lanes(base_lanes, max_points=180 if grid <= 5 else 260)
    allpts = np.vstack([l["points"] for l in base_lanes])
    base_R = float(np.max(np.sqrt(allpts[:,0]**2 + allpts[:,1]**2)))
    freqs = np.geomspace(float(f_min), float(f_max), int(samples))

    for R in radii:
        lanes = scale_lanes(base_lanes, float(R)/base_R)
        length = max(path_length(l["points"]) for l in lanes)
        X, Y, Z = grid_from_bounds(bounds=max(2.2*R, 0.08), res=grid)
        for f0 in freqs:
            Bx = 0j * np.zeros_like(X)
            By = 0j * np.zeros_like(X)
            Bz = 0j * np.zeros_like(X)
            for n in range(1, int(harmonics)+1):
                I = harmonic_current(f0, n, duty, length, wire_diameter_m=wire_diameter)
                currents = phase_currents(I, phases=3, mirror_sign=-1.0 if len(lanes)==6 else 1.0)[:len(lanes)]
                bx, by, bz = field_for_lanes(lanes, currents, X, Y, Z, r_softening=max(R/grid * 0.15, 1e-4))
                Bx += bx; By += by; Bz += bz
            obs = field_observables(Bx, By, Bz, X, Y, Z)
            rows.append({
                "geometry": geometry_name,
                "R_m": float(R),
                "f0_hz": float(f0),
                "f0R_Hz_m": float(f0*R),
                "duty": duty,
                "harmonics": harmonics,
                **obs
            })

    write_csv_dicts(run / "csv" / f"SST-Coil_v10_{geometry_name}_radius_scaling.csv", rows)

    # Absolute-frequency and fR-collapse plots
    for xkey, xlabel, suffix, title_extra in [
        ("f0_hz", "base frequency f0 [Hz]", "freq", "vs absolute frequency"),
        ("f0R_Hz_m", "f0 R [Hz m]", "fR", "fR collapse check"),
    ]:
        fig, ax = plt.subplots(figsize=(9,5.5))
        for R in sorted({r["R_m"] for r in rows}):
            rr = [r for r in rows if r["R_m"] == R]
            y = np.array([r.get("gradB2_mean_T2_per_m", 0.0) for r in rr], dtype=float)
            y = y / max(float(np.nanmax(y)), 1e-30)
            ax.plot([r[xkey] for r in rr], y, label=f"R={R:.3f} m")
        ax.set_xscale("log")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("normalized mean |grad B²|")
        ax.set_title(f"{geometry_name}: {title_extra}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(run / "figures" / f"SST-Coil_v10_{geometry_name}_radius_scaling_{suffix}.png", dpi=170)
        plt.close(fig)

    return rows


def response_compare_plot(run: Path, all_rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(9,5.5))
    for geom in sorted({r["geometry"] for r in all_rows}):
        rr = [r for r in all_rows if r["geometry"] == geom and abs(r["R_m"] - 0.05) < 1e-12]
        if not rr:
            continue
        y = np.array([r.get("gradB2_mean_T2_per_m", 0.0) for r in rr], dtype=float)
        y = y / max(float(np.nanmax(y)), 1e-30)
        ax.plot([r["f0_hz"] for r in rr], y, label=geom)
    ax.set_xscale("log")
    ax.set_xlabel("f0 [Hz]")
    ax.set_ylabel("normalized mean |grad B²|")
    ax.set_title("Geometry comparison at R=0.05 m")
    ax.legend()
    fig.tight_layout()
    fig.savefig(run / "figures" / "SST-Coil_v10_geometry_comparison_response.png", dpi=170)
    plt.close(fig)


def node_prediction_rows(radii=(0.03,0.05,0.10), n_values=range(1,10), x_nodes=(2.405,3.832,5.520,7.016)) -> list[dict]:
    rows = []
    for R in radii:
        for n in n_values:
            for j, x in enumerate(x_nodes, start=1):
                f0 = x * V_SWIRL / (2*np.pi*n*R)
                rows.append({
                    "R_m": float(R),
                    "harmonic_n": int(n),
                    "node_index": int(j),
                    "x_node": float(x),
                    "f0_hz": float(f0),
                    "f0_MHz": float(f0/1e6),
                    "f0R_Hz_m": float(f0*R),
                })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-base", default="exports/SST-Coil")
    ap.add_argument("--quick", action="store_true", help="fewer sweep samples and smaller grid")
    ap.add_argument("--grid", type=int, default=None)
    ap.add_argument("--samples", type=int, default=None)
    ap.add_argument("--harmonics", type=int, default=None)
    ap.add_argument("--duty", type=float, default=0.382)
    args = ap.parse_args()

    grid = args.grid if args.grid is not None else (5 if args.quick else 9)
    samples = args.samples if args.samples is not None else (6 if args.quick else 18)
    harmonics = args.harmonics if args.harmonics is not None else (1 if args.quick else 3)

    run = make_run_dirs(args.out_base)
    figdir = run / "figures"
    csvdir = run / "csv"
    repdir = run / "reports"

    # Build corrected geometry sectors.
    geoms = {
        "sawbowl_curved": build_sawbowl_3phase(Rb=0.025, Rt=0.030, height=0.006, n_pairs=20, mode="curved", profile="Exponential"),
        "sawbowl_chord": build_sawbowl_3phase(Rb=0.025, Rt=0.030, height=0.006, n_pairs=20, mode="chord", profile="Exponential"),
        "rodin6lane": build_rodin_6lane(units="m", n_path=(700 if args.quick else 1400)),
    }

    # Geometry plots.
    plot_lanes_3d(geoms["sawbowl_curved"], figdir/"SST-Coil_v10_geometry_sawbowl_curved.png", "SST-Coil v10 SawBowl curved: original continuous z/r logic")
    plot_lanes_3d(geoms["sawbowl_chord"], figdir/"SST-Coil_v10_geometry_sawbowl_chord.png", "SST-Coil v10 SawBowl chord: straight slot-to-slot version")
    plot_lanes_3d(geoms["rodin6lane"], figdir/"SST-Coil_v10_geometry_rodin6lane.png", "SST-Coil v10 Rodin (5,12): exact 6-lane z-mirror guide", units="mm")

    # Geometry tables and analytic winding checks.
    write_csv_dicts(csvdir/"SST-Coil_v10_lane_summary.csv", lane_summary_rows(geoms))
    write_csv_dicts(csvdir/"SST-Coil_v10_winding_factors.csv", winding_rows(harmonics=range(1,41)))
    write_csv_dicts(csvdir/"SST-Coil_v10_phase_table.csv", phase_table_rows())
    write_csv_dicts(csvdir/"SST-Coil_v10_kernel_node_predictions.csv", node_prediction_rows())

    # Current spectrum for each geometry length scale.
    current_rows = []
    for name, lanes in geoms.items():
        length = max(path_length(l["points"]) for l in lanes)
        for row in current_spectrum(1e6, 40, args.duty, length, 0.0012):
            row = dict(row)
            row["geometry"] = name
            row["lane_length_m"] = length
            current_rows.append(row)
    write_csv_dicts(csvdir/"SST-Coil_v10_current_spectrum_1MHz_by_geometry.csv", current_rows)
    fig, ax = plt.subplots(figsize=(9,5.5))
    for name in sorted({r["geometry"] for r in current_rows}):
        rr = [r for r in current_rows if r["geometry"] == name]
        ax.plot([r["n"] for r in rr], [r["I_abs_A"] for r in rr], marker="o", ms=2, label=name)
    ax.set_xlabel("harmonic n")
    ax.set_ylabel("|I_n| [A]")
    ax.set_title(f"PWM→copper/RL current spectrum, duty={args.duty}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figdir/"SST-Coil_v10_current_spectrum_by_geometry.png", dpi=170)
    plt.close(fig)

    # Static field diagnostics.
    field_rows = static_field_diagnostics(run, geoms, grid=grid, current_a=5.0)
    write_csv_dicts(csvdir/"SST-Coil_v10_static_field_diagnostics.csv", field_rows)

    # Radius scaling sweeps.
    sweep_geoms = {
        "sawbowl_curved": geoms["sawbowl_curved"],
        "sawbowl_chord": geoms["sawbowl_chord"],
        "rodin6lane": geoms["rodin6lane"],
    }
    all_sweep_rows = []
    for name, lanes in sweep_geoms.items():
        rows = radius_scaling_sweep(
            run, name, lanes,
            samples=samples,
            harmonics=harmonics,
            grid=max(5, min(grid, 9)),
            duty=args.duty,
        )
        all_sweep_rows.extend(rows)

    write_csv_dicts(csvdir/"SST-Coil_v10_all_radius_scaling_combined.csv", all_sweep_rows)
    response_compare_plot(run, all_sweep_rows)

    report = {
        "run": str(run),
        "quick": bool(args.quick),
        "grid": int(grid),
        "samples": int(samples),
        "harmonics": int(harmonics),
        "duty": float(args.duty),
        "geometries": {k: summarize_lanes(v) for k,v in geoms.items()},
        "artifacts_note": "v10 restores broad output: geometry, winding, current, static field, radius scaling, fR collapse, comparison.",
    }
    save_json(repdir/"SST-Coil_v10_RunAll_summary.json", report)

    print("Wrote complete v10 run:", run)


if __name__ == "__main__":
    main()
