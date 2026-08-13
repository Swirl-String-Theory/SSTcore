"""Audit R3: spacetime boosts, contact/rank gates, list_bindings classes."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_lorentz_boost_arbitrary_direction_preserves_interval():
    ev = [1.0, 0.5, 0.0, 0.0]
    r = sst.OperationalSpacetimeAPI.lorentz_boost(ev, [0.0, 0.3, 0.0], c=1.0)
    assert math.isfinite(r.gamma)
    assert r.invariant_residual < 1e-12


def test_contact_rejects_negative_pressure():
    r = sst.GeometryCertificateAPI.evaluate_contact_saturation([-0.1, 0.2], 1.0)
    assert r.status == sst.CertificateStatus.Indeterminate


def test_rank9_conditioning_ceiling():
    # Nearly singular: rank may count as 9 with huge conditioning → Indeterminate.
    s = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1e-20]
    r = sst.GeometryCertificateAPI.rank9_from_singular_values(s, tau_rank=1e-30, max_conditioning=1e6)
    assert r.numerical_rank == 9
    assert r.conditioning > 1e6
    assert r.status == sst.CertificateStatus.Indeterminate


def test_list_bindings_reports_classes():
    info = sst.list_bindings()
    assert info["counts"]["classes"] > 0
    assert "ActionPhaseAPI" in info["classes"] or any("API" in c for c in info["classes"])
