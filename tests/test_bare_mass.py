"""Bare-mass M0(T) helpers (Canon v0.8.26)."""
from __future__ import annotations

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_trefoil_bare_mass_ratio():
    L_tot = 16.3716
    ratio = sst.ValueOriginAPI.bare_mass_ratio_from_dimensionless_length(L_tot)
    assert ratio == pytest.approx(4.0929, rel=1e-6)


def test_bare_mass_scales_with_me():
    m_e = sst.SSTCanonicalConstants.electron_mass()
    M0 = sst.ValueOriginAPI.bare_mass_from_dimensionless_length(16.3716, m_e)
    assert M0 == pytest.approx(4.0929 * m_e, rel=1e-6)
