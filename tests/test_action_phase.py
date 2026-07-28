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
    assert r.hamiltonian_consistency < 1e-12
    assert r.velocity_consistency < 1e-12
    assert r.gamma_consistency < 1e-12
    assert r.proper_time_consistency < 1e-12
    assert r.phase_rate_consistency < 1e-12


def test_rejects_nonfinite():
    assert math.isnan(sst.ActionPhaseAPI.mass_shell_hamiltonian(float("nan"), 1.0, 1.0))
    assert math.isnan(sst.ActionPhaseAPI.mass_shell_hamiltonian(1.0, -1.0, 1.0))
