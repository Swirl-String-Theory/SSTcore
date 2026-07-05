#!/usr/bin/env python3
"""Ridgerunner-style KKT/NNLS contact solver example for SSTcore.

This example demonstrates the second resolved-tube patch: build active strut/kink
constraint columns, solve the non-negative least-squares balance

    A lambda ~= grad Len(V), lambda >= 0,

and report the dimensionless KKT residual.
"""
from __future__ import annotations

try:
    import SSTcore as sst
except ImportError:
    import sstcore as sst


def square_polygon():
    return [
        [1.0, 1.0, 0.0],
        [-1.0, 1.0, 0.0],
        [-1.0, -1.0, 0.0],
        [1.0, -1.0, 0.0],
    ]


def main() -> None:
    pts = square_polygon()
    metrics = sst.ResolvedTubeGeometry.analyze(
        pts, skip_neighbors=1, contact_tol=1e-9, equilateral_tol=1e-12
    )

    grad_len = sst.ResolvedTubeGeometry.length_gradient_flat(pts)
    rigidity = sst.ContactStressMap.build_rigidity_matrix(pts, metrics)
    sparse = sst.ContactStressMap.build_sparse_rigidity_matrix(pts, metrics)
    nnls = sst.ContactStressMap.solve_nonnegative_least_squares(
        rigidity, grad_len, max_iterations=10000, tolerance=1e-12
    )
    nnls_sparse = sst.ContactStressMap.solve_nonnegative_least_squares_sparse(
        sparse, grad_len, max_iterations=10000, tolerance=1e-12
    )
    diag = sst.ContactStressMap.diagnose_length_criticality(
        pts, metrics, solve_nnls=True, max_iterations=10000, tolerance=1e-12,
        use_sparse_solver=True, use_analytic_kink_gradient=True
    )

    print("Resolved tube KKT/NNLS diagnostics")
    print("length:", metrics.length)
    print("thickness_rad:", metrics.thickness_rad)
    print("struts/kinks:", len(metrics.struts), len(metrics.kinks))
    print("rigidity matrix rows/columns:", rigidity.row_count, rigidity.column_count)
    print("sparse nonzeros:", sparse.nonzero_count)
    print("first column kind/norm:", rigidity.columns[0].kind, rigidity.columns[0].norm)
    print("dense NNLS converged:", nnls.converged)
    print("dense NNLS iterations:", nnls.iterations)
    print("dense NNLS relative residual:", nnls.relative_residual)
    print("sparse NNLS converged:", nnls_sparse.converged)
    print("sparse NNLS relative residual:", nnls_sparse.relative_residual)
    print("diagnostic contact residual:", diag.contact_residual)
    print("strut weight sum:", diag.strut_weight_sum)
    print("kink weight sum:", diag.kink_weight_sum)
    print("contact entropy:", diag.contact_entropy)


if __name__ == "__main__":
    main()
