#!/usr/bin/env python3
"""Tests for binding/examples audit tooling (canonical demos under examples/)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
EXAMPLES = ROOT / "examples"

# Import map from audit script
sys.path.insert(0, str(SCRIPTS))
from audit_binding_examples import (  # noqa: E402
    BINDING_MODULES,
    MODULE_TO_EXAMPLES,
    missing_modules,
)


@pytest.fixture(scope="module")
def audit_report(tmp_path_factory):
    out = tmp_path_factory.mktemp("audit") / "binding_examples_audit"
    cmd = [
        sys.executable,
        str(SCRIPTS / "audit_binding_examples.py"),
        "--out-dir",
        str(out),
    ]
    completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr or completed.stdout
    return json.loads((out / "audit.json").read_text(encoding="utf-8"))


def test_all_binding_modules_have_examples_demo():
    missing = missing_modules(EXAMPLES)
    assert not missing, f"missing examples/ demos for modules: {missing}"
    # Every mapped primary file must exist (or an alternate in the tuple)
    for mod in BINDING_MODULES:
        names = MODULE_TO_EXAMPLES[mod]
        assert any((EXAMPLES / n).is_file() for n in names), f"{mod}: none of {names} exist"


def test_audit_generates_summary(audit_report):
    assert audit_report["summary"]["binding_modules"] == 30
    assert audit_report["summary"]["missing_example_files"] == 0
    assert audit_report["summary"]["example_files"] == 30
    # Compat aliases
    assert audit_report["summary"]["src_example_files"] == 30
    assert audit_report["summary"]["missing_src_example_files"] == 0


def test_example_bootstrap_importable():
    sys.path.insert(0, str(EXAMPLES))
    import _example_bootstrap as boot  # noqa: WPS433

    sst, info = boot.import_sstcore()
    pytest.importorskip("SSTcore", exc_type=ImportError)
    assert info["import_ok"] is True
    assert sst is not None
