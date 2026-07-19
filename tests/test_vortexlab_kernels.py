"""Golden / smoke tests for VortexLab kernel migration APIs."""
from __future__ import annotations

import math

import numpy as np
import pytest

sst = pytest.importorskip("SSTcore")


def _circle(n: int, R: float = 1.0, z: float = 0.0) -> np.ndarray:
    t = 2 * math.pi * np.arange(n) / n
    return np.column_stack([R * np.cos(t), R * np.sin(t), np.full(n, z)])


def test_resample_closed_curve_preserves_length_order():
    pts = _circle(64)
    out = sst.resample_closed_curve(pts, 128)
    assert out.shape == (128, 3)
    # Closed length should be close to 2π
    d = np.linalg.norm(np.diff(out, axis=0, append=out[:1]), axis=1).sum()
    assert abs(d - 2 * math.pi) < 1e-2


def test_polygonal_gauss_hopf_link():
    a = _circle(96, 1.0, 0.0)
    a[:, 0] -= 0.5
    b = np.column_stack([
        0.5 + np.cos(2 * math.pi * np.arange(96) / 96),
        np.zeros(96),
        np.sin(2 * math.pi * np.arange(96) / 96),
    ])
    r = sst.compute_polygonal_gauss(a, b, same_curve=False)
    assert abs(abs(r["signed_integral"]) - 1.0) < 5e-2
    assert r["linking_integer_audit"] in (-1, 1)


def test_continuous_reach_unit_circle():
    if not hasattr(sst, "compute_continuous_reach"):
        pytest.skip("compute_continuous_reach missing")
    r = sst.compute_continuous_reach([_circle(128)])
    assert abs(r["reach"] - 1.0) < 2e-3
    assert r["limiter"] in ("CURVATURE", "SELF_DCSD", "TIE")


def test_continuous_reach_two_circles():
    r = sst.compute_continuous_reach([_circle(96, 1.0, -0.4), _circle(96, 1.0, 0.4)])
    assert abs(r["reach"] - 0.4) < 5e-3
    assert r["limiter"] == "INTER_COMPONENT"
    assert r["orth_residual"] < 1e-6


def test_topology_clearance_positive():
    r = sst.compute_topology_clearance([_circle(48)])
    assert r["clearance"] > 0.1


def test_filament_velocity_and_rk4_smoke():
    pts = _circle(32)
    fils = [{"id": "0", "points": pts, "circulation": 1.0}]
    opts = {"core_radius": 0.05, "a_sim": 0.05, "lia_constant": 0.25, "core_delta": 0.0}
    v = sst.compute_filament_velocity(fils, opts)
    assert v["maximum_speed"] >= 0.0
    assert len(v["velocity"]) == 1
    step = sst.rk4_step(fils, 1e-4, opts)
    assert "filaments" in step
    dt = sst.estimate_cfl_dt(fils, opts, 0.5)
    assert dt > 0.0


def test_intrinsic_frame_and_rigid_motion():
    pts = _circle(40)
    frame = sst.compute_intrinsic_frame(pts)
    assert len(frame["centroid"]) == 3
    vel = np.zeros_like(pts)
    vel[:, 2] = 1.0
    rm = sst.compute_rigid_motion(pts, vel)
    assert abs(rm["translation"][2] - 1.0) < 1e-6
