#!/usr/bin/env python3
"""
solve_farfield_two_cell_coupling.py

Two-cell far-field certificate for the BEM/NLS finite-cell fine-structure scale.

Purpose
-------
Given a finite-cell aspect eigenvalue E_star and trefoil ropelength L_K/D,
this script tests/certifies the far-field theorem

    V(R) = alpha_cell * hbar*c / R + O(R^-2),

in dimensionless form:

    V(R)/(hbar*c) = alpha_cell/R + O(R^-2).

The key theoretical bridge is the far-field stiffness normalization

    K_cell = E_eff / (8*pi),

where

    E_eff = E_star * [1 - (pi/(4 E_star^2))*Xi_sph],
    Xi_sph = 1 + 3/(4L) + 1/(16L^2),
    alpha_cell = 2/E_eff.

Then the massless scalar/U(1) boundary phase energy

    A_far[u] = K_cell/2 * int |grad u|^2 d^3x - sum_a q_a u(x_a)

gives the Poisson equation

    -K_cell * Laplacian(u) = sum_a q_a delta(x-x_a),

and therefore for two unit cells

    A_++(R) - A_+-(R)
      = 2 * alpha_cell/R + O(R^-2).

The certificate quantity is

    C_far(R) = R/2 * [A_++(R) - A_+-(R)],

which must converge to alpha_cell.

What this script does
---------------------
1. Loads an ideal trefoil Fourier curve from ideal.txt or an embedded fallback.
2. Builds a finite tube boundary distribution around the trefoil.
3. Normalizes the total topological charge to q=+1 or q=-1.
4. Computes the two-cell Green interaction for separations R.
5. Exports:
      two_cell_farfield_scan.csv
      farfield_fit_summary.csv
      alpha_farfield_certificate.csv
      farfield_coupling_scan.png/.pdf

Important status
----------------
This is a numerical far-field certificate for the conditional theorem

    K_cell = E_eff/(8*pi)  =>  alpha_far = 2/E_eff.

It does not by itself prove K_cell = E_eff/(8*pi) from a microscopic action.
That stiffness identification must be justified in the manuscript.  The script
does verify the 1/R law and the coefficient implied by that stiffness.

Typical usage
-------------
Using explicit E_star from the BEM/NLS batch:

    python solve_farfield_two_cell_coupling.py --ideal-txt ideal.txt --knot-id 3:1:1 --e-star 274.074904 --r-min 50 --r-max 5000 --r-count 80 --outdir outputs_farfield_two_cell

Using batch aggregate CSV:

    python solve_farfield_two_cell_coupling.py --ideal-txt ideal.txt --batch-aggregate batch_aggregate_stats.csv --r-min 50 --r-max 5000 --r-count 80 --outdir outputs_farfield_two_cell

Heavier geometry:

    python solve_farfield_two_cell_coupling.py --ideal-txt ideal.txt --n-s 240 --n-theta 24 --r-min 100 --r-max 10000 --r-count 120 --outdir outputs_farfield_two_cell_heavy
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Embedded fallback trefoil coefficients.
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
# Data loading and geometry.
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
    return coeffs, length_ref, diameter_ref, f"{path.name} ({knot_id}, {len(coeffs)} modes, k_max={coeffs[-1][0]})"


def get_coefficients(args: argparse.Namespace) -> Tuple[List[Tuple[int, float, float, float, float, float, float]], float, float, str]:
    if args.ideal_txt:
        path = Path(args.ideal_txt)
        if path.exists():
            return load_coeffs_from_ideal_txt(path, args.knot_id, args.max_mode)
        print(f"[warning] {path} not found; using embedded fallback.")

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


def unit(v: np.ndarray, eps: float = 1e-14) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.clip(n, eps, None)


def rotation_matrix_from_vectors(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / max(np.linalg.norm(a), 1e-15)
    b = b / max(np.linalg.norm(b), 1e-15)
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    if c > 1.0 - 1e-12:
        return np.eye(3)
    if c < -1.0 + 1e-12:
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


def build_tube_surface_points(geom: Dict[str, np.ndarray | float], tube_radius: float, n_theta: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return panel points and positive weights normalized by area.
    """
    X = geom["points"]  # type: ignore[assignment]
    N = geom["N"]       # type: ignore[assignment]
    B = geom["B"]       # type: ignore[assignment]
    ds = geom["ds"]     # type: ignore[assignment]
    n_s = len(X)
    theta = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=False)
    dtheta = 2.0 * math.pi / n_theta

    pts = []
    area = []
    for i in range(n_s):
        for th in theta:
            radial = math.cos(th) * N[i] + math.sin(th) * B[i]
            pts.append(X[i] + tube_radius * radial)
            area.append(tube_radius * dtheta * ds[i])

    pts = np.asarray(pts, dtype=float)
    area = np.asarray(area, dtype=float)

    # Center the distribution at its area centroid to suppress dipole terms.
    centroid = np.sum(pts * area[:, None], axis=0) / np.sum(area)
    pts = pts - centroid

    weights = area / np.sum(area)
    return pts, weights


