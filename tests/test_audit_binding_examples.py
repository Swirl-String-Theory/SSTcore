#!/usr/bin/env python3
"""Tests for binding/examples audit tooling."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
SRC = ROOT / "src"


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
    assert completed.returncode == 0, completed.stderr
    return json.loads((out / "audit.json").read_text(encoding="utf-8"))


def test_all_binding_modules_have_src_example():
    missing = [
        mod
        for mod in [
            "ab_initio_mass", "atomic_bridge_model", "biot_savart", "canonical_constants",
            "chronos_kelvin_transport", "clock_field_eft", "delay_mode_selector", "field_kernels",
            "field_ops", "fluid_dynamics", "frenet_helicity", "hyperbolic_volume", "knot_dynamics",
            "magnus_integrator", "multisector_fitter", "potential_timefield", "radiation_flow",
            "resolved_tube_geometry", "spectroscopic_gap", "sst_extensions", "sst_gravity",
            "sst_integrator", "sst_master_equation", "sst_tension_scales", "swirl_field",
            "thermo_dynamics", "time_evolution", "trefoil_operator", "vortex_ring", "vorticity_dynamics",
        ]
        if not (SRC / f"{mod}_example.py").is_file()
    ]
    assert not missing, f"missing src examples: {missing}"


def test_audit_generates_summary(audit_report):
    assert audit_report["summary"]["binding_modules"] == 30
    assert audit_report["summary"]["src_example_files"] == 30


def test_example_bootstrap_importable():
    sys.path.insert(0, str(SRC))
    import _example_bootstrap as boot  # noqa: WPS433

    sst, info = boot.import_sstcore()
    pytest.importorskip("SSTcore", exc_type=ImportError)
    assert info["import_ok"] is True
    assert sst is not None
