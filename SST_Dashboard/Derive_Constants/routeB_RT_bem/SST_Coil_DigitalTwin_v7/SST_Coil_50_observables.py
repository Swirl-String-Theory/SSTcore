"""Observable reductions for field arrays."""
from __future__ import annotations
import numpy as np
MU0=4*np.pi*1e-7

def reduce_observable(obs, mode="weighted_gradB2"):
    if mode == "mean_B2": return float(np.mean(obs["B2"]))
    if mode == "max_Bmag": return float(np.max(obs["Bmag"]))
    if mode == "mean_gradB2": return float(np.mean(obs["gradB2"]))
    if mode == "weighted_gradB2":
        B2=obs["B2"]; g=obs["gradB2"]
        return float(np.sum(B2*g)/(np.sum(B2)+1e-30))
    if mode == "z_asym_gradB2":
        gz=obs["gradB2_z"]
        return float(np.mean(gz))
    raise ValueError(mode)

def pressure_B(B2):
    return -B2/(2*MU0)
