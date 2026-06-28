from __future__ import annotations
import numpy as np
from .pwm import pwm_fourier_magnitudes
from .copper import wire_resistance_dc, ac_resistance_factor, crude_wire_inductance


def harmonic_currents_for_geometry(total_wire_length_m: float, f0_hz: float, duty: float = 0.382,
                                   harmonics: int = 25, v_bus: float = 24.0,
                                   wire_radius: float = 0.0005, extra_series_R: float = 0.25,
                                   L_scale: float = 1.0) -> np.ndarray:
    Vn = pwm_fourier_magnitudes(duty=duty, harmonics=harmonics, v_bus=v_bus, bipolar=True)
    Rdc = wire_resistance_dc(total_wire_length_m, wire_radius=wire_radius) + float(extra_series_R)
    L = crude_wire_inductance(total_wire_length_m, wire_radius=wire_radius) * float(L_scale)
    currents = []
    for idx, V in enumerate(Vn, start=1):
        f = idx*float(f0_hz)
        Rac = Rdc * ac_resistance_factor(f, wire_radius=wire_radius)
        Xl = 2*np.pi*f*L
        Z = np.sqrt(Rac*Rac + Xl*Xl)
        currents.append(V/max(Z, 1e-30))
    return np.asarray(currents, dtype=float)


def current_model_summary(total_wire_length_m: float, f0_hz: float = 1e6, wire_radius: float = 0.0005) -> dict:
    from .copper import skin_depth
    return {
        "length_m": float(total_wire_length_m),
        "Rdc_ohm": wire_resistance_dc(total_wire_length_m, wire_radius=wire_radius),
        "L_crude_H": crude_wire_inductance(total_wire_length_m, wire_radius=wire_radius),
        "skin_depth_at_f0_m": skin_depth(f0_hz),
        "Rac_factor_at_f0": ac_resistance_factor(f0_hz, wire_radius=wire_radius),
    }
