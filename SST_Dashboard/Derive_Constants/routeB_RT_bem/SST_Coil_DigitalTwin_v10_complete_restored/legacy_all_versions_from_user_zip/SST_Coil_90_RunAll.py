from __future__ import annotations
from pathlib import Path
import shutil

from SST_Coil_00_common import make_run_paths, save_json
from SST_Coil_10_PWM_Spectrum import run as run_pwm
from SST_Coil_20_Geometry_SawShape import run as run_geometry
from SST_Coil_30_BiotSavart import compute_field
from SST_Coil_40_FieldAnalysis import analyze as run_field_analysis
from SST_Coil_50_MaxwellStress import run as run_maxwell
from SST_Coil_60_FRScaling import run as run_fr
from SST_Coil_70_HarmonicScanner import run as run_harmonic
from SST_Coil_75_RadiusScalingSweep import run as run_radius_scaling
from SST_Coil_80_ParamSweep import run as run_sweep


def main():
    # One shared output root for the entire pipeline.
    root_paths = make_run_paths("exports/SST-Coil")
    export_base = root_paths.root.parent
    run_name = root_paths.root.name

    print(f"Export root: {root_paths.root}")
    run_pwm(export_base=export_base, run_name=run_name)
    run_geometry(export_base=export_base, run_name=run_name)
    biot_paths, biot_report = compute_field(export_base=export_base, run_name=run_name)
    npz = root_paths.npz / "SST-Coil_BiotSavart_midplane.npz"
    run_field_analysis(npz, export_base=export_base, run_name=run_name)
    run_maxwell(npz, export_base=export_base, run_name=run_name)
    run_fr(export_base=export_base, run_name=run_name)
    run_harmonic(export_base=export_base, run_name=run_name)
    run_radius_scaling(export_base=export_base, run_name=run_name)
    run_sweep(export_base=export_base, run_name=run_name)

    save_json(root_paths.reports / "SST-Coil_RunAll_summary.json", {
        "export_root": str(root_paths.root),
        "biot_report": biot_report,
        "status": "complete"
    })
    print("Done.")
    print(root_paths.root)


if __name__ == "__main__":
    main()
