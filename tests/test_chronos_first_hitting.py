"""Chronos first-hitting time tests (Canon v0.8.20)."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_exact_hit_at_sample():
    r = sst.GeometryCertificateAPI.chronos_first_hitting([0.0, 1.0, 2.0], [0.0, 1.0, 2.0], threshold=1.0)
    assert r.status == sst.CertificateStatus.Pass
    assert r.first_hitting_time == pytest.approx(1.0)
    assert r.event_index == 1
    assert r.threshold == pytest.approx(1.0)


def test_interpolated_crossing():
    r = sst.GeometryCertificateAPI.chronos_first_hitting([0.0, 1.0, 2.0], [0.0, 0.5, 1.5], threshold=1.0)
    assert r.status == sst.CertificateStatus.Pass
    assert r.first_hitting_time == pytest.approx(1.5)
    assert r.event_index == 2


def test_hit_at_t0():
    r = sst.GeometryCertificateAPI.chronos_first_hitting([0.0, 1.0], [2.0, 3.0], threshold=1.0)
    assert r.status == sst.CertificateStatus.Pass
    assert r.first_hitting_time == pytest.approx(0.0)
    assert r.event_index == 0


def test_no_hit_fails():
    r = sst.GeometryCertificateAPI.chronos_first_hitting([0.0, 1.0, 2.0], [0.0, 0.2, 0.4], threshold=1.0)
    assert r.status == sst.CertificateStatus.Fail
    assert math.isinf(r.first_hitting_time)
    assert r.event_index == 3


def test_bad_input_indeterminate():
    short = sst.GeometryCertificateAPI.chronos_first_hitting([0.0], [0.0], threshold=1.0)
    assert short.status == sst.CertificateStatus.Indeterminate

    mismatch = sst.GeometryCertificateAPI.chronos_first_hitting([0.0, 1.0], [0.0], threshold=1.0)
    assert mismatch.status == sst.CertificateStatus.Indeterminate

    nonmono = sst.GeometryCertificateAPI.chronos_first_hitting([0.0, 2.0, 1.0], [0.0, 0.5, 1.5], threshold=1.0)
    assert nonmono.status == sst.CertificateStatus.Indeterminate
