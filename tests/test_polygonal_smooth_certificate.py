"""Polygonal→smooth certification tests (Canon v0.8.21)."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def circle(n: int, radius: float = 1.0):
    return [
        [radius * math.cos(2.0 * math.pi * i / n), radius * math.sin(2.0 * math.pi * i / n), 0.0]
        for i in range(n)
    ]


def test_identical_circle_samples_pass():
    pts = circle(64)
    cert = sst.PolygonalSmoothCertificateAPI.evaluate(
        pts, pts, tube_radius=0.05, hausdorff_tol=1e-9, tangent_tol=1e-9, curvature_tol=1e-6
    )
    assert cert.status == sst.CertificateStatus.Pass
    assert cert.hausdorff_bound == pytest.approx(0.0)
    assert cert.tangent_error == pytest.approx(0.0)
    assert cert.thickness_lower_bound > 0.05
    assert cert.polygon_hash == cert.smooth_hash


def test_refinement_series_within_loose_tangent_budget():
    poly = circle(32)
    smooth = circle(128)
    cert = sst.PolygonalSmoothCertificateAPI.evaluate(
        poly, smooth, tube_radius=0.05, hausdorff_tol=0.2, tangent_tol=2.1, curvature_tol=0.5
    )
    assert cert.status == sst.CertificateStatus.Pass
    assert cert.hausdorff_bound <= 0.2
    assert cert.polygon_hash != cert.smooth_hash


def test_coarse_mismatch_fails():
    poly = circle(16)
    # Intentionally wrong smooth: scaled circle
    smooth = circle(64, radius=1.5)
    cert = sst.PolygonalSmoothCertificateAPI.evaluate(
        poly, smooth, tube_radius=0.05, hausdorff_tol=0.01, tangent_tol=0.01, curvature_tol=0.01
    )
    assert cert.status == sst.CertificateStatus.Fail
    assert cert.hausdorff_bound > 0.01


def test_missing_input_indeterminate():
    cert = sst.PolygonalSmoothCertificateAPI.evaluate([], circle(16), 0.05, 0.1, 0.1, 0.1)
    assert cert.status == sst.CertificateStatus.Indeterminate


def test_fingerprint_stable():
    pts = circle(24)
    assert sst.PolygonalSmoothCertificateAPI.fingerprint_points(pts) == sst.PolygonalSmoothCertificateAPI.fingerprint_points(pts)
