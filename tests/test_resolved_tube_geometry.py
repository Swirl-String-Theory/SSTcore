"""Resolved-tube / ropelength regression tests.

These tests lock the lightweight Rawdon/Cantarella geometry API added for
Canon guardrails v3.  They avoid external knot resources and use simple
closed polygons with analytically checkable lengths and distances.
"""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:  # wheels may expose lower-case module in local CMake builds
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def unit_square():
    return [
        [1.0, 1.0, 0.0],
        [-1.0, 1.0, 0.0],
        [-1.0, -1.0, 0.0],
        [1.0, -1.0, 0.0],
    ]


def two_parallel_segments():
    return ([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [1.0, 2.0, 0.0])


def test_basic_length_edge_stats_and_turning_angle():
    pts = unit_square()
    assert sst.ResolvedTubeGeometry.length(pts) == pytest.approx(8.0)
    assert sst.resolved_tube_length(pts) == pytest.approx(8.0)
    assert sst.ResolvedTubeGeometry.edge_length_mean(pts) == pytest.approx(2.0)
    assert sst.ResolvedTubeGeometry.edge_length_relative_std(pts) == pytest.approx(0.0)
    assert sst.ResolvedTubeGeometry.turning_angle(pts[0], pts[1], pts[2]) == pytest.approx(math.pi / 2)


def test_minrad_kink_and_global_minrad():
    pts = unit_square()
    expected = 1.0 / math.tan(math.pi / 4.0)
    assert sst.ResolvedTubeGeometry.minrad_at_vertex(pts, 0) == pytest.approx(expected)
    kink = sst.ResolvedTubeGeometry.kink_at_vertex(pts, 0)
    assert kink.vertex == 0
    assert kink.minrad == pytest.approx(expected)
    assert kink.turning_angle == pytest.approx(math.pi / 2)
    assert sst.ResolvedTubeGeometry.global_minrad(pts) == pytest.approx(expected)
    assert sst.resolved_tube_minrad(pts) == pytest.approx(expected)


def test_segment_distance_and_dcsd_candidates():
    p0, p1, q0, q1 = two_parallel_segments()
    distance, s, t = sst.ResolvedTubeGeometry.segment_segment_distance(p0, p1, q0, q1)
    assert distance == pytest.approx(2.0)
    assert 0.0 <= s <= 1.0
    assert 0.0 <= t <= 1.0

    pts = unit_square()
    candidates = sst.ResolvedTubeGeometry.dcsd_candidates(pts, skip_neighbors=1, distance_tol=1e-9)
    assert len(candidates) >= 1
    assert min(c.distance for c in candidates) == pytest.approx(2.0)


def test_analyze_ropelength_radius_and_diameter_conventions():
    pts = unit_square()
    metrics = sst.ResolvedTubeGeometry.analyze(pts, skip_neighbors=1, contact_tol=1e-9, equilateral_tol=1e-12)
    assert metrics.length == pytest.approx(8.0)
    assert metrics.minrad == pytest.approx(1.0)
    assert metrics.min_dcsd == pytest.approx(2.0)
    assert metrics.thickness_rad == pytest.approx(1.0)
    assert metrics.reach_rad == pytest.approx(metrics.thickness_rad)
    assert metrics.ropelength_rad == pytest.approx(8.0)
    assert metrics.ropelength_diam == pytest.approx(4.0)
    assert metrics.equilateral_ok is True
    assert len(metrics.struts) >= 1
    assert len(metrics.kinks) == 4

    flat = sst.resolved_tube_analyze(pts, skip_neighbors=1, contact_tol=1e-9, equilateral_tol=1e-12)
    assert flat.ropelength_rad == pytest.approx(metrics.ropelength_rad)


def test_lower_bound_and_convention_converters():
    lower = sst.ResolvedTubeGeometry.nontrivial_knot_lower_bound_rad()
    assert lower == pytest.approx(4.0 * math.pi + 2.0 * math.pi * math.sqrt(2.0))
    assert sst.resolved_tube_lower_bound_rad() == pytest.approx(lower)
    assert sst.ResolvedTubeGeometry.radius_to_diameter_ropelength(32.743274) == pytest.approx(16.371637)
    assert sst.ResolvedTubeGeometry.diameter_to_radius_ropelength(16.371637) == pytest.approx(32.743274)


def test_rigidity_matrix_gradient_columns_and_nnls_kkt_solver():
    pts = unit_square()
    metrics = sst.ResolvedTubeGeometry.analyze(pts, skip_neighbors=1, contact_tol=1e-9, equilateral_tol=1e-12)

    grad = sst.ResolvedTubeGeometry.length_gradient_flat(pts)
    assert len(grad) == 3 * len(pts)
    assert math.sqrt(sum(g * g for g in grad)) > 0.0

    strut_grad = sst.ResolvedTubeGeometry.strut_gradient_flat(pts, metrics.struts[0])
    assert len(strut_grad) == 3 * len(pts)
    assert math.sqrt(sum(g * g for g in strut_grad)) > 0.0

    kink_grad = sst.ResolvedTubeGeometry.kink_minrad_gradient_flat(pts, metrics.kinks[0])
    assert len(kink_grad) == 3 * len(pts)
    assert math.sqrt(sum(g * g for g in kink_grad)) > 0.0

    matrix = sst.ContactStressMap.build_rigidity_matrix(pts, metrics)
    assert matrix.row_count == 3 * len(pts)
    assert matrix.column_count == len(matrix.columns)
    assert matrix.column_count >= len(metrics.kinks)
    assert all(c.kind in {"strut", "kink"} for c in matrix.columns)
    assert all(len(c.values) == matrix.row_count for c in matrix.columns)

    nnls = sst.ContactStressMap.solve_nonnegative_least_squares(matrix, grad, max_iterations=10000, tolerance=1e-12)
    assert nnls.converged is True
    assert nnls.relative_residual < 1e-5
    assert len(nnls.multipliers) == matrix.column_count
    assert all(x >= 0.0 for x in nnls.multipliers)

    diag = sst.ContactStressMap.diagnose_length_criticality(pts, metrics, solve_nnls=True, max_iterations=10000, tolerance=1e-12)
    assert diag.strut_count == len(metrics.struts)
    assert diag.kink_count == len(metrics.kinks)
    assert diag.rigidity_rows == matrix.row_count
    assert diag.rigidity_columns == matrix.column_count
    assert diag.solved_nnls is True
    assert diag.nnls_converged is True
    assert diag.contact_residual < 1e-5
    assert diag.contact_entropy >= 0.0
    assert len(diag.multipliers) == matrix.column_count

    flat = sst.resolved_tube_kkt_diagnostics(pts, metrics, solve_nnls=True, max_iterations=10000, tolerance=1e-12)
    assert flat.contact_residual == pytest.approx(diag.contact_residual)


def test_knot_particle_gate_uses_full_compton_wavelength():
    params = sst.KnotParticleModelParams()
    model = sst.KnotParticleModel(params)
    K = sst.KnotInvariants()
    K.name = "gate-guard"
    K.crossing_number = 8  # force exposed sector in the simple v1 gate
    K.min_self_distance = 1.0
    pred = model.predict(K)
    vals = sst.SSTCanonicalConstants.values()
    expected = vals.lambda_c / (math.pi * vals.r_c)
    assert pred.gate_factor == pytest.approx(expected, rel=1e-8)
    alpha = sst.SSTCanonicalConstants.alpha()
    assert pred.gate_factor == pytest.approx(4.0 / alpha, rel=1e-7)
    assert pred.gate_factor > 100.0  # reduced-Compton gate would be ~87, not ~548


def test_master_equation_horn_baseline_is_separate_from_rho_m_baseline():
    vals = sst.SSTCanonicalConstants.values()
    L_diam_trefoil = 16.371637
    rho_m_mass = sst.SSTMasterEquation.geometric_baseline_mass_from_rho_m(
        vals.rho_m, vals.r_c, vals.lambda_c, L_diam_trefoil
    )
    horn_mass = sst.SSTMasterEquation.geometric_horn_baseline_mass(
        vals.rho_horn, vals.r_c, vals.lambda_c, L_diam_trefoil
    )
    assert horn_mass > rho_m_mass * 1e20
    assert horn_mass / vals.m_e == pytest.approx(4.09, rel=0.05)
