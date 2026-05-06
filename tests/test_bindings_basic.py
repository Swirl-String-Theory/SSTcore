#!/usr/bin/env python
import pytest

# Use compatibility module ``sstcore`` (re-exports ``SSTcore`` / native bindings only).
sstcore = pytest.importorskip("sstcore", exc_type=ImportError)


def test_compute_helicity_simple():
    velocity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    vorticity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    H = sstcore.compute_helicity(velocity, vorticity)
    assert H == pytest.approx(1.0)


def test_compute_kinetic_energy():
    velocity = [[1.0, 2.0, 2.0], [0.0, 0.0, 0.0]]
    rho_ae = 2.0
    E = sstcore.compute_kinetic_energy(velocity, rho_ae)
    assert E == pytest.approx(9.0)


def test_biot_savart_symmetry_zero():
    r = [0.0, 0.0, 0.0]
    X = [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]
    T = [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    v = sstcore.biot_savart_velocity(r, X, T)
    assert v == pytest.approx([0.0, 0.0, 0.0])


def test_time_dilation_map():
    tangents = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    factors = sstcore.compute_time_dilation_map(tangents, 2.0)
    assert len(factors) == 2
