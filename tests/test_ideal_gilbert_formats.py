"""Patch D: Gilbert HT/TL/STRING parser and find_ideal_by_id."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent


def _import_sstcore_package():
    pkg_dir = _ROOT / "SSTcore"
    init_py = pkg_dir / "__init__.py"
    import importlib.util

    for name in ("sstcore", "SSTcore"):
        if name in sys.modules:
            del sys.modules[name]

    spec = importlib.util.spec_from_file_location(
        "SSTcore",
        init_py,
        submodule_search_locations=[str(pkg_dir.resolve())],
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["SSTcore"] = mod
    spec.loader.exec_module(mod)
    return mod


sstcore = _import_sstcore_package()


def test_find_ideal_by_id_ab_trefoil():
    hit = sstcore.find_ideal_by_id("3:1:1", tag="AB")
    assert hit is not None
    assert hit.xml_tag == "AB"
    assert hit.geometry_kind == sstcore.IdealGeometryKind.FOURIER_XML
    assert hit.block is not None
    assert 'Id="3:1:1"' in hit.block
    assert hit.source_key == "ideal"
    assert hit.source_file == "ideal.txt"


def test_find_ideal_by_id_ht_k11a1():
    hit = sstcore.find_ideal_by_id("K11a1", tag="HT")
    assert hit is not None
    assert hit.xml_tag == "HT"
    assert hit.source_key == "ideal_11a"
    assert "ideal_11a" in hit.source_file
    assert hit.author == "Brian Gilbert"
    assert hit.block is not None
    assert "<HT" in hit.block


def test_find_ideal_by_id_ht_k11n1_string_wrapper():
    hit = sstcore.find_ideal_by_id("K11n1", tag="HT")
    assert hit is not None
    assert hit.source_key == "ideal_11n"
    assert "<STRING" in hit.block


def test_find_ideal_by_id_tl_l10a1():
    hit = sstcore.find_ideal_by_id("L10a1", tag="TL")
    assert hit is not None
    assert hit.xml_tag == "TL"
    assert hit.source_key == "idealLinks_10a"
    assert hit.block is not None
    assert "<STRING" in hit.block


def test_get_ideal_12_points_12a4():
    pts = sstcore.get_ideal_12_points("12a4")
    assert pts is not None
    assert len(pts) > 10
    hit = sstcore.find_ideal_by_id("12a4")
    assert hit is not None
    assert hit.geometry_kind == sstcore.IdealGeometryKind.POINT_CLOUD
    assert hit.block is None


def test_parse_ideal_gilbert_ht_components():
    parse = getattr(sstcore, "parse_ideal_gilbert_from_string", None)
    if parse is None:
        pytest.skip("parse_ideal_gilbert_from_string not in native bindings")
    path = sstcore.get_ideal_file_path("idealLinks_10a")
    if path is None:
        pytest.skip("idealLinks_10a not present")
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = parse(text)
    l10 = [b for b in blocks if getattr(b, "id", "") == "L10a1"]
    assert l10, "L10a1 not parsed"
    blk = l10[0]
    assert getattr(blk, "source_tag", "") == "TL"
    assert len(blk.components) >= 2


def test_ideal_txt_priority_over_other_sources_for_ab():
    hit = sstcore.find_ideal_by_id("3:1:1")
    assert hit is not None
    assert hit.source_file == "ideal.txt"


def test_particle_evaluator_still_ab_only_regression():
    ev = sstcore.ParticleEvaluator("3:1:1", 200)
    assert ev is not None