# ---------------------------------------------------------------------------
# E_star / alpha_cell definitions.
# ---------------------------------------------------------------------------

def load_e_star_from_batch_aggregate(path: Path) -> Optional[float]:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    for col in ["E_star_mean", "E_star", "E_star_derived"]:
        if col in df.columns and len(df) > 0 and np.isfinite(df[col].iloc[0]):
            return float(df[col].iloc[0])
    return None


def compute_cell_constants(E_star: float, ropelength: float) -> Dict[str, float]:
    xi = 1.0 + 3.0 / (4.0 * ropelength) + 1.0 / (16.0 * ropelength * ropelength)
    E_eff = E_star * (1.0 - (math.pi / (4.0 * E_star * E_star)) * xi)
    alpha_cell = 2.0 / E_eff
    K_cell = E_eff / (8.0 * math.pi)
    return {
        "ropelength_L_over_D": ropelength,
        "Xi_sph": xi,
        "E_star": E_star,
        "E_eff": E_eff,
        "alpha_cell": alpha_cell,
        "alpha_cell_inverse": 1.0 / alpha_cell,
        "K_cell": K_cell,
        "K_cell_formula_value": E_eff / (8.0 * math.pi),
    }


# ---------------------------------------------------------------------------
# Two-cell far-field calculation.
# ---------------------------------------------------------------------------

def pair_green_average(
    pts: np.ndarray,
    weights: np.ndarray,
    R: float,
    axis: str,
    eps: float,
    block: int,
) -> float:
    """
    Compute I(R) = sum_i sum_j w_i w_j / sqrt(|Rvec + y_j - x_i|^2 + eps^2).
    """
    if axis == "x":
        Rvec = np.array([R, 0.0, 0.0])
    elif axis == "y":
        Rvec = np.array([0.0, R, 0.0])
    elif axis == "z":
        Rvec = np.array([0.0, 0.0, R])
    else:
        raise ValueError("--axis must be x, y, or z")

    n = len(pts)
    total = 0.0
    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        pi = pts[i0:i1]
        wi = weights[i0:i1]
        subtotal = np.zeros(i1 - i0)
        for j0 in range(0, n, block):
            j1 = min(j0 + block, n)
            pj = pts[j0:j1]
            wj = weights[j0:j1]
            diff = Rvec[None, None, :] + pj[None, :, :] - pi[:, None, :]
            dist = np.linalg.norm(diff, axis=2)
            subtotal += np.sum(wj[None, :] / np.sqrt(dist * dist + eps * eps), axis=1)
        total += float(np.sum(wi * subtotal))
    return total


def scan_farfield(
    pts: np.ndarray,
    weights: np.ndarray,
    R_values: np.ndarray,
    constants: Dict[str, float],
    axis: str,
    eps: float,
    block: int,
) -> pd.DataFrame:
    alpha = constants["alpha_cell"]
    K = constants["K_cell"]
    rows = []

    for R in R_values:
        I = pair_green_average(pts, weights, R=R, axis=axis, eps=eps, block=block)
        # Dimensionless pair interaction in units of hbar*c.
        A_pair = I / (4.0 * math.pi * K)
        A_pp_minus_self = +A_pair
        A_pm_minus_self = -A_pair
        C_far = R * (A_pp_minus_self - A_pm_minus_self) / 2.0

        rows.append({
            "R": float(R),
            "I_green_average": float(I),
            "R_times_I": float(R * I),
            "A_pair_pp_minus_self": float(A_pp_minus_self),
            "A_pair_pm_minus_self": float(A_pm_minus_self),
            "A_pp_minus_A_pm": float(A_pp_minus_self - A_pm_minus_self),
            "C_far_R": float(C_far),
            "alpha_cell": float(alpha),
            "relative_error_C_far": float((C_far - alpha) / alpha),
            "abs_error_C_far": float(C_far - alpha),
        })
        print(f"  R={R:12.6g}  R*I={R*I:.12g}  C_far={C_far:.12g}  rel.err={(C_far-alpha)/alpha:.3e}")

    return pd.DataFrame(rows)


