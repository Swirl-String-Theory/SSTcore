"""SHA-256 helper + source-bundle manifest (audit B-001/B-004)."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_script_passes():
    script = ROOT / "scripts" / "check_source_bundle_manifest.py"
    assert script.is_file()
    r = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_geometry_hash_matches_python_sha256():
    pytest.importorskip("SSTcore")
    import SSTcore as sst
    import struct

    pts = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    h = sst.GeometryCertificateAPI.sha256_hex_of_points(pts)
    buf = bytearray()
    for p in pts:
        for c in p:
            buf.extend(struct.pack("<d", c))
    assert h == hashlib.sha256(buf).hexdigest()
