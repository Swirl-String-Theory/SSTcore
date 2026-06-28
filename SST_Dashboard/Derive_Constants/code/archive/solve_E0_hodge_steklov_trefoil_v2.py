#!/usr/bin/env python3
"""
solve_E0_hodge_steklov_trefoil.py

Research prototype for the next step after reproduce_alpha_cell_closure.py.

Purpose
-------
The earlier reproducibility script extracts the local Biot-Savart coefficient A_K
and evaluates the spherical-cell alpha closure.  It does NOT derive the
zeroth-order aspect scale E0.

This script starts the E0 problem.  It builds a finite-core trefoil boundary model
and scans a Hodge/Steklov-inspired boundary-response proxy over an aspect parameter

    E = R_phi / a,

where a is the tube radius.  It computes a 2x2 period-response matrix for the
meridian/longitude cycles of the finite-core trefoil boundary and searches for
stationary points of a topological-sector action

    A_K(E) = 0.5 * n^T C(E) n,       n = (n_m, n_l).

The key change relative to a calibrated E0 workflow is this:

    E0 is never inserted into the calculation.
    E0_derived is accepted only when the computed action has an interior
    stationary point, dA/dlogE = 0, with positive second derivative.

If no such interior stationary point exists, the script reports that E0 has NOT
been derived by the chosen model.  A reference value may be plotted for comparison,
but it is never used in the computation.

Important status
----------------
This is NOT a proof of E0 = 274.074996.  It is an executable scaffold for the
eigenvalue program:

    trefoil geometry -> boundary cycles -> period-response matrix C(E)
    -> action A(E) -> dA/dlogE -> candidate stationary aspect values.

The Green kernel used here is a finite-cell proxy, not a certified FEM/BEM solution
of the full Hodge-Steklov boundary-value problem.  A proof-grade version must replace
the proxy kernel by a validated Hodge-Laplace / Steklov solver on

    Omega_E = B_R \\ T_a(K).

Usage
-----
    python solve_E0_hodge_steklov_trefoil.py

With Knot Atlas ideal.txt:

    python solve_E0_hodge_steklov_trefoil.py --ideal-txt ideal.txt --knot-id 3:1:1

Faster smoke test:

    python solve_E0_hodge_steklov_trefoil.py --n-s 80 --n-theta 12 --e-count 80

Outputs
-------
    outputs_E0_hodge_steklov/
        geometry_summary.csv
        period_matrix_scan.csv
        stationary_candidates.csv
        derived_E0_summary.csv
        alpha_from_derived_E0_summary.csv
        period_action_scan.png

Dependencies
------------
    numpy, pandas, matplotlib
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Optional downstream alpha-cell evaluation.
# These are NOT used to find E0. They are only evaluated if an interior
# stationary eigenvalue E_star has been derived by the scan.
# ---------------------------------------------------------------------------

ALPHA_CODATA_2022 = 7.2973525643e-3
C_EXACT = 299792458.0



# ---------------------------------------------------------------------------
# Fallback ideal trefoil coefficients: Gilbert / Knot Atlas 3:1:1 first 30 modes.
# Format: (k, Ax, Ay, Az, Bx, By, Bz).
# ---------------------------------------------------------------------------

FALLBACK_TREFOIL_COEFFS: List[Tuple[int, float, float, float, float, float, float]] = [
    (1, 0.374139, 0.000000, 0.000000, 0.000000, 0.373928, 0.000000),
    (2, 0.824246, 0.750260, 0.000352, 0.750450, -0.823952, -0.001991),
    (3, 0.000257, -0.000932, 0.352397, -0.000770, 0.000726, -0.386764),
    (4, 0.011652, -0.010656, 0.000743, 0.010739, 0.011613, -0.000230),
    (5, 0.010504, 0.110306, 0.000199, 0.110745, -0.010366, -0.000235),
    (6, 0.000015, -0.000006, -0.047465, -0.000050, -0.000001, 0.004595),
    (7, -0.000292, 0.002417, -0.000008, -0.002529, -0.000255, -0.000009),
    (8, 0.016487, -0.021784, 0.000041, -0.021922, -0.016421, -0.000044),
    (9, -0.000029, -0.000018, 0.011178, 0.000049, 0.000041, 0.008414),
    (10, -0.000216, -0.000290, -0.000018, 0.000311, -0.000197, -0.000044),
    (11, -0.011727, 0.002184, 0.000007, 0.002202, 0.011682, 0.000020),
    (12, 0.000026, 0.000019, -0.001308, -0.000004, -0.000019, -0.007039),
    (13, 0.000325, 0.000055, -0.000009, -0.000059, 0.000289, 0.000024),
    (14, 0.005213, 0.003201, 0.000001, 0.003210, -0.005188, 0.000010),
    (15, -0.000015, -0.000016, -0.001917, -0.000017, 0.000001, 0.003121),
    (16, -0.000136, 0.000062, 0.000019, -0.000075, -0.000112, -0.000007),
    (17, -0.000995, -0.003463, -0.000001, -0.003474, 0.000988, -0.000015),
    (18, 0.000003, 0.000008, 0.002178, 0.000019, 0.000008, -0.000615),
    (19, 0.000033, -0.000094, -0.000016, 0.000113, 0.000028, -0.000004),
    (20, -0.000999, 0.002013, -0.000000, 0.002019, 0.000998, 0.000000),
    (21, 0.000004, 0.000001, -0.001270, -0.000013, -0.000012, -0.000626),
    (22, 0.000034, 0.000060, 0.000009, -0.000072, 0.000026, 0.000010),
    (23, 0.001383, -0.000539, 0.000002, -0.000540, -0.001382, 0.000004),
    (24, -0.000005, -0.000011, 0.000344, 0.000009, 0.000007, 0.000890),
    (25, -0.000057, -0.000025, 0.000001, 0.000019, -0.000048, -0.000008),
    (26, -0.000931, -0.000356, -0.000000, -0.000357, 0.000931, -0.000005),
    (27, 0.000006, 0.000009, 0.000228, -0.000002, -0.000000, -0.000597),
    (28, 0.000040, -0.000007, -0.000004, 0.000019, 0.000036, 0.000004),
    (29, 0.000308, 0.000611, 0.000001, 0.000611, -0.000307, 0.000007),
    (30, 0.000002, 0.000001, -0.000391, -0.000006, 0.000001, 0.000195),
]


# ---------------------------------------------------------------------------
# Ideal.txt loading and Fourier evaluation.
# ---------------------------------------------------------------------------

def parse_triplet(text: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected 3 components, got {text!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def load_coeffs_from_ideal_txt(
    path: Path,
    knot_id: str,
    max_mode: Optional[int],
) -> Tuple[List[Tuple[int, float, float, float, float, float, float]], float, float, str]:
    text = path.read_text(encoding="utf-8")
    block_re = re.compile(
        rf'<AB\s+Id="{re.escape(knot_id)}"[^>]*L="([^"]+)"[^>]*D="([^"]+)"[^>]*>(.*?)</AB>',
        re.DOTALL,
    )
    match = block_re.search(text)
    if not match:
        raise ValueError(f"Knot Id {knot_id!r} not found in {path}")

    length_ref = float(match.group(1))
    diameter_ref = float(match.group(2))
    block = match.group(3)

    coeffs: List[Tuple[int, float, float, float, float, float, float]] = []
    coeff_re = re.compile(r'<Coeff\s+I="\s*([0-9]+)"\s+A="([^"]+)"\s+B="([^"]+)"\s*/?>')
    for item in coeff_re.finditer(block):
        k = int(item.group(1))
        if max_mode is not None and k > max_mode:
            continue
        ax, ay, az = parse_triplet(item.group(2))
        bx, by, bz = parse_triplet(item.group(3))
        coeffs.append((k, ax, ay, az, bx, by, bz))

    coeffs.sort(key=lambda row: row[0])
    if not coeffs:
        raise ValueError(f"No coefficients found for {knot_id!r}")

    source = f"{path.name} ({knot_id}, {len(coeffs)} modes, k_max={coeffs[-1][0]})"
    return coeffs, length_ref, diameter_ref, source


def get_coefficients(args: argparse.Namespace) -> Tuple[List[Tuple[int, float, float, float, float, float, float]], float, float, str]:
    if args.ideal_txt:
        path = Path(args.ideal_txt)
        if path.exists():
            return load_coeffs_from_ideal_txt(path, args.knot_id, args.max_mode)
        print(f"[warning] {path} not found; using embedded 30-mode fallback.")

    coeffs = list(FALLBACK_TREFOIL_COEFFS)
    if args.max_mode is not None:
        coeffs = [row for row in coeffs if row[0] <= args.max_mode]
    return coeffs, 16.371498, 1.0, f"embedded fallback ({len(coeffs)} modes)"


def eval_curve(t: np.ndarray, coeffs: List[Tuple[int, float, float, float, float, float, float]]) -> np.ndarray:
    x = np.zeros((len(t), 3), dtype=float)
    for k, ax, ay, az, bx, by, bz in coeffs:
        phase = 2.0 * math.pi * k * t
        x[:, 0] += ax * np.cos(phase) + bx * np.sin(phase)
        x[:, 1] += ay * np.cos(phase) + by * np.sin(phase)
        x[:, 2] += az * np.cos(phase) + bz * np.sin(phase)
    return x


def eval_curve_derivative(t: np.ndarray, coeffs: List[Tuple[int, float, float, float, float, float, float]]) -> np.ndarray:
    dx = np.zeros((len(t), 3), dtype=float)
    for k, ax, ay, az, bx, by, bz in coeffs:
        phase = 2.0 * math.pi * k * t
        w = 2.0 * math.pi * k
        dx[:, 0] += w * (-ax * np.sin(phase) + bx * np.cos(phase))
        dx[:, 1] += w * (-ay * np.sin(phase) + by * np.cos(phase))
        dx[:, 2] += w * (-az * np.sin(phase) + bz * np.cos(phase))
    return dx


# ---------------------------------------------------------------------------
# Geometry: centerline, parallel-transport frame, and boundary cycles.
# ---------------------------------------------------------------------------

def unit(v: np.ndarray, eps: float = 1e-14) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.clip(n, eps, None)


def rotation_matrix_from_vectors(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Return R with R @ a ~= b for unit vectors a,b."""
    a = a / max(np.linalg.norm(a), 1e-15)
    b = b / max(np.linalg.norm(b), 1e-15)
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    if c > 1.0 - 1e-12:
        return np.eye(3)
    if c < -1.0 + 1e-12:
        # 180 deg: choose an arbitrary perpendicular axis.
        axis = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(axis, a)) > 0.8:
            axis = np.array([0.0, 1.0, 0.0])
        v = unit(np.cross(a, axis)[None, :])[0]
        return -np.eye(3) + 2.0 * np.outer(v, v)
    s = float(np.linalg.norm(v))
    vx = np.array([[0.0, -v[2], v[1]],
                   [v[2], 0.0, -v[0]],
                   [-v[1], v[0], 0.0]])
    return np.eye(3) + vx + vx @ vx * ((1.0 - c) / (s * s))


