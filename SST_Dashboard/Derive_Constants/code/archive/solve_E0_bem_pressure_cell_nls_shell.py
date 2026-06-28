#!/usr/bin/env python3
"""
solve_E0_bem_pressure_cell.py

Prototype BEM + pressure-compliance solver for the E0 aspect-eigenvalue problem.

This is the next step after:
    reproduce_alpha_cell_closure.py
and after the lightweight period-kernel proxy:
    solve_E0_hodge_steklov_trefoil_v2.py

Goal
----
Treat E0 as a derived eigenvalue, not as a calibration.

The script builds a finite-core trefoil tube boundary, adds a spherical outer
boundary, solves a scalar Laplace single-layer BEM response for two independent
tube-boundary modes, constructs a 2x2 response matrix C(E), and searches for an
interior stationary point of

    A_total(E) = 0.5 n^T C_BEM(E) n + A_pressure(E).

If an interior minimum is found, the script reports:

    status = E0_derived

If no interior minimum is found, it reports:

    status = E0_not_derived

and refuses to compute alpha_cell from a calibrated or boundary value.

Status
------
This is a research prototype, not a proof-grade validated FEM/BEM/DEC solver.

It is nevertheless closer to the intended Hodge-Steklov program than the earlier
free-space/neutralized period-kernel proxy because it solves a boundary integral
system for each E.

The scalar BEM modes are still proxies for the true harmonic 1-form/Hodge
period problem.  A proof-grade version must replace them by validated finite
element exterior-calculus or boundary-element Hodge-Laplace/Steklov operators.

Typical commands
----------------
Smoke test:
    python solve_E0_bem_pressure_cell.py --n-s 48 --n-theta 10 --sphere-n 160 --e-count 32

With Knot Atlas ideal.txt:
    python solve_E0_bem_pressure_cell.py --ideal-txt ideal.txt --knot-id 3:1:1

BEM only:
    python solve_E0_bem_pressure_cell.py --pressure-mode none

BEM plus geometric spherical pressure-compliance term:
    python solve_E0_bem_pressure_cell.py --pressure-mode spherical --pressure-scale-mode ropelength_16pi_over_3 --pressure-kappa 1.0

BEM plus NLS finite-shell pressure scale and Golden-branch NLS stiffness:
    python solve_E0_bem_pressure_cell.py --pressure-mode spherical --pressure-scale-mode nls_shell --pressure-kappa-mode nls_log_core

BEM plus NLS finite-shell pressure scale and shell stiffness:
    python solve_E0_bem_pressure_cell.py --pressure-mode spherical --pressure-scale-mode nls_shell --pressure-kappa-mode nls_shell_stiffness

Outputs
-------
    outputs_E0_bem_pressure/
        geometry_summary.csv
        bem_period_matrix_scan.csv
        stationary_candidates.csv
        derived_E0_summary.csv
        alpha_from_derived_E0_summary.csv
        action_scan.png/.pdf
        stationarity_diagnostic.png/.pdf
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
# Constants for downstream alpha-cell evaluation only.
# They are NOT used to find E_star.
# ---------------------------------------------------------------------------

ALPHA_CODATA_2022 = 7.2973525643e-3
C_EXACT = 299792458.0

PHI = 0.5 * (1.0 + math.sqrt(5.0))
PHI_INV = 1.0 / PHI



# ---------------------------------------------------------------------------
# Embedded fallback ideal trefoil coefficients.
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
# Fourier loading.
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


# ---------------------------------------------------------------------------
# Geometry and surface meshes.
# ---------------------------------------------------------------------------

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


def fibonacci_sphere(n: int, radius: float) -> Tuple[np.ndarray, np.ndarray]:
    """Approximately uniform sphere points and equal panel areas."""
    i = np.arange(n, dtype=float)
    z = 1.0 - 2.0 * (i + 0.5) / n
    theta = math.pi * (3.0 - math.sqrt(5.0)) * i
    r = np.sqrt(np.maximum(0.0, 1.0 - z * z))
    pts = np.column_stack([r * np.cos(theta), r * np.sin(theta), z]) * radius
    area = np.full(n, 4.0 * math.pi * radius * radius / n)
    return pts, area


def build_tube_surface(geom: Dict[str, np.ndarray | float], tube_radius: float, n_theta: int) -> Dict[str, np.ndarray]:
    X = geom["points"]  # type: ignore[assignment]
    N = geom["N"]       # type: ignore[assignment]
    B = geom["B"]       # type: ignore[assignment]
    ds = geom["ds"]     # type: ignore[assignment]
    n_s = len(X)

    theta = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=False)
    dtheta = 2.0 * math.pi / n_theta

    pts = []
    normals = []
    area = []
    phase_s = []
    phase_theta = []
    for i in range(n_s):
        for th in theta:
            radial = math.cos(th) * N[i] + math.sin(th) * B[i]
            pts.append(X[i] + tube_radius * radial)
            normals.append(radial)
            area.append(tube_radius * dtheta * ds[i])
            phase_s.append(2.0 * math.pi * i / n_s)
            phase_theta.append(th)

    return {
        "points": np.asarray(pts),
        "normals": np.asarray(normals),
        "area": np.asarray(area),
        "phase_s": np.asarray(phase_s),
        "phase_theta": np.asarray(phase_theta),
    }


# ---------------------------------------------------------------------------
# BEM solver.
# ---------------------------------------------------------------------------

def build_single_layer_matrix(points: np.ndarray, areas: np.ndarray, eps: float, block: int) -> np.ndarray:
    """
    Collocation single-layer matrix:
        V_i = sum_j (A_j / (4*pi*sqrt(|x_i-x_j|^2+eps^2))) sigma_j.
    """
    n = len(points)
    G = np.empty((n, n), dtype=float)
    pref = areas / (4.0 * math.pi)
    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        diff = points[i0:i1, None, :] - points[None, :, :]
        dist = np.linalg.norm(diff, axis=2)
        G[i0:i1, :] = pref[None, :] / np.sqrt(dist * dist + eps * eps)
    return G


def solve_bem_response(G: np.ndarray, phi: np.ndarray, reg: float) -> np.ndarray:
    A = G.copy()
    if reg > 0.0:
        A.flat[:: A.shape[0] + 1] += reg
    return np.linalg.solve(A, phi)


def bem_response_matrix(
    tube: Dict[str, np.ndarray],
    sphere_points: np.ndarray,
    sphere_area: np.ndarray,
    eps: float,
    reg: float,
    sector_mode: str,
    block: int,
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Solve scalar Dirichlet BEM for two tube boundary modes.
    Sphere boundary is grounded: phi=0 on outer boundary.

    Tube modes:
      trig:
        meridian = cos(theta)
        longitude = cos(s)
      sincos:
        meridian = cos(theta)+sin(theta) normalized by sqrt(2)
        longitude = cos(s)+sin(s) normalized by sqrt(2)

    These are scalar proxies for the true Hodge period basis.
    """
    tube_points = tube["points"]
    tube_area = tube["area"]
    points = np.vstack([tube_points, sphere_points])
    areas = np.concatenate([tube_area, sphere_area])
    nt = len(tube_points)
    nsph = len(sphere_points)

    theta = tube["phase_theta"]
    s = tube["phase_s"]

    if sector_mode == "trig":
        phi_m_tube = np.cos(theta)
        phi_l_tube = np.cos(s)
    elif sector_mode == "sincos":
        phi_m_tube = (np.cos(theta) + np.sin(theta)) / math.sqrt(2.0)
        phi_l_tube = (np.cos(s) + np.sin(s)) / math.sqrt(2.0)
    else:
        raise ValueError(f"Unknown sector_mode {sector_mode!r}")

    # Remove area-weighted tube means to avoid monopole bias.
    phi_m_tube = phi_m_tube - np.sum(phi_m_tube * tube_area) / np.sum(tube_area)
    phi_l_tube = phi_l_tube - np.sum(phi_l_tube * tube_area) / np.sum(tube_area)

    phi_m = np.concatenate([phi_m_tube, np.zeros(nsph)])
    phi_l = np.concatenate([phi_l_tube, np.zeros(nsph)])

    G = build_single_layer_matrix(points, areas, eps=eps, block=block)
    sigma_m = solve_bem_response(G, phi_m, reg=reg)
    sigma_l = solve_bem_response(G, phi_l, reg=reg)

    # Dirichlet energy bilinear form: int phi_a sigma_b dS.
    # Use total boundary areas; sphere phi is zero but retained for consistency.
    C_mm = float(np.sum(phi_m * sigma_m * areas))
    C_ll = float(np.sum(phi_l * sigma_l * areas))
    C_ml = 0.5 * float(np.sum(phi_m * sigma_l * areas) + np.sum(phi_l * sigma_m * areas))
    C = np.array([[C_mm, C_ml], [C_ml, C_ll]], dtype=float)

    meta = {
        "n_boundary_total": float(len(points)),
        "n_tube_panels": float(nt),
        "n_sphere_panels": float(nsph),
        "area_tube": float(np.sum(tube_area)),
        "area_sphere": float(np.sum(sphere_area)),
        "cond_G": float(np.linalg.cond(G)) if len(points) <= 2000 else np.nan,
    }
    return C, meta


