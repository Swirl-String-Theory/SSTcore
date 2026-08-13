"""Core–torsion mass without factor two (Canon v0.8.24)."""
from __future__ import annotations

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_canonical_mass_no_factor_two():
    r = sst.CoreTorsionAPI.torsion_inertial_mass(E0=2.0, I=3.0, c_T=1.0)
    assert r.ok
    assert r.mass == pytest.approx(6.0)
    assert r.convention == "E0*I/c_T^2"


def test_legacy_factor2_is_double():
    canon = sst.CoreTorsionAPI.torsion_inertial_mass(2.0, 3.0, 1.0)
    legacy = sst.CoreTorsionAPI.torsion_inertial_mass_legacy_factor2(2.0, 3.0, 1.0)
    assert legacy.mass == pytest.approx(2.0 * canon.mass)
    assert "legacy" in legacy.convention


def test_invalid_inputs():
    bad = sst.CoreTorsionAPI.torsion_inertial_mass(-1.0, 1.0, 1.0)
    assert not bad.ok


def test_anisotropy_isotropic():
    M = [1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0]
    r = sst.CoreTorsionAPI.anisotropy_residuals(M, E0=1.0, c_T=1.0)
    assert r.ok
    assert r.chi_hat == pytest.approx(1.0)
    assert r.delta_aniso == pytest.approx(0.0)
    assert r.epistemic_status == "OPEN_RESEARCH_GATE"


def test_dimensional_residual_near_zero():
    r = sst.CoreTorsionAPI.torsion_inertial_mass(2.0, 3.0, 1.0)
    assert r.ok
    assert r.dimensional_residual == pytest.approx(0.0)


def test_asymmetric_tensor_rejected():
    M = [1.0, 0.5, 0, 0.1, 1.0, 0, 0, 0, 1.0]
    r = sst.CoreTorsionAPI.anisotropy_residuals(M, E0=1.0, c_T=1.0)
    assert not r.ok
