"""Geometry-certificate gate tests (Canon v0.8.20)."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def circle_pts(n: int = 64, radius: float = 1.0):
    return [
        [radius * math.cos(2.0 * math.pi * i / n), radius * math.sin(2.0 * math.pi * i / n), 0.0]
        for i in range(n)
    ]


def test_valid_resolved_tube_circle_passes():
    pts = circle_pts(64, 1.0)
    cert = sst.GeometryCertificateAPI.evaluate_tube_geometry(pts, tube_radius=0.05)
    assert cert.status == sst.CertificateStatus.Pass
    assert cert.tube_radius == pytest.approx(0.05)
    assert cert.minimum_radius_of_curvature == pytest.approx(1.0, rel=5e-2)
    assert cert.minimum_separation > 2.0 * cert.tube_radius
    assert cert.thickness_margin > 0.0
    assert isinstance(cert.geometry_hash, str) and len(cert.geometry_hash) == 64


def test_self_contact_failure_large_tube_radius():
    pts = circle_pts(48, 1.0)
    cert = sst.GeometryCertificateAPI.evaluate_tube_geometry(pts, tube_radius=2.0)
    assert cert.status == sst.CertificateStatus.Fail
    assert cert.thickness_margin < 0.0


def test_missing_input_is_indeterminate_not_pass():
    empty = sst.GeometryCertificateAPI.evaluate_tube_geometry([], tube_radius=0.1)
    assert empty.status == sst.CertificateStatus.Indeterminate

    bad_a = sst.GeometryCertificateAPI.evaluate_tube_geometry(circle_pts(16), tube_radius=0.0)
    assert bad_a.status == sst.CertificateStatus.Indeterminate


def test_geometry_hash_stable_and_sensitive():
    pts = circle_pts(32)
    h1 = sst.GeometryCertificateAPI.sha256_hex_of_points(pts)
    h2 = sst.GeometryCertificateAPI.sha256_hex_of_points(pts)
    assert h1 == h2
    pts2 = list(pts)
    pts2[0] = [pts2[0][0] + 1e-6, pts2[0][1], pts2[0][2]]
    assert sst.GeometryCertificateAPI.sha256_hex_of_points(pts2) != h1