# ---------------------------------------------------------------------------
# Pressure-compliance term and downstream alpha.
# ---------------------------------------------------------------------------

def pressure_scale_from_mode(
    mode: str,
    ropelength: float,
    input_scale: Optional[float],
    nls_shell_coeff: float = 11.0,
) -> float:
    """
    Return the pressure equilibrium aspect scale E_p.

    Modes:
      input:
        use --pressure-Ep directly.
      ropelength_16pi_over_3:
        E_p = (16*pi/3) L_K/D.
      nls_shell:
        NLS finite-shell correction:
        E_p = (16*pi/3) L * [1 - 11/(48 L^2)].

    The nls_shell coefficient is exposed as --nls-shell-coeff for sensitivity,
    but the canonical NLS candidate is 11.
    """
    if mode == "input":
        if input_scale is None or not np.isfinite(input_scale) or input_scale <= 0:
            raise ValueError("--pressure-Ep is required for --pressure-scale-mode input")
        return float(input_scale)

    if mode == "ropelength_16pi_over_3":
        return (16.0 * math.pi / 3.0) * ropelength

    if mode == "nls_shell":
        base = (16.0 * math.pi / 3.0) * ropelength
        corr = 1.0 - nls_shell_coeff / (48.0 * ropelength * ropelength)
        return base * corr

    if mode == "ropelength_4pi":
        return 4.0 * math.pi * ropelength

    if mode == "ropelength_8pi":
        return 8.0 * math.pi * ropelength

    raise ValueError(f"Unknown pressure scale mode {mode!r}")


