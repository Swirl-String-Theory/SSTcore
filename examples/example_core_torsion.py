"""Smoke example for core_torsion + link_field_gate (Canon v0.8.24+)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    from SSTcore import CoreTorsionAPI, LinkFieldGateAPI
except ImportError:
    from sstcore import CoreTorsionAPI, LinkFieldGateAPI

canon = CoreTorsionAPI.torsion_inertial_mass(2.0, 3.0, 1.0)
print("torsion_inertial_mass:", canon.ok, canon.mass, canon.convention)

legacy = CoreTorsionAPI.torsion_inertial_mass_legacy_factor2(2.0, 3.0, 1.0)
print("legacy_factor2:", legacy.ok, legacy.mass, legacy.convention)

M = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
aniso = CoreTorsionAPI.anisotropy_residuals(M, E0=1.0, c_T=1.0)
print("anisotropy_residuals:", aniso.ok, aniso.chi_hat, aniso.delta_aniso, aniso.epistemic_status)

gate = LinkFieldGateAPI.evaluate(1.0, 2.0, 3.0, phase_residual=0.0)
print("link_field_gate:", gate.passed, gate.failure, gate.epistemic_status)
print("failure_name:", LinkFieldGateAPI.failure_name(gate.failure))
