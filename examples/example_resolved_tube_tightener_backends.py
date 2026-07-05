"""Compare resolved-tube tightening backend choices.

The same initial polygon is tightened with the sparse active-set path and with the
older coordinate-descent fallback.  For high-resolution knots, prefer the sparse
active-set path or export the rigidity system to SciPy/Eigen.
"""
from __future__ import annotations

import math

try:
    import SSTcore as sst
except ImportError:
    import sstcore as sst


def wavy_circle(n: int = 40):
    return [
        [(1.0 + 0.12 * math.cos(5 * 2.0 * math.pi * k / n)) * math.cos(2.0 * math.pi * k / n),
         (1.0 + 0.08 * math.sin(3 * 2.0 * math.pi * k / n)) * math.sin(2.0 * math.pi * k / n),
         0.03 * math.sin(4 * 2.0 * math.pi * k / n)]
        for k in range(n)
    ]


def run(label: str, active_set: bool, sparse: bool):
    opts = sst.TighteningOptions()
    opts.max_steps = 12
    opts.max_step_size = 2e-3
    opts.contact_tol = 5e-2
    opts.equilateral_tol = 1.0
    opts.correction_strategy = "newton"
    opts.use_active_set_solver = active_set
    opts.use_sparse_solver = sparse
    result = sst.ResolvedTubeTightener.tighten(wavy_circle(), opts)
    print(
        f"{label:28s} steps={len(result.steps):2d} reason={result.reason:24s} "
        f"rop_rad={result.metrics.ropelength_rad:.6f} "
        f"thick={result.metrics.thickness_rad:.6f}"
    )


run("sparse active-set", active_set=True, sparse=True)
run("sparse coordinate", active_set=False, sparse=True)
run("dense active-set", active_set=True, sparse=False)
