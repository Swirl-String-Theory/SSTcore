#!/usr/bin/env python3
"""Large-knot resolved-tube sparse backend example.

This example builds a moderately large torus-knot polygon, constructs the sparse
strut/kink rigidity matrix, and runs the internal sparse NNLS contact-balance
solver.  It is intentionally dependency-light: no Eigen, scipy, tsnnls, or TAUCS
is required.  A C++ Eigen adapter is available behind the SSTCORE_USE_EIGEN macro
for downstream builds that want to hand the matrix to an external sparse solver.
"""
from __future__ import annotations

import math

try:
    import SSTcore as sst
except ImportError:
    import sstcore as sst


def torus_knot(p: int = 2, q: int = 3, n: int = 240, R: float = 2.0, r: float = 0.65):
    pts = []
    for k in range(n):
        t = 2.0 * math.pi * k / n
        x = (R + r * math.cos(q * t)) * math.cos(p * t)
        y = (R + r * math.cos(q * t)) * math.sin(p * t)
        z = r * math.sin(q * t)
        pts.append([x, y, z])
    return pts


def main() -> None:
    pts = torus_knot()
    metrics = sst.ResolvedTubeGeometry.analyze(
        pts, skip_neighbors=8, contact_tol=2.5e-2, equilateral_tol=5e-2
    )
    sparse = sst.ContactStressMap.build_sparse_rigidity_matrix(
        pts, metrics, include_struts=True, include_kinks=True, use_analytic_kink_gradient=True
    )
    grad = sst.ResolvedTubeGeometry.length_gradient_flat(pts)
    nnls = sst.ContactStressMap.solve_nonnegative_least_squares_sparse(
        sparse, grad, max_iterations=2000, tolerance=1e-8
    )

    print("large resolved-tube sparse path")
    print("vertices:", len(pts))
    print("length:", metrics.length)
    print("thickness_rad:", metrics.thickness_rad)
    print("ropelength_rad/diam:", metrics.ropelength_rad, metrics.ropelength_diam)
    print("struts/kinks:", len(metrics.struts), len(metrics.kinks))
    print("sparse matrix rows/cols/nonzeros:", sparse.row_count, sparse.column_count, sparse.nonzero_count)
    print("NNLS converged:", nnls.converged)
    print("NNLS iterations:", nnls.iterations)
    print("NNLS relative residual:", nnls.relative_residual)


if __name__ == "__main__":
    main()