def fit_farfield(df: pd.DataFrame, fit_fraction: float, poly_order: int) -> Dict[str, float | str]:
    """
    Fit C_far(R) = c0 + c1/R + c2/R^2 + ...
    using the largest fit_fraction of R values.
    """
    fit_fraction = min(max(fit_fraction, 0.1), 1.0)
    n = len(df)
    start = int(math.floor((1.0 - fit_fraction) * n))
    sub = df.sort_values("R").iloc[start:].copy()
    x = 1.0 / sub["R"].to_numpy()
    y = sub["C_far_R"].to_numpy()
    order = min(poly_order, len(sub) - 1)
    coeff = np.polyfit(x, y, deg=order)
    intercept = float(coeff[-1])
    pred = np.polyval(coeff, x)
    rms = float(np.sqrt(np.mean((pred - y) ** 2)))

    return {
        "fit_model": f"C_far = c0 + c1/R + ... + c{order}/R^{order}",
        "fit_fraction_largest_R": fit_fraction,
        "n_fit_points": int(len(sub)),
        "poly_order": int(order),
        "C_far_intercept": intercept,
        "fit_rms": rms,
        "fit_R_min": float(sub["R"].min()),
        "fit_R_max": float(sub["R"].max()),
        "poly_coefficients_high_to_low": json.dumps([float(c) for c in coeff]),
    }


