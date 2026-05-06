#!/usr/bin/env python3
"""Minimal Biot–Savart sanity check via ``sstcore``."""

import pytest

pytest.importorskip("sstcore", exc_type=ImportError)


def test_biot_savart_velocity_basic():
    import sstcore

    r = [0.1, 0.2, 0.3]
    X = [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]
    T = [[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]]

    v = sstcore.biot_savart_velocity(r, X, T)
    assert len(v) == 3
