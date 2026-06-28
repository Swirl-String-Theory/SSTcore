"""
SST-Coil digital twin common utilities.
Research-tool status: classical EM + circuit approximations; no gravity claim.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

MU0 = 4.0e-7 * math.pi
MU0_4PI = 1.0e-7
RHO_CU_20C = 1.724e-8  # ohm m
V_SWIRL = 1.09384563e6  # m/s, canonical SST swirl speed
RHO_F = 7.0e-7  # kg/m^3, canonical effective fluid density

@dataclass
class CoilConfig:
    S: int = 40
    step_fwd: int = 11
    step_bwd: int = -9
    phases: int = 3
    turns_pairs: int = 40
    samples_per_segment: int = 4
    radius_m: float = 0.05
    height_m: float = 0.0
    layer_count: int = 1
    layer_spacing_m: float = 0.0015
    path_mode: str = "chord"  # chord or arc

@dataclass
class CircuitConfig:
    v_bus: float = 24.0
    duty: float = 0.382
    current_limit_A: float = 8.0
    wire_diameter_m: float = 0.0010
    mosfet_rds_on_ohm: float = 0.055
    driver_deadtime_s: float = 250e-9
    phase_resistance_extra_ohm: float = 0.05
    inductance_scale: float = 1.0
    mutual_k: float = 0.06
    include_skin: bool = True
    waveform: str = "bipolar_pwm"  # bipolar_pwm, sinusoidal

@dataclass
class SweepConfig:
    radii_m: Tuple[float, ...] = (0.03, 0.05, 0.10)
    f_min_hz: float = 1.0e5
    f_max_hz: float = 15.0e6
    samples: int = 260
    harmonics: int = 25
    duty: float = 0.382
    observable: str = "weighted_gradB2"  # weighted_gradB2, axis_B2, asymmetry_Bz


def ensure_run_dirs(root: str | Path = "exports/SST-Coil") -> Dict[str, Path]:
    root = Path(root)
    run_id = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    base = root / run_id
    dirs = {
        "base": base,
        "figures": base / "figures",
        "csv": base / "csv",
        "npz": base / "npz",
        "reports": base / "reports",
        "logs": base / "logs",
    }
    for p in dirs.values():
        p.mkdir(parents=True, exist_ok=True)
    return dirs


def save_json(path: str | Path, obj) -> None:
    def default(o):
        if hasattr(o, "__dataclass_fields__"):
            return asdict(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        raise TypeError(type(o).__name__)
    Path(path).write_text(json.dumps(obj, indent=2, default=default), encoding="utf-8")


def skin_depth_cu(f_hz: float, rho: float = RHO_CU_20C) -> float:
    omega = 2.0 * math.pi * max(float(f_hz), 1e-30)
    return math.sqrt(2.0 * rho / (MU0 * omega))


def ac_resistance_factor_round_wire(f_hz: float, wire_diameter_m: float) -> float:
    """Crude high-frequency AC resistance factor for a round wire.
    Low f -> 1. High f -> area/(skin shell area) approx r/(2 delta).
    """
    r = 0.5 * wire_diameter_m
    delta = skin_depth_cu(f_hz)
    if delta >= r:
        return 1.0
    shell_area = math.pi * (r*r - max(r-delta, 0.0)**2)
    full_area = math.pi * r*r
    return max(1.0, full_area / max(shell_area, 1e-30))


def pwm_harmonic_complex(n: int, duty: float, amplitude: float = 1.0, bipolar: bool = True) -> complex:
    """Complex Fourier coefficient for ideal rectangular PWM.
    Returns coefficient for exp(i n omega t). Magnitude convention is useful comparatively.
    Bipolar waveform has levels +/-amplitude. Unipolar has 0/amplitude.
    """
    d = float(np.clip(duty, 1e-9, 1.0-1e-9))
    if n == 0:
        return amplitude * (2*d - 1.0 if bipolar else d)
    # integral over on-window [0,dT]; bipolar removes DC only, AC coeff doubled vs unipolar.
    coeff = amplitude * (1.0 - np.exp(-2j*np.pi*n*d)) / (2j*np.pi*n)
    if bipolar:
        coeff *= 2.0
    return coeff


def phase_angle(phase_index: int, phases: int = 3) -> float:
    return 2.0 * math.pi * phase_index / phases


def normalize_response(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    m = np.nanmax(np.abs(y))
    if not np.isfinite(m) or m <= 0:
        return y * 0.0
    return y / m


def find_zero_crossings(x: np.ndarray, y: np.ndarray) -> List[float]:
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    out = []
    for i in range(len(y)-1):
        if not np.isfinite(y[i]) or not np.isfinite(y[i+1]):
            continue
        if y[i] == 0:
            out.append(float(x[i]))
        elif y[i] * y[i+1] < 0:
            t = abs(y[i]) / (abs(y[i]) + abs(y[i+1]))
            out.append(float((1-t)*x[i] + t*x[i+1]))
    return out


def local_extrema(x: np.ndarray, y: np.ndarray, min_separation: int = 3) -> List[Tuple[str, float, float]]:
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    out = []
    last = -10**9
    for i in range(1, len(y)-1):
        if i - last < min_separation:
            continue
        if y[i] > y[i-1] and y[i] >= y[i+1]:
            out.append(("max", float(x[i]), float(y[i]))); last = i
        elif y[i] < y[i-1] and y[i] <= y[i+1]:
            out.append(("min", float(x[i]), float(y[i]))); last = i
    return out
