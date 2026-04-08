#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test whether a knot/link .fseries geometry can behave as a monopole candidate
under SST-inspired organized-transport source models.

Model summary
-------------
Given a centerline curve reconstructed from a Fourier-series file (.fseries),
we construct a smoothed tube source on a 3D Cartesian grid.

We test two source models:

(1) Pure tensor source:
    S_tensor(x) = ∂i∂j Σ_ij
    with
    Σ_ij(x) = rho_f * v_swirl^2 * t_i t_j * W(x)

(2) Mixed monopole-capable source:
    S_mix(x) = alpha * rho_f * v_swirl^2 * W(x) + beta * ∂i∂j Σ_ij

where:
- t is the local unit tangent of the reconstructed centerline
- W(x) is a Gaussian tube kernel deposited around the centerline

Outputs:
- monopole Q = ∫ S dV
- dipole D_i = ∫ x_i S dV
- quadrupole M_ij = ∫ x_i x_j S dV
- normalized diagnostics to assess monopole dominance

Assumptions / limits
--------------------
- With ``sstbindings`` installed, the largest Fourier block is taken (``parse_fseries_multi`` +
  ``index_of_largest_block``), matching ``src/knot_dynamics.cpp``. Without bindings, a simple
  all-rows reader is used (less reliable for multi-block ``.fseries`` files).
- This is a geometric/coarse-grained test, not a full fluid simulation.
- It assumes a constant organized transport speed v_swirl along the centerline.
- It tests whether the geometry of the source supports an effective monopole
  after coarse-graining on the chosen tube radius and grid scale.

Usage
-----
python test_monopole_from_fseries.py /path/to/knot_TL3.3_Gear.fseries

Optional arguments:
  --n-curve 4000
  --grid 96
  --grid 80 96 128          (Cartesian product with other sweeps)
  --tube-radius 0.06
  --tube-radius 0.04 0.06 0.08
  --padding 0.6
  --alpha 1.0
  --beta 1.0
  --beta 0.1 1.0 10.0
  --report-out monopole_report.txt
  --npz-out monopole_fields.npz

