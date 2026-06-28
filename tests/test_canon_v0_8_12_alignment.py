"""Canon v0.8.12 alignment regression tests (patches 0001–0003)."""
from __future__ import annotations

import pytest

sst = pytest.importorskip("SSTcore")
pytest.importorskip("SSTcore._native")

ChronosKelvinTransport = sst.ChronosKelvinTransport
SSTCanonicalConstants = sst.SSTCanonicalConstants

ALPHA_CODATA2018 = 7.2973525693e-3


def test_alpha_codata2018() -> None:
    assert SSTCanonicalConstants.alpha() == pytest.approx(ALPHA_CODATA2018, rel=0, abs=1e-12)


def test_vorticity_is_twice_omega() -> None:
    s_t, r_c = 0.42, 1.40897017e-15
    omega = ChronosKelvinTransport.omega_from_swirl_clock(s_t, r_c)
    vorticity = ChronosKelvinTransport.vorticity_from_swirl_clock(s_t, r_c)
    assert vorticity == pytest.approx(2.0 * omega, rel=0, abs=1e-30)


def test_rho_horn_alias() -> None:
    vals = SSTCanonicalConstants.values()
    assert vals.rho_horn == pytest.approx(vals.rho_core, rel=0, abs=0.0)


def test_horn_envelope_density_alias() -> None:
    m_e = SSTCanonicalConstants.electron_mass()
    c = SSTCanonicalConstants.speed_of_light()
    v_swirl = SSTCanonicalConstants.values().v_swirl
    r_c = SSTCanonicalConstants.values().r_c
    horn = SSTCanonicalConstants.horn_envelope_density(m_e, c, v_swirl, r_c)
    core = SSTCanonicalConstants.core_density_closure(m_e, c, v_swirl, r_c)
    assert horn == pytest.approx(core, rel=0, abs=0.0)
