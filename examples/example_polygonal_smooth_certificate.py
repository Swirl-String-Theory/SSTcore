"""Smoke example for polygonal_smooth_certificate + Biot–Savart gate (Canon v0.8.21+)."""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    from SSTcore import PolygonalSmoothCertificateAPI, BiotSavartGateAPI
except ImportError:
    from sstcore import PolygonalSmoothCertificateAPI, BiotSavartGateAPI


def circle(n: int = 48, radius: float = 1.0):
    return [
        [radius * math.cos(2.0 * math.pi * i / n), radius * math.sin(2.0 * math.pi * i / n), 0.0]
        for i in range(n)
    ]


pts = circle(48)
cert = PolygonalSmoothCertificateAPI.evaluate(
    pts, pts, tube_radius=0.05, hausdorff_tol=1e-9, tangent_tol=1e-9, curvature_tol=1e-6
)
print("polygonal_smooth evaluate:", cert.status, "hausdorff=", cert.hausdorff_bound)
print("fingerprint:", PolygonalSmoothCertificateAPI.fingerprint_points(pts))

a_k = 1.0 / (4.0 * math.pi)
biot = BiotSavartGateAPI.evaluate(
    observable=a_k,
    estimated_limit=0.0,
    boundary_margin=1.0,
    min_boundary_margin=0.1,
    sample_count=128,
    regularization_id="desing_core_v1",
    residual_tol=1e-12,
    use_four_pi_identity=True,
)
print("biot_savart_gate:", biot.status, "residual=", biot.relative_residual)
