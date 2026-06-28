from __future__ import annotations
import numpy as np
MU0 = 4*np.pi*1e-7
RHO_F = 7.0e-7


def field_maps(Bx, By, Bz, spacing=None):
    B2 = np.real(Bx*np.conjugate(Bx) + By*np.conjugate(By) + Bz*np.conjugate(Bz))
    Bmag = np.sqrt(np.maximum(B2, 0.0))
    if spacing is None:
        grad = np.gradient(B2)
    else:
        grad = np.gradient(B2, *spacing, edge_order=1)
    gradB2 = np.sqrt(sum(g*g for g in grad))
    pressure_B = -B2/(2*MU0)
    pressure_sst_proxy = -0.5*RHO_F*B2  # only a normalized proxy, not a physical B->v conversion
    return {"B2": B2, "Bmag": Bmag, "gradB2": gradB2, "pressure_B": pressure_B, "pressure_sst_proxy": pressure_sst_proxy}


def summarize_maps(maps: dict) -> dict:
    out = {}
    for k, arr in maps.items():
        a = np.asarray(arr)
        out[f"{k}_mean"] = float(np.nanmean(a))
        out[f"{k}_max"] = float(np.nanmax(a))
        out[f"{k}_p95"] = float(np.nanpercentile(a, 95))
    return out


def observable_scalar(maps: dict, kind: str = "gradB2_mean") -> float:
    if kind == "gradB2_mean": return float(np.mean(maps["gradB2"]))
    if kind == "gradB2_p95": return float(np.percentile(maps["gradB2"], 95))
    if kind == "B2_mean": return float(np.mean(maps["B2"]))
    if kind == "B2_max": return float(np.max(maps["B2"]))
    if kind == "pressureB_abs_mean": return float(np.mean(np.abs(maps["pressure_B"])))
    raise ValueError(f"Unknown observable kind: {kind}")
