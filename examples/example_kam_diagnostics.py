"""Smoke example for sst_kam_diagnostics (Canon v0.8.25+)."""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    from SSTcore import KAMDiagnosticsAPI, KAMSector
except ImportError:
    from sstcore import KAMDiagnosticsAPI, KAMSector

r = KAMDiagnosticsAPI.stage1(
    KAMSector.S,
    frequencies=[1.0, math.sqrt(2.0)],
    hessian_row_major=[2.0, 0.0, 0.0, 3.0],
    diophantine_tau=1e-4,
)
print(
    "stage1:",
    r.status,
    r.achieved_stage,
    "det=",
    r.hessian_determinant,
    KAMDiagnosticsAPI.stage_name(r.achieved_stage),
)

phi = 0.5 * (1.0 + math.sqrt(5.0))
print("golden_ratio_null_test:", KAMDiagnosticsAPI.golden_ratio_null_test(phi), KAMDiagnosticsAPI.golden_ratio_null_test(1.5))
print("sector_name:", KAMDiagnosticsAPI.sector_name(KAMSector.S))
