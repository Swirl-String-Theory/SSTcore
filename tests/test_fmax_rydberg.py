"""Fmax Rydberg 16π² helpers (Canon v0.8.26)."""
from __future__ import annotations

import math

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_fmax_snapshot_unchanged():
    assert sst.ValueOriginAPI.fmax_snapshot() == pytest.approx(29.053507)


def test_16pi2_preferred_over_32pi2():
    hbar = sst.SSTCanonicalConstants.hbar()
    c = sst.SSTCanonicalConstants.speed_of_light()
    alpha = sst.SSTCanonicalConstants.alpha()
    R = sst.SSTCanonicalConstants.values().R_infty_sst
    f16 = sst.ValueOriginAPI.fmax_rydberg_16pi2(hbar, R, c, alpha)
    f32 = sst.ValueOriginAPI.fmax_rydberg_32pi2(hbar, R, c, alpha)
    assert math.isfinite(f16)
    assert f32 == pytest.approx(2.0 * f16)
    snap = sst.ValueOriginAPI.fmax_snapshot()
    # 32π² must not be treated as the snapshot identity.
    assert abs(f32 - snap) > abs(f16 - snap)


def test_snapshot_vs_recompute_residual_does_not_mutate_snapshot():
    cmp = sst.ValueOriginAPI.compare_fmax_snapshot_to_recomputed()
    assert cmp.snapshot_unchanged is True
    assert cmp.snapshot == pytest.approx(29.053507)
    assert cmp.residual >= 0.0
