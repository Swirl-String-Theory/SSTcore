from __future__ import annotations

import numpy as np
from geometry.base import CoilGeometry
from .pwm import pwm_fourier_magnitudes
from .copper import wire_resistance_dc, ac_resistance_factor
from .mutual_inductance import estimate_phase_inductance_matrix


def phase_resistances(coil: CoilGeometry, wire_radius: float = 0.0005,
                      extra_series_R: float = 0.25, phase_count: int = 3) -> np.ndarray:
    lengths = np.zeros(phase_count, dtype=float)
    for lane in coil.lanes:
        lengths[int(lane.phase_index) % phase_count] += lane.length
    return np.asarray([wire_resistance_dc(L, wire_radius=wire_radius) + float(extra_series_R) for L in lengths], dtype=float)


def three_phase_voltage_vector(Vn: float, harmonic_n: int, phase_count: int = 3) -> np.ndarray:
    phases = np.arange(phase_count, dtype=float)
    return Vn * np.exp(-1j * 2.0 * np.pi * harmonic_n * phases / phase_count)


def solve_phase_currents_mutual(coil: CoilGeometry, f_hz: float, Vn: float, harmonic_n: int,
                                L_matrix: np.ndarray | None = None,
                                wire_radius: float = 0.0005,
                                extra_series_R: float = 0.25,
                                phase_count: int = 3) -> np.ndarray:
    if L_matrix is None:
        L_matrix = estimate_phase_inductance_matrix(coil, wire_radius=wire_radius)
    omega = 2.0 * np.pi * float(f_hz)
    Rdc = phase_resistances(coil, wire_radius=wire_radius, extra_series_R=extra_series_R, phase_count=phase_count)
    Rac = Rdc * ac_resistance_factor(f_hz, wire_radius=wire_radius)
    Z = np.diag(Rac.astype(complex)) + 1j * omega * np.asarray(L_matrix, dtype=float)
    V = three_phase_voltage_vector(float(Vn), int(harmonic_n), phase_count=phase_count)
    try:
        return np.linalg.solve(Z, V)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(Z, V, rcond=None)[0]


def harmonic_phase_currents_mutual(coil: CoilGeometry, f0_hz: float, duty: float = 0.382,
                                   harmonics: int = 25, v_bus: float = 24.0,
                                   wire_radius: float = 0.0005,
                                   extra_series_R: float = 0.25,
                                   L_matrix: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    Vn = pwm_fourier_magnitudes(duty=duty, harmonics=harmonics, v_bus=v_bus, bipolar=True)
    if L_matrix is None:
        L_matrix = estimate_phase_inductance_matrix(coil, wire_radius=wire_radius)
    rows = []
    for n, V in enumerate(Vn, start=1):
        rows.append(solve_phase_currents_mutual(
            coil, f_hz=n * float(f0_hz), Vn=float(V), harmonic_n=n,
            L_matrix=L_matrix, wire_radius=wire_radius, extra_series_R=extra_series_R))
    return np.asarray(rows, dtype=np.complex128), L_matrix


def lane_currents_from_phase_currents(coil: CoilGeometry, phase_currents: np.ndarray,
                                      mirror_sign: bool = True) -> list[complex]:
    out = []
    for lane in coil.lanes:
        I = phase_currents[int(lane.phase_index) % len(phase_currents)]
        if mirror_sign and lane.family in ('mirror_z', 'CCW'):
            I = -I
        out.append(complex(I))
    return out
