"""KAM stage-1 diagnostics (Canon v0.8.25)."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_stage1_pass_nonresonant():
    # Incommensurate-ish frequencies and non-degenerate Hessian.
    r = sst.KAMDiagnosticsAPI.stage1(
        sst.KAMSector.S,
        frequencies=[1.0, math.sqrt(2.0)],
        hessian_row_major=[2.0, 0.0, 0.0, 3.0],
        diophantine_tau=1e-4,
    )
    assert r.status == sst.CertificateStatus.Pass
    assert r.achieved_stage == sst.KAMStage.KAM1
    assert r.hessian_determinant == pytest.approx(6.0)


def test_stage1_fail_resonant():
    r = sst.KAMDiagnosticsAPI.stage1(
        sst.KAMSector.T,
        frequencies=[1.0, 2.0],
        hessian_row_major=[1.0, 0.0, 0.0, 1.0],
        diophantine_tau=1e-3,
    )
    # k=(2,-1) => detuning 0
    assert r.status == sst.CertificateStatus.Fail
    assert r.minimum_detuning == pytest.approx(0.0)


def test_golden_ratio_null_test_only():
    phi = 0.5 * (1.0 + math.sqrt(5.0))
    assert sst.KAMDiagnosticsAPI.golden_ratio_null_test(phi)
    assert not sst.KAMDiagnosticsAPI.golden_ratio_null_test(1.5)


def test_indeterminate_bad_shape():
    r = sst.KAMDiagnosticsAPI.stage1(sst.KAMSector.S, [1.0], [1.0, 2.0])
    assert r.status == sst.CertificateStatus.Indeterminate
