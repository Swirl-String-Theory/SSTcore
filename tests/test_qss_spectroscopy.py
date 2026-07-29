"""QSS spectroscopy scaffolding tests (Canon v0.8.22)."""
from __future__ import annotations

import pytest

try:
    import SSTcore as sst
except ImportError:
    sst = pytest.importorskip("sstcore", exc_type=ImportError)


def test_diagonal_eigenvalues():
    r = sst.QSSSpectroscopyAPI.eigen_2x2([2.0, 0.0, 0.0, 5.0])
    assert r.epistemic_status == "SYNTHETIC_DIAGNOSTIC"
    vals = sorted(z.real for z in r.eigenvalues)
    assert vals[0] == pytest.approx(2.0)
    assert vals[1] == pytest.approx(5.0)
    assert r.eigen_residual < 1e-12
    assert r.eigenvalue_magnitude_ratio == pytest.approx(2.5)
    assert r.conditioning == r.eigenvalue_magnitude_ratio


def test_defective_matrix_magnitude_ratio_not_true_conditioning():
    # Huge off-diagonal: eigenvalue magnitude ratio can be ~1 while matrix is ill for eigenvectors.
    r = sst.QSSSpectroscopyAPI.eigen_2x2([1.0, 1e12, 0.0, 1.0])
    assert r.eigenvalue_magnitude_ratio == pytest.approx(1.0)


def test_jordan_block_complex_possible():
    # Rotation-scale matrix with complex eigenvalues
    r = sst.QSSSpectroscopyAPI.eigen_2x2([0.0, -1.0, 1.0, 0.0])
    assert r.epistemic_status == "SYNTHETIC_DIAGNOSTIC"
    assert len(r.eigenvalues) == 2
    assert abs(r.eigenvalues[0].imag) == pytest.approx(1.0)


def test_bad_matrix_open_research():
    r = sst.QSSSpectroscopyAPI.eigen_2x2([1.0, 2.0])
    assert r.epistemic_status == "OPEN_RESEARCH_GATE"


def test_pseudospectrum_peaks_near_spectrum():
    ps = sst.QSSSpectroscopyAPI.pseudospectrum_diag_2x2(1.0, 2.0, 0.5, 2.5, 5, -0.5, 0.5, 3)
    assert ps.epistemic_status == "SYNTHETIC_DIAGNOSTIC"
    assert len(ps.samples) == 15
    assert ps.max_resolvent_norm > 1.0
