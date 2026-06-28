"""
SST_Coil_00_common.py
Shared utilities for the SST SawShape / 3-phase coil test suite.

Scope: classical EM + signal processing + geometry-kernel diagnostics.
This suite does not assume or claim gravitational anomaly. It tests whether
PWM, winding topology, layer geometry, and fR scaling produce reproducible
field/response lobes that could later be compared against experiments.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Literal
import csv
import json
import math
import time

import numpy as np

MU0 = 4.0 * math.pi * 1e-7
MU0_4PI = 1e-7
V_SWIRL = 1.09384563e6          # m/s, SST canonical characteristic swirl speed
RHO_F = 7.0e-7                  # kg/m^3, SST canonical effective fluid density
RHO_CU_20C = 1.724e-8           # ohm m, copper around 20 C
C_LIGHT = 2.99792458e8

Profile = Literal["linear", "exponential", "inverse_exponential"]
PathMode = Literal["chord", "arc"]


@dataclass(frozen=True)
class SawShapeParams:
    slots: int = 40
    step_forward: int = 11
    step_backward: int = -9
    n_pairs: int = 20
    radius_bottom: float = 0.05
    radius_top: float = 0.05
    height: float = 0.0
    profile: Profile = "linear"
    profile_power: float = 2.2
    samples_per_segment: int = 16
    start_slot: int = 0
    phase_offsets: tuple[float, ...] = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)
    z_center: float = 0.0
    path_mode: PathMode = "chord"  # "chord" = straight saw/star segments; "arc" = rounded circular interpolation


@dataclass(frozen=True)
class RunPaths:
    root: Path
    figures: Path
    csv: Path
    npz: Path
    reports: Path
    logs: Path


def make_run_paths(base: str | Path = "exports/SST-Coil", run_name: str | None = None) -> RunPaths:
    stamp = time.strftime("run_%Y%m%d_%H%M%S") if run_name is None else run_name
    root = Path(base) / stamp
    paths = RunPaths(
        root=root,
        figures=root / "figures",
        csv=root / "csv",
        npz=root / "npz",
        reports=root / "reports",
        logs=root / "logs",
    )
    for p in asdict(paths).values():
        Path(p).mkdir(parents=True, exist_ok=True)
    return paths


def save_json(path: str | Path, obj: object) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)


def write_csv(path: str | Path, header: Iterable[str], rows: Iterable[Iterable[object]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(list(header))
        w.writerows(rows)


def alternating_skip_indices(slots: int, step_forward: int, step_backward: int,
                             n_pairs: int, start_slot: int = 0) -> np.ndarray:
    idx = int(start_slot) % int(slots)
    seq = [idx]
    for k in range(2 * int(n_pairs)):
        idx = (idx + (int(step_forward) if k % 2 == 0 else int(step_backward))) % int(slots)
        seq.append(idx)
    return np.asarray(seq, dtype=int)


def radius_profile(s: np.ndarray, rb: float, rt: float, profile: Profile, power: float) -> np.ndarray:
    s = np.asarray(s, dtype=float)
    if profile == "exponential":
        return rb + (rt - rb) * np.power(s, power)
    if profile == "inverse_exponential":
        return rt - (rt - rb) * np.power(s, power)
    return rb + (rt - rb) * s


def sawshape_phase_polyline(params: SawShapeParams, phase_offset: float = 0.0) -> np.ndarray:
    """Build one SawShape phase as a polyline.

    The important default is path_mode="chord": each +11/-9 step is drawn as a
    straight segment between two slot positions. This preserves the star / saw geometry.
    path_mode="arc" is available only for rounded visualizations; it will look close
    to a ring when radius_bottom == radius_top and height == 0.
    """
    seq = alternating_skip_indices(params.slots, params.step_forward, params.step_backward,
                                   params.n_pairs, params.start_slot)
    base_angles = np.linspace(0.0, 2.0 * math.pi, params.slots, endpoint=False) - math.pi / 2.0
    n_seg = len(seq) - 1
    samples = max(2, int(params.samples_per_segment))
    s_nodes = np.linspace(0.0, 1.0, n_seg + 1)
    r_nodes = radius_profile(s_nodes, params.radius_bottom, params.radius_top,
                             params.profile, params.profile_power)
    z_nodes = params.z_center + (s_nodes - 0.5) * params.height

    angles = base_angles[seq] + phase_offset
    node_xyz = np.column_stack([
        r_nodes * np.cos(angles),
        r_nodes * np.sin(angles),
        z_nodes,
    ])

    chunks = []
    for k in range(n_seg):
        u = np.linspace(0.0, 1.0, samples, endpoint=False)[:, None]
        if params.path_mode == "arc":
            a0 = angles[k]
            a1 = angles[k + 1]
            da = (a1 - a0 + math.pi) % (2.0 * math.pi) - math.pi
            uu = u[:, 0]
            a = a0 + uu * da
            r = r_nodes[k] + uu * (r_nodes[k + 1] - r_nodes[k])
            z = z_nodes[k] + uu * (z_nodes[k + 1] - z_nodes[k])
            seg = np.column_stack([r * np.cos(a), r * np.sin(a), z])
        else:
            # Correct SawShape geometry: straight chord from slot to slot.
            seg = node_xyz[k] + u * (node_xyz[k + 1] - node_xyz[k])
        chunks.append(seg)

    chunks.append(node_xyz[-1][None, :])
    return np.vstack(chunks)


def build_three_phase_sawshape(params: SawShapeParams) -> list[np.ndarray]:
    return [sawshape_phase_polyline(params, off) for off in params.phase_offsets]


def pwm_fourier_unipolar(duty: float, n_harmonics: int, amplitude: float = 1.0) -> np.ndarray:
    """Complex Fourier coefficients c[n] for unipolar PWM over phase interval [0,duty)."""
    d = float(np.clip(duty, 0.0, 1.0))
    n_harmonics = int(n_harmonics)
    c = np.zeros(n_harmonics + 1, dtype=np.complex128)
    c[0] = amplitude * d
    for n in range(1, n_harmonics + 1):
        c[n] = amplitude * np.exp(-1j * math.pi * n * d) * math.sin(math.pi * n * d) / (math.pi * n)
    return c


def pwm_real_harmonic_amplitude(duty: float, n: int, amplitude: float = 1.0) -> float:
    c = pwm_fourier_unipolar(duty, int(n), amplitude)
    return 2.0 * abs(c[int(n)])


def three_phase_currents_from_pwm(duty: float, n_harmonics: int, current_peak: float = 1.0) -> np.ndarray:
    c = pwm_fourier_unipolar(duty, n_harmonics, current_peak)
    offsets = np.asarray([0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0])
    out = np.zeros((3, n_harmonics + 1), dtype=np.complex128)
    for p, off in enumerate(offsets):
        for n in range(n_harmonics + 1):
            out[p, n] = c[n] * np.exp(-1j * n * off)
    return out


def biot_savart_points(points: np.ndarray, polyline: np.ndarray, current: complex | float = 1.0,
                       softening: float = 1e-5) -> np.ndarray:
    pts = np.asarray(points, dtype=float)
    poly = np.asarray(polyline, dtype=float)
    dtype = np.complex128 if np.iscomplexobj(current) else np.float64
    B = np.zeros((pts.shape[0], 3), dtype=dtype)
    p0 = poly[:-1]
    p1 = poly[1:]
    dl = p1 - p0
    mid = 0.5 * (p0 + p1)
    eps2 = float(softening) ** 2
    for dL, m in zip(dl, mid):
        r_vec = pts - m
        r2 = np.sum(r_vec * r_vec, axis=1) + eps2
        r3 = r2 * np.sqrt(r2)
        B += (MU0_4PI * current) * np.cross(np.broadcast_to(dL, r_vec.shape), r_vec) / r3[:, None]
    return B


def make_grid(bounds: float = 0.10, res: int = 21, z: float | None = None) -> tuple[np.ndarray, tuple[np.ndarray, ...]]:
    x = np.linspace(-bounds, bounds, int(res))
    y = np.linspace(-bounds, bounds, int(res))
    if z is None:
        zz = np.linspace(-bounds, bounds, int(res))
        X, Y, Z = np.meshgrid(x, y, zz, indexing="ij")
    else:
        X, Y = np.meshgrid(x, y, indexing="ij")
        Z = np.full_like(X, float(z))
    points = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    return points, (X, Y, Z)


def magnetic_energy_density(B: np.ndarray) -> np.ndarray:
    return np.real(np.sum(B * np.conjugate(B), axis=-1)) / (2.0 * MU0)


def magnetic_pressure_proxy(B: np.ndarray) -> np.ndarray:
    return -magnetic_energy_density(B)


def kernel_x(n: int, f0: float, radius: float, v: float = V_SWIRL) -> float:
    return 2.0 * math.pi * int(n) * float(f0) * float(radius) / float(v)


def frequency_for_x(x: float, n: int, radius: float, v: float = V_SWIRL) -> float:
    return float(x) * float(v) / (2.0 * math.pi * int(n) * float(radius))


def skin_depth_copper(f: float, rho: float = RHO_CU_20C, mu: float = MU0) -> float:
    return math.sqrt(2.0 * rho / (mu * 2.0 * math.pi * float(f)))


def estimate_ac_resistance_round_wire(length_m: float, radius_wire_m: float, frequency_hz: float,
                                      rho: float = RHO_CU_20C) -> dict[str, float]:
    """Approximate copper AC resistance using DC area when delta>=a and surface shell when delta<a."""
    a = float(radius_wire_m)
    L = float(length_m)
    delta = skin_depth_copper(float(frequency_hz), rho=rho)
    area_dc = math.pi * a * a
    area_eff = area_dc if delta >= a else 2.0 * math.pi * a * delta
    r_dc = rho * L / area_dc
    r_ac = rho * L / area_eff
    return {"skin_depth_m": delta, "R_dc_ohm": r_dc, "R_ac_ohm": r_ac, "R_ac_over_R_dc": r_ac / r_dc}


def polyline_length(polyline: np.ndarray) -> float:
    p = np.asarray(polyline, dtype=float)
    return float(np.sum(np.linalg.norm(p[1:] - p[:-1], axis=1)))
