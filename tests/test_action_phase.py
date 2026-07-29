"""Action–phase mass-shell clock (Canon v0.8.28)."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_rest_frame():
    H = sst.ActionPhaseAPI.mass_shell_hamiltonian(0.0, 2.0, 1.0)
    assert H == pytest.approx(2.0)
    assert sst.ActionPhaseAPI.gamma_from_mass_shell(0.0, 2.0, 1.0) == pytest.approx(1.0)
    assert sst.ActionPhaseAPI.proper_time_rate(0.0, 2.0, 1.0) == pytest.approx(1.0)
    assert sst.ActionPhaseAPI.velocity_from_mass_shell(0.0, 2.0, 1.0) == pytest.approx(0.0)


def test_hypot_identity():
    P, E0, c = 3.0, 4.0, 1.0
    H = sst.ActionPhaseAPI.mass_shell_hamiltonian(P, E0, c)
    assert H == pytest.approx(5.0)
    assert sst.ActionPhaseAPI.gamma_from_mass_shell(P, E0, c) == pytest.approx(1.25)


def test_fixed_momentum_phase_rate():
    P, E0, c, O0 = 3.0, 4.0, 1.0, 10.0
    Om = sst.ActionPhaseAPI.internal_phase_rate_at_fixed_momentum(P, E0, c, O0)
    g = sst.ActionPhaseAPI.gamma_from_mass_shell(P, E0, c)
    assert Om == pytest.approx(O0 / g)


def test_residuals_near_zero():
    r = sst.ActionPhaseAPI.action_phase_residuals(3.0, 4.0, 1.0, 2.0)
    assert r.ok
    assert r.finite
    assert r.within_tolerance
    assert r.hamiltonian_consistency < 1e-12
    assert r.velocity_consistency < 1e-12
    assert r.gamma_consistency < 1e-12
    assert r.proper_time_consistency < 1e-12
    assert r.phase_rate_consistency < 1e-12
    assert r.delta_shape_separability == pytest.approx(0.0)


def test_rejects_nonfinite():
    assert math.isnan(sst.ActionPhaseAPI.mass_shell_hamiltonian(float("nan"), 1.0, 1.0))
    assert math.isnan(sst.ActionPhaseAPI.mass_shell_hamiltonian(1.0, -1.0, 1.0))


def test_shape_separability_and_coupled_countermodel():
    assert sst.ActionPhaseAPI.delta_shape_separability(3.0, 4.0, 1.5, 1.0) == pytest.approx(0.0)
    coupled = sst.ActionPhaseAPI.coupled_shape_residual(3.0, 4.0, 1.5, 1.0, eps=0.01, f_q=1.0, df_dq=2.0)
    assert coupled == pytest.approx(0.01 * 9.0 * 2.0)


def test_fixed_v_error_factor_is_gamma_sq_minus_one():
    P, E0, c = 3.0, 4.0, 1.0
    g = sst.ActionPhaseAPI.gamma_from_mass_shell(P, E0, c)
    assert sst.ActionPhaseAPI.fixed_v_phase_error_factor(P, E0, c) == pytest.approx(g * g - 1.0)


def test_large_momentum_velocity_stays_finite():
    V = sst.ActionPhaseAPI.velocity_from_mass_shell(1e150, 1.0, 1.0)
    assert math.isfinite(V)
    assert abs(V) <= 1.0 + 1e-12
