"""Canonical snapshot / ValueOrigin tests (Canon v0.8.26)."""
from __future__ import annotations

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_value_origin_enum_and_make():
    v = sst.ValueOriginAPI.make_canonical_value(
        "F_SWIRL_MAX", 29.053507, sst.ValueOrigin.CanonicalSnapshot, significant_figures=-1
    )
    assert v.origin == sst.ValueOrigin.CanonicalSnapshot
    assert v.name == "F_SWIRL_MAX"


def test_rho_f_two_sigfig():
    # 7.0e-7 already 1–2 sig; derived should round to 6.8e-7
    assert sst.ValueOriginAPI.rho_f_two_sigfig(6.8398588e-07) == pytest.approx(6.8e-7)
    assert sst.ValueOriginAPI.rho_f_two_sigfig(7.0e-7) == pytest.approx(7.0e-7)


def test_rho_horn_public():
    vals = sst.SSTCanonicalConstants.values()
    assert vals.rho_horn == pytest.approx(vals.rho_core)
