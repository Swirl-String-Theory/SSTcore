"""Patch A: ideal.txt AB lookup and ParticleEvaluator smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent


def _import_sstcore_package():
    """Import full SSTcore package (not native-only shadow from build/)."""
    pkg_dir = _ROOT / "SSTcore"
    if not pkg_dir.is_dir():
        pkg_dir = _ROOT / "sstcore"
    init_py = pkg_dir / "__init__.py"
    if not init_py.is_file():
        raise ImportError(f"SSTcore package not found under {_ROOT}")

    import importlib.util

    for name in ("sstcore", "SSTcore"):
        if name in sys.modules:
            del sys.modules[name]

    spec = importlib.util.spec_from_file_location(
        "SSTcore",
        init_py,
        submodule_search_locations=[str(pkg_dir.resolve())],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load SSTcore from {init_py}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["SSTcore"] = mod
    spec.loader.exec_module(mod)
    return mod


sstcore = _import_sstcore_package()


def test_import_shims():
    assert sstcore.__version__
    assert hasattr(sstcore, "ParticleEvaluator")


def test_resources_dir_and_ideal_txt():
    root = sstcore.get_resources_dir()
    assert root is not None
    ideal_path = sstcore.get_ideal_txt_path()
    assert ideal_path is not None
    assert ideal_path.name == "ideal.txt"
    assert ideal_path.is_file()


def test_find_ideal_ab_block_by_id_trefoil():
    block = sstcore.find_ideal_ab_block_by_id("3:1:1")
    assert block is not None
    assert 'Id="3:1:1"' in block
    assert "<AB" in block
    assert "</AB>" in block


def test_find_ideal_ab_block_by_id_missing_returns_none():
    assert sstcore.find_ideal_ab_block_by_id("NO_SUCH_AB_ID_XYZ") is None


def test_get_ideal_ab_matches_find():
    ab = sstcore.get_ideal_ab("3:1:1")
    assert ab is not None
    assert ab == sstcore.find_ideal_ab_block_by_id("3:1:1")


def test_particle_evaluator_trefoil():
    ev = sstcore.ParticleEvaluator("3:1:1", 200)
    assert ev is not None


def test_particle_evaluator_rejects_knotplot_style_id():
    with pytest.raises(RuntimeError):
        sstcore.ParticleEvaluator("knot_3.1", 200)


def test_knotplot_ideal_not_used_for_ab_lookup():
    """knotplot *_ideal.txt must not satisfy AB lookup for canon trefoil id."""
    kp_path = sstcore.get_knotplot_ideal_path("knot_3.1")
    if kp_path is None:
        pytest.skip("knotplot trefoil ideal not present in resources")
    kp_text = kp_path.read_text(encoding="utf-8", errors="replace")
    assert 'Id="3:1:1"' in kp_text or "<AB" in kp_text
    block = sstcore.find_ideal_ab_block_by_id("3:1:1")
    assert block is not None
    # Canon block comes from Gilbert ideal.txt (Conway="3"), not KnotPlot conversion header.
    assert 'Conway="3"' in block
    assert "Generated from KnotPlot coordinates" not in block
