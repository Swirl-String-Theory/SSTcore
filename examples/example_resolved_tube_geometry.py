#!/usr/bin/env python3
"""Resolved-tube geometry example.

Covers the lightweight Rawdon/Cantarella API: length, MinRad, dcsd candidates,
thickness/reach, radius/diameter ropelength conventions, and contact diagnostics.
"""
from __future__ import annotations

import math

try:
    import SSTcore as sst
except ImportError:
    import sstcore as sst


def regular_polygon(n: int = 64, radius: float = 1.0):
    return [
        [radius * math.cos(2.0 * math.pi * i / n),
         radius * math.sin(2.0 * math.pi * i / n),
         0.0]
        for i in range(n)
    ]


def main() -> None:
    square = [
        [1.0, 1.0, 0.0],
        [-1.0, 1.0, 0.0],
        [-1.0, -1.0, 0.0],
        [1.0, -1.0, 0.0],
    ]

    print("=== ResolvedTubeGeometry: square sanity case ===")
    print("length:", sst.ResolvedTubeGeometry.length(square))
    print("edge mean:", sst.ResolvedTubeGeometry.edge_length_mean(square))
    print("edge rel std:", sst.ResolvedTubeGeometry.edge_length_relative_std(square))
    print("turning angle v0:", sst.ResolvedTubeGeometry.turning_angle(square[-1], square[0], square[1]))
    print("minrad v0:", sst.ResolvedTubeGeometry.minrad_at_vertex(square, 0))
    print("global minrad:", sst.ResolvedTubeGeometry.global_minrad(square))
    print("segment distance:", sst.ResolvedTubeGeometry.segment_segment_distance(
        [0, 0, 0], [1, 0, 0], [0, 2, 0], [1, 2, 0]
    ))

    candidates = sst.ResolvedTubeGeometry.dcsd_candidates(square, skip_neighbors=1, distance_tol=1e-9)
    print("dcsd candidates:", len(candidates))

    metrics = sst.ResolvedTubeGeometry.analyze(square, skip_neighbors=1, contact_tol=1e-9, equilateral_tol=1e-12)
    print("thickness_rad = reach_rad:", metrics.thickness_rad)
    print("ropelength_rad:", metrics.ropelength_rad)
    print("ropelength_diam:", metrics.ropelength_diam)
    print("struts/kinks:", len(metrics.struts), len(metrics.kinks))

    matrix = sst.ContactStressMap.build_rigidity_matrix(square, metrics)
    grad = sst.ResolvedTubeGeometry.length_gradient_flat(square)
    nnls = sst.ContactStressMap.solve_nonnegative_least_squares(matrix, grad)
    diag = sst.ContactStressMap.diagnose_length_criticality(square, metrics, solve_nnls=True)
    print("rigidity rows/cols:", matrix.row_count, matrix.column_count)
    print("NNLS converged / relative residual:", nnls.converged, nnls.relative_residual)
    print("KKT contact residual:", diag.contact_residual)
    print("contact entropy:", diag.contact_entropy)
    print("strut/kink weights:", diag.strut_weight_sum, diag.kink_weight_sum)

    print("\n=== Convention guards ===")
    lower = sst.ResolvedTubeGeometry.nontrivial_knot_lower_bound_rad()
    print("nontrivial lower bound, radius convention:", lower)
    print("trefoil diameter 16.371637 -> radius:",
          sst.ResolvedTubeGeometry.diameter_to_radius_ropelength(16.371637))
    print("trefoil radius 32.743274 -> diameter:",
          sst.ResolvedTubeGeometry.radius_to_diameter_ropelength(32.743274))

    print("\n=== Smooth unknot polygon ===")
    circle = regular_polygon(96)
    cm = sst.resolved_tube_analyze(circle, skip_neighbors=8, contact_tol=1e-3, equilateral_tol=1e-3)
    print("circle ropelength_rad ~ 2*pi:", cm.ropelength_rad)
    print("circle lower_bound_ok is false because the nontrivial-knot bound does not apply to the unknot:",
          cm.lower_bound_ok)


if __name__ == "__main__":
    main()
