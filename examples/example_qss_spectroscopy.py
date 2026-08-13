"""Smoke example for qss_spectroscopy bindings (Canon v0.8.22+)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    from SSTcore import QSSSpectroscopyAPI
except ImportError:
    from sstcore import QSSSpectroscopyAPI

eig = QSSSpectroscopyAPI.eigen_2x2([2.0, 0.0, 0.0, 5.0])
print("eigen_2x2:", eig.epistemic_status, "residual=", eig.eigen_residual, eig.eigenvalues)

ps = QSSSpectroscopyAPI.pseudospectrum_diag_2x2(1.0, 2.0, 0.5, 2.5, 5, -0.5, 0.5, 3)
print("pseudospectrum_diag_2x2:", ps.epistemic_status, "max_norm=", ps.max_resolvent_norm, "n=", len(ps.samples))
