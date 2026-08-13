"""Smoke example: ideal regime + transverse projector + Maxwell stack."""
from __future__ import annotations
import math, os, sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))
try:
    from SSTcore import (
        IdealKnotRegimeAPI, TransverseProjectorAPI, SpectroResponseAPI,
        MaxwellKineticAPI, MechanicalFalsifierAPI, SwirlTonicAPI, WorldsheetGuardsAPI,
    )
except ImportError:
    from sstcore import (
        IdealKnotRegimeAPI, TransverseProjectorAPI, SpectroResponseAPI,
        MaxwellKineticAPI, MechanicalFalsifierAPI, SwirlTonicAPI, WorldsheetGuardsAPI,
    )

print("worldsheet", WorldsheetGuardsAPI.evaluate(3, 1.0, 1e-8, False, False).passed)
print("regime", IdealKnotRegimeAPI.evaluate(1.0, 1.0, 1.0, 1.0, 0.0, 0.0).regime)
print("8pi/3", TransverseProjectorAPI.projector_sphere_integral())
print("R0", TransverseProjectorAPI.leading_response_R0(TransverseProjectorAPI.high_res_ld()))
print("spectro", SpectroResponseAPI.evaluate(2.0, 1.0, 1.0, [1.0], [0.1], False).delta_nu)
print("three_gate", MaxwellKineticAPI.three_gate_condition(1.0, 2.0, 1.0, 0.1, 1.0))
print("falsifier", MechanicalFalsifierAPI.evaluate(2.0, 1.0, 7e-7, 1.0).C_blind)
print("tonic", SwirlTonicAPI.evaluate([1.0],[0.0],[0.0],[1.0],[0.0],[0.0], 1.0, False).holonomy)
