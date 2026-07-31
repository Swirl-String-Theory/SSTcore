"""Smoke example for value_origin / Fmax / M0(T) helpers (Canon v0.8.26+)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    from SSTcore import ValueOriginAPI, ValueOrigin, SSTCanonicalConstants
except ImportError:
    from sstcore import ValueOriginAPI, ValueOrigin, SSTCanonicalConstants

print("fmax_snapshot:", ValueOriginAPI.fmax_snapshot())
cmp = ValueOriginAPI.compare_fmax_snapshot_to_recomputed()
print("compare_fmax:", cmp.snapshot, cmp.recomputed, cmp.residual, cmp.snapshot_unchanged)

hbar = SSTCanonicalConstants.hbar()
c = SSTCanonicalConstants.speed_of_light()
alpha = SSTCanonicalConstants.alpha()
R = SSTCanonicalConstants.values().R_infty_sst
print("fmax_rydberg_16pi2:", ValueOriginAPI.fmax_rydberg_16pi2(hbar, R, c, alpha))

print("bare_mass_ratio:", ValueOriginAPI.bare_mass_ratio_from_dimensionless_length(16.3716))
m_e = SSTCanonicalConstants.electron_mass()
print("bare_mass:", ValueOriginAPI.bare_mass_from_dimensionless_length(16.3716, m_e))
print("rho_f_two_sigfig:", ValueOriginAPI.rho_f_two_sigfig(6.8398588e-07))

cv = ValueOriginAPI.make_canonical_value("F_SWIRL_MAX", 29.053507, ValueOrigin.CanonicalSnapshot)
print("make_canonical_value:", cv.name, cv.origin, cv.value)
