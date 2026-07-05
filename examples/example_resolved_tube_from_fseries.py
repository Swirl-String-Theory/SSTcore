#!/usr/bin/env python3
"""Analyze resolved-tube metrics from an SST/Gilbert .fseries file.

Usage:
    python example_resolved_tube_from_fseries.py path/to/knot.3_1.fseries
"""
from __future__ import annotations

import sys

try:
    import SSTcore as sst
except ImportError:
    import sstcore as sst


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 0

    path = argv[1]
    metrics = sst.resolved_tube_metrics_from_fseries(path, nsamples=2048, skip=4)
    print(f"path: {path}")
    print(f"length: {metrics.length:.9g}")
    print(f"thickness_rad/reach: {metrics.thickness_rad:.9g}")
    print(f"minrad: {metrics.minrad:.9g}")
    print(f"min_dcsd: {metrics.min_dcsd:.9g}")
    print(f"ropelength_rad: {metrics.ropelength_rad:.9g}")
    print(f"ropelength_diam: {metrics.ropelength_diam:.9g}")
    print(f"struts: {len(metrics.struts)}")
    print(f"kinks: {len(metrics.kinks)}")
    print(f"nontrivial lower-bound guard: {metrics.lower_bound_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
