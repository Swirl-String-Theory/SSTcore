"""
SST-Coil Digital Twin v7 common utilities.
Pure functions only; no GUI side effects.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import json
import numpy as np

MU0 = 4*np.pi*1e-7
MU0_4PI = 1e-7
RHO_CU = 1.724e-8
V_SWIRL = 1.09384563e6

@dataclass
class ExportPaths:
    root: Path
    figures: Path
    csv: Path
    npz: Path
    reports: Path
    logs: Path


def make_export_paths(base: str | Path = "exports/SST-Coil", run_name: str | None = None) -> ExportPaths:
    base = Path(base)
    if run_name is None:
        run_name = "run_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    root = base / run_name
    p = ExportPaths(root, root/"figures", root/"csv", root/"npz", root/"reports", root/"logs")
    for d in asdict(p).values():
        Path(d).mkdir(parents=True, exist_ok=True)
    return p


def write_json(path: str | Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=float)


def save_csv(path: str | Path, rows: list[dict]) -> None:
    import csv
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({k for r in rows for k in r.keys()})
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def unit(v: np.ndarray, eps: float = 1e-30) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, eps)


def make_grid(bounds: float, res: int):
    x = np.linspace(-bounds, bounds, int(res))
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    return x, X, Y, Z


def skin_depth(f_hz: float, rho: float = RHO_CU, mu: float = MU0) -> float:
    w = 2*np.pi*max(float(f_hz), 1e-30)
    return float(np.sqrt(2*rho/(mu*w)))


def pwm_harmonic_unipolar(n: int, duty: float, v_bus: float = 24.0) -> complex:
    """Complex Fourier coefficient for 0..V unipolar PWM at harmonic n of f0."""
    n = int(n)
    if n == 0:
        return v_bus*duty + 0j
    # coefficient c_n = V/T int_0^{dT} exp(-i2πnt/T) dt
    return v_bus * np.exp(-1j*np.pi*n*duty) * np.sin(np.pi*n*duty)/(np.pi*n)


def phase_current_coeffs(f0: float, duty: float, harmonics: int, v_bus: float,
                         R_ohm: float, L_h: float, C_f: float | None = None,
                         phase_offset: float = 0.0) -> dict[int, complex]:
    """Return harmonic current coefficients for one phase with crude series R-L and optional parallel-ish C shunt rolloff.
    Phase offset is temporal phase of this phase in radians at fundamental; harmonic n gets n*offset.
    """
    out = {}
    for n in range(1, harmonics+1):
        f = n*float(f0)
        w = 2*np.pi*f
        Z = complex(R_ohm, w*L_h)
        if C_f and C_f > 0:
            # crude: capacitance reduces current through ideal series coil near/above SRF by admittance competition
            # keep numerically stable and explicitly approximate.
            Y = 1/Z + 1j*w*C_f
            Z_eff = 1/Y if abs(Y) > 0 else Z
        else:
            Z_eff = Z
        Vn = pwm_harmonic_unipolar(n, duty, v_bus) * np.exp(-1j*n*phase_offset)
        out[n] = Vn / Z_eff
    return out


def normalize_response(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    m = np.nanmax(np.abs(y)) if y.size else 0.0
    return y/m if m > 0 else y
