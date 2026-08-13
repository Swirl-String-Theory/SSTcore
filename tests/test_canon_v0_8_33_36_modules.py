"""Canon 0.8.33–0.8.36 knot / projector / Maxwell tests."""
from __future__ import annotations

import math

import pytest

sst = pytest.importorskip("SSTcore")


def test_worldsheet_guards():
    r = sst.WorldsheetGuardsAPI.evaluate(3, 1.0, 9.68e-9, False, False)
    assert r.passed
    assert r.form_degree_ok
    assert sst.WorldsheetGuardsAPI.ladder_stage_name(0) == "mode_census"


def test_ideal_knot_regime():
    r = sst.IdealKnotRegimeAPI.evaluate(1.0, 1.0, 1.0, 2.0, 3.0, 1.0, 0.01)
    assert r.regime == sst.KnotRegime.Compact
    assert r.lia_kam_excluded
    assert math.isclose(r.helicity_moffatt_ricca, 16.0)  # Γ²(Wr+Tw)=4*(3+1)
    assert math.isclose(sst.IdealKnotRegimeAPI.moffatt_ricca_helicity(2.0, 3.0, 1.0), 16.0)
    s = sst.IdealKnotRegimeAPI.evaluate(0.01, 1.0, 10.0, 1.0, 0.0, 0.0)
    assert s.regime == sst.KnotRegime.Slender


def test_transverse_projector():
    eight_pi_3 = sst.TransverseProjectorAPI.projector_sphere_integral()
    assert math.isclose(eight_pi_3, 8.0 * math.pi / 3.0)
    ld = sst.TransverseProjectorAPI.high_res_ld()
    R0 = sst.TransverseProjectorAPI.leading_response_R0(ld)
    assert math.isclose(R0, eight_pi_3 * ld)
    r = sst.TransverseProjectorAPI.evaluate(ld, 0.0, 0.0, 1.0, 10.0, 0.0, 0.0, 4.0, 3.0)
    assert r.twist_bound_ok
    assert sst.TransverseProjectorAPI.conventions_mixed(
        sst.RopelengthConvention.HighRes, sst.RopelengthConvention.Gilbert
    )


def test_maxwell_stack():
    sr = sst.SpectroResponseAPI.evaluate(2.0, 1.0, 6.626e-34, [1.0], [1e-34], False)
    assert sr.passed
    assert math.isclose(sr.delta_E, 1.0)
    mk = sst.MaxwellKineticAPI.evaluate(1.0, 2.0, 1.0, 0.1, 1.0, 1.0, 1.0, 1.0)
    assert mk.three_gate_ok
    mf = sst.MechanicalFalsifierAPI.evaluate(3.0, 1.0, 7e-7, 1e3)
    assert mf.scaling_ok
    assert math.isclose(mf.delta_p_omega, 2.0)
    st = sst.SwirlTonicAPI.evaluate(
        [1.0, 0.0], [0.0, 1.0], [0.0, 0.0],
        [1.0, 0.0], [0.0, 1.0], [0.0, 0.0],
        1.0, False,
    )
    assert st.passed
    assert math.isclose(st.circulation, 2.0)
