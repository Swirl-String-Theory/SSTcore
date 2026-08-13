#!/usr/bin/env python3
"""Deelplan res-4: knotplot resource API (INDEX-backed getters + deprecation shims)."""

from __future__ import annotations

import warnings

import pytest

from sstcore_test_import import load_sstcore_package

sstcore = load_sstcore_package()


@pytest.fixture(scope="module")
def kp():
    root = sstcore.get_knotplot_dir()
    if root is None or not (root / "INDEX.json").is_file():
        pytest.fail("resources/knotplot/INDEX.json required for API tests")
    return sstcore


def test_list_and_entry(kp) -> None:
    ids = kp.list_knotplot_ids()
    assert "knot_3.1" in ids
    assert "knot_9.2" in ids  # stub
    near = kp.list_knotplot_ids(status="near-ideal-candidate")
    assert "knot_3.1" in near
    entry = kp.get_knotplot_entry("knot_3.1")
    assert entry is not None
    assert entry["relaxed"] is True


def test_getters_relaxed_vs_stub(kp) -> None:
    assert kp.get_knotplot_polish_path("knot_3.1", uniform=True) is not None
    assert kp.get_knotplot_ab_path("knot_3.1") is not None
    assert kp.get_knotplot_ab("knot_3.1")
    assert kp.get_knotplot_build_script("knot_3.1") is not None

    assert kp.get_knotplot_polish_path("knot_9.2") is None
    assert kp.get_knotplot_ab_path("knot_9.2") is None
    assert kp.get_knotplot_build_script("knot_9.2") is not None


def test_id_normalization(kp) -> None:
    assert kp.normalize_knotplot_id("knot_3.1") == "knot_3.1"
    assert kp.normalize_knotplot_id("3.1") == "knot_3.1"
    # legacy torus alias
    assert kp.normalize_knotplot_id("knot_TL6.9") in ("torus_6.9", "knot_TL6.9")
    assert kp.normalize_knotplot_id("foo/bar") is None
    assert kp.normalize_knotplot_id("..\\evil") is None


def test_deprecation_shims_warn_once(kp) -> None:
    kp._knotplot_deprecation_warned.clear()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        p1 = kp.get_knotplot_ideal_path("knot_3.1")
        p2 = kp.get_knotplot_ideal_path("knot_3.1")
        t1 = kp.knotplot("knot_3.1")
        t2 = kp.knotplot("knot_3.1")
    assert p1 is not None and p1 == p2
    assert t1 and t1 == t2
    dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert len(dep) == 2


def test_resolve_relaxed_import(kp) -> None:
    res = kp.resolve_knot_ref("knot_3.1", source="knotplot")
    assert res is not None
    assert res.role == kp.KnotCurveRole.RELAXED_IMPORT
    assert res.native_length is not None
    with pytest.raises(ValueError, match="canon_mass"):
        kp.assert_canon_ideal(res, kp.CalculationRole.CANON_MASS)
