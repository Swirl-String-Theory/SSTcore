"""Resource discovery without SSTCORE_RESOURCES (audit H-008)."""
from __future__ import annotations

from pathlib import Path

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_get_resources_dir_finds_repo_root_without_env(monkeypatch):
    monkeypatch.delenv("SSTCORE_RESOURCES", raising=False)
    root = sst.get_resources_dir()
    assert root is not None
    assert (Path(root) / "ideal.txt").is_file()
    assert Path(root).name == "resources"
