"""Smoke example for CheckKind + evidence_report (Canon v0.8.27+)."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    import SSTcore as sst
    from SSTcore import (
        CheckKind,
        CheckResult,
        EvidenceReportAPI,
        EvidenceReportMeta,
        check_kind_export_string,
        check_kind_from_export_string,
    )
except ImportError:
    import sstcore as sst
    from sstcore import (
        CheckKind,
        CheckResult,
        EvidenceReportAPI,
        EvidenceReportMeta,
        check_kind_export_string,
        check_kind_from_export_string,
    )

print("export:", check_kind_export_string(CheckKind.SyntheticDiagnostic))
print("from_string:", check_kind_from_export_string("OPEN_RESEARCH_GATE"))

meta = EvidenceReportMeta()
meta.sstcore_version = sst.__version__
meta.canon_version = getattr(sst, "CANON_VERSION", sst.__version__)
meta.git_commit = "example"
meta.numeric_profile = "deterministic"
meta.compiler = "msvc"
meta.platform = "win32"

c = CheckResult()
c.name = "demo_check"
c.passed = True
c.kind = CheckKind.AlgebraicIdentity
c.residual = 0.0
c.tolerance = 1e-12
c.supports_empirical_claim = False
c.message = "example"

js = EvidenceReportAPI.build_report_json(meta, [c])
data = json.loads(js)
print("build_report_json checks[0].kind =", data["checks"][0]["kind"])
print("versions:", data["sstcore_version"], data["canon_version"])