def make_certificate(scan: pd.DataFrame, fit: Dict[str, float | str], constants: Dict[str, float], tolerance: float) -> Dict[str, float | str | bool]:
    alpha = constants["alpha_cell"]
    c0 = float(fit["C_far_intercept"])
    rel = (c0 - alpha) / alpha
    max_tail_rel = float(np.max(np.abs(scan.tail(max(3, len(scan)//5))["relative_error_C_far"])))
    status = "pass" if abs(rel) <= tolerance else "fail"

    return {
        "status": status,
        "statement": "lim_{R->infty} C_far(R) = alpha_cell within the stated numerical fit tolerance",
        "alpha_cell": alpha,
        "alpha_cell_inverse": constants["alpha_cell_inverse"],
        "E_star": constants["E_star"],
        "E_eff": constants["E_eff"],
        "K_cell": constants["K_cell"],
        "C_far_intercept": c0,
        "relative_error_intercept_vs_alpha": rel,
        "abs_error_intercept_vs_alpha": c0 - alpha,
        "tail_max_abs_relative_error": max_tail_rel,
        "tolerance": tolerance,
        "proof_status": (
            "numerical_certificate_for_conditional_farfield_theorem; "
            "requires independent justification of K_cell=E_eff/(8*pi)"
        ),
    }


def save_plots(scan: pd.DataFrame, fit: Dict[str, float | str], constants: Dict[str, float], outdir: Path) -> None:
    alpha = constants["alpha_cell"]
    fig, ax = plt.subplots(figsize=(9, 5.6))
    ax.plot(scan["R"], scan["C_far_R"], marker="o", ms=3, lw=1.2, label=r"$C_{\rm far}(R)$")
    ax.axhline(alpha, ls="--", label=r"$\alpha_{\rm cell}$")
    ax.set_xscale("log")
    ax.set_xlabel("cell separation R")
    ax.set_ylabel("far-field coefficient")
    ax.set_title("Two-cell far-field coefficient")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "farfield_coupling_scan.png", dpi=180)
    fig.savefig(outdir / "farfield_coupling_scan.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.6))
    ax.plot(1.0 / scan["R"], scan["C_far_R"], marker="o", ms=3, lw=1.2, label=r"$C_{\rm far}$ vs $1/R$")
    ax.axhline(alpha, ls="--", label=r"$\alpha_{\rm cell}$")
    ax.axhline(float(fit["C_far_intercept"]), ls=":", label="fit intercept")
    ax.set_xlabel("1/R")
    ax.set_ylabel("far-field coefficient")
    ax.set_title("Far-field intercept fit")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "farfield_intercept_fit.png", dpi=180)
    fig.savefig(outdir / "farfield_intercept_fit.pdf")
    plt.close(fig)


def print_table(title: str, data: Dict[str, object]) -> None:
    print("\n" + title)
    print("-" * len(title))
    for k, v in data.items():
        if isinstance(v, float):
            print(f"{k:42s} = {v:.12g}")
        else:
            print(f"{k:42s} = {v}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--ideal-txt", default=None, help="Optional Knot Atlas ideal.txt.")
    parser.add_argument("--knot-id", default="3:1:1")
    parser.add_argument("--max-mode", type=int, default=None)

    parser.add_argument("--batch-aggregate", default=None, help="Optional batch_aggregate_stats.csv with E_star_mean.")
    parser.add_argument("--e-star", type=float, default=None, help="Aspect eigenvalue from BEM/NLS batch.")
    parser.add_argument("--default-e-star", type=float, default=274.074904, help="Fallback E_star if no CSV or --e-star is supplied.")
    parser.add_argument("--use-default-e-star", action="store_true", help="Allow fallback E_star without CSV or explicit --e-star.")

    parser.add_argument("--n-s", type=int, default=180)
    parser.add_argument("--n-theta", type=int, default=18)
    parser.add_argument("--tube-radius", type=float, default=None, help="Tube radius a; default D_ref/2.")

    parser.add_argument("--r-min", type=float, default=50.0)
    parser.add_argument("--r-max", type=float, default=5000.0)
    parser.add_argument("--r-count", type=int, default=80)
    parser.add_argument("--axis", choices=["x", "y", "z"], default="x")
    parser.add_argument("--eps-factor", type=float, default=0.0, help="Regularization eps = eps_factor * tube_radius.")
    parser.add_argument("--block", type=int, default=512)

    parser.add_argument("--fit-fraction", type=float, default=0.5, help="Use largest fraction of R values for intercept fit.")
    parser.add_argument("--fit-order", type=int, default=2)
    parser.add_argument("--tolerance", type=float, default=1e-6, help="Relative tolerance for certificate pass/fail.")

    parser.add_argument("--outdir", default="outputs_farfield_two_cell")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    coeffs, L_ref, D_ref, source = get_coefficients(args)
    ropelength = L_ref / D_ref

    # Determine E_star.
    e_star_source = "explicit --e-star"
    if args.e_star is not None:
        E_star = float(args.e_star)
    elif args.batch_aggregate:
        loaded = load_e_star_from_batch_aggregate(Path(args.batch_aggregate))
        if loaded is None:
            raise ValueError(f"Could not read E_star_mean from {args.batch_aggregate}")
        E_star = loaded
        e_star_source = f"batch aggregate {args.batch_aggregate}"
    elif args.use_default_e_star:
        E_star = float(args.default_e_star)
        e_star_source = "fallback --default-e-star; use only for quick tests"
    else:
        raise ValueError("Provide --e-star, --batch-aggregate, or --use-default-e-star.")

    constants = compute_cell_constants(E_star=E_star, ropelength=ropelength)

    tube_radius = 0.5 * D_ref if args.tube_radius is None else args.tube_radius
    geom = build_centerline_geometry(coeffs, args.n_s)
    pts, weights = build_tube_surface_points(geom, tube_radius=tube_radius, n_theta=args.n_theta)
    eps = args.eps_factor * tube_radius

    R_values = np.logspace(math.log10(args.r_min), math.log10(args.r_max), args.r_count)

    print("Two-cell far-field coupling certificate")
    print("=" * 76)
    print(f"source                  : {source}")
    print(f"E_star source            : {e_star_source}")
    print(f"E_star                   : {E_star:.12g}")
    print(f"E_eff                    : {constants['E_eff']:.12g}")
    print(f"alpha_cell               : {constants['alpha_cell']:.12g}")
    print(f"alpha_cell^-1            : {constants['alpha_cell_inverse']:.12g}")
    print(f"K_cell                   : {constants['K_cell']:.12g}")
    print(f"surface panels           : {len(pts)}")
    print(f"R scan                   : {args.r_min} ... {args.r_max}, count={args.r_count}")
    print(f"outdir                   : {outdir.resolve()}")
    print()

    scan = scan_farfield(
        pts=pts,
        weights=weights,
        R_values=R_values,
        constants=constants,
        axis=args.axis,
        eps=eps,
        block=args.block,
    )
    scan.to_csv(outdir / "two_cell_farfield_scan.csv", index=False)

    fit = fit_farfield(scan, fit_fraction=args.fit_fraction, poly_order=args.fit_order)
    pd.DataFrame([fit]).to_csv(outdir / "farfield_fit_summary.csv", index=False)

    cert = make_certificate(scan, fit, constants, tolerance=args.tolerance)
    pd.DataFrame([cert]).to_csv(outdir / "alpha_farfield_certificate.csv", index=False)

    metadata = {
        "source": source,
        "E_star_source": e_star_source,
        "L_ref": L_ref,
        "D_ref": D_ref,
        "ropelength_L_over_D": ropelength,
        "n_s": args.n_s,
        "n_theta": args.n_theta,
        "tube_radius": tube_radius,
        "surface_panels": len(pts),
        "axis": args.axis,
        "eps_factor": args.eps_factor,
        "block": args.block,
        **constants,
    }
    with open(outdir / "farfield_model_assumptions.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    save_plots(scan, fit, constants, outdir)

    print_table("Fit summary", fit)
    print_table("Alpha far-field certificate", cert)

    print("\nOutput files")
    print("------------")
    for p in sorted(outdir.iterdir()):
        print(f"  {p.name}")

    print("\nInterpretation")
    print("--------------")
    print("If status=pass, the numerical scan certifies the conditional theorem")
    print("K_cell=E_eff/(8*pi) => lim_{R->infty} C_far(R)=alpha_cell.")
    print("It does not independently derive K_cell; that stiffness normalization")
    print("must be justified in the far-field section of the manuscript.")


if __name__ == "__main__":
    main()