Batch (all .fseries under a tree)
---------------------------------
  python test_monopole_from_fseries.py --batch [DIR]

  Discovers every **/*.fseries under DIR (default: current directory) and writes
  <same_stem>_monopole_report.txt next to each file. Other flags (--n-curve,
  --grid, etc.) apply to every run. Do not pass --report-out or --npz-out with
  --batch.

  After a batch run, a single summary file is written under DIR (default name
  ``monopole_batch_summary.txt``) with one TSV row per knot plus aggregate
  counts. Override with ``--batch-summary PATH``.

  Multiple ``--grid``, ``--tube-radius``, and/or ``--beta`` values run the full
  Cartesian product per file. Per-knot reports are named
  ``<stem>_monopole_<paramtag>_report.txt`` when more than one combination is
  used; with a single combination the legacy ``<stem>_monopole_report.txt`` name
  is kept. Do not use ``--report-out`` / ``--npz-out`` when more than one
  parameter combination is requested (single-file mode).

Recommended workflow
--------------------
Run multiple times with different:
- tube radius
- grid resolution
- alpha/beta
to test robustness.

Author
------
Prepared for SST organized-transport monopole diagnostics.
"""

from __future__ import annotations

import argparse
import itertools
import re
import shlex
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


def _get_sstbindings() -> Any | None:
    """Return the ``sstbindings`` module if importable (same knot/Fourier API as SSTcore ``src``)."""
    try:
        import sstbindings as _sst  # type: ignore

        return _sst
    except ImportError:
        return None


# -----------------------------
# Canonical SST constants
# -----------------------------
V_SWIRL = 1.09384563e6          # m/s
R_C = 1.40897017e-15            # m
RHO_F = 7.0e-7                 # kg/m^3


# -----------------------------
# Data structures
# -----------------------------
@dataclass
class CurveData:
    theta: np.ndarray        # (N,)
    xyz: np.ndarray          # (N, 3)
    dxyz_dtheta: np.ndarray  # (N, 3)
    tangents: np.ndarray     # (N, 3)
    segment_lengths: np.ndarray  # (N,)
    total_length: float


@dataclass
class GridData:
    X: np.ndarray
    Y: np.ndarray
    Z: np.ndarray
    dx: float
    dy: float
    dz: float
    dV: float
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray


# -----------------------------
# .fseries -> curve (SSTcore sstbindings when available)
# -----------------------------
def _length_l_from_header(header: str) -> float | None:
    """Parse ``L = ...`` from a Fourier block header (matches C++ ``FourierBlock::header``)."""
    m = re.search(r"L\s*=\s*([0-9eE+\-.]+)", header)
    return float(m.group(1)) if m else None


def _coeffs_from_fourier_block(block: Any) -> np.ndarray:
    """Stack ``FourierBlock`` coefficient vectors into shape (N_harmonics, 6) ax,bx,ay,by,az,bz."""
    ax = np.asarray(block.a_x, dtype=float)
    n = ax.size
    if n == 0:
        return np.zeros((0, 6), dtype=float)
    return np.column_stack(
        [
            ax,
            np.asarray(block.b_x, dtype=float),
            np.asarray(block.a_y, dtype=float),
            np.asarray(block.b_y, dtype=float),
            np.asarray(block.a_z, dtype=float),
            np.asarray(block.b_z, dtype=float),
        ]
    )


def _parse_fseries_py_fallback(path: str) -> tuple[np.ndarray, float | None]:
    """
    Pure-Python .fseries reader (no multi-block flush). Used only when ``sstbindings`` is missing.
    Prefer installing SSTcore bindings so ``parse_fseries_multi`` / largest-block logic applies.
    """
    coeffs: list[list[float]] = []
    length_L: float | None = None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("%"):
                m = re.search(r"L\s*=\s*([0-9eE+\-.]+)", s)
                if m:
                    length_L = float(m.group(1))
                continue
            parts = s.split()
            if len(parts) != 6:
                raise ValueError(f"Expected 6 columns in coeff row, got {len(parts)}: {s}")
            coeffs.append([float(v) for v in parts])

    if not coeffs:
        raise ValueError("No Fourier coefficient rows found in file.")

    return np.asarray(coeffs, dtype=float), length_L


def curve_from_coeffs(coeffs: np.ndarray, n_curve: int = 4000) -> CurveData:
    """
    Reconstruct x(theta), y(theta), z(theta) and d/dtheta (harmonics j = 1..N per row).
    Centers the curve to match SST ``FourierKnot::center_points`` usage elsewhere.
    """
    n_h = coeffs.shape[0]
    theta = np.linspace(0.0, 2.0 * np.pi, n_curve, endpoint=False)

    xyz = np.zeros((n_curve, 3), dtype=float)
    dxyz_dtheta = np.zeros((n_curve, 3), dtype=float)

    for idx in range(n_h):
        j = idx + 1
        ax, bx, ay, by, az, bz = coeffs[idx]
        cj = np.cos(j * theta)
        sj = np.sin(j * theta)

        xyz[:, 0] += ax * cj + bx * sj
        xyz[:, 1] += ay * cj + by * sj
        xyz[:, 2] += az * cj + bz * sj

        dxyz_dtheta[:, 0] += -j * ax * sj + j * bx * cj
        dxyz_dtheta[:, 1] += -j * ay * sj + j * by * cj
        dxyz_dtheta[:, 2] += -j * az * sj + j * bz * cj

    xyz -= xyz.mean(axis=0, keepdims=True)

    speed_theta = np.linalg.norm(dxyz_dtheta, axis=1)
    speed_theta = np.maximum(speed_theta, 1e-30)
    tangents = dxyz_dtheta / speed_theta[:, None]

    xyz_next = np.roll(xyz, -1, axis=0)
    segment_vectors = xyz_next - xyz
    segment_lengths = np.linalg.norm(segment_vectors, axis=1)
    total_length = float(segment_lengths.sum())

    return CurveData(
        theta=theta,
        xyz=xyz,
        dxyz_dtheta=dxyz_dtheta,
        tangents=tangents,
        segment_lengths=segment_lengths,
        total_length=total_length,
    )


def load_fseries_curve(path: str, n_curve: int) -> tuple[CurveData, float | None, int]:
    """
    Load the largest Fourier block via ``sstbindings.parse_fseries_multi`` when available
    (same policy as ``build_invariants_from_fseries`` in ``src/knot_dynamics.cpp``), then
    reconstruct the sampled centerline.
    """
    sst = _get_sstbindings()
    if sst is not None:
        blocks = sst.parse_fseries_multi(path)
        if not blocks:
            raise ValueError("No Fourier blocks parsed from file (empty or unreadable).")
        idx = int(sst.index_of_largest_block(blocks))
        block = blocks[idx]
        coeffs = _coeffs_from_fourier_block(block)
        if coeffs.shape[0] == 0:
            raise ValueError("Largest Fourier block contains no harmonics.")
        length_L = _length_l_from_header(getattr(block, "header", "") or "")
        return curve_from_coeffs(coeffs, n_curve=n_curve), length_L, int(coeffs.shape[0])

    coeffs, length_L = _parse_fseries_py_fallback(path)
    return curve_from_coeffs(coeffs, n_curve=n_curve), length_L, int(coeffs.shape[0])


# -----------------------------
# Build 3D grid
# -----------------------------
def build_grid(curve_xyz: np.ndarray, grid_n: int = 96, padding_frac: float = 0.6) -> GridData:
    """
    Build a cubic grid around the curve with isotropic spacing.
    padding_frac is relative to the max span of the curve.
    """
    mins = curve_xyz.min(axis=0)
    maxs = curve_xyz.max(axis=0)
    center = 0.5 * (mins + maxs)
    spans = maxs - mins
    max_span = float(np.max(spans))

    half_extent = 0.5 * max_span * (1.0 + padding_frac)
    if half_extent <= 0:
        half_extent = 1.0

    x = np.linspace(center[0] - half_extent, center[0] + half_extent, grid_n)
    y = np.linspace(center[1] - half_extent, center[1] + half_extent, grid_n)
    z = np.linspace(center[2] - half_extent, center[2] + half_extent, grid_n)

    dx = float(x[1] - x[0]) if len(x) > 1 else 1.0
    dy = float(y[1] - y[0]) if len(y) > 1 else 1.0
    dz = float(z[1] - z[0]) if len(z) > 1 else 1.0
    dV = dx * dy * dz

    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    return GridData(X=X, Y=Y, Z=Z, dx=dx, dy=dy, dz=dz, dV=dV, x=x, y=y, z=z)


# -----------------------------
# Deposit smoothed tube source
# -----------------------------
def deposit_tube_sources(
        curve: CurveData,
        grid: GridData,
        tube_radius: float,
        rho_f: float = RHO_F,
        v_swirl: float = V_SWIRL,
) -> Dict[str, np.ndarray]:
    """
    Deposit a Gaussian tube kernel W and tensor Sigma_ij onto the grid.

    We approximate the curve as a sequence of points with arc-length weights ds_k.
    For each point:
      W += ds_k * G_sigma(|x-r_k|)
    with G_sigma normalized to integrate to 1 over R^3:
      G_sigma(r) = (2*pi*sigma^2)^(-3/2) exp(-r^2/(2 sigma^2))

    Then:
      rho_org = rho_f * v_swirl^2 * W
      Sigma_ij = rho_f * v_swirl^2 * t_i t_j * W_contrib
    """
    sigma = float(tube_radius)
    if sigma <= 0:
        raise ValueError("tube_radius must be > 0")

    X, Y, Z = grid.X, grid.Y, grid.Z
    shape = X.shape

    W = np.zeros(shape, dtype=np.float64)
    Sigma = np.zeros(shape + (3, 3), dtype=np.float64)

    norm = 1.0 / ((2.0 * np.pi * sigma * sigma) ** 1.5)

    # Use local segment lengths as weights
    ds = curve.segment_lengths
    pts = curve.xyz
    tangents = curve.tangents

    # Truncate Gaussian at ~3 sigma for speed by masking local boxes
    x = grid.x
    y = grid.y
    z = grid.z

    for k in range(len(pts)):
        px, py, pz = pts[k]
        tx, ty, tz = tangents[k]
        weight = ds[k]

        ix0 = max(0, int(np.searchsorted(x, px - 3.0 * sigma) - 1))
        ix1 = min(len(x), int(np.searchsorted(x, px + 3.0 * sigma) + 1))
        iy0 = max(0, int(np.searchsorted(y, py - 3.0 * sigma) - 1))
        iy1 = min(len(y), int(np.searchsorted(y, py + 3.0 * sigma) + 1))
        iz0 = max(0, int(np.searchsorted(z, pz - 3.0 * sigma) - 1))
        iz1 = min(len(z), int(np.searchsorted(z, pz + 3.0 * sigma) + 1))

        XX = X[ix0:ix1, iy0:iy1, iz0:iz1]
        YY = Y[ix0:ix1, iy0:iy1, iz0:iz1]
        ZZ = Z[ix0:ix1, iy0:iy1, iz0:iz1]

        r2 = (XX - px) ** 2 + (YY - py) ** 2 + (ZZ - pz) ** 2
        G = weight * norm * np.exp(-0.5 * r2 / (sigma * sigma))

        W[ix0:ix1, iy0:iy1, iz0:iz1] += G

        t = np.array([tx, ty, tz], dtype=float)
        outer_tt = np.outer(t, t)
        for i in range(3):
            for j in range(3):
                Sigma[ix0:ix1, iy0:iy1, iz0:iz1, i, j] += rho_f * (v_swirl ** 2) * outer_tt[i, j] * G

    rho_org = rho_f * (v_swirl ** 2) * W
    return {
        "W": W,
        "rho_org": rho_org,
        "Sigma": Sigma,
    }


# -----------------------------
# Differential operators
# -----------------------------
def gradient_scalar(f: np.ndarray, dx: float, dy: float, dz: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    gx, gy, gz = np.gradient(f, dx, dy, dz, edge_order=2)
    return gx, gy, gz


def divergence_vector(v: np.ndarray, dx: float, dy: float, dz: float) -> np.ndarray:
    # v shape: (nx, ny, nz, 3)
    dvx_dx = np.gradient(v[..., 0], dx, axis=0, edge_order=2)
    dvy_dy = np.gradient(v[..., 1], dy, axis=1, edge_order=2)
    dvz_dz = np.gradient(v[..., 2], dz, axis=2, edge_order=2)
    return dvx_dx + dvy_dy + dvz_dz


def double_divergence_tensor(T: np.ndarray, dx: float, dy: float, dz: float) -> np.ndarray:
    """
    Compute ∂i∂j T_ij.
    T shape: (nx, ny, nz, 3, 3)
    """
    # First divergence over j: v_i = ∂j T_ij
    v = np.zeros(T.shape[:3] + (3,), dtype=np.float64)

    for i in range(3):
        dTix_dx = np.gradient(T[..., i, 0], dx, axis=0, edge_order=2)
        dTiy_dy = np.gradient(T[..., i, 1], dy, axis=1, edge_order=2)
        dTiz_dz = np.gradient(T[..., i, 2], dz, axis=2, edge_order=2)
        v[..., i] = dTix_dx + dTiy_dy + dTiz_dz

    # Then divergence over i
    return divergence_vector(v, dx, dy, dz)


# -----------------------------
# Moments
# -----------------------------
def compute_moments(S: np.ndarray, grid: GridData) -> Dict[str, np.ndarray | float]:
    """
    Compute:
      Q = ∫ S dV
      D_i = ∫ x_i S dV
      M_ij = ∫ x_i x_j S dV
    """
    X, Y, Z = grid.X, grid.Y, grid.Z
    dV = grid.dV

    Q = float(np.sum(S) * dV)

    D = np.array([
        np.sum(X * S) * dV,
        np.sum(Y * S) * dV,
        np.sum(Z * S) * dV,
        ], dtype=float)

    coords = [X, Y, Z]
    M = np.zeros((3, 3), dtype=float)
    for i in range(3):
        for j in range(3):
            M[i, j] = float(np.sum(coords[i] * coords[j] * S) * dV)

    # Trace-free quadrupole often useful
    trM = np.trace(M)
    Qtf = M - np.eye(3) * trM / 3.0

    return {
        "Q": Q,
        "D": D,
        "M": M,
        "Qtf": Qtf,
    }


def fro_norm(A: np.ndarray) -> float:
    return float(np.sqrt(np.sum(A * A)))


@dataclass
class MonopoleDiagnosticNumbers:
    """Normalized multipole diagnostics (same thresholds as interpretation text)."""

    Qt: float
    Qm: float
    rt_d: float
    rt_m: float
    rm_d: float
    rm_m: float
    tensor_monopole_suppressed: bool
    mix_plausible: bool


def compute_diagnostic_numbers(
        moments_tensor: Dict[str, np.ndarray | float],
        moments_mix: Dict[str, np.ndarray | float],
        total_scalar_mass: float,
        bbox_scale: float,
) -> MonopoleDiagnosticNumbers:
    Qt = abs(float(moments_tensor["Q"]))
    Dt = np.linalg.norm(np.asarray(moments_tensor["D"]))
    Mt = fro_norm(np.asarray(moments_tensor["Qtf"]))

    Qm = abs(float(moments_mix["Q"]))
    Dm = np.linalg.norm(np.asarray(moments_mix["D"]))
    Mm = fro_norm(np.asarray(moments_mix["Qtf"]))

    eps = 1e-30
    bs = max(bbox_scale, 1e-12)
    rt_d = Dt / max(Qt * bs, eps)
    rt_m = Mt / max(Qt * bs * bs, eps)
    rm_d = Dm / max(Qm * bs, eps)
    rm_m = Mm / max(Qm * bs * bs, eps)

    tensor_monopole_suppressed = Qt < 1e-8 * max(total_scalar_mass, 1.0)
    mix_plausible = Qm > 0 and rm_d < 0.2 and rm_m < 0.5

    return MonopoleDiagnosticNumbers(
        Qt=Qt,
        Qm=Qm,
        rt_d=rt_d,
        rt_m=rt_m,
        rm_d=rm_d,
        rm_m=rm_m,
        tensor_monopole_suppressed=tensor_monopole_suppressed,
        mix_plausible=mix_plausible,
    )


# -----------------------------
# Diagnostics / interpretation
# -----------------------------
def assess_monopole_candidate(
        moments_tensor: Dict[str, np.ndarray | float],
        moments_mix: Dict[str, np.ndarray | float],
        total_scalar_mass: float,
        bbox_scale: float,
) -> str:
    """Qualitative interpretation (uses :func:`compute_diagnostic_numbers`)."""
    d = compute_diagnostic_numbers(
        moments_tensor, moments_mix, total_scalar_mass, bbox_scale
    )
    lines = []
    lines.append("Interpretation")
    lines.append("--------------")
    lines.append(f"Pure tensor source |Q| = {d.Qt:.6e}")
    lines.append(f"Pure tensor normalized dipole ratio = {d.rt_d:.6e}")
    lines.append(f"Pure tensor normalized quadrupole ratio = {d.rt_m:.6e}")
    lines.append("")
    lines.append(f"Mixed source |Q| = {d.Qm:.6e}")
    lines.append(f"Mixed source normalized dipole ratio = {d.rm_d:.6e}")
    lines.append(f"Mixed source normalized quadrupole ratio = {d.rm_m:.6e}")
    lines.append(f"Scalar organized reservoir ∫rho_org dV = {total_scalar_mass:.6e}")
    lines.append("")

    if d.tensor_monopole_suppressed:
        lines.append(
            "Pure tensor source: monopole is numerically suppressed relative to the scalar organized reservoir."
        )
    else:
        lines.append(
            "Pure tensor source: non-negligible monopole appears numerically; check grid/tube robustness to see if it is physical or discretization leakage."
        )

    if d.mix_plausible:
        lines.append(
            "Mixed source: plausible effective monopole candidate after coarse-graining; dipole/quadrupole contamination is moderate."
        )
    else:
        lines.append(
            "Mixed source: not yet a clean monopole candidate; higher multipoles remain too important or net monopole is weak."
        )

    return "\n".join(lines)


def _param_tag_for_filename(grid_n: int, tube: float, alpha: float, beta: float) -> str:
    """Filesystem-safe token (no dots) for sweep output names."""

    def fmt(x: float) -> str:
        return f"{x:.8g}".replace(".", "p").replace("-", "m")

    return f"g{int(grid_n)}_s{fmt(tube)}_a{fmt(alpha)}_b{fmt(beta)}"


@dataclass
class MonopoleSummaryRow:
    """One row for batch summary tables (TSV)."""

    relpath: str
    stem: str
    ok: bool
    err: str | None = None
    grid_n: int | None = None
    tube_radius: float | None = None
    alpha: float | None = None
    beta: float | None = None
    header_L: float | None = None
    n_harmonics: int | None = None
    curve_length: float | None = None
    bbox_diag: float | None = None
    Q_tensor: float | None = None
    Q_mix: float | None = None
    tensor_norm_dipole: float | None = None
    tensor_norm_quad: float | None = None
    mix_norm_dipole: float | None = None
    mix_norm_quad: float | None = None
    mix_plausible: bool | None = None
    tensor_monopole_suppressed: bool | None = None
    scalar_mass: float | None = None


def format_batch_summary(
        *,
        root: Path,
        rows: List[MonopoleSummaryRow],
        argv_str: str,
        n_curve: int,
        grid_vals: List[int],
        tube_vals: List[float],
        padding: float,
        alpha: float,
        beta_vals: List[float],
) -> str:
    """Human-readable + TSV block for all knots in a batch."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ok_rows = [r for r in rows if r.ok]
    bad_rows = [r for r in rows if not r.ok]
    plausible = sum(1 for r in ok_rows if r.mix_plausible)
    suppressed = sum(1 for r in ok_rows if r.tensor_monopole_suppressed)
    n_combo = max(1, len(grid_vals) * len(tube_vals) * len(beta_vals))
    n_files = len({r.relpath for r in rows}) if rows else 0

    lines: List[str] = []
    lines.append("Monopole batch summary")
    lines.append("======================")
    lines.append(f"Generated (UTC): {now}")
    lines.append(f"Root: {root}")
    lines.append(f"Command: {argv_str}")
    lines.append("")
    lines.append("Run parameters")
    lines.append("--------------")
    lines.append(f"n_curve={n_curve} padding={padding} alpha={alpha}")
    lines.append(f"grid sweep: {grid_vals}")
    lines.append(f"tube_radius sweep: {tube_vals}")
    lines.append(f"beta sweep: {beta_vals}")
    lines.append(f"Cartesian combinations per file: {n_combo}")
    lines.append("")
    lines.append("Aggregate")
    lines.append("---------")
    lines.append(f"Total runs (file × parameter set): {len(rows)}")
    lines.append(f"Distinct .fseries paths: {n_files}")
    lines.append(f"Succeeded: {len(ok_rows)}")
    lines.append(f"Failed: {len(bad_rows)}")
    lines.append(f"Mixed 'plausible monopole candidate' (heuristic): {plausible} / {len(ok_rows) if ok_rows else 0}")
    lines.append(f"Pure tensor monopole suppressed (heuristic): {suppressed} / {len(ok_rows) if ok_rows else 0}")
    lines.append("")

    # TSV (Excel-friendly)
    hdr = (
        "ok\trelpath\tstem\terror\tgrid_n\ttube_radius\talpha\tbeta\theader_L\tn_harmonics\tcurve_length\tbbox_diag\t"
        "Q_tensor\tQ_mix\ttensor_norm_dipole\ttensor_norm_quad\t"
        "mix_norm_dipole\tmix_norm_quad\tmix_plausible\ttensor_monopole_suppressed\tscalar_mass"
    )
    lines.append("Per-knot (tab-separated)")
    lines.append("------------------------")
    lines.append(hdr)
    for r in rows:
        def fnum(x: float | None) -> str:
            return "" if x is None else f"{x:.17e}"

        def fbool(x: bool | None) -> str:
            return "" if x is None else ("1" if x else "0")

        def fint(x: int | None) -> str:
            return "" if x is None else str(x)

        lines.append(
            "\t".join(
                [
                    "1" if r.ok else "0",
                    r.relpath.replace("\t", " "),
                    r.stem.replace("\t", " "),
                    (r.err or "").replace("\t", " ").replace("\n", " "),
                    fint(r.grid_n),
                    fnum(r.tube_radius),
                    fnum(r.alpha),
                    fnum(r.beta),
                    fnum(r.header_L) if r.header_L is not None else "",
                    "" if r.n_harmonics is None else str(r.n_harmonics),
                    fnum(r.curve_length),
                    fnum(r.bbox_diag),
                    fnum(r.Q_tensor),
                    fnum(r.Q_mix),
                    fnum(r.tensor_norm_dipole),
                    fnum(r.tensor_norm_quad),
                    fnum(r.mix_norm_dipole),
                    fnum(r.mix_norm_quad),
                    fbool(r.mix_plausible),
                    fbool(r.tensor_monopole_suppressed),
                    fnum(r.scalar_mass),
                ]
            )
        )

    if bad_rows:
        lines.append("")
        lines.append("Failures (detail)")
        lines.append("-----------------")
        for r in bad_rows:
            tag = ""
            if r.grid_n is not None and r.tube_radius is not None and r.beta is not None:
                tag = f" [grid={r.grid_n} tube={r.tube_radius} beta={r.beta}]"
            lines.append(f"  {r.relpath}{tag}: {r.err}")

    return "\n".join(lines)


# -----------------------------
# Main driver
# -----------------------------
def run_monopole_analysis(
    fseries_path: str,
    *,
    n_curve: int,
    grid_n: int,
    tube_radius: float,
    padding: float,
    alpha: float,
    beta: float,
    report_out: str | None,
    npz_out: str | None,
    print_report: bool = True,
    summary_relpath: str | None = None,
    summary_stem: str | None = None,
) -> MonopoleSummaryRow:
    """Run full pipeline for one .fseries file; optionally write report/npz and print. Returns a summary row."""
    curve, length_L, n_harmonics = load_fseries_curve(fseries_path, n_curve)

    mins = curve.xyz.min(axis=0)
    maxs = curve.xyz.max(axis=0)
    bbox_diag = float(np.linalg.norm(maxs - mins))
    rms_radius = float(np.sqrt(np.mean(np.sum(curve.xyz ** 2, axis=1))))
    max_radius = float(np.max(np.linalg.norm(curve.xyz, axis=1)))

    grid = build_grid(curve.xyz, grid_n=grid_n, padding_frac=padding)

    dep = deposit_tube_sources(curve, grid, tube_radius=tube_radius, rho_f=RHO_F, v_swirl=V_SWIRL)
    W = dep["W"]
    rho_org = dep["rho_org"]
    Sigma = dep["Sigma"]

    S_tensor = double_divergence_tensor(Sigma, grid.dx, grid.dy, grid.dz)
    S_mix = alpha * rho_org + beta * S_tensor

    moments_tensor = compute_moments(S_tensor, grid)
    moments_mix = compute_moments(S_mix, grid)

    total_scalar_mass = float(np.sum(rho_org) * grid.dV)
    bbox_scale = max(bbox_diag, 1e-12)
    diag = compute_diagnostic_numbers(
        moments_tensor, moments_mix, total_scalar_mass, bbox_scale
    )

    report_lines = []
    report_lines.append("Monopole test from .fseries geometry")
    report_lines.append("===================================")
    report_lines.append(f"File: {fseries_path}")
    report_lines.append(f"Header L: {length_L}")
    report_lines.append(f"Harmonics: {n_harmonics}")
    report_lines.append(f"Curve samples: {n_curve}")
    report_lines.append(f"Approx reconstructed length: {curve.total_length:.12e}")
    report_lines.append("")
    report_lines.append("Geometry scales")
    report_lines.append("---------------")
    report_lines.append(f"bbox_diag: {bbox_diag:.12e}")
    report_lines.append(f"rms_radius: {rms_radius:.12e}")
    report_lines.append(f"max_radius: {max_radius:.12e}")
    report_lines.append("")
    report_lines.append("Grid / coarse-graining")
    report_lines.append("----------------------")
    report_lines.append(f"grid_n: {grid_n}")
    report_lines.append(f"dx, dy, dz: {grid.dx:.12e}, {grid.dy:.12e}, {grid.dz:.12e}")
    report_lines.append(f"dV: {grid.dV:.12e}")
    report_lines.append(f"tube_radius: {tube_radius:.12e}")
    report_lines.append(f"padding_frac: {padding:.12e}")
    report_lines.append("")
    report_lines.append("Canonical SST constants used")
    report_lines.append("----------------------------")
    report_lines.append(f"rho_f: {RHO_F:.12e}")
    report_lines.append(f"v_swirl: {V_SWIRL:.12e}")
    report_lines.append(f"r_c: {R_C:.12e}")
    report_lines.append("")
    report_lines.append("Pure tensor source moments")
    report_lines.append("--------------------------")
    report_lines.append(f"Q_tensor = {moments_tensor['Q']:.12e}")
    report_lines.append(f"D_tensor = {np.asarray(moments_tensor['D'])}")
    report_lines.append("M_tensor =")
    report_lines.append(str(np.asarray(moments_tensor["M"])))
    report_lines.append("Qtf_tensor =")
    report_lines.append(str(np.asarray(moments_tensor["Qtf"])))
    report_lines.append("")
    report_lines.append("Mixed source moments")
    report_lines.append("--------------------")
    report_lines.append(f"alpha = {alpha:.12e}")
    report_lines.append(f"beta = {beta:.12e}")
    report_lines.append(f"Q_mix = {moments_mix['Q']:.12e}")
    report_lines.append(f"D_mix = {np.asarray(moments_mix['D'])}")
    report_lines.append("M_mix =")
    report_lines.append(str(np.asarray(moments_mix["M"])))
    report_lines.append("Qtf_mix =")
    report_lines.append(str(np.asarray(moments_mix["Qtf"])))
    report_lines.append("")
    report_lines.append("Scalar organized reservoir")
    report_lines.append("--------------------------")
    report_lines.append(f"Integral rho_org dV = {total_scalar_mass:.12e}")
    report_lines.append("")
    report_lines.append(
        assess_monopole_candidate(
            moments_tensor=moments_tensor,
            moments_mix=moments_mix,
            total_scalar_mass=total_scalar_mass,
            bbox_scale=bbox_scale,
        )
    )

    report = "\n".join(report_lines)
    if print_report:
        print(report)

    if report_out:
        with open(report_out, "w", encoding="utf-8") as f:
            f.write(report)

    if npz_out:
        np.savez_compressed(
            npz_out,
            theta=curve.theta,
            xyz=curve.xyz,
            tangents=curve.tangents,
            W=W,
            rho_org=rho_org,
            S_tensor=S_tensor,
            S_mix=S_mix,
            Q_tensor=np.array(moments_tensor["Q"]),
            D_tensor=np.asarray(moments_tensor["D"]),
            M_tensor=np.asarray(moments_tensor["M"]),
            Qtf_tensor=np.asarray(moments_tensor["Qtf"]),
            Q_mix=np.array(moments_mix["Q"]),
            D_mix=np.asarray(moments_mix["D"]),
            M_mix=np.asarray(moments_mix["M"]),
            Qtf_mix=np.asarray(moments_mix["Qtf"]),
        )

    path_obj = Path(fseries_path)
    stem = summary_stem if summary_stem is not None else path_obj.stem
    relp = summary_relpath if summary_relpath is not None else str(path_obj)

    return MonopoleSummaryRow(
        relpath=relp,
        stem=stem,
        ok=True,
        grid_n=grid_n,
        tube_radius=tube_radius,
        alpha=alpha,
        beta=beta,
        header_L=length_L,
        n_harmonics=n_harmonics,
        curve_length=curve.total_length,
        bbox_diag=bbox_diag,
        Q_tensor=float(moments_tensor["Q"]),
        Q_mix=float(moments_mix["Q"]),
        tensor_norm_dipole=diag.rt_d,
        tensor_norm_quad=diag.rt_m,
        mix_norm_dipole=diag.rm_d,
        mix_norm_quad=diag.rm_m,
        mix_plausible=diag.mix_plausible,
        tensor_monopole_suppressed=diag.tensor_monopole_suppressed,
        scalar_mass=total_scalar_mass,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Test monopole candidacy from an .fseries knot/link geometry.")
    parser.add_argument(
        "fseries_path",
        nargs="?",
        default=None,
        help="Path to .fseries file (omit when using --batch)",
    )
    parser.add_argument(
        "--batch",
        metavar="DIR",
        nargs="?",
        const=".",
        default=None,
        help="Run on all **/*.fseries under DIR (default: .). Writes per-knot report(s); with one "
        "(grid,tube,beta) combo: <stem>_monopole_report.txt, else <stem>_monopole_<paramtag>_report.txt.",
    )
    parser.add_argument("--n-curve", type=int, default=4000, help="Number of curve samples for reconstruction")
    parser.add_argument(
        "--grid",
        type=int,
        nargs="+",
        default=[96],
        metavar="N",
        help="Grid resolution per axis (one or more; Cartesian product with tube-radius and beta sweeps)",
    )
    parser.add_argument(
        "--tube-radius",
        type=float,
        nargs="+",
        default=[0.06],
        metavar="R",
        help="Gaussian tube radius in geometry units (one or more)",
    )
    parser.add_argument("--padding", type=float, default=0.6, help="Relative padding around bounding box")
    parser.add_argument("--alpha", type=float, default=1.0, help="Weight of scalar organized source in mixed model")
    parser.add_argument(
        "--beta",
        type=float,
        nargs="+",
        default=[1.0],
        metavar="B",
        help="Weight of tensor source in mixed model (one or more)",
    )
    parser.add_argument("--report-out", type=str, default=None, help="Optional text report output path (single-file mode only)")
    parser.add_argument("--npz-out", type=str, default=None, help="Optional npz output path (single-file mode only)")
    parser.add_argument(
        "--batch-summary",
        type=str,
        default=None,
        metavar="PATH",
        help="With --batch: write aggregate summary to this file (default: DIR/monopole_batch_summary.txt).",
    )
    args = parser.parse_args()

    sweep_combos = list(itertools.product(args.grid, args.tube_radius, args.beta))
    n_sweep = len(sweep_combos)
    if n_sweep > 1 and (args.report_out is not None or args.npz_out is not None) and args.batch is None:
        parser.error(
            "With multiple --grid / --tube-radius / --beta values, omit --report-out and --npz-out "
            "(outputs are named automatically next to the .fseries for each combination)."
        )

    if args.batch is not None:
        if args.fseries_path is not None:
            parser.error("Do not pass fseries_path together with --batch.")
        if args.report_out is not None or args.npz_out is not None:
            parser.error("--report-out and --npz-out are not used with --batch (reports are named automatically).")

        root = Path(args.batch).resolve()
        if not root.is_dir():
            print(f"Not a directory: {root}", file=sys.stderr)
            return 1

        files = sorted(root.rglob("*.fseries"))
        if not files:
            print(f"No .fseries files under {root}", file=sys.stderr)
            return 1

        rows: List[MonopoleSummaryRow] = []
        n_ok = 0
        n_total = len(files) * n_sweep
        for p in files:
            try:
                rel = str(p.resolve().relative_to(root))
            except ValueError:
                rel = str(p)
            for grid_n, tube_r, beta in sweep_combos:
                tag = _param_tag_for_filename(grid_n, tube_r, args.alpha, beta)
                report_name = (
                    f"{p.stem}_monopole_report.txt"
                    if n_sweep == 1
                    else f"{p.stem}_monopole_{tag}_report.txt"
                )
                report_path = p.parent / report_name
                try:
                    row = run_monopole_analysis(
                        str(p),
                        n_curve=args.n_curve,
                        grid_n=grid_n,
                        tube_radius=tube_r,
                        padding=args.padding,
                        alpha=args.alpha,
                        beta=beta,
                        report_out=str(report_path),
                        npz_out=None,
                        print_report=False,
                        summary_relpath=rel,
                        summary_stem=p.stem,
                    )
                    rows.append(row)
                    print(f"OK  {p} [{grid_n},{tube_r},{beta}] -> {report_path}")
                    n_ok += 1
                except Exception as e:
                    rows.append(
                        MonopoleSummaryRow(
                            relpath=rel,
                            stem=p.stem,
                            ok=False,
                            err=str(e),
                            grid_n=grid_n,
                            tube_radius=tube_r,
                            alpha=args.alpha,
                            beta=beta,
                        )
                    )
                    print(f"ERR {p} [{grid_n},{tube_r},{beta}]: {e}", file=sys.stderr)

        summary_path = Path(args.batch_summary) if args.batch_summary else (root / "monopole_batch_summary.txt")
        argv_str = " ".join(shlex.quote(a) for a in sys.argv)
        summary_text = format_batch_summary(
            root=root,
            rows=rows,
            argv_str=argv_str,
            n_curve=args.n_curve,
            grid_vals=list(args.grid),
            tube_vals=list(args.tube_radius),
            padding=args.padding,
            alpha=args.alpha,
            beta_vals=list(args.beta),
        )
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(summary_text, encoding="utf-8")
        print(f"Summary: {summary_path}")
        print(f"Batch done: {n_ok}/{n_total} runs succeeded ({len(files)} files × {n_sweep} parameter sets).")
        return 0 if n_ok == n_total else 1

    if args.fseries_path is None:
        parser.error("Provide a path to an .fseries file, or use --batch [DIR].")

    fpath = Path(args.fseries_path)
    parent = fpath.parent
    stem = fpath.stem

    for grid_n, tube_r, beta in sweep_combos:
        if n_sweep == 1:
            rout = args.report_out
            nzout = args.npz_out
            do_print = True
        else:
            tag = _param_tag_for_filename(grid_n, tube_r, args.alpha, beta)
            rout = str(parent / f"{stem}_monopole_{tag}_report.txt")
            nzout = None
            do_print = False
            print(f"--- grid={grid_n} tube_radius={tube_r} beta={beta} -> {rout}", flush=True)

        _ = run_monopole_analysis(
            str(fpath),
            n_curve=args.n_curve,
            grid_n=grid_n,
            tube_radius=tube_r,
            padding=args.padding,
            alpha=args.alpha,
            beta=beta,
            report_out=rout,
            npz_out=nzout,
            print_report=do_print,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())