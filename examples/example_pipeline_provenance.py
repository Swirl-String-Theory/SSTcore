"""Smoke example for pipeline_provenance bindings (Canon v0.8.23+)."""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    from SSTcore import (
        PipelineProvenanceAPI,
        ProvenanceRecord,
        PipelineStage,
        PipelineCertificationStatus,
    )
except ImportError:
    from sstcore import (
        PipelineProvenanceAPI,
        ProvenanceRecord,
        PipelineStage,
        PipelineCertificationStatus,
    )


def _h(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def base(**kwargs):
    r = ProvenanceRecord()
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


a = base(stage=PipelineStage.KnotPlot, input_sha256=_h("a0"), output_sha256=_h("a1"), parent_record_sha256="")
fp = PipelineProvenanceAPI.record_fingerprint(a)
print("record_fingerprint:", fp)

b = base(
    stage=PipelineStage.SSTcore,
    input_sha256=_h("a1"),
    output_sha256=_h("a2"),
    parent_record_sha256=fp,
)
status = PipelineProvenanceAPI.evaluate_chain([a, b])
print("evaluate_chain:", status)
print("Certified enum:", PipelineCertificationStatus.Certified)
print("stage_name:", PipelineProvenanceAPI.stage_name(PipelineStage.KnotPlot))
