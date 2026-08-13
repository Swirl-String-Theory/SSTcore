"""Smoke example for sst_action_phase mass-shell clock (Canon v0.8.28+)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    from SSTcore import ActionPhaseAPI
except ImportError:
    from sstcore import ActionPhaseAPI

P, E0, c, Omega0 = 3.0, 4.0, 1.0, 2.0
print("mass_shell_hamiltonian:", ActionPhaseAPI.mass_shell_hamiltonian(P, E0, c))
print("velocity_from_mass_shell:", ActionPhaseAPI.velocity_from_mass_shell(P, E0, c))
print("gamma_from_mass_shell:", ActionPhaseAPI.gamma_from_mass_shell(P, E0, c))
print("proper_time_rate:", ActionPhaseAPI.proper_time_rate(P, E0, c))
print(
    "internal_phase_rate_at_fixed_momentum:",
    ActionPhaseAPI.internal_phase_rate_at_fixed_momentum(P, E0, c, Omega0),
)
r = ActionPhaseAPI.action_phase_residuals(P, E0, c, Omega0)
print("action_phase_residuals ok=", r.ok, "H_res=", r.hamiltonian_consistency)
