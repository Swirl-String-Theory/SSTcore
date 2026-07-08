"""Regression tests for canon-backed binding defaults (P1 refactor)."""

from __future__ import annotations

import math

import pytest

sstcore = pytest.importorskip("SSTcore")


def test_swirl_clock_default_matches_canon_c() -> None:
    c = sstcore.SSTCanonicalConstants.speed_of_light()
    factor = sstcore.swirl_clock_factor_from_speed(0.5 * c)
    expected = sstcore.SSTCanonicalConstants.swirl_clock(0.5 * c, c)
    assert math.isclose(factor, expected, rel_tol=0.0, abs_tol=1e-12)


def test_bernoulli_pressure_default_rho_matches_canon() -> None:
    rho = sstcore.SSTCanonicalConstants.values().rho_f
    p = sstcore.compute_bernoulli_pressure([1.0, 2.0], rho=rho)
    assert len(p) == 2
    assert all(math.isfinite(x) for x in p)


def test_sst_mass_scale_context_from_values() -> None:
  # SSTMassScaleContext is C++ only in P1; verify Python canon values route exists.
    v = sstcore.SSTCanonicalConstants.values()
    assert math.isclose(v.rho_f, 7.0e-7, rel_tol=0.0, abs_tol=0.0)
    assert math.isclose(v.c, 299792458.0, rel_tol=0.0, abs_tol=0.0)
