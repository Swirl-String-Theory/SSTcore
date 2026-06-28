from __future__ import annotations
import numpy as np
MU0 = 4*np.pi*1e-7
RHO_CU = 1.724e-8


def skin_depth(f_hz: float, rho: float = RHO_CU, mu: float = MU0) -> float:
    omega = 2*np.pi*max(float(f_hz), 1e-30)
    return float(np.sqrt(2*rho/(mu*omega)))


def ac_resistance_factor(f_hz: float, wire_radius: float = 0.0005) -> float:
    delta = skin_depth(f_hz)
    # Round wire crude high-frequency approximation: effective area is annulus depth delta.
    # Use exact area when delta >= radius.
    r = float(wire_radius)
    if delta >= r:
        return 1.0
    area_dc = np.pi*r*r
    area_ac = np.pi*(r*r - max(r-delta, 0.0)**2)
    return float(area_dc/max(area_ac, 1e-30))


def wire_resistance_dc(length_m: float, wire_radius: float = 0.0005, rho: float = RHO_CU) -> float:
    area = np.pi*wire_radius*wire_radius
    return float(rho*length_m/max(area, 1e-30))


def crude_wire_inductance(length_m: float, wire_radius: float = 0.0005) -> float:
    # Rough isolated-wire loop-scale inductance. Good only for relative geometry-dependent rolloff.
    l = max(float(length_m), 1e-9)
    a = max(float(wire_radius), 1e-9)
    return float(MU0*l*(np.log(max(2*l/a, 1.0001))-1.0)/(2*np.pi))
