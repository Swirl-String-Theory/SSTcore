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
    assert r["curvature_intervals_examined"] >= 128
    assert r["dcsd_seed_count"] > 0
    assert r["search_converged"] is True


def test_continuous_reach_two_circles():
    r = sst.compute_continuous_reach([_circle(96, 1.0, -0.4), _circle(96, 1.0, 0.4)])
    assert abs(r["reach"] - 0.4) < 5e-3
    assert r["limiter"] == "INTER_COMPONENT"
    assert r["orth_residual"] < 1e-6
    assert r["search_converged"] is True


def test_smooth_tube_unit_circle_ropelength_conventions():
    """Test A: analytic circle R=1 → L=2π, reach=1, Rop_rad=2π, Rop_diam=π."""
    if not hasattr(sst, "analyze_smooth_resolved_tube"):
        pytest.skip("analyze_smooth_resolved_tube missing")
    m = sst.analyze_smooth_resolved_tube([_circle(256)])
    assert abs(m["spline_length"] - 2 * math.pi) < 1e-4
    assert m["spline_length_error"] < 1e-6
    assert abs(m["reach"] - 1.0) < 2e-3
    assert abs(m["ropelength_rad"] - 2 * math.pi) < 1e-2
    assert abs(m["ropelength_diam"] - math.pi) < 5e-3
    assert abs(m["ropelength_rad"] - 2.0 * m["ropelength_diam"]) < 1e-9
    assert m["limiter"] in ("CURVATURE", "SELF_DCSD", "TIE")
    assert m["converged"] is True
    assert m["search_converged"] is True


def test_smooth_tube_two_circles_inter_component():
    """Test B (smooth path): axial separation 0.8 → reach=0.4."""
    m = sst.analyze_smooth_resolved_tube(
        [_circle(96, 1.0, -0.4), _circle(96, 1.0, 0.4)]
    )
    assert abs(m["reach"] - 0.4) < 5e-3
    assert m["limiter"] == "INTER_COMPONENT"


def test_smooth_tube_multiresolution_circle():
    """Test E: multiresolution stability of circle reach / Rop_*."""
    prev_reach = None
    for n in (300, 600, 1200, 2400):
        m = sst.analyze_smooth_resolved_tube([_circle(n)])
        assert abs(m["reach"] - 1.0) < 5e-3
        assert abs(m["ropelength_rad"] - 2 * math.pi) < 2e-2
        if prev_reach is not None:
            assert abs(m["reach"] - prev_reach) < 5e-3
        prev_reach = m["reach"]


def test_smooth_tube_ideal_trefoil_dual_ropelength():
    """Test D: ideal 3:1:1 exports both Rop conventions near atlas values."""
    import re

    try:
        import SSTcore as pkg
    except ImportError:
        pkg = pytest.importorskip("sstcore")

    load_block = getattr(pkg, "load_ideal_ab_embedded", None)
    find_block = getattr(pkg, "find_ideal_ab_block_by_id", None)
    block = None
    if load_block is not None:
        block = load_block("3:1:1")
    if block is None and find_block is not None:
        block = find_block("3:1:1")
    if block is None:
        pytest.skip("ideal 3:1:1 block missing")

    coeffs = []
    for cm in re.finditer(r"<Coeff\s+([^>]*)/>", block):
        attr = dict(re.findall(r'(\w+)="([^"]*)"', cm.group(1)))
        k = int(attr["I"])
        a = [float(x) for x in attr["A"].split(",")]
        b = [float(x) for x in attr["B"].split(",")]
        coeffs.append((k, a, b))
    if not coeffs:
        pytest.skip("no Fourier coeffs in ideal block")

    import numpy as np

    n = 1200
    t = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    pts = np.zeros((n, 3), dtype=float)
    for k, a, b in coeffs:
        kt = k * t
        co = np.cos(kt)
        si = np.sin(kt)
        pts[:, 0] += co * a[0] + si * b[0]
        pts[:, 1] += co * a[1] + si * b[1]
        pts[:, 2] += co * a[2] + si * b[2]

    m = sst.analyze_smooth_resolved_tube([pts])
    assert abs(m["ropelength_rad"] - 2.0 * m["ropelength_diam"]) < 1e-9
    # Atlas diameter convention L ≈ 16.371637 ⇒ Rop_rad ≈ 32.743274.
    # Smooth reach is numerical (reach_spline^num); allow a wider band than polygonal.
    assert m["ropelength_diam"] == pytest.approx(16.371637, rel=0.10)
    assert m["ropelength_rad"] == pytest.approx(32.743274, rel=0.10)
    assert m["reach"] > 0.0
    assert m["search_converged"] is True
    assert "ropelength_rad" in m and "ropelength_diam" in m


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
