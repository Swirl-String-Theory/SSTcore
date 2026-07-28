"""Link-field phase-gate scaffolding (Canon v0.8.24)."""
from __future__ import annotations

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_pass_gate():
    r = sst.LinkFieldGateAPI.evaluate(1.0, 2.0, 3.0, phase_residual=0.0)
    assert r.passed
    assert r.failure == sst.LinkGateFailure.None_
    assert r.epistemic_status == "OPEN_RESEARCH_GATE"


def test_failure_classes():
    assert sst.LinkFieldGateAPI.evaluate(0.0, 1.0, 1.0, 0.0).failure == sst.LinkGateFailure.E
    assert sst.LinkFieldGateAPI.evaluate(1.0, 0.0, 1.0, 0.0).failure == sst.LinkGateFailure.T
    assert sst.LinkFieldGateAPI.evaluate(1.0, 1.0, 0.0, 0.0).failure == sst.LinkGateFailure.N
    assert sst.LinkFieldGateAPI.evaluate(1.0, 1.0, 1.0, 1.0, tol=1e-3).failure == sst.LinkGateFailure.M
