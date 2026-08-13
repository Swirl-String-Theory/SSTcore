"""Operational spacetime helpers (Canon v0.8.22)."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_radar_roundtrip():
    r = sst.OperationalSpacetimeAPI.radar_interval(1.0, 3.0, c=1.0)
    assert r.causal is True
    assert r.radar_time == pytest.approx(2.0)
    assert r.radar_distance == pytest.approx(1.0)


def test_radar_acausal():
    r = sst.OperationalSpacetimeAPI.radar_interval(3.0, 1.0, c=1.0)
    assert r.causal is False
    assert math.isnan(r.radar_time)


def test_minkowski_and_lorentz_invariance():
    event = [2.0, 1.0, 0.0, 0.0]
    origin = [0.0, 0.0, 0.0, 0.0]
    s2 = sst.OperationalSpacetimeAPI.minkowski_interval2(event, origin, c=1.0)
    assert s2 == pytest.approx(3.0)
    boost = sst.OperationalSpacetimeAPI.lorentz_boost_x(event, v=0.6, c=1.0)
    assert boost.gamma == pytest.approx(1.25)
    assert boost.invariant_residual < 1e-12


def test_near_c_rejected():
    bad = sst.OperationalSpacetimeAPI.lorentz_boost_x([1.0, 0.0, 0.0, 0.0], v=1.0, c=1.0)
    assert math.isnan(bad.gamma)
