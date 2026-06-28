#!/usr/bin/env python3
"""
reproduce_alpha_cell_closure.py

Minimal reproducibility script for a finite-core trefoil filament
and spherical pressure-cell closure calculation.

Pipeline:
    Fourier trefoil coefficients
        -> Biot-Savart cutoff-energy scan E_BS(a)
        -> global and local-plateau extraction of A_K
        -> no-contact core-radius closure a_nc/r_c = sqrt(4*pi*A_K)
        -> spherical pressure-cell correction Xi_sph
        -> alpha_cell prediction and numerical summary table

The script is intentionally self-contained. It can either use the embedded
30-mode Gilbert ideal-trefoil coefficients or load an `ideal.txt` file with
AB-format coefficients, e.g.

    <AB Id="3:1:1" L="16.371637" D="1.0">
       <Coeff I="1" A="..." B="..." />
       ...
    </AB>

Examples:
    python reproduce_alpha_cell_closure.py
    python reproduce_alpha_cell_closure.py --ideal-txt ideal.txt --knot-id 3:1:1
    python reproduce_alpha_cell_closure.py --n-geom 4000 --n-int 4000 --a-count 24

Outputs:
    outputs_alpha_cell/bs_scan.csv
    outputs_alpha_cell/local_A_curve.csv
    outputs_alpha_cell/closure_summary.csv
    outputs_alpha_cell/alpha_cell_summary.csv
    outputs_alpha_cell/local_A_curve.png

Dependencies:
    numpy, pandas, matplotlib
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Reference constants used only for numerical evaluation of the closure table.
# ---------------------------------------------------------------------------

R_CORE_REF = 1.40897017e-15                 # m
V_CORE_REF = 1.09384563e6                   # m/s
RHO_MEDIUM = 7.0e-7                         # kg/m^3
C_EXACT = 299792458.0                       # m/s
CIRCULATION_QUANTUM = 9.68361918e-9         # m^2/s

# CODATA-2022 reference value used only for comparison, not as an input.
ALPHA_CODATA_2022 = 7.2973525643e-3

# Topological zeroth-order aspect eigenvalue from the pressure-cell model.
E0_TOPOLOGICAL = 274.074996

# Ideal trefoil ropelength L/D. If an ideal.txt file provides L,D, this is
# overwritten by L_ref/D_ref.
IDEAL_TREFOIL_ROPELENGTH = 16.371498

A_REQUIRED = 1.0 / (4.0 * math.pi)


# ---------------------------------------------------------------------------
# Embedded fallback: Gilbert ideal trefoil, Id=3:1:1, first 30 Fourier modes.
# Format: (k, Ax, Ay, Az, Bx, By, Bz), with
# X(t) = sum_k A_k cos(2*pi*k*t) + B_k sin(2*pi*k*t).
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
# Fourier loading and curve evaluation.
# ---------------------------------------------------------------------------

def parse_triplet(text: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated components, got {text!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def load_coeffs_from_ideal_txt(
    path: Path,
    knot_id: str = "3:1:1",
    max_mode: Optional[int] = None,
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

    coeffs = []
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
        raise ValueError(f"No Fourier coefficients extracted for knot {knot_id!r}")

    source = f"{path.name} ({knot_id}, {len(coeffs)} modes, k_max={coeffs[-1][0]})"
    return coeffs, length_ref, diameter_ref, source


def get_coefficients(args: argparse.Namespace) -> Tuple[List[Tuple[int, float, float, float, float, float, float]], float, float, str]:
    if args.ideal_txt:
        path = Path(args.ideal_txt)
        if path.exists():
            return load_coeffs_from_ideal_txt(path, args.knot_id, args.max_mode)
        print(f"[warning] ideal.txt path does not exist: {path}. Falling back to embedded 30-mode trefoil.")

    coeffs = list(FALLBACK_TREFOIL_COEFFS)
    if args.max_mode is not None:
        coeffs = [row for row in coeffs if row[0] <= args.max_mode]
    source = f"embedded 30-mode ideal trefoil fallback ({len(coeffs)} modes)"
    return coeffs, IDEAL_TREFOIL_ROPELENGTH, 1.0, source


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
# Geometry and Biot-Savart cutoff scan.
# ---------------------------------------------------------------------------

def circular_index_distance(ii: np.ndarray, jj: np.ndarray, n: int) -> np.ndarray:
    d = np.abs(ii[:, None] - jj[None, :])
    return np.minimum(d, n - d)


def coarse_min_self_distance(points: np.ndarray, exclusion: int, block: int) -> float:
    n = len(points)
    d_min = np.inf
    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        pi = points[i0:i1]
        ii = np.arange(i0, i1)
        for j0 in range(i0, n, block):
            j1 = min(j0 + block, n)
            pj = points[j0:j1]
            jj = np.arange(j0, j1)
            diff = pi[:, None, :] - pj[None, :, :]
            dist = np.linalg.norm(diff, axis=2)
            mask = circular_index_distance(ii, jj, n) > exclusion
            if j0 == i0:
                mask &= np.triu(np.ones_like(mask, dtype=bool), k=1)
            if np.any(mask):
                d_min = min(d_min, float(np.min(dist[mask])))
    return float(d_min)


def build_geometry(
    coeffs: List[Tuple[int, float, float, float, float, float, float]],
    n_geom: int,
    n_int: int,
    block: int,
) -> dict:
    t_full = np.linspace(0.0, 1.0, n_geom, endpoint=False)
    points_full = eval_curve(t_full, coeffs)
    deriv_full = eval_curve_derivative(t_full, coeffs)
    speed_full = np.linalg.norm(deriv_full, axis=1)
    ds_full = speed_full / n_geom
    tangents_full = deriv_full / speed_full[:, None]
    length_dimless = float(np.sum(ds_full))

    stride = 1 if n_int >= n_geom else max(1, int(math.ceil(n_geom / n_int)))
    points = points_full[::stride]
    tangents = tangents_full[::stride]
    ds = ds_full[::stride] * stride
    ds[-1] += length_dimless - float(np.sum(ds))

    exclusion = max(5, len(points) // 15)
    d_min = coarse_min_self_distance(points, exclusion, block)

    return {
        "points": points,
        "tangents": tangents,
        "ds": ds,
        "length_dimless": length_dimless,
        "d_min_dimless": d_min,
        "n_int_actual": len(points),
    }


def bs_cutoff_energy_norm(
    cutoff: float,
    points: np.ndarray,
    tangents: np.ndarray,
    ds: np.ndarray,
    block: int,
) -> float:
    """
    Dimensionless Biot-Savart cutoff integral:

        E_BS_norm(a) = (1/(8*pi)) int int_{|X-X'|>a}
                        T(s).T(s') / |X-X'| ds ds'

    This is the dimensionless coefficient used to extract A_K from
    E_BS_norm(a)/L_K = A_K log(L_K/a) + a_K + ...
    """
    n = len(points)
    total = 0.0
    all_idx = np.arange(n)

    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        pi = points[i0:i1]
        ti = tangents[i0:i1]
        dsi = ds[i0:i1]
        ii = all_idx[i0:i1]
        row_sum = np.zeros(i1 - i0, dtype=float)

        for j0 in range(0, n, block):
            j1 = min(j0 + block, n)
            pj = points[j0:j1]
            tj = tangents[j0:j1]
            dsj = ds[j0:j1]
            jj = all_idx[j0:j1]

            diff = pj[None, :, :] - pi[:, None, :]
            dist = np.linalg.norm(diff, axis=2)
            dot_tt = ti @ tj.T
            mask = (dist > cutoff) & (ii[:, None] != jj[None, :])

            contrib = np.where(mask, dot_tt / np.maximum(dist, 1e-300), 0.0)
            row_sum += contrib @ dsj

        total += float(np.sum(row_sum * dsi))

    return total / (8.0 * math.pi)


def run_bs_scan(geometry: dict, a_count: int, block: int) -> pd.DataFrame:
    ds_med = float(np.median(geometry["ds"]))
    d_min = float(geometry["d_min_dimless"])

    # Same conservative scan region as the robustness script:
    # avoid discretization-dominated cutoffs and avoid near-contact overlap.
    a_lo = max(3.0 * ds_med, d_min * 5e-4)
    a_hi = d_min * 0.35
    a_values = np.logspace(math.log10(a_lo), math.log10(a_hi), a_count)

    rows = []
    for a in a_values:
        e = bs_cutoff_energy_norm(a, geometry["points"], geometry["tangents"], geometry["ds"], block)
        rows.append({"a_dimless": a, "E_BS_norm": e, "E_BS_per_length": e / geometry["length_dimless"]})
        print(f"  cutoff a={a:.6e}  E_BS_norm={e:.8f}")

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Fit extraction.
# ---------------------------------------------------------------------------

def extract_fits(
    scan: pd.DataFrame,
    length_dimless: float,
    d_min_dimless: float,
    rel_de_thresh: float,
    plateau_frac: float,
) -> Tuple[dict, pd.DataFrame]:
    a = scan["a_dimless"].to_numpy()
    e_per_len = scan["E_BS_per_length"].to_numpy()
    e_norm = scan["E_BS_norm"].to_numpy()

    x = -np.log(a)
    y = e_per_len

    global_slope, global_intercept = np.polyfit(x, y, 1)
    global_a_k = global_intercept - global_slope * math.log(length_dimless)

    a_mid = np.sqrt(a[:-1] * a[1:])
    local_A = np.diff(y) / np.diff(x)
    rel_dE = np.abs(np.diff(e_norm)) / np.maximum(np.abs(e_norm[:-1]), 1e-300)

    local_df = pd.DataFrame({
        "a_mid_dimless": a_mid,
        "A_local": local_A,
        "rel_dE": rel_dE,
        "in_plateau": (local_A > 0.0) & (rel_dE > rel_de_thresh) & (a_mid < plateau_frac * d_min_dimless),
    })

    plateau = local_df[local_df["in_plateau"]]
    if len(plateau) > 0:
        A_plateau = float(plateau["A_local"].median())
        A_spread = float(plateau["A_local"].std(ddof=0))
        n_plateau = int(len(plateau))
        fit_method = f"plateau_{plateau_frac:.2f}"
        A_use = A_plateau
    else:
        A_plateau = float("nan")
        A_spread = float("nan")
        n_plateau = 0
        fit_method = "global_fallback"
        A_use = float(global_slope)

    summary = {
        "global_A_K": float(global_slope),
        "global_a_K": float(global_a_k),
        "plateau_A_K": A_plateau,
        "plateau_A_spread": A_spread,
        "plateau_n": n_plateau,
        "fit_method_used": fit_method,
        "A_K_used": float(A_use),
        "A_required_1_over_4pi": A_REQUIRED,
        "A_ratio_to_required": float(A_use / A_REQUIRED),
    }
    return summary, local_df


# ---------------------------------------------------------------------------
# Spherical cell closure and numerical table.
# ---------------------------------------------------------------------------

def alpha_cell_from_geometry(
    A_K: float,
    ropelength: float,
    e0: float = E0_TOPOLOGICAL,
    use_A_for_core_factor: bool = False,
) -> dict:
    """
    Spherical-cell closure.

    Robust trefoil closure gives A_K -> 1/(4*pi), hence pi^2 A_K -> pi/4.
    By default the alpha-cell formula uses the theorem-limit pi/4, not the noisy
    finite-resolution A_K. Set use_A_for_core_factor=True to instead use pi^2 A_K.
    """
    eta = 1.0 / (4.0 * ropelength)
    xi_sph = 1.0 + 3.0 * eta + eta**2

    if use_A_for_core_factor:
        core_factor = math.pi**2 * A_K
    else:
        core_factor = math.pi / 4.0

    delta = core_factor * xi_sph / (e0**2)
    e_eff = e0 * (1.0 - delta)
    alpha_cell = 2.0 / e_eff

    return {
        "ropelength_L_over_D": ropelength,
        "eta": eta,
        "Xi_sph": xi_sph,
        "core_factor": core_factor,
        "core_factor_source": "pi^2*A_K" if use_A_for_core_factor else "pi/4 theorem limit",
        "delta_cell": delta,
        "E0_topological": e0,
        "E_eff": e_eff,
        "alpha_cell": alpha_cell,
        "alpha_cell_inverse": 1.0 / alpha_cell,
        "alpha_CODATA_2022": ALPHA_CODATA_2022,
        "alpha_CODATA_2022_inverse": 1.0 / ALPHA_CODATA_2022,
        "relative_error_vs_CODATA_2022": (alpha_cell - ALPHA_CODATA_2022) / ALPHA_CODATA_2022,
        "v_core_pred_m_per_s": 0.5 * alpha_cell * C_EXACT,
    }


def closure_from_A(A_K: float) -> dict:
    a_nc_over_rc = math.sqrt(max(0.0, 4.0 * math.pi * A_K))
    return {
        "A_K": A_K,
        "A_required_1_over_4pi": A_REQUIRED,
        "A_ratio_to_required": A_K / A_REQUIRED,
        "a_nc_over_r_core": a_nc_over_rc,
        "r_core_ref_m": R_CORE_REF,
        "a_nc_m": a_nc_over_rc * R_CORE_REF,
    }


def save_plot(local_df: pd.DataFrame, outdir: Path, A_use: float) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.plot(local_df["a_mid_dimless"], local_df["A_local"], marker="o", lw=1.2, label=r"local slope $A_K(a)$")
    plateau = local_df[local_df["in_plateau"]]
    if len(plateau) > 0:
        ax.scatter(plateau["a_mid_dimless"], plateau["A_local"], s=45, label="selected plateau")
    ax.axhline(A_REQUIRED, ls="--", label=r"$1/(4\pi)$")
    ax.axhline(A_use, ls=":", label=f"A_K used = {A_use:.8f}")
    ax.set_xscale("log")
    ax.set_xlabel("cutoff midpoint a (dimensionless)")
    ax.set_ylabel(r"local logarithmic slope $A_K$")
    ax.set_title("Trefoil Biot-Savart local-slope extraction")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "local_A_curve.png", dpi=180)
    fig.savefig(outdir / "local_A_curve.pdf")
    plt.close(fig)


def print_table(title: str, data: dict) -> None:
    print("\n" + title)
    print("-" * len(title))
    for key, value in data.items():
        if isinstance(value, float):
            print(f"{key:34s} = {value:.12g}")
        else:
            print(f"{key:34s} = {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ideal-txt", default=None, help="Optional ideal.txt file with AB Fourier coefficients.")
    parser.add_argument("--knot-id", default="3:1:1", help="Knot Id to load from ideal.txt.")
    parser.add_argument("--max-mode", type=int, default=None, help="Optional maximum Fourier mode.")
    parser.add_argument("--n-geom", type=int, default=2400, help="Number of geometry samples.")
    parser.add_argument("--n-int", type=int, default=2400, help="Number of integration samples.")
    parser.add_argument("--a-count", type=int, default=22, help="Number of cutoff radii in the scan.")
    parser.add_argument("--block", type=int, default=384, help="Block size for vectorized O(N^2) integration.")
    parser.add_argument("--plateau-frac", type=float, default=0.12, help="Plateau cutoff as fraction of d_min.")
    parser.add_argument("--rel-de-thresh", type=float, default=1e-4, help="Minimum relative E change for plateau inclusion.")
    parser.add_argument("--outdir", default="outputs_alpha_cell", help="Output directory.")
    parser.add_argument(
        "--use-A-for-alpha",
        action="store_true",
        help="Use finite-resolution pi^2*A_K instead of theorem-limit pi/4 in alpha-cell formula.",
    )
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    coeffs, length_ref, diameter_ref, source = get_coefficients(args)
    ropelength = float(length_ref / diameter_ref)

    print("Finite-core trefoil / spherical-cell closure reproducibility run")
    print("=" * 72)
    print(f"coefficient source       : {source}")
    print(f"reference ropelength L/D : {ropelength:.9f}")
    print(f"n_geom, n_int target     : {args.n_geom}, {args.n_int}")
    print(f"a-count                  : {args.a_count}")
    print(f"output directory         : {outdir.resolve()}")

    geometry = build_geometry(coeffs, args.n_geom, args.n_int, args.block)
    geom_summary = {
        "coefficient_source": source,
        "n_geom": args.n_geom,
        "n_int_target": args.n_int,
        "n_int_actual": geometry["n_int_actual"],
        "length_dimless_from_samples": geometry["length_dimless"],
        "length_ref_from_coeff_file": length_ref,
        "diameter_ref_from_coeff_file": diameter_ref,
        "ropelength_L_over_D": ropelength,
        "d_min_dimless": geometry["d_min_dimless"],
        "median_ds": float(np.median(geometry["ds"])),
    }
    print_table("Geometry summary", geom_summary)

    print("\nRunning Biot-Savart cutoff scan...")
    scan = run_bs_scan(geometry, args.a_count, args.block)
    scan.to_csv(outdir / "bs_scan.csv", index=False)

    fit_summary, local_df = extract_fits(
        scan,
        geometry["length_dimless"],
        geometry["d_min_dimless"],
        args.rel_de_thresh,
        args.plateau_frac,
    )
    local_df.to_csv(outdir / "local_A_curve.csv", index=False)

    A_use = float(fit_summary["A_K_used"])
    closure = closure_from_A(A_use)
    alpha_cell = alpha_cell_from_geometry(
        A_use,
        ropelength,
        E0_TOPOLOGICAL,
        use_A_for_core_factor=args.use_A_for_alpha,
    )

    geom_df = pd.DataFrame([geom_summary])
    fit_df = pd.DataFrame([fit_summary])
    closure_df = pd.DataFrame([{**fit_summary, **closure}])
    alpha_df = pd.DataFrame([{**fit_summary, **closure, **alpha_cell}])

    geom_df.to_csv(outdir / "geometry_summary.csv", index=False)
    fit_df.to_csv(outdir / "fit_summary.csv", index=False)
    closure_df.to_csv(outdir / "closure_summary.csv", index=False)
    alpha_df.to_csv(outdir / "alpha_cell_summary.csv", index=False)

    save_plot(local_df, outdir, A_use)

    print_table("Fit summary", fit_summary)
    print_table("No-contact core closure", closure)
    print_table("Spherical-cell alpha closure", alpha_cell)

    print("\nOutput files")
    print("------------")
    for path in sorted(outdir.iterdir()):
        print(f"  {path.name}")

    print("\nRecommended citation statement for manuscript/supplement:")
    print("  This script reproduces the numerical Biot-Savart coefficient extraction")
    print("  and the stated spherical-cell closure formula. It does not replace the")
    print("  analytic assumptions listed in the appendices.")


if __name__ == "__main__":
    main()
