"""Resolved-tube active-set NNLS / KKT diagnostic example.

Run after building SSTcore with the resolved_tube_geometry bindings.
This example uses a unit-thickness square because its KKT balance is
small and deterministic enough for a compact smoke test.
"""
from __future__ import annotations

try:
    import SSTcore as sst
except ImportError:
    import sstcore as sst


def main() -> None:
    points = [
        [1.0, 1.0, 0.0],
        [-1.0, 1.0, 0.0],
        [-1.0, -1.0, 0.0],
        [1.0, -1.0, 0.0],
    ]

    tube = sst.ResolvedTubeGeometry.analyze(points, skip_neighbors=1, contact_tol=1e-9)
    grad_len = sst.ResolvedTubeGeometry.length_gradient_flat(points)
    sparse = sst.ContactStressMap.build_sparse_rigidity_matrix(points, tube)

    result = sst.ContactStressMap.solve_nonnegative_least_squares_sparse_active_set(
        sparse, grad_len, max_iterations=1000, tolerance=1e-12
    )

    diagnostics = sst.ContactStressMap.diagnose_length_criticality(
        points,
        tube,
        solve_nnls=True,
        max_iterations=1000,
        tolerance=1e-12,
        use_sparse_solver=True,
        use_active_set_solver=True,
    )

    print("Resolved tube active-set NNLS")
    print(f"length              = {tube.length:.12g}")
    print(f"thickness_rad       = {tube.thickness_rad:.12g}")
    print(f"columns / nnz       = {sparse.column_count} / {sparse.nonzero_count}")
    print(f"algorithm           = {result.algorithm}")
    print(f"iterations          = {result.iterations}")
    print(f"active set size     = {result.active_set_size}")
    print(f"relative residual   = {result.relative_residual:.3e}")
    print(f"KKT contact residual= {diagnostics.contact_residual:.3e}")
    print(f"strut weight sum    = {diagnostics.strut_weight_sum:.12g}")
    print(f"kink weight sum     = {diagnostics.kink_weight_sum:.12g}")


if __name__ == "__main__":
    main()
