#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SawBowl/SawShape geometry sector extracted from GUI-SawBowl.py.

This file intentionally preserves the user's original interpretation:
S=40, step sequence (+11, -9), three phase offsets, and continuous z/r progression
along the wire. `n_pairs` is not a flat-layer count; it is the number of alternating
(+11,-9) pairs traversed by one continuous lane.
"""
from __future__ import annotations
import numpy as np

S_DEFAULT = 40
STEP_FWD_DEFAULT = 11
STEP_BWD_DEFAULT = -9
POWER_DEFAULT = 2.2
PHASE_OFFSETS = (0.0, 2*np.pi/3, 4*np.pi/3)


def alternating_skip_indices(S: int = S_DEFAULT, step_fwd: int = STEP_FWD_DEFAULT,
                             step_bwd: int = STEP_BWD_DEFAULT, n_pairs: int = 20,
                             start: int = 1) -> np.ndarray:
    idx = int(start)
    seq = [idx]
    for k in range(2*int(n_pairs)):
        if k % 2 == 0:
            idx = (idx + int(step_fwd) - 1) % int(S) + 1
        else:
            idx = (idx + int(step_bwd) - 1) % int(S) + 1
        seq.append(idx)
    return np.array(seq, dtype=int)


def r_profile(s, Rb: float, Rt: float, profile: str = 'Exponential', power: float = POWER_DEFAULT):
    s = np.asarray(s, dtype=float)
    if profile == 'Exponential':
        return Rb + (Rt - Rb)*(s**power)
    if profile == 'Inverse Exp':
        return Rt - (Rt - Rb)*(s**power)
    return Rb + (Rt - Rb)*s


def build_sawbowl_phase(seq: np.ndarray, *, Rb: float = 0.025, Rt: float = 0.030,
                         height: float = 0.006, angle_offset: float = 0.0,
                         profile: str = 'Exponential', mode: str = 'curved',
                         samples_per_seg: int = 24, S: int = S_DEFAULT,
                         power: float = POWER_DEFAULT) -> np.ndarray:
    slot_angles_base = np.linspace(0, 2*np.pi, int(S), endpoint=False) - np.pi/2.0
    N = len(seq) - 1
    s_nodes = np.linspace(0, 1, N+1)
    r_nodes = r_profile(s_nodes, Rb, Rt, profile, power)
    z_nodes = s_nodes * float(height)

    if mode in ('straight', 'chord'):
        pts = []
        for k in range(N+1):
            a = slot_angles_base[seq[k]-1] + angle_offset
            pts.append([r_nodes[k]*np.cos(a), r_nodes[k]*np.sin(a), z_nodes[k]])
        return np.array(pts, dtype=float)

    xs, ys, zs = [], [], []
    for k in range(N):
        i0, i1 = seq[k]-1, seq[k+1]-1
        a0 = slot_angles_base[i0] + angle_offset
        a1 = slot_angles_base[i1] + angle_offset
        da = (a1 - a0 + np.pi) % (2*np.pi) - np.pi
        u = np.linspace(0, 1, int(samples_per_seg), endpoint=False)
        a_line = a0 + u*da
        r_line = r_nodes[k] + u*(r_nodes[k+1] - r_nodes[k])
        z_line = z_nodes[k] + u*(z_nodes[k+1] - z_nodes[k])
        xs.append(r_line*np.cos(a_line)); ys.append(r_line*np.sin(a_line)); zs.append(z_line)
    a_end = slot_angles_base[seq[-1]-1] + angle_offset
    xs.append(np.array([r_nodes[-1]*np.cos(a_end)])); ys.append(np.array([r_nodes[-1]*np.sin(a_end)])); zs.append(np.array([z_nodes[-1]]))
    return np.column_stack([np.concatenate(xs), np.concatenate(ys), np.concatenate(zs)])


def build_sawbowl_3phase(*, Rb: float = 0.025, Rt: float = 0.030, height: float = 0.006,
                         n_pairs: int = 20, profile: str = 'Exponential', mode: str = 'curved',
                         samples_per_seg: int = 24, S: int = S_DEFAULT,
                         step_fwd: int = STEP_FWD_DEFAULT, step_bwd: int = STEP_BWD_DEFAULT,
                         start: int = 1) -> list[dict]:
    seq = alternating_skip_indices(S=S, step_fwd=step_fwd, step_bwd=step_bwd, n_pairs=n_pairs, start=start)
    lanes = []
    for i, off in enumerate(PHASE_OFFSETS):
        pts = build_sawbowl_phase(seq, Rb=Rb, Rt=Rt, height=height, angle_offset=off,
                                  profile=profile, mode=mode, samples_per_seg=samples_per_seg, S=S)
        lanes.append(dict(name=f'SawBowl phase {i+1}', geometry='sawbowl', phase=i,
                          mirror=False, seq=seq.copy(), points=pts))
    return lanes
