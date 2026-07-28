"""Rank-nine contact-channel diagnostic tests (Canon v0.8.20)."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_full_rank9_passes():
    sv = [9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    r = sst.GeometryCertificateAPI.rank9_from_singular_values(sv, tau_rank=1e-12)
    assert r.status == sst.CertificateStatus.Pass
    assert r.numerical_rank == 9
    assert r.conditioning == pytest.approx(9.0)


def test_rank8_fails():
    sv = [9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 0.0]
    r = sst.GeometryCertificateAPI.rank9_from_singular_values(sv, tau_rank=1e-12)
    assert r.status == sst.CertificateStatus.Fail
    assert r.numerical_rank == 8


def test_ill_conditioned_still_rank9():
    sv = [1.0, 1e-3, 1e-3, 1e-3, 1e-3, 1e-3, 1e-3, 1e-3, 1e-3]
    r = sst.GeometryCertificateAPI.rank9_from_singular_values(sv, tau_rank=1e-12)
    assert r.status == sst.CertificateStatus.Pass
    assert r.numerical_rank == 9
    assert r.conditioning == pytest.approx(1e3)


def test_zero_spectrum_fails():
    r = sst.GeometryCertificateAPI.rank9_from_singular_values([0.0] * 9)
    assert r.status == sst.CertificateStatus.Fail
    assert r.numerical_rank == 0
    assert math.isinf(r.conditioning)


def test_invalid_tau_or_values_indeterminate():
    bad_tau = sst.GeometryCertificateAPI.rank9_from_singular_values([1.0] * 9, tau_rank=0.0)
    assert bad_tau.status == sst.CertificateStatus.Indeterminate

    neg = sst.GeometryCertificateAPI.rank9_from_singular_values([1.0, -0.1] + [0.0] * 7)
    assert neg.status == sst.CertificateStatus.Indeterminate
