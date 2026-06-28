from __future__ import annotations
import numpy as np
from .base import CoilGeometry, Lane

# Direct extraction of the logic of GUI-SawBowl.py:
# S=40, alternating steps +11,-9, continuous r(s), z(s), three phase offsets.

def alternating_skip_indices(S: int = 40, step_fwd: int = 11, step_bwd: int = -9,
                             n_pairs: int = 20, start: int = 1) -> np.ndarray:
    idx = int(start)
    seq = [idx]
    for k in range(2 * int(n_pairs)):
        if k % 2 == 0:
            idx = (idx + step_fwd - 1) % S + 1
        else:
            idx = (idx + step_bwd - 1) % S + 1
        seq.append(idx)
    return np.asarray(seq, dtype=int)


def r_profile(s: np.ndarray, Rb: float, Rt: float, profile: str = "Exponential", power: float = 2.2) -> np.ndarray:
    if profile == "Exponential":
        return Rb + (Rt - Rb) * (s ** power)
    if profile == "Inverse Exp":
        return Rt - (Rt - Rb) * (s ** power)
    return Rb + (Rt - Rb) * s


def build_phase(seq: np.ndarray, Rb: float, Rt: float, height: float, angle_offset: float = 0.0,
                profile: str = "Exponential", power: float = 2.2,
                mode: str = "curved", samples_per_seg: int = 24,
                S: int = 40) -> np.ndarray:
    slot_angles_base = np.linspace(0.0, 2.0*np.pi, S, endpoint=False) - np.pi/2.0
    N = len(seq) - 1
    s_nodes = np.linspace(0.0, 1.0, N + 1)
    r_nodes = r_profile(s_nodes, Rb, Rt, profile, power)
    z_nodes = s_nodes * height

    if mode == "straight" or mode == "chord":
        pts = []
        for k in range(N + 1):
            a = slot_angles_base[seq[k]-1] + angle_offset
            pts.append([r_nodes[k]*np.cos(a), r_nodes[k]*np.sin(a), z_nodes[k]])
        return np.asarray(pts, dtype=float)

    xs, ys, zs = [], [], []
    for k in range(N):
        i0, i1 = seq[k]-1, seq[k+1]-1
        a0 = slot_angles_base[i0] + angle_offset
        a1 = slot_angles_base[i1] + angle_offset
        da = (a1 - a0 + np.pi) % (2*np.pi) - np.pi
        u = np.linspace(0.0, 1.0, int(samples_per_seg), endpoint=False)
        a_line = a0 + u * da
        r_line = r_nodes[k] + u * (r_nodes[k+1] - r_nodes[k])
        z_line = z_nodes[k] + u * (z_nodes[k+1] - z_nodes[k])
        xs.append(r_line*np.cos(a_line)); ys.append(r_line*np.sin(a_line)); zs.append(z_line)
    # append final node to make length complete
    a_end = slot_angles_base[seq[-1]-1] + angle_offset
    xs.append(np.array([r_nodes[-1]*np.cos(a_end)])); ys.append(np.array([r_nodes[-1]*np.sin(a_end)])); zs.append(np.array([z_nodes[-1]]))
    return np.column_stack([np.concatenate(xs), np.concatenate(ys), np.concatenate(zs)])


def build_sawbowl_3phase(Rb: float = 0.025, Rt: float = 0.030, height: float = 0.006,
                         pairs: int = 20, profile: str = "Exponential", mode: str = "curved",
                         samples_per_seg: int = 24, start: int = 1) -> CoilGeometry:
    seq = alternating_skip_indices(n_pairs=pairs, start=start)
    offsets = [0.0, 2*np.pi/3, 4*np.pi/3]
    lanes = []
    for i, off in enumerate(offsets):
        pts = build_phase(seq, Rb, Rt, height, off, profile=profile, mode=mode, samples_per_seg=samples_per_seg)
        lanes.append(Lane(name=f"sawbowl_{mode}_phase_{i+1}", points=pts, phase_index=i, family="sawbowl"))
    return CoilGeometry(name=f"sawbowl_{mode}", lanes=lanes, metadata={
        "source": "GUI-SawBowl.py", "S": 40, "step_fwd": 11, "step_bwd": -9,
        "pairs": pairs, "profile": profile, "mode": mode, "height_m": height, "Rb_m": Rb, "Rt_m": Rt,
        "rule": "continuous z(s) and r(s); no flat layer replication"
    })