def pressure_kappa_from_mode(
    mode: str,
    input_kappa: float,
    E_p: float,
    ropelength: float,
) -> Tuple[float, str]:
    """
    Return dimensionless pressure stiffness kappa.

    This stiffness multiplies the convex pressure enthalpy

        H_p = kappa * [x^3/3 - log(x)],  x = E/E_p,

    so the log-coordinate curvature near x=1 is approximately 3*kappa.

    Modes:
      input:
        use --pressure-kappa directly.

      nls_log_core:
        Golden-NLS ring-energy bracket:
        kappa = log(8 E_p) - phi.
        This follows the large vortex-ring NLS bracket
        E(R) ~ R [log(8R/a) - A] with A=phi.

      nls_velocity_core:
        kappa = log(8 E_p) - phi^{-1}.
        This uses the velocity bracket B=phi^{-1}; diagnostic.

      nls_geometric_mean:
        geometric mean of the two NLS brackets.

      nls_shell_stiffness:
        kappa = 8*pi*(L_K/D)^2 = pi/(2 eta_K^2), with eta_K=1/(4 L_K).
        This is the finite spherical shell stiffness candidate inferred from
        the NLS finite-core pressure scale.

      nls_shell_stiffness_half:
        kappa = 4*pi*(L_K/D)^2, diagnostic lower-stiffness shell variant.

      nls_shell_stiffness_double:
        kappa = 16*pi*(L_K/D)^2, diagnostic upper-stiffness shell variant.

      ropelength:
        kappa = L_K/D; deliberately strong pressure stiffness, diagnostic only.
    """
    if mode == "input":
        return float(input_kappa), "input --pressure-kappa"

    energy_bracket = math.log(8.0 * E_p) - PHI
    velocity_bracket = math.log(8.0 * E_p) - PHI_INV

    if mode == "nls_log_core":
        return max(energy_bracket, 1e-12), "log(8 E_p) - phi"

    if mode == "nls_velocity_core":
        return max(velocity_bracket, 1e-12), "log(8 E_p) - phi^{-1}"

    if mode == "nls_geometric_mean":
        return max(math.sqrt(max(energy_bracket, 1e-12) * max(velocity_bracket, 1e-12)), 1e-12), \
            "sqrt([log(8 E_p)-phi][log(8 E_p)-phi^{-1}])"

    if mode == "nls_shell_stiffness":
        return 8.0 * math.pi * ropelength * ropelength, "8*pi*(L_K/D)^2 = pi/(2 eta_K^2)"

    if mode == "nls_shell_stiffness_half":
        return 4.0 * math.pi * ropelength * ropelength, "4*pi*(L_K/D)^2 diagnostic"

    if mode == "nls_shell_stiffness_double":
        return 16.0 * math.pi * ropelength * ropelength, "16*pi*(L_K/D)^2 diagnostic"

    if mode == "ropelength":
        return float(ropelength), "L_K/D diagnostic stiffness"

    raise ValueError(f"Unknown pressure kappa mode {mode!r}")


