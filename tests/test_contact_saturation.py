"""Contact-pressure saturation gate tests (Canon v0.8.20)."""
from __future__ import annotations

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_under_saturation_passes():
    r = sst.GeometryCertificateAPI.evaluate_contact_saturation([0.1, 0.4, 0.0], saturation_pressure=1.0)
    assert r.status == sst.CertificateStatus.Pass
    assert r.peak_contact_pressure == pytest.approx(0.4)
    assert r.saturation_ratio == pytest.approx(0.4)
    assert r.active_contact_count == 2


def test_on_threshold_passes():
    r = sst.GeometryCertificateAPI.evaluate_contact_saturation([1.0], saturation_pressure=1.0, epsilon=1e-9)
    assert r.status == sst.CertificateStatus.Pass
    assert r.saturation_ratio == pytest.approx(1.0)


def test_above_saturation_fails():
    r = sst.GeometryCertificateAPI.evaluate_contact_saturation([1.2], saturation_pressure=1.0)
    assert r.status == sst.CertificateStatus.Fail
    assert r.saturation_ratio == pytest.approx(1.2)


def test_empty_or_invalid_is_indeterminate():
    empty = sst.GeometryCertificateAPI.evaluate_contact_saturation([], saturation_pressure=1.0)
    assert empty.status == sst.CertificateStatus.Indeterminate

    bad = sst.GeometryCertificateAPI.evaluate_contact_saturation([0.5], saturation_pressure=0.0)
    assert bad.status == sst.CertificateStatus.Indeterminate

    nan = sst.GeometryCertificateAPI.evaluate_contact_saturation([float("nan")], saturation_pressure=1.0)
    assert nan.status == sst.CertificateStatus.Indeterminate
