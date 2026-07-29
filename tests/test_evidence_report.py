"""Evidence report writer tests (Canon v0.8.27)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_build_and_write_roundtrip(tmp_path: Path):
    meta = sst.EvidenceReportMeta()
    meta.sstcore_version = sst.__version__
    meta.canon_version = sst.CANON_VERSION
    meta.git_commit = "deadbeef"
    meta.numeric_profile = "deterministic"
    meta.compiler = "msvc"
    meta.platform = "win32"

    c = sst.CheckResult()
    c.name = "bare_mass_ratio"
    c.passed = True
    c.kind = sst.CheckKind.AlgebraicIdentity
    c.residual = 0.0
    c.tolerance = 1e-12
    c.supports_empirical_claim = False
    c.message = "L_tot/4 identity"

    js = sst.EvidenceReportAPI.build_report_json(meta, [c])
    data = json.loads(js)
    assert data["schema_version"] == "1.0"
    assert data["sstcore_version"] == data["canon_version"] == sst.__version__
    assert data["checks"][0]["kind"] == "ALGEBRAIC_IDENTITY"

    path = tmp_path / "evidence.json"
    assert sst.EvidenceReportAPI.write_evidence_report(str(path), meta, [c])
    assert path.read_text(encoding="utf-8") == js


def test_empty_path_fails():
    meta = sst.EvidenceReportMeta()
    assert not sst.EvidenceReportAPI.write_evidence_report("", meta, [])


def test_nonfinite_residual_is_null_json():
    meta = sst.EvidenceReportMeta()
    c = sst.CheckResult()
    c.name = "nan_check"
    c.passed = False
    c.kind = sst.CheckKind.AlgebraicIdentity
    c.residual = float("nan")
    c.tolerance = float("inf")
    c.message = "ctrl\x01"
    js = sst.EvidenceReportAPI.build_report_json(meta, [c])
    data = json.loads(js)
    assert data["checks"][0]["residual"] is None
    assert data["checks"][0]["tolerance"] is None