def pressure_action(E: float, mode: str, kappa: float, E_p: float) -> float:
    if mode == "none" or kappa == 0.0:
        return 0.0
    if mode == "spherical":
        x = max(E / E_p, 1e-300)
        # Convex enthalpy with stationary point at E=E_p:
        # d/dlogE [x^3/3 - log x] = x^3 - 1.
        return kappa * (x**3 / 3.0 - math.log(x))
    raise ValueError(f"Unknown pressure mode {mode!r}")


def alpha_cell_from_E_star(E_star: float, ropelength: float, chi_R: float = 2.0, beta_quad: float = 1.0) -> Dict[str, object]:
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


# ---------------------------------------------------------------------------
# Scan, stationary candidates, plotting.
# ---------------------------------------------------------------------------

def scan_E_values(args, coeffs, L_ref: float, D_ref: float, source: str) -> Tuple[pd.DataFrame, Dict[str, object]]:
    ropelength = L_ref / D_ref
    tube_radius = 0.5 * D_ref if args.tube_radius is None else args.tube_radius
    geom = build_centerline_geometry(coeffs, args.n_s)
    tube = build_tube_surface(geom, tube_radius=tube_radius, n_theta=args.n_theta)

    E_p = pressure_scale_from_mode(
        args.pressure_scale_mode,
        ropelength,
        args.pressure_Ep,
        nls_shell_coeff=args.nls_shell_coeff,
    )
    kappa_eff, kappa_formula = pressure_kappa_from_mode(
        args.pressure_kappa_mode,
        args.pressure_kappa,
        E_p,
        ropelength,
    )

    e_values = np.logspace(math.log10(args.e_min), math.log10(args.e_max), args.e_count)
    sector = np.array([args.sector_nm, args.sector_nl], dtype=float)

    rows = []
    bem_meta_last: Dict[str, float] = {}
    for E in e_values:
        R = E * tube_radius / args.zeta
        sphere_points, sphere_area = fibonacci_sphere(args.sphere_n, radius=R)
        eps = args.eps_factor * tube_radius

        C, meta = bem_response_matrix(
            tube,
            sphere_points=sphere_points,
            sphere_area=sphere_area,
            eps=eps,
            reg=args.bem_reg,
            sector_mode=args.boundary_mode,
            block=args.block,
        )
        bem_meta_last = meta

        eigvals = np.linalg.eigvalsh(C)
        action_bem = 0.5 * float(sector @ C @ sector)
        action_pressure = pressure_action(E, args.pressure_mode, kappa_eff, E_p)
        action_total = action_bem + action_pressure

        rows.append({
            "E": float(E),
            "R_over_a": float(R / tube_radius),
            "C_mm": C[0, 0],
            "C_ml": C[0, 1],
            "C_ll": C[1, 1],
            "lambda_min": float(eigvals[0]),
            "lambda_max": float(eigvals[-1]),
            "sector_nm": args.sector_nm,
            "sector_nl": args.sector_nl,
            "action_bem": action_bem,
            "action_pressure": action_pressure,
            "action_total": action_total,
            "pressure_Ep": E_p,
            "pressure_kappa_eff": kappa_eff,
        })
        print(f"  E={E:12.6f}  A_bem={action_bem: .8e}  A_p={action_pressure: .8e}  A_total={action_total: .8e}")

    df = pd.DataFrame(rows)
    logE = np.log(df["E"].to_numpy())
    for col in ["action_bem", "action_pressure", "action_total", "lambda_min"]:
        vals = df[col].to_numpy()
        df[f"d_{col}_dlogE"] = np.gradient(vals, logE)
        df[f"d2_{col}_dlogE2"] = np.gradient(df[f"d_{col}_dlogE"].to_numpy(), logE)

    summary = {
        "source": source,
        "L_ref": L_ref,
        "D_ref": D_ref,
        "ropelength_L_over_D": ropelength,
        "n_s": args.n_s,
        "n_theta": args.n_theta,
        "sphere_n": args.sphere_n,
        "tube_radius": tube_radius,
        "centerline_length_sampled": float(geom["length"]),
        "sector_nm": args.sector_nm,
        "sector_nl": args.sector_nl,
        "pressure_mode": args.pressure_mode,
        "pressure_scale_mode": args.pressure_scale_mode,
        "pressure_Ep": E_p,
        "pressure_kappa_mode": args.pressure_kappa_mode,
        "pressure_kappa_input": args.pressure_kappa,
        "pressure_kappa_eff": kappa_eff,
        "pressure_kappa_formula": kappa_formula,
        "nls_shell_coeff": args.nls_shell_coeff,
        "nls_phi": PHI,
        "nls_phi_inv": PHI_INV,
        "nls_eta": 1.0 / (4.0 * ropelength),
        "nls_shell_stiffness_candidate": 8.0 * math.pi * ropelength * ropelength,
        "nls_shell_stiffness_formula": "8*pi*(L_K/D)^2 = pi/(2 eta_K^2)",
        "boundary_mode": args.boundary_mode,
        "eps_factor": args.eps_factor,
        "bem_reg": args.bem_reg,
        **bem_meta_last,
    }
    return df, summary


