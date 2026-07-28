"""Pipeline provenance chain tests (Canon v0.8.23)."""
from __future__ import annotations

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def _base(**kwargs):
    r = sst.ProvenanceRecord()
    r.tool_name = "tool"
    r.tool_version = "1"
    r.input_sha256 = "in"
    r.output_sha256 = "out"
    r.parameter_sha256 = "par"
    r.coordinate_convention = "xyz"
    r.scale_convention = "R=1"
    r.timestamp_utc = "2026-01-01T00:00:00Z"
    for k, v in kwargs.items():
        setattr(r, k, v)
    return r


def test_empty_chain_unknown():
    assert sst.PipelineProvenanceAPI.evaluate_chain([]) == sst.PipelineCertificationStatus.Unknown


def test_incomplete_record_unknown():
    r = sst.ProvenanceRecord()
    r.stage = sst.PipelineStage.KnotPlot
    assert sst.PipelineProvenanceAPI.evaluate_chain([r]) == sst.PipelineCertificationStatus.Unknown


def test_valid_chain_certified():
    a = _base(stage=sst.PipelineStage.KnotPlot, input_sha256="a0", output_sha256="a1", parent_record_sha256="")
    b = _base(
        stage=sst.PipelineStage.Ridgerunner,
        input_sha256="a1",
        output_sha256="a2",
        parent_record_sha256=sst.PipelineProvenanceAPI.record_fingerprint(a),
    )
    c = _base(
        stage=sst.PipelineStage.SSTcore,
        input_sha256="a2",
        output_sha256="a3",
        parent_record_sha256=sst.PipelineProvenanceAPI.record_fingerprint(b),
    )
    assert sst.PipelineProvenanceAPI.evaluate_chain([a, b, c]) == sst.PipelineCertificationStatus.Certified


def test_tampered_parent_is_candidate():
    a = _base(stage=sst.PipelineStage.KnotPlot, input_sha256="a0", output_sha256="a1", parent_record_sha256="")
    b = _base(
        stage=sst.PipelineStage.SSTcore,
        input_sha256="a1",
        output_sha256="a2",
        parent_record_sha256="tampered",
    )
    assert sst.PipelineProvenanceAPI.evaluate_chain([a, b]) == sst.PipelineCertificationStatus.Candidate


def test_fingerprint_deterministic():
    a = _base(stage=sst.PipelineStage.KnotPlot)
    assert sst.PipelineProvenanceAPI.record_fingerprint(a) == sst.PipelineProvenanceAPI.record_fingerprint(a)
