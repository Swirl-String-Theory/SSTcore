"""Binding manifest vs runtime export presence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from binding_inventory import (  # noqa: E402
    check_manifest_runtime,
    default_manifest_path,
    load_binding_manifest,
    resolve_native_module,
)
from sstcore_test_import import load_sstcore_package  # noqa: E402

sstcore = load_sstcore_package()


def _manifest() -> dict:
    path = default_manifest_path(ROOT)
    assert path.is_file(), f"missing binding manifest: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_binding_manifest_summary_nonzero():
    manifest = _manifest()
    summary = manifest.get("summary", {})
    assert summary.get("py_bound", 0) > 0
    assert summary.get("cpp_public", 0) > 0
    assert manifest.get("entries")


def test_binding_manifest_load_helper():
    manifest, path = load_binding_manifest(sstcore, root=ROOT)
    assert manifest is not None
    assert path
    assert Path(path).is_file()


def test_binding_manifest_runtime_presence():
    manifest = _manifest()
    native, _ = resolve_native_module(sstcore)
    native_file = getattr(native, "__file__", "") or ""
    native_path = native_file.replace("\\", "/")
    if native and "site-packages" in native_path and (ROOT / "src" / "SSTcore").is_dir():
        pytest.skip(
            "installed native extension may lag src checkout; "
            "rebuild or pip install -e . for strict runtime parity"
        )
    result = check_manifest_runtime(manifest, sstcore, native)
    assert result["runtime_present"] > 0
    missing = result.get("missing_entries") or []
    if missing:
        preview = ", ".join(row["py_export"] for row in missing[:8])
        pytest.fail(
            f"{len(missing)} bound export(s) missing at runtime "
            f"(rebuild/install native extension?): {preview}"
        )


def test_gen_binding_manifest_check():
    gen = SCRIPTS / "gen_binding_manifest.py"
    if not gen.is_file():
        pytest.skip("gen_binding_manifest.py not present")
    import subprocess

    completed = subprocess.run(
        [sys.executable, str(gen), "--check"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