def find_stationary_candidates(df: pd.DataFrame, y_col: str, dy_col: str, d2_col: str) -> pd.DataFrame:
    E = df["E"].to_numpy()
    y = df[y_col].to_numpy()
    dy = df[dy_col].to_numpy()
    d2 = df[d2_col].to_numpy()

    rows = []
    for i in range(len(E) - 1):
        if not (np.isfinite(dy[i]) and np.isfinite(dy[i + 1])):
            continue
        if dy[i] == 0.0 or dy[i] * dy[i + 1] < 0.0:
            x0, x1 = math.log(E[i]), math.log(E[i + 1])
            t = 0.0 if dy[i + 1] == dy[i] else -dy[i] / (dy[i + 1] - dy[i])
            xr = x0 + t * (x1 - x0)
            Er = math.exp(xr)
            yr = y[i] + t * (y[i + 1] - y[i])
            d2r = d2[i] + t * (d2[i + 1] - d2[i])
            derives = bool(d2r > 0)
            rows.append({
                "observable": y_col,
                "E_candidate": Er,
                "value_interp": yr,
                "d2_interp": d2r,
                "classification": "interior_minimum" if d2r > 0 else "interior_maximum_or_saddle",
                "derives_E0": derives,
                "is_interior": True,
                "bracket_E_lo": E[i],
                "bracket_E_hi": E[i + 1],
                "reason": "sign_change_in_log_derivative",
            })

    if not rows:
        idx = int(np.nanargmin(np.abs(dy)))
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
            "reason": "closest_abs_derivative_at_boundary" if idx in (0, len(E)-1) else "closest_abs_derivative_without_sign_change",
        })
    return pd.DataFrame(rows)


def summarize_derived_E0(candidates: pd.DataFrame, preferred_observable: str) -> Dict[str, object]:
    valid = candidates[
        (candidates["observable"] == preferred_observable)
        & (candidates["derives_E0"] == True)
        & (candidates["is_interior"] == True)
    ].copy()
    if len(valid) == 0:
        diagnostic = candidates[candidates["observable"] == preferred_observable]
        if len(diagnostic):
            row = diagnostic.iloc[0]
            return {
                "status": "E0_not_derived",
                "preferred_observable": preferred_observable,
                "E_star_derived": np.nan,
                "diagnostic_E_candidate": float(row["E_candidate"]),
                "diagnostic_classification": row["classification"],
                "diagnostic_reason": row["reason"],
                "message": "No interior stationary eigenvalue was found. E0 remains external/conjectured for this model.",
            }
        return {"status": "E0_not_derived", "preferred_observable": preferred_observable, "E_star_derived": np.nan}
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
        "message": "Interior stationary eigenvalue found. This E_star is used as E0 downstream.",
    }


