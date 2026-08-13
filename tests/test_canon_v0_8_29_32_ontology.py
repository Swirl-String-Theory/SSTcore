"""Canon 0.8.29–0.8.32 ontology / scaling tests."""
from __future__ import annotations

import math

import pytest

sst = pytest.importorskip("SSTcore")


def test_rho_f_provenance_guards():
    assert sst.ValueOriginAPI.rho_f_is_two_sigfig_calibration(7.0e-7)
    assert sst.ValueOriginAPI.rho_eff_rescale_preserves_calibrated_primitives(
        1.0, 2.0, 3.0, 4.0, 1.0, 2.0, 3.0, 4.0
    )
    assert not sst.ValueOriginAPI.rho_eff_rescale_preserves_calibrated_primitives(
        1.0, 2.0, 3.0, 4.0, 1.1, 2.0, 3.0, 4.0
    )
    assert sst.ValueOriginAPI.reject_vam_line_inertia_as_rho_f_derivation(1e-11, 7e-7)


def test_density_ontology():
    assert sst.DensityOntologyAPI.rho_f_aliases_rho_eff()
    assert sst.DensityOntologyAPI.symbol_unit(sst.DensitySymbol.JOmega) == "kg/m"
    ok = sst.DensityOntologyAPI.validate_energy_density_form(
        sst.EnergyDensityForm.HalfJOmegaOmegaSquared
    )
    bad = sst.DensityOntologyAPI.validate_energy_density_form(
        sst.EnergyDensityForm.HalfRhoFOmegaSquaredNoLength
    )
    assert ok.allowed and not bad.allowed


def test_rotor_participation_numerics():
    r = sst.RotorParticipationAPI.evaluate()
    assert math.isclose(r.j_omega_rot, 2.4282114e-11, rel_tol=1e-4)
    assert math.isclose(r.phi_dyn_ref, 5.7229e-26, rel_tol=1e-3)
    assert math.isclose(r.ell_rho_eq_ref, 5.8897e-3, rel_tol=1e-3)
    assert r.c_omega == sst.SSTCanonicalConstants.values().v_swirl


def test_scaling_audit_rho_ref_legacy():
    assert sst.ScalingAuditAPI.rho_ref_legacy() == 7.0e-7
    m = sst.ScalingAuditAPI.classify_symbol("rho_ref")
    assert m.in_p_ref and m.legacy_reference
    assert sst.ScalingAuditAPI.classify_symbol("v_swirl").in_p_cal
    assert sst.ScalingAuditAPI.classify_observable("acceleration") == sst.ScalingClass.A
    assert sst.ScalingAuditAPI.classify_observable("absolute_mass") == sst.ScalingClass.C
    assert sst.ScalingAuditAPI.classify_observable("bogus") == sst.ScalingClass.X
