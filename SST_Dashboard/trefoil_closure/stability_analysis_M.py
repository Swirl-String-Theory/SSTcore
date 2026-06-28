import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from trefoil_multisector_fitterv2 import (
    load_phi_csv,
    MultisectorConfig,
    fit_multisector,
)

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
phi_csv = "exports/phi-3_1/phi3_1_transform.csv"
df = load_phi_csv(phi_csv)

M_values = [100, 150, 200, 250, 300, 400]
results = []

for M in M_values:
    print(f"\nRunning fit for M = {M}")

    cfg = MultisectorConfig(
        sectors=[2, 3, 5],
        truncation_M=M,
        completion_mode="none",
        t_min=20,
        t_max=35,
        target_near_nodes=[25.18, 26.75, 32.80],
        match_count=3,
        fit_sector_weights=False,
    )

    res = fit_multisector(df, cfg)

    results.append({
        "M": M,
        "objective": res.objective_value,
        "theta2": res.fitted_params["thetas"][0],
        "theta3": res.fitted_params["thetas"][1],
        "theta5": res.fitted_params["thetas"][2],
        "min1": res.predicted_minima[0] if len(res.predicted_minima) > 0 else np.nan,
        "min2": res.predicted_minima[1] if len(res.predicted_minima) > 1 else np.nan,
        "min3": res.predicted_minima[2] if len(res.predicted_minima) > 2 else np.nan,
    })

# Convert to DataFrame
df_res = pd.DataFrame(results)
df_res.to_csv("multisector_stability_M.csv", index=False)

print("\nStability results:")
print(df_res)

# ---------------------------------------------------------------------
# Plot results
# ---------------------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.plot(df_res["M"], df_res["objective"], "o-")
plt.title("Objective Stability vs Truncation M")
plt.xlabel("M")
plt.ylabel("Objective Value")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(df_res["M"], df_res["theta2"], label="θ₂")
plt.plot(df_res["M"], df_res["theta3"], label="θ₃")
plt.plot(df_res["M"], df_res["theta5"], label="θ₅")
plt.title("Phase Stability vs Truncation M")
plt.xlabel("M")
plt.ylabel("θ")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()