from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from SST_Coil_00_common import make_export_paths, save_csv, write_json, normalize_response
from SST_Coil_10_geometry_sawbowl import build_sawbowl_3phase, plot_geometry as plot_sawbowl
from SST_Coil_11_geometry_rodin_torus import build_rodin_torus_coils, plot_geometry as plot_rodin
from SST_Coil_20_winding_factors import winding_rows, phase_table
from SST_Coil_30_biot_savart import field_from_coils, field_observables
from SST_Coil_50_observables import reduce_observable
from SST_Coil_40_current_model import three_phase_current_harmonics
from SST_Coil_80_compare_geometries import evaluate_geometry

if __name__ == "__main__":
    ex = make_export_paths()

    # Geometry sector A: SawBowl. Save both original curved mode and literal straight/chord mode.
    saw_curved = build_sawbowl_3phase(pairs=20, Rb=0.05, Rt=0.05, height=0.006, samples_per_seg=24, mode="curved")
    saw_straight = build_sawbowl_3phase(pairs=20, Rb=0.05, Rt=0.05, height=0.006, samples_per_seg=24, mode="straight")
    plot_sawbowl(saw_curved, ex.figures/"SST-Coil_v7_geometry_sawbowl_curved_original_logic.png")
    plot_sawbowl(saw_straight, ex.figures/"SST-Coil_v7_geometry_sawbowl_straight_chords.png")

    # Geometry sector B: Rodin / torus-knot.
    rod = build_rodin_torus_coils(R_major=0.049, r_minor=0.012, p=5, q=12, phases=3, turns=1, points=700, separate_families=False, gap=0.0, ccw_mode="overlay_reversed")
    plot_rodin(rod, ex.figures/"SST-Coil_v7_geometry_rodin_torus.png")

    # Winding diagnostics.
    save_csv(ex.csv/"SST-Coil_v7_winding_factors.csv", winding_rows(nus=range(1,41)))
    save_csv(ex.csv/"SST-Coil_v7_slot_phase_table.csv", phase_table())

    # Comparison. Use straight SawBowl for saw/star preservation, and Rodin torus as separate sector.
    f0s = np.geomspace(1e5, 5e6, 20)
    rows=[]
    rows += evaluate_geometry(saw_straight, f0s, "SawBowl_straight_S40_11_-9", 0.09, 9, 0.382, 5, "weighted_gradB2", 1e-4)
    rows += evaluate_geometry(saw_curved, f0s, "SawBowl_curved_original", 0.09, 9, 0.382, 5, "weighted_gradB2", 1e-4)
    rows += evaluate_geometry(rod, f0s, "Rodin_T5_12_CWCCW", 0.09, 9, 0.382, 5, "weighted_gradB2", 1e-4)
    save_csv(ex.csv/"SST-Coil_v7_compare_geometries.csv", rows)

    fig, ax = plt.subplots(figsize=(9,5.5))
    for geom in sorted(set(r["geometry"] for r in rows)):
        sub=[r for r in rows if r["geometry"]==geom]
        f=np.array([r["f0_hz"] for r in sub]); y=normalize_response(np.array([r["observable"] for r in sub]))
        ax.plot(f,y,label=geom)
    ax.set_xscale("log"); ax.set_xlabel("base frequency f0 [Hz]"); ax.set_ylabel("normalized weighted_gradB2")
    ax.set_title("v7: SawBowl curved/straight vs Rodin torus")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(ex.figures/"SST-Coil_v7_compare_geometries_response.png",dpi=170); plt.close(fig)

    write_json(ex.reports/"v7_runall_summary.json", {
        "status":"ok",
        "geometry_sectors":["SawBowl curved original interpolation", "SawBowl straight/chord", "Rodin torus T(5,12) CW/CCW co-located overlay"],
        "current_model":"first-order PWM Fourier + R/L; not full SPICE/FEM",
        "note":"Use straight/chord for star visibility; use curved for exact GUI-SawBowl interpolation logic."
    })
    print(ex.root)
