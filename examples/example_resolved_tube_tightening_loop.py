"""Projected-gradient resolved-tube tightening demo.

This example uses the lightweight SSTcore tightener added after the resolved-tube
KKT/NNLS modules.  It is not a full ridgerunner clone; it performs conservative
projected-gradient steps, keeps polygonal thickness from dropping, and records a
KKT residual history.
"""
from __future__ import annotations

import math

try:
    import SSTcore as sst
except ImportError:  # local editable builds may use lower-case name
    import sstcore as sst


def ellipse_points(n: int = 48):
    return [
        [1.5 * math.cos(2.0 * math.pi * k / n),
         0.75 * math.sin(2.0 * math.pi * k / n),
         0.04 * math.sin(6.0 * math.pi * k / n)]
        for k in range(n)
    ]


points = ellipse_points()
before = sst.ResolvedTubeGeometry.analyze(points, skip_neighbors=2, contact_tol=5e-2, equilateral_tol=1.0)

opts = sst.TighteningOptions()
opts.max_steps = 25
opts.max_step_size = 2.5e-3
opts.contact_tol = 5e-2
opts.equilateral_tol = 1.0
opts.target_kkt_residual = 1e-4
opts.correction_strategy = "newton"      # try "scale" for SONO-like rescaling
opts.preserve_initial_thickness = True
opts.use_sparse_solver = True
opts.use_active_set_solver = True

result = sst.ResolvedTubeTightener.tighten(points, opts)

after = result.metrics
print("Resolved-tube tightening")
print(f"  reason: {result.reason}")
print(f"  converged: {result.converged}")
print(f"  steps: {len(result.steps)}")
print(f"  ropelength_rad: {before.ropelength_rad:.9f} -> {after.ropelength_rad:.9f}")
print(f"  thickness_rad:  {before.thickness_rad:.9f} -> {after.thickness_rad:.9f}")
print(f"  struts/kinks:   {len(after.struts)} / {len(after.kinks)}")

for step in result.steps[:10]:
    print(
        f"  step {step.step:02d}: alpha={step.alpha:.3e}, "
        f"KKT={step.kkt_residual_before:.3e}, "
        f"Rop={step.ropelength_before:.6f}->{step.ropelength_after:.6f}, "
        f"corrected={step.thickness_corrected}"
    )
