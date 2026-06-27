"""Patch B: knot_registry and ParticleEvaluator canon guards."""

from __future__ import annotations

import pytest

from sstcore_test_import import load_sstcore_package

sstcore = load_sstcore_package()


def test_resolve_knot_ref_ideal_trefoil():
    res = sstcore.resolve_knot_ref("3:1:1")
    assert res is not None
    assert res.role == sstcore.KnotCurveRole.CANON_IDEAL
    assert res.source == sstcore.KnotSource.IDEAL
    assert res.ropelength == pytest.approx(16.371637, rel=1e-6)
    assert res.canonical_ab_id == "3:1:1"


def test_resolve_knot_ref_fremlin_role():
    res = sstcore.resolve_knot_ref("3_1", source="fremlin")
    assert res is not None
    assert res.role == sstcore.KnotCurveRole.ANALYTIC_TEST
    assert res.source == sstcore.KnotSource.FREMLIN
    assert res.fremlin_label == "3_1"


def test_resolve_knot_ref_knotplot_legacy():
    kp_path = sstcore.get_knotplot_ideal_path("knot_3.1")
    if kp_path is None:
        pytest.skip("knotplot trefoil not in resources")
    res = sstcore.resolve_knot_ref("knot_3.1", source="knotplot")
    assert res is not None
    assert res.role == sstcore.KnotCurveRole.LEGACY_IMPORT
    assert res.native_length == pytest.approx(57.006641704311, rel=1e-4)


def test_assert_canon_ideal_rejects_knotplot():
    kp_path = sstcore.get_knotplot_ideal_path("knot_3.1")
    if kp_path is None:
        pytest.skip("knotplot trefoil not in resources")
    res = sstcore.resolve_knot_ref("knot_3.1", source="knotplot")
    with pytest.raises(ValueError, match="canon_mass"):
        sstcore.assert_canon_ideal(res, sstcore.CalculationRole.CANON_MASS)


def test_particle_evaluator_rejects_knotplot_id():
    with pytest.raises(RuntimeError, match="non-canon|Non-canon|ideal.txt"):
        sstcore.ParticleEvaluator("knot_3.1", 200)


def test_particle_evaluator_research_flag_allows_non_ab_id():
    with pytest.raises(RuntimeError, match="niet gevonden|not found"):
        sstcore.ParticleEvaluator(
            "knot_3.1",
            200,
            allow_non_canonical_geometry_for_research_only=True,
        )
