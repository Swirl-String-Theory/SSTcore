"""Bounded-domain Biot–Savart diagnostic gate tests (Canon v0.8.21)."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_four_pi_identity_pass():
    a_k = 1.0 / (4.0 * math.pi)
    r = sst.BiotSavartGateAPI.evaluate(
        observable=a_k,
        estimated_limit=0.0,
        boundary_margin=1.0,
        min_boundary_margin=0.1,
        sample_count=1024,
        regularization_id="desing_core_v1",
        residual_tol=1e-12,
        use_four_pi_identity=True,
    )
    assert r.status == sst.CertificateStatus.Pass
    assert r.relative_residual == pytest.approx(0.0, abs=1e-12)
    assert r.estimated_limit == pytest.approx(a_k)
    assert r.regularization_id == "desing_core_v1"
    assert r.sample_count == 1024


def test_four_pi_identity_fail_residual():
    r = sst.BiotSavartGateAPI.evaluate(
        0.1, 0.0, 1.0, 0.1, 100, "desing_core_v1", residual_tol=1e-6, use_four_pi_identity=True
    )
    assert r.status == sst.CertificateStatus.Fail
    assert r.relative_residual > 1e-6


def test_too_small_domain_fails():
    a_k = 1.0 / (4.0 * math.pi)
    r = sst.BiotSavartGateAPI.evaluate(a_k, 0.0, 0.01, 0.1, 100, "desing_core_v1")
    assert r.status == sst.CertificateStatus.Fail


def test_missing_regularization_indeterminate():
    a_k = 1.0 / (4.0 * math.pi)
    r = sst.BiotSavartGateAPI.evaluate(a_k, 0.0, 1.0, 0.1, 100, "")
    assert r.status == sst.CertificateStatus.Indeterminate

    zero_n = sst.BiotSavartGateAPI.evaluate(a_k, 0.0, 1.0, 0.1, 0, "desing_core_v1")
    assert zero_n.status == sst.CertificateStatus.Indeterminate


def test_relative_limit_mode():
    r = sst.BiotSavartGateAPI.evaluate(
        1.0, 1.0, 1.0, 0.1, 10, "cutoff_scan", residual_tol=1e-9, use_four_pi_identity=False
    )
    assert r.status == sst.CertificateStatus.Pass
    assert r.relative_residual == pytest.approx(0.0)
