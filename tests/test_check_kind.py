"""CheckKind vocabulary tests (Canon v0.8.27)."""
from __future__ import annotations

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_export_roundtrip():
    for kind in [
        sst.CheckKind.AlgebraicIdentity,
        sst.CheckKind.SyntheticDiagnostic,
        sst.CheckKind.OpenResearchGate,
        sst.CheckKind.ConditionalBridge,
    ]:
        s = sst.check_kind_export_string(kind)
        assert sst.check_kind_from_export_string(s) == kind


def test_retrofit_qss_string():
    assert sst.check_kind_from_export_string("SYNTHETIC_DIAGNOSTIC") == sst.CheckKind.SyntheticDiagnostic
    assert sst.check_kind_from_export_string("OPEN_RESEARCH_GATE") == sst.CheckKind.OpenResearchGate
