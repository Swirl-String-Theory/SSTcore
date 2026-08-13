"""Smoke example: density ontology + rotor + scaling (Canon 0.8.30–0.8.32)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))
try:
    from SSTcore import DensityOntologyAPI, EnergyDensityForm, RotorParticipationAPI, ScalingAuditAPI
except ImportError:
    from sstcore import DensityOntologyAPI, EnergyDensityForm, RotorParticipationAPI, ScalingAuditAPI

print("forbidden form allowed?", DensityOntologyAPI.validate_energy_density_form(
    EnergyDensityForm.HalfRhoFOmegaSquaredNoLength).allowed)
r = RotorParticipationAPI.evaluate()
print("j_omega_rot", r.j_omega_rot, "phi_dyn", r.phi_dyn_ref, "ell", r.ell_rho_eq_ref)
print("rho_ref", ScalingAuditAPI.rho_ref_legacy(), "class A", ScalingAuditAPI.classify_observable("acceleration"))
