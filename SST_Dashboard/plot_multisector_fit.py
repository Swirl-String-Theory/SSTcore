import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from trefoil_multisector_fitterv2 import (
    MultisectorConfig,
    load_phi_csv,
    phi_pc_abs_at_t_fast,
)

# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------
phi_csv = "exports/phi-3_1/phi3_1_transform.csv"
result_json = "multisector_fit_result.json"

df = load_phi_csv(phi_csv)

with open(result_json, "r", encoding="utf-8") as f:
    result = json.load(f)

params = result["fitted_params"]
targets = result["target_near_nodes"]
predicted = result["predicted_minima"]
cfg_dict = result["config"]

config = MultisectorConfig(
    sectors=cfg_dict["sectors"],
    a_nc_over_rc=cfg_dict["a_nc_over_rc"],
    truncation_M=cfg_dict["truncation_M"],
    completion_mode=cfg_dict["completion_mode"],
    t_min=cfg_dict["t_min"],
    t_max=cfg_dict["t_max"],
    match_count=cfg_dict["match_count"],
    fit_sector_weights=cfg_dict["fit_sector_weights"],
)

# ---------------------------------------------------------------------
# Prepare grid
# ---------------------------------------------------------------------
w = df.copy()
if config.t_min is not None:
    w = w[w["t"] >= config.t_min]
if config.t_max is not None:
    w = w[w["t"] <= config.t_max]

t_grid = w["t"].to_numpy(dtype=float)
phi_data = w["phi_abs"].to_numpy(dtype=float)

phi_model = phi_pc_abs_at_t_fast(t_grid, config, params)

# ---------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.plot(t_grid, phi_data, label="Numerical |Φ₃₁(t)|", lw=2)
plt.plot(t_grid, phi_model, "--", label="Multisector Model", lw=2)

# Target nodes
for tn in targets:
    plt.axvline(tn, color="green", linestyle=":", alpha=0.6)

# Predicted minima
for pm in predicted:
    plt.axvline(pm, color="red", linestyle="--", alpha=0.5)

plt.title("Trefoil Multisector Primitive-Cycle Fit")
plt.xlabel("t")
plt.ylabel("|Φ₃₁(t)|")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()