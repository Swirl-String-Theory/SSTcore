from __future__ import annotations
from pathlib import Path
import shutil

from SST_Coil_00_common import ensure_run_dirs, save_json, CoilConfig, CircuitConfig
from SST_Coil_20_Geometry_SawShape import plot_geometry
from SST_Coil_30_CircuitModel import summarize_circuit
from SST_Coil_80_ExtractEffectiveKernel import run_effective_kernel_sweep


def main():
    # One shared timestamped folder for the whole run.
    dirs = ensure_run_dirs("exports/SST-Coil")
    root = dirs["base"]
    cfg = CoilConfig(radius_m=0.05, path_mode="chord")
    circ = CircuitConfig(duty=0.382)
    plot_geometry(cfg, dirs["figures"] / "SST-Coil_geometry_3phase.png")
    summarize_circuit(1e6, cfg, circ, 25).to_csv(dirs["csv"] / "SST-Coil_circuit_harmonics.csv", index=False)
    # Run effective kernel sweep into same root by passing parent and renaming result if needed.
    # Simpler: run directly into root by monkey using export_root=root.parent and accept nested second run? Avoid nested by calling custom temp then move.
    sweep_dirs = run_effective_kernel_sweep([0.03,0.05,0.10], 1e5, 8e6, 70, 0.382, 9, "weighted_gradB2", 13, root.parent)
    # move sweep products into main run folder if separate timestamp was made
    if sweep_dirs["base"] != root:
        for sub in ["figures","csv","npz","reports","logs"]:
            for p in sweep_dirs[sub].glob("*"):
                dest = dirs[sub] / p.name
                if dest.exists(): dest.unlink()
                shutil.move(str(p), str(dest))
        try:
            shutil.rmtree(sweep_dirs["base"])
        except Exception:
            pass
    save_json(dirs["reports"] / "run_parameters.json", {"coil": cfg, "circuit": circ})
    print(root)

if __name__ == "__main__":
    main()