def build_parallel_transport_frame(tangents: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    n = len(tangents)
    T = unit(tangents)

    # Initial normal: choose a direction least aligned with T[0].
    ref = np.array([0.0, 0.0, 1.0])
    if abs(float(np.dot(ref, T[0]))) > 0.85:
        ref = np.array([0.0, 1.0, 0.0])
    N = np.zeros_like(T)
    B = np.zeros_like(T)
    N[0] = unit((ref - np.dot(ref, T[0]) * T[0])[None, :])[0]
    B[0] = unit(np.cross(T[0], N[0])[None, :])[0]

    for i in range(1, n):
        R = rotation_matrix_from_vectors(T[i - 1], T[i])
        N[i] = R @ N[i - 1]
        N[i] = unit((N[i] - np.dot(N[i], T[i]) * T[i])[None, :])[0]
        B[i] = unit(np.cross(T[i], N[i])[None, :])[0]

    return N, B


def build_centerline_geometry(coeffs, n_s: int) -> Dict[str, np.ndarray | float]:
    t = np.linspace(0.0, 1.0, n_s, endpoint=False)
    points = eval_curve(t, coeffs)
    deriv = eval_curve_derivative(t, coeffs)
    speed = np.linalg.norm(deriv, axis=1)
    ds = speed / n_s
    T = deriv / speed[:, None]
    N, B = build_parallel_transport_frame(T)
    length = float(np.sum(ds))
    return {"t": t, "points": points, "T": T, "N": N, "B": B, "ds": ds, "length": length}


def make_loop_segments(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Closed polygon -> segment midpoints and dl vectors."""
    nxt = np.roll(points, -1, axis=0)
    mids = 0.5 * (points + nxt)
    dls = nxt - points
    return mids, dls


def build_boundary_cycles(
    geom: Dict[str, np.ndarray | float],
    tube_radius: float,
    n_theta: int,
    meridian_count: int,
    longitude_count: int,
) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """
    Build two averaged cycle-current bases on the tube boundary.

    Meridian basis:
        Average of small circular loops around the tube, sampled at several arclength stations.

    Longitude basis:
        Average of curves running along the tube at fixed theta.
    """
    X = geom["points"]  # type: ignore[assignment]
    N = geom["N"]       # type: ignore[assignment]
    B = geom["B"]       # type: ignore[assignment]
    T = geom["T"]       # type: ignore[assignment]
    n_s = len(X)

    theta = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=False)

    # Meridian loops.
    mer_mids_all = []
    mer_dls_all = []
    station_ids = np.linspace(0, n_s - 1, meridian_count, dtype=int)
    for idx in station_ids:
        loop = (
            X[idx][None, :]
            + tube_radius * np.cos(theta)[:, None] * N[idx][None, :]
            + tube_radius * np.sin(theta)[:, None] * B[idx][None, :]
        )
        mids, dls = make_loop_segments(loop)
        mer_mids_all.append(mids)
        mer_dls_all.append(dls / math.sqrt(max(1, meridian_count)))

    mer_mids = np.vstack(mer_mids_all)
    mer_dls = np.vstack(mer_dls_all)

    # Longitude loops.
    lon_mids_all = []
    lon_dls_all = []
    theta_ids = np.linspace(0, n_theta - 1, longitude_count, dtype=int)
    for j in theta_ids:
        th = theta[j]
        loop = X + tube_radius * math.cos(th) * N + tube_radius * math.sin(th) * B
        mids, dls = make_loop_segments(loop)
        lon_mids_all.append(mids)
        lon_dls_all.append(dls / math.sqrt(max(1, longitude_count)))

    lon_mids = np.vstack(lon_mids_all)
    lon_dls = np.vstack(lon_dls_all)

    return {
        "meridian": (mer_mids, mer_dls),
        "longitude": (lon_mids, lon_dls),
    }


# ---------------------------------------------------------------------------
# Finite-cell kernel and period matrix.
# ---------------------------------------------------------------------------

def finite_cell_green(
    r: np.ndarray,
    R: float,
    eps: float,
    model: str,
) -> np.ndarray:
    """
    Proxy finite-cell Green factor.

    free:
        1/sqrt(r^2 + eps^2)
    neutralized:
        1/sqrt(r^2 + eps^2) - 1/sqrt(r^2 + (2R)^2 + eps^2)
    screened:
        exp(-r/R)/sqrt(r^2 + eps^2)

    These are proxies; not exact spherical-boundary Green functions.
    """
    base = 1.0 / np.sqrt(r * r + eps * eps)
    if model == "free":
        return base
    if model == "neutralized":
        return base - 1.0 / np.sqrt(r * r + (2.0 * R) ** 2 + eps * eps)
    if model == "screened":
        return np.exp(-r / max(R, 1e-12)) * base
    raise ValueError(f"Unknown kernel model: {model}")


def loop_pair_energy(
    loop_a: Tuple[np.ndarray, np.ndarray],
    loop_b: Tuple[np.ndarray, np.ndarray],
    R: float,
    eps: float,
    kernel: str,
    block: int,
) -> float:
    pts_a, dl_a = loop_a
    pts_b, dl_b = loop_b
    n = len(pts_a)
    m = len(pts_b)

    total = 0.0
    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        pa = pts_a[i0:i1]
        da = dl_a[i0:i1]
        row = np.zeros(i1 - i0)
        for j0 in range(0, m, block):
            j1 = min(j0 + block, m)
            pb = pts_b[j0:j1]
            db = dl_b[j0:j1]
            diff = pb[None, :, :] - pa[:, None, :]
            dist = np.linalg.norm(diff, axis=2)
            dot = da @ db.T
            G = finite_cell_green(dist, R=R, eps=eps, model=kernel)
            row += np.sum(dot * G, axis=1)
        total += float(np.sum(row))
    return total / (8.0 * math.pi)


def period_matrix(cycles: Dict[str, Tuple[np.ndarray, np.ndarray]], R: float, eps: float, kernel: str, block: int) -> np.ndarray:
    mm = loop_pair_energy(cycles["meridian"], cycles["meridian"], R, eps, kernel, block)
    ll = loop_pair_energy(cycles["longitude"], cycles["longitude"], R, eps, kernel, block)
    ml = loop_pair_energy(cycles["meridian"], cycles["longitude"], R, eps, kernel, block)
    C = np.array([[mm, ml], [ml, ll]], dtype=float)
    return 0.5 * (C + C.T)


def scan_aspect(
    cycles: Dict[str, Tuple[np.ndarray, np.ndarray]],
    e_values: np.ndarray,
    tube_radius: float,
    zeta: float,
    kernel: str,
    eps_factor: float,
    sector: Tuple[int, int],
    block: int,
) -> pd.DataFrame:
    eps = eps_factor * tube_radius
    n_vec = np.array(sector, dtype=float)

    rows = []
    for E in e_values:
        R = E * tube_radius / zeta
        C = period_matrix(cycles, R=R, eps=eps, kernel=kernel, block=block)
        eigvals = np.linalg.eigvalsh(C)
        action = 0.5 * float(n_vec @ C @ n_vec)
        rows.append({
            "E": float(E),
            "R_over_a": float(R / tube_radius),
            "C_mm": C[0, 0],
            "C_ml": C[0, 1],
            "C_ll": C[1, 1],
            "lambda_min": float(eigvals[0]),
            "lambda_max": float(eigvals[-1]),
            "sector_nm": sector[0],
            "sector_nl": sector[1],
            "sector_action": action,
        })
        print(f"  E={E:12.6f}  action={action: .8e}  lambda_min={eigvals[0]: .8e}")
    df = pd.DataFrame(rows)

    logE = np.log(df["E"].to_numpy())
    A = df["sector_action"].to_numpy()
    lam = df["lambda_min"].to_numpy()

    df["d_action_dlogE"] = np.gradient(A, logE)
    df["d2_action_dlogE2"] = np.gradient(df["d_action_dlogE"].to_numpy(), logE)
    df["d_lambdamin_dlogE"] = np.gradient(lam, logE)
    df["d2_lambdamin_dlogE2"] = np.gradient(df["d_lambdamin_dlogE"].to_numpy(), logE)
    return df


def find_stationary_candidates(
    df: pd.DataFrame,
    y_col: str,
    dy_col: str,
    d2_col: str,
    min_kind: str = "minimum",
) -> pd.DataFrame:
    """
    Find interior stationary points only.

    A derived E0 is accepted only if:
        1. dY/dlogE changes sign inside the scan interval, and
        2. d2Y/dlogE2 > 0 for a minimum-type eigenvalue.

    Boundary points are written as diagnostics but are explicitly marked
    derives_E0 = False.
    """
    E = df["E"].to_numpy()
    y = df[y_col].to_numpy()
    dy = df[dy_col].to_numpy()
    d2 = df[d2_col].to_numpy()

    rows = []
    for i in range(len(E) - 1):
        if not (np.isfinite(dy[i]) and np.isfinite(dy[i + 1])):
            continue
        if dy[i] == 0.0 or dy[i] * dy[i + 1] < 0.0:
            # Linear interpolation in logE for a root of dy.
            x0 = math.log(E[i])
            x1 = math.log(E[i + 1])
            t = 0.0 if dy[i + 1] == dy[i] else -dy[i] / (dy[i + 1] - dy[i])
            x_root = x0 + t * (x1 - x0)
            E_root = math.exp(x_root)
            y_root = y[i] + t * (y[i + 1] - y[i])
            d2_root = d2[i] + t * (d2[i + 1] - d2[i])

            if d2_root > 0:
                classification = "interior_minimum"
                derives = True
            elif d2_root < 0:
                classification = "interior_maximum"
                derives = min_kind == "maximum"
            else:
                classification = "interior_flat_stationary"
                derives = False

            rows.append({
                "observable": y_col,
                "E_candidate": E_root,
                "value_interp": y_root,
                "d2_interp": d2_root,
                "classification": classification,
                "derives_E0": bool(derives),
                "is_interior": True,
                "bracket_E_lo": E[i],
                "bracket_E_hi": E[i + 1],
                "reason": "sign_change_in_log_derivative",
            })

    if not rows:
        # Report the closest derivative point as a diagnostic only.
        idx = int(np.nanargmin(np.abs(dy)))
        is_left = idx == 0
        is_right = idx == len(E) - 1
        rows.append({
            "observable": y_col,
            "E_candidate": float(E[idx]),
            "value_interp": float(y[idx]),
            "d2_interp": float(d2[idx]),
            "classification": "no_interior_stationary_point",
            "derives_E0": False,
            "is_interior": False,
            "bracket_E_lo": np.nan,
            "bracket_E_hi": np.nan,
            "reason": "closest_abs_derivative_at_boundary" if (is_left or is_right) else "closest_abs_derivative_without_sign_change",
        })
    return pd.DataFrame(rows)


def alpha_cell_from_E_star(E_star: float, ropelength: float, chi_R: float = 2.0, beta_quad: float = 1.0) -> Dict[str, object]:
    """
    Evaluate the previous spherical-cell alpha closure using a derived E_star.

    This function is downstream only. It is not used to find E_star.

    Generalized spherical-cell factor:
        eta = 1/(2 chi_R L_K)
        Xi = 1 + 3 eta + beta_quad eta^2

    For chi_R=2 and beta_quad=1 this reduces to:
        Xi = 1 + 3/(4 L_K) + 1/(16 L_K^2).
    """
    eta = 1.0 / (2.0 * chi_R * ropelength)
    xi = 1.0 + 3.0 * eta + beta_quad * eta * eta
    e_eff = E_star * (1.0 - (math.pi / 4.0) * xi / (E_star * E_star))
    alpha_cell = 2.0 / e_eff
    return {
        "E_star_derived": E_star,
        "ropelength_L_over_D": ropelength,
        "chi_R": chi_R,
        "beta_quad": beta_quad,
        "eta": eta,
        "Xi_sph": xi,
        "E_eff": e_eff,
        "alpha_cell_from_derived_E0": alpha_cell,
        "alpha_cell_inverse_from_derived_E0": 1.0 / alpha_cell,
        "alpha_CODATA_2022": ALPHA_CODATA_2022,
        "alpha_CODATA_2022_inverse": 1.0 / ALPHA_CODATA_2022,
        "relative_error_vs_CODATA_2022": (alpha_cell - ALPHA_CODATA_2022) / ALPHA_CODATA_2022,
        "v_core_pred_m_per_s": 0.5 * alpha_cell * C_EXACT,
        "status": "computed_from_derived_E_star_not_used_in_eigenvalue_scan",
    }


def summarize_derived_E0(candidates: pd.DataFrame, preferred_observable: str) -> Dict[str, object]:
    """
    Choose the first valid interior E0 candidate for the preferred observable.
    If none exists, return a no-derivation status.
    """
    valid = candidates[
        (candidates["observable"] == preferred_observable)
        & (candidates["derives_E0"] == True)
        & (candidates["is_interior"] == True)
    ].copy()

    if len(valid) == 0:
        diagnostics = candidates[candidates["observable"] == preferred_observable].copy()
        if len(diagnostics) > 0:
            row = diagnostics.iloc[0]
            return {
                "status": "E0_not_derived",
                "preferred_observable": preferred_observable,
                "E_star_derived": np.nan,
                "diagnostic_E_candidate": float(row["E_candidate"]),
                "diagnostic_classification": row["classification"],
                "diagnostic_reason": row["reason"],
                "message": "No interior stationary eigenvalue was found. E0 remains an external/conjectured input for this model.",
            }
        return {
            "status": "E0_not_derived",
            "preferred_observable": preferred_observable,
            "E_star_derived": np.nan,
            "message": "No candidate rows were produced.",
        }

    # If multiple minima exist, choose the lowest action/eigenvalue candidate.
    valid = valid.sort_values(["value_interp", "E_candidate"])
    row = valid.iloc[0]
    return {
        "status": "E0_derived",
        "preferred_observable": preferred_observable,
        "E_star_derived": float(row["E_candidate"]),
        "classification": row["classification"],
        "bracket_E_lo": float(row["bracket_E_lo"]),
        "bracket_E_hi": float(row["bracket_E_hi"]),
        "value_interp": float(row["value_interp"]),
        "d2_interp": float(row["d2_interp"]),
        "message": "Interior stationary eigenvalue found. This E_star is used as E0 in downstream alpha-cell evaluation.",
    }


def save_plot(df: pd.DataFrame, candidates: pd.DataFrame, outdir: Path, reference_e0: Optional[float]) -> None:
    fig, ax = plt.subplots(figsize=(9.0, 5.6))
    ax.plot(df["E"], df["sector_action"], lw=1.6, label="A_K(E) = 0.5 n^T C(E)n")
    ax.set_xscale("log")
    ax.set_xlabel("aspect parameter E")
    ax.set_ylabel("period-response action (proxy units)")
    ax.set_title("Finite-cell period-response scan")
    for _, row in candidates.iterrows():
        if row["observable"] == "sector_action":
            if bool(row.get("derives_E0", False)):
                ax.axvline(row["E_candidate"], ls="--", alpha=0.8, label=f"derived E*={row['E_candidate']:.6g}")
            else:
                ax.axvline(row["E_candidate"], ls="--", alpha=0.35, label=f"diagnostic E={row['E_candidate']:.6g}")
    if reference_e0 is not None:
        ax.axvline(reference_e0, ls=":", alpha=0.9, label=f"reference E0={reference_e0:.6g}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "period_action_scan.png", dpi=180)
    fig.savefig(outdir / "period_action_scan.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.0, 5.6))
    ax.axhline(0.0, lw=0.8)
    ax.plot(df["E"], df["d_action_dlogE"], lw=1.6, label="d A_K / d log(E)")
    ax.set_xscale("log")
    ax.set_xlabel("aspect parameter E")
    ax.set_ylabel("log-derivative")
    ax.set_title("Stationarity diagnostic")
    if reference_e0 is not None:
        ax.axvline(reference_e0, ls=":", alpha=0.9, label=f"reference E0={reference_e0:.6g}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "stationarity_diagnostic.png", dpi=180)
    fig.savefig(outdir / "stationarity_diagnostic.pdf")
    plt.close(fig)


def print_table(title: str, data: Dict[str, object]) -> None:
    print("\n" + title)
    print("-" * len(title))
    for k, v in data.items():
        if isinstance(v, float):
            print(f"{k:34s} = {v:.12g}")
        else:
            print(f"{k:34s} = {v}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ideal-txt", default=None, help="Optional Knot Atlas ideal.txt file.")
    parser.add_argument("--knot-id", default="3:1:1", help="Knot Id to load from ideal.txt.")
    parser.add_argument("--max-mode", type=int, default=None, help="Optional maximum Fourier mode.")
    parser.add_argument("--n-s", type=int, default=180, help="Number of arclength stations.")
    parser.add_argument("--n-theta", type=int, default=18, help="Tube cross-section samples.")
    parser.add_argument("--meridian-count", type=int, default=24, help="Number of averaged meridian loops.")
    parser.add_argument("--longitude-count", type=int, default=6, help="Number of averaged longitude loops.")
    parser.add_argument("--e-min", type=float, default=50.0, help="Minimum aspect parameter E.")
    parser.add_argument("--e-max", type=float, default=600.0, help="Maximum aspect parameter E.")
    parser.add_argument("--e-count", type=int, default=120, help="Number of E samples.")
    parser.add_argument("--sector", default="2,3", help="Topological sector n_m,n_l, e.g. 2,3.")
    parser.add_argument("--kernel", choices=["free", "neutralized", "screened"], default="neutralized")
    parser.add_argument("--zeta", type=float, default=1.0, help="R_phi = zeta * R, so R = E*a/zeta.")
    parser.add_argument("--tube-radius", type=float, default=None, help="Tube radius a. Default: D_ref/2.")
    parser.add_argument("--eps-factor", type=float, default=0.08, help="Regularization eps = eps_factor * a.")
    parser.add_argument("--block", type=int, default=256, help="Pairwise integration block size.")
    parser.add_argument("--reference-e0", type=float, default=None, help="Optional reference line in plots; not used in computation.")
    parser.add_argument("--preferred-observable", choices=["sector_action", "lambda_min"], default="sector_action", help="Observable used to accept a derived E0 eigenvalue.")
    parser.add_argument("--chi-R", type=float, default=2.0, help="Downstream spherical-cell chi_R. Not used to derive E0.")
    parser.add_argument("--beta-quad", type=float, default=1.0, help="Downstream spherical-cell quadratic coefficient. Not used to derive E0.")
    parser.add_argument("--outdir", default="outputs_E0_hodge_steklov", help="Output directory.")
    args = parser.parse_args()

    sector_parts = [int(x.strip()) for x in args.sector.split(",")]
    if len(sector_parts) != 2:
        raise ValueError("--sector must be 'n_m,n_l'")
    sector = (sector_parts[0], sector_parts[1])

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    coeffs, L_ref, D_ref, source = get_coefficients(args)
    tube_radius = 0.5 * D_ref if args.tube_radius is None else args.tube_radius

    print("Finite-core trefoil E0 Hodge/Steklov proxy scan")
    print("=" * 72)
    print(f"source                  : {source}")
    print(f"L_ref, D_ref             : {L_ref:.9f}, {D_ref:.9f}")
    print(f"tube radius a            : {tube_radius:.9f}")
    print(f"sector (n_m,n_l)         : {sector}")
    print(f"kernel                   : {args.kernel}")
    print(f"aspect scan              : {args.e_min} ... {args.e_max} ({args.e_count} samples)")
    print(f"output directory         : {outdir.resolve()}")
    print("\nSTATUS: proxy kernel only; not a proof-grade Hodge-Steklov solve.\n")

    geom = build_centerline_geometry(coeffs, args.n_s)
    cycles = build_boundary_cycles(
        geom,
        tube_radius=tube_radius,
        n_theta=args.n_theta,
        meridian_count=args.meridian_count,
        longitude_count=args.longitude_count,
    )

    geometry_summary = {
        "source": source,
        "L_ref": L_ref,
        "D_ref": D_ref,
        "ropelength_L_over_D": L_ref / D_ref,
        "n_s": args.n_s,
        "n_theta": args.n_theta,
        "centerline_length_sampled": float(geom["length"]),
        "tube_radius": tube_radius,
        "meridian_count": args.meridian_count,
        "longitude_count": args.longitude_count,
        "sector_nm": sector[0],
        "sector_nl": sector[1],
        "kernel": args.kernel,
        "eps_factor": args.eps_factor,
    }
    pd.DataFrame([geometry_summary]).to_csv(outdir / "geometry_summary.csv", index=False)
    print_table("Geometry summary", geometry_summary)

    e_values = np.logspace(math.log10(args.e_min), math.log10(args.e_max), args.e_count)
    df = scan_aspect(
        cycles,
        e_values=e_values,
        tube_radius=tube_radius,
        zeta=args.zeta,
        kernel=args.kernel,
        eps_factor=args.eps_factor,
        sector=sector,
        block=args.block,
    )
    df.to_csv(outdir / "period_matrix_scan.csv", index=False)

    cand_action = find_stationary_candidates(df, "sector_action", "d_action_dlogE", "d2_action_dlogE2")
    cand_lambda = find_stationary_candidates(df, "lambda_min", "d_lambdamin_dlogE", "d2_lambdamin_dlogE2")
    candidates = pd.concat([cand_action, cand_lambda], ignore_index=True)
    candidates.to_csv(outdir / "stationary_candidates.csv", index=False)

    derived_summary = summarize_derived_E0(candidates, args.preferred_observable)
    pd.DataFrame([derived_summary]).to_csv(outdir / "derived_E0_summary.csv", index=False)

    alpha_summary: Dict[str, object]
    if derived_summary.get("status") == "E0_derived" and np.isfinite(float(derived_summary["E_star_derived"])):
        alpha_summary = alpha_cell_from_E_star(
            float(derived_summary["E_star_derived"]),
            ropelength=L_ref / D_ref,
            chi_R=args.chi_R,
            beta_quad=args.beta_quad,
        )
    else:
        alpha_summary = {
            "status": "not_computed_because_E0_was_not_derived",
            "message": "The script refuses to compute alpha_cell from a calibrated or boundary E0.",
        }
    pd.DataFrame([alpha_summary]).to_csv(outdir / "alpha_from_derived_E0_summary.csv", index=False)

    save_plot(df, candidates, outdir, args.reference_e0)

    print("\nStationary candidates")
    print("---------------------")
    print(candidates.to_string(index=False))

    print_table("Derived E0 summary", derived_summary)
    print_table("Alpha from derived E0 summary", alpha_summary)

    print("\nOutput files")
    print("------------")
    for p in sorted(outdir.iterdir()):
        print(f"  {p.name}")

    print("\nInterpretation")
    print("--------------")
    print("E0 is treated as a derived eigenvalue only if an interior stationary point")
    print("is found. Boundary candidates and reference lines are diagnostics only.")
    print("If no interior stationary point appears, this script explicitly reports")
    print("E0_not_derived and refuses to compute alpha_cell from a calibrated E0.")
    print("A proof-grade version must replace this proxy kernel by a validated")
    print("FEM/BEM/DEC Hodge-Steklov solver on B_R \\ T_a(K).")


if __name__ == "__main__":
    main()
