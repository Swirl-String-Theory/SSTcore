"""Smoke example for geometry_certificate bindings (Canon v0.8.20+)."""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    from SSTcore import GeometryCertificateAPI, CertificateStatus
except ImportError:
    from sstcore import GeometryCertificateAPI, CertificateStatus


def circle(n: int = 64, radius: float = 1.0):
    return [
        [radius * math.cos(2.0 * math.pi * i / n), radius * math.sin(2.0 * math.pi * i / n), 0.0]
        for i in range(n)
    ]


pts = circle(64)
geom = GeometryCertificateAPI.evaluate_tube_geometry(pts, tube_radius=0.05)
print("evaluate_tube_geometry:", geom.status, "sep=", geom.minimum_separation)

sat = GeometryCertificateAPI.evaluate_contact_saturation([0.4, 0.1], saturation_pressure=1.0)
print("evaluate_contact_saturation:", sat.status, sat.saturation_ratio)

hit = GeometryCertificateAPI.chronos_first_hitting([0.0, 1.0, 2.0], [0.0, 0.5, 1.5], 1.0)
print("chronos_first_hitting:", hit.status, hit.first_hitting_time)

rank = GeometryCertificateAPI.rank9_from_singular_values([9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0])
print("rank9_from_singular_values:", rank.status, rank.numerical_rank)

fp = GeometryCertificateAPI.sha256_hex_of_points(pts)
print("sha256_hex_of_points:", fp)
print("CertificateStatus.Pass =", CertificateStatus.Pass)
