#!/usr/bin/env python3
"""Minimal checks for Frenet frames + helicity via ``sstcore``."""

import numpy as np
import pytest

sstcore = pytest.importorskip("sstcore", exc_type=ImportError)


def test_frenet_helicity_roundtrip():
    X = np.random.randn(10, 3)

    T, N, B = sstcore.compute_frenet_frames(X)
    T = np.asarray(T)
    N = np.asarray(N)
    B = np.asarray(B)

    assert T.shape == X.shape
    assert N.shape == X.shape
    assert B.shape == X.shape

    curvature, torsion = sstcore.compute_curvature_torsion(T, N)
    curvature = np.asarray(curvature)
    torsion = np.asarray(torsion)

    assert curvature.shape[0] == X.shape[0]
    assert torsion.shape[0] == X.shape[0]

    helicity = sstcore.compute_helicity(T, T)
    assert np.isfinite(helicity)
