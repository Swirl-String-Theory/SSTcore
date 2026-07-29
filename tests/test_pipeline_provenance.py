"""Pipeline provenance chain tests (Canon v0.8.23 + audit B-004)."""
from __future__ import annotations

import hashlib

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def _h(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _base(**kwargs):
    r = sst.ProvenanceRecord()
    r.tool_name = "tool"
    r.tool_version = "1"
    r.input_sha256 = _h("in")
    r.output_sha256 = _h("out")
    r.parameter_sha256 = _h("par")
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
    a = _base(stage=sst.PipelineStage.KnotPlot, input_sha256=_h("a0"), output_sha256=_h("a1"), parent_record_sha256="")
    b = _base(
        stage=sst.PipelineStage.Ridgerunner,
        input_sha256=_h("a1"),
        output_sha256=_h("a2"),
        parent_record_sha256=sst.PipelineProvenanceAPI.record_fingerprint(a),
    )
    c = _base(
        stage=sst.PipelineStage.SSTcore,
        input_sha256=_h("a2"),
        output_sha256=_h("a3"),
        parent_record_sha256=sst.PipelineProvenanceAPI.record_fingerprint(b),
    )
    assert sst.PipelineProvenanceAPI.evaluate_chain([a, b, c]) == sst.PipelineCertificationStatus.Certified


def test_tampered_parent_is_candidate():
    a = _base(stage=sst.PipelineStage.KnotPlot, input_sha256=_h("a0"), output_sha256=_h("a1"), parent_record_sha256="")
    b = _base(
        stage=sst.PipelineStage.SSTcore,
        input_sha256=_h("a1"),
        output_sha256=_h("a2"),
        parent_record_sha256=_h("tampered"),
    )
    assert sst.PipelineProvenanceAPI.evaluate_chain([a, b]) == sst.PipelineCertificationStatus.Candidate


def test_non_sha256_fields_are_candidate_not_certified():
    a = _base(stage=sst.PipelineStage.KnotPlot, input_sha256="short", output_sha256="also-short", parent_record_sha256="")
    b = _base(
        stage=sst.PipelineStage.SSTcore,
        input_sha256="also-short",
        output_sha256=_h("a2"),
        parent_record_sha256="nope",
    )
    assert sst.PipelineProvenanceAPI.evaluate_chain([a, b]) == sst.PipelineCertificationStatus.Candidate


def test_fingerprint_is_real_sha256_hex():
    a = _base(stage=sst.PipelineStage.KnotPlot)
    fp = sst.PipelineProvenanceAPI.record_fingerprint(a)
    assert len(fp) == 64
    assert all(c in "0123456789abcdef" for c in fp)
    assert fp == sst.PipelineProvenanceAPI.record_fingerprint(a)


def test_fingerprint_deterministic():
    a = _base(stage=sst.PipelineStage.KnotPlot)
    assert sst.PipelineProvenanceAPI.record_fingerprint(a) == sst.PipelineProvenanceAPI.record_fingerprint(a)
