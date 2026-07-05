"""Export a resolved-tube sparse rigidity matrix to SciPy / Matrix Market.

The C++ side writes a dependency-free Matrix Market file.  If SciPy is
available, this example also solves the non-negative sparse least-squares
problem with scipy.optimize.lsq_linear as a high-resolution external backend.
"""
from __future__ import annotations

from pathlib import Path
import tempfile

try:
    import SSTcore as sst
except ImportError:
    import sstcore as sst


def torus_knot_points(p: int = 3, q: int = 2, n: int = 240):
    import math

    pts = []
    for k in range(n):
        t = 2.0 * math.pi * k / n
        R = 2.2 + 0.7 * math.cos(q * t)
        pts.append([R * math.cos(p * t), R * math.sin(p * t), 0.7 * math.sin(q * t)])
    return pts


def main() -> None:
    pts = torus_knot_points()
    tube = sst.ResolvedTubeGeometry.analyze(pts, skip_neighbors=3, contact_tol=5e-3)
    sparse = sst.ContactStressMap.build_sparse_rigidity_matrix(pts, tube)
    grad_len = sst.ResolvedTubeGeometry.length_gradient_flat(pts)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        A_path = tmp / "sst_resolved_tube_A.mtx"
        b_path = tmp / "sst_resolved_tube_b.mtx"
        b_csv = tmp / "sst_resolved_tube_b.csv"
        sst.ContactStressMap.write_sparse_matrix_market(sparse, str(A_path))
        sst.ContactStressMap.write_vector_market(grad_len, str(b_path))
        sst.ContactStressMap.write_vector_csv(grad_len, str(b_csv))
        print(f"wrote Matrix Market A: {A_path}")
        print(f"wrote Matrix Market b: {b_path}")
        print(f"wrote CSV b:           {b_csv}")

        try:
            import scipy.io
            import scipy.optimize
        except ImportError:
            print("SciPy not installed; Matrix Market export is still complete.")
            return

        A = scipy.io.mmread(A_path).tocsc()
        b = grad_len
        sol = scipy.optimize.lsq_linear(A, b, bounds=(0.0, float("inf")), method="trf", lsmr_tol="auto")
        rel = float(__import__("numpy").linalg.norm(A @ sol.x - b) / max(__import__("numpy").linalg.norm(b), 1e-15))
        print("SciPy sparse bounded least-squares")
        print(f"success           = {sol.success}")
        print(f"active multipliers= {(sol.x > 1e-10).sum()}")
        print(f"relative residual = {rel:.3e}")


if __name__ == "__main__":
    main()