def save_plots(df: pd.DataFrame, candidates: pd.DataFrame, outdir: Path, reference_e0: Optional[float]) -> None:
    fig, ax = plt.subplots(figsize=(9, 5.6))
    ax.plot(df["E"], df["action_bem"], label="BEM action")
    if np.any(df["action_pressure"] != 0):
        ax.plot(df["E"], df["action_pressure"], label="pressure action")
    ax.plot(df["E"], df["action_total"], label="total action", lw=2.0)
    ax.set_xscale("log")
    ax.set_xlabel("aspect parameter E")
    ax.set_ylabel("action (proxy units)")
    ax.set_title("BEM/pressure finite-cell action scan")
    for _, row in candidates.iterrows():
        if row["observable"] == "action_total":
            if bool(row["derives_E0"]):
                ax.axvline(row["E_candidate"], ls="--", alpha=0.8, label=f"derived E*={row['E_candidate']:.6g}")
            else:
                ax.axvline(row["E_candidate"], ls="--", alpha=0.35, label=f"diagnostic E={row['E_candidate']:.6g}")
    if reference_e0 is not None:
        ax.axvline(reference_e0, ls=":", alpha=0.8, label=f"reference E0={reference_e0:.6g}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "action_scan.png", dpi=180)
    fig.savefig(outdir / "action_scan.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.6))
    ax.axhline(0.0, lw=0.8)
    ax.plot(df["E"], df["d_action_total_dlogE"], label="d total / d log(E)")
    ax.plot(df["E"], df["d_action_bem_dlogE"], label="d BEM / d log(E)", alpha=0.8)
    if np.any(df["action_pressure"] != 0):
        ax.plot(df["E"], df["d_action_pressure_dlogE"], label="d pressure / d log(E)", alpha=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("aspect parameter E")
    ax.set_ylabel("log-derivative")
    ax.set_title("Stationarity diagnostic")
    if reference_e0 is not None:
        ax.axvline(reference_e0, ls=":", alpha=0.8, label=f"reference E0={reference_e0:.6g}")
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
            print(f"{k:36s} = {v:.12g}")
        else:
            print(f"{k:36s} = {v}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ideal-txt", default=None)
    parser.add_argument("--knot-id", default="3:1:1")
    parser.add_argument("--max-mode", type=int, default=None)

    parser.add_argument("--n-s", type=int, default=72, help="Centerline stations.")
    parser.add_argument("--n-theta", type=int, default=12, help="Tube cross-section samples.")
    parser.add_argument("--sphere-n", type=int, default=240, help="Outer sphere boundary panels.")
    parser.add_argument("--tube-radius", type=float, default=None, help="Tube radius a; default D_ref/2.")

    parser.add_argument("--e-min", type=float, default=30.0)
    parser.add_argument("--e-max", type=float, default=1200.0)
    parser.add_argument("--e-count", type=int, default=60)
    parser.add_argument("--zeta", type=float, default=1.0, help="R_phi=zeta*R, so R=E*a/zeta.")

    parser.add_argument("--sector-nm", type=int, default=2)
    parser.add_argument("--sector-nl", type=int, default=3)
    parser.add_argument("--boundary-mode", choices=["trig", "sincos"], default="trig")

    parser.add_argument("--eps-factor", type=float, default=0.06)
    parser.add_argument("--bem-reg", type=float, default=1e-10)
    parser.add_argument("--block", type=int, default=512)

    parser.add_argument("--pressure-mode", choices=["none", "spherical"], default="none")
    parser.add_argument("--pressure-scale-mode", choices=["input", "ropelength_16pi_over_3", "nls_shell", "ropelength_4pi", "ropelength_8pi"], default="ropelength_16pi_over_3")
    parser.add_argument("--pressure-Ep", type=float, default=None, help="Pressure equilibrium scale if scale-mode=input.")
    parser.add_argument("--nls-shell-coeff", type=float, default=11.0, help="NLS finite-shell coefficient in E_p correction; canonical candidate is 11.")
    parser.add_argument("--pressure-kappa", type=float, default=1.0, help="Input kappa when --pressure-kappa-mode input.")
    parser.add_argument("--pressure-kappa-mode", choices=["input", "nls_log_core", "nls_velocity_core", "nls_geometric_mean", "nls_shell_stiffness", "nls_shell_stiffness_half", "nls_shell_stiffness_double", "ropelength"], default="input")

    parser.add_argument("--preferred-observable", choices=["action_total", "action_bem", "lambda_min"], default="action_total")
    parser.add_argument("--chi-R", type=float, default=2.0, help="Downstream alpha-cell chi_R; not used to derive E0.")
    parser.add_argument("--beta-quad", type=float, default=1.0, help="Downstream alpha-cell beta; not used to derive E0.")
    parser.add_argument("--reference-e0", type=float, default=None, help="Optional plot line only; not used.")
    parser.add_argument("--outdir", default="outputs_E0_bem_pressure")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    coeffs, L_ref, D_ref, source = get_coefficients(args)
    print("Finite-core trefoil BEM + pressure-compliance E0 scan")
    print("=" * 76)
    print(f"source                  : {source}")
    print(f"L_ref, D_ref             : {L_ref:.9f}, {D_ref:.9f}")
    print(f"pressure mode            : {args.pressure_mode}")
    print(f"pressure scale mode      : {args.pressure_scale_mode}")
    print(f"pressure kappa mode      : {args.pressure_kappa_mode}")
    print(f"output directory         : {outdir.resolve()}")
    print("\nSTATUS: scalar BEM prototype. E0 is accepted only if an interior minimum is found.\n")

    df, geom_summary = scan_E_values(args, coeffs, L_ref, D_ref, source)
    df.to_csv(outdir / "bem_period_matrix_scan.csv", index=False)
    pd.DataFrame([geom_summary]).to_csv(outdir / "geometry_summary.csv", index=False)
    with open(outdir / "model_assumptions.json", "w", encoding="utf-8") as f:
        json.dump(geom_summary, f, indent=2)

    cand_total = find_stationary_candidates(df, "action_total", "d_action_total_dlogE", "d2_action_total_dlogE2")
    cand_bem = find_stationary_candidates(df, "action_bem", "d_action_bem_dlogE", "d2_action_bem_dlogE2")
    cand_lam = find_stationary_candidates(df, "lambda_min", "d_lambda_min_dlogE", "d2_lambda_min_dlogE2")
    candidates = pd.concat([cand_total, cand_bem, cand_lam], ignore_index=True)
    candidates.to_csv(outdir / "stationary_candidates.csv", index=False)

    derived = summarize_derived_E0(candidates, args.preferred_observable)
    pd.DataFrame([derived]).to_csv(outdir / "derived_E0_summary.csv", index=False)

    if derived.get("status") == "E0_derived" and np.isfinite(float(derived["E_star_derived"])):
        alpha_summary = alpha_cell_from_E_star(
            float(derived["E_star_derived"]),
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

    save_plots(df, candidates, outdir, args.reference_e0)

    print_table("Geometry / model summary", geom_summary)
    print("\nStationary candidates")
    print("---------------------")
    print(candidates.to_string(index=False))
    print_table("Derived E0 summary", derived)
    print_table("Alpha from derived E0 summary", alpha_summary)

    print("\nOutput files")
    print("------------")
    for p in sorted(outdir.iterdir()):
        print(f"  {p.name}")

    print("\nInterpretation")
    print("--------------")
    print("E0 is derived only if action_total, action_bem, or lambda_min has an")
    print("interior stationary minimum, depending on --preferred-observable.")
    print("Pressure mode can create a finite stationary point, but then the result")
    print("is conditional on the stated pressure-compliance closure in model_assumptions.json.")
    print("For the NLS route, inspect pressure_scale_mode=nls_shell and")
    print("pressure_kappa_mode=nls_shell_stiffness. This uses the non-fitted")
    print("finite-shell stiffness kappa=8*pi*(L_K/D)^2 = pi/(2 eta_K^2).")
    print("The log-core and geometric-mean modes remain diagnostic low-stiffness variants.")


if __name__ == "__main__":
    main()
