from __future__ import annotations
import numpy as np
from .base import CoilGeometry, Lane

# Exact modelling intention from rodin_6lane_channel_guide_knot512.py:
# (P,Q)=(5,12), 3 phase offsets [0,1/3,2/3] of one q-sector, mirror via z -> -z.

def torus_knot_5_12(t: np.ndarray, R_major: float = 0.03340, R_tube: float = 0.0090,
                    cell_phase: float = 0.0, mirror: bool = False, P: int = 5, Q: int = 12) -> np.ndarray:
    dt = cell_phase * (2.0*np.pi / Q)
    tp = t + dt
    theta = P * tp
    phi = Q * tp
    x = (R_major + R_tube*np.cos(phi)) * np.cos(theta)
    y = (R_major + R_tube*np.cos(phi)) * np.sin(theta)
    z = R_tube * np.sin(phi)
    if mirror:
        z = -z
    return np.column_stack([x, y, z])


def build_rodin6lane(R_major: float = 0.03340, R_tube: float = 0.0090, n_path: int = 3000,
                     P: int = 5, Q: int = 12) -> CoilGeometry:
    t = np.linspace(0.0, 2.0*np.pi, int(n_path), endpoint=True)
    cell_phases = [0.0, 1.0/3.0, 2.0/3.0]
    lanes = []
    for i, cp in enumerate(cell_phases):
        pts = torus_knot_5_12(t, R_major, R_tube, cp, mirror=False, P=P, Q=Q)
        lanes.append(Lane(name=f"rodin6lane_CW_phase_{i+1}_cp_{cp:.2f}", points=pts, phase_index=i, family="CW"))
    for i, cp in enumerate(cell_phases):
        pts = torus_knot_5_12(t, R_major, R_tube, cp, mirror=True, P=P, Q=Q)
        lanes.append(Lane(name=f"rodin6lane_MIRROR_phase_{i+1}_cp_{cp:.2f}", points=pts, phase_index=i, family="mirror_z"))
    return CoilGeometry(name="rodin6lane", lanes=lanes, metadata={
        "source": "rodin_6lane_channel_guide_knot512.py", "P": P, "Q": Q,
        "cell_phases": cell_phases, "mirror_rule": "z -> -z", "R_major_m": R_major, "R_tube_m": R_tube
    })
