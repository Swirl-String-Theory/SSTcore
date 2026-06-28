"""Shared scale-role definitions for Route-B BEM.

This module is informational.  It deliberately does not change numerical BEM
results unless imported explicitly by future scans.

Default convention:
    r_c == R_horn, the horn-torus / return-flow circulation radius.
    a_tube = r_c / chi_h, the local ideal-tube radius.
    L_cert remains the dimensionless certified ropelength coordinate.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BEMScaleRoles:
    """Scale-role record for physical reconstruction."""

    R_horn: float
    chi_h: float = 1.0

    @property
    def a_tube(self) -> float:
        return self.R_horn / self.chi_h

    def physical_length(self, L_cert: float) -> float:
        return 2.0 * self.a_tube * L_cert

    def certified_normalizer(self, M_max: float, L_cert: float) -> float:
        return M_max * L_cert**2

    def horn_effective_normalizer(self, M_max: float, L_cert: float) -> float:
        return M_max * (L_cert / self.chi_h)**2
