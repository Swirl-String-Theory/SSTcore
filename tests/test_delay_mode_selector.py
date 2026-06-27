#!/usr/bin/env python3
"""Canon v0.8.12 delay-mode selector sign convention (audit regression)."""

from __future__ import annotations

import math

import pytest

sstcore = pytest.importorskip("SSTcore", exc_type=ImportError)
DMS = sstcore.DelayModeSelector


def test_phase_lock_residual_matches_canon_sign():
    """f(Omega) = Omega - omega0 + kappa*sin(Omega*tau); root => Omega = omega0 - kappa*sin(Omega*tau)."""
    omega0, kappa, tau = 1.0e6, 2.0e4, 1.0e-6
    result = DMS.solve_phase_locked_frequency(omega0, kappa, tau, initial_guess=omega0)
    assert result.converged
    assert abs(result.residual) < 1e-5
    omega = result.omega
    assert omega == pytest.approx(omega0 - kappa * math.sin(omega * tau), rel=1e-9, abs=1e-3)


def test_newton_derivative_matches_canon():
    omega0, kappa, tau = 5.0e5, 1.0e4, 2.0e-6
    result = DMS.solve_phase_locked_frequency(omega0, kappa, tau, initial_guess=omega0)
    assert result.converged
    omega = result.omega
    expected_df = 1.0 + kappa * tau * math.cos(omega * tau)
    residual_at_omega = DMS.phase_lock_residual(omega, omega0, kappa, tau)
    assert abs(residual_at_omega) < 1e-5
    # Finite-difference check on residual (Newton uses f' = 1 + kappa*tau*cos(Omega*tau))
    eps = 1e-6 * max(1.0, abs(omega))
    fd = (
        DMS.phase_lock_residual(omega + eps, omega0, kappa, tau)
        - DMS.phase_lock_residual(omega - eps, omega0, kappa, tau)
    ) / (2.0 * eps)
    assert fd == pytest.approx(expected_df, rel=1e-5, abs=1e-3)


def test_phase_lock_stability_slope_is_kappa_tau_cos():
    omega, kappa, tau = 3.0e5, 8.0e3, 1.5e-6
    assert DMS.phase_lock_stability_slope(omega, kappa, tau) == pytest.approx(
        kappa * tau * math.cos(omega * tau)
    )
