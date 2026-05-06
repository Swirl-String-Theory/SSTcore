#!/usr/bin/env python3
"""
SST helicity-balance scan for .fseries knot files.

Expected .fseries format:
    % comment lines allowed
    % columns: ax bx ay by az bz
    ax_1 bx_1 ay_1 by_1 az_1 bz_1
    ax_2 bx_2 ay_2 by_2 az_2 bz_2
    ...

The script:
  1. parses Fourier-series knot files,
  2. evaluates the centerline,
  3. computes a Biot–Savart velocity field on a Cartesian grid,
  4. computes the curl (vorticity),
  5. forms a dimensionless SST balance diagnostic
         a_mu = 0.5 * (Hc / Hm - 1)
     in the same normalized knot units used by the input geometry.

Notes
-----
- This is an SST-only script. It contains no VAM labels, outputs, or terminology.
- The balance index is meaningful only when comparing files under the same geometric
  normalization convention. If different files are scaled differently, normalize first.
- The script prefers SSTcore bindings when available and falls back to NumPy routines.
"""

from __future__ import annotations

import glob
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from sst_exports import get_exports_dir
from fseries_compat import parse_fseries_multi, eval_fourier_block

# -----------------------------------------------------------------------------
# Optional SSTcore bindings
# -----------------------------------------------------------------------------
try:
    import SSTcore as _sstcore  # preferred local name
except ImportError:
    try:
        import sstcore as _sstcore
    except ImportError:
        _sstcore = None

HAVE_SSTCORE = False
fourier_knot_eval = None
biot_savart_velocity_grid = None
curl3d_central = None
if _sstcore is not None:
    try:
        fourier_knot_eval = getattr(_sstcore, "fourier_knot_eval", None)
        biot_savart_velocity_grid = getattr(_sstcore, "biot_savart_velocity_grid", None)
        curl3d_central = getattr(_sstcore, "curl3d_central", None)
        HAVE_SSTCORE = (biot_savart_velocity_grid is not None and curl3d_central is not None)
    except Exception:
        HAVE_SSTCORE = False

# -----------------------------------------------------------------------------
# Defaults
# -----------------------------------------------------------------------------
DEFAULT_RESOLUTIONS: Sequence[Tuple[int, float, int]] = (
    (32, 0.10, 8),
    (48, 0.08, 12),
    (64, 0.06, 16),
)
NUM_CENTERLINE_SAMPLES = 1000
# Provisional SST taxonomy seed set for balanced / amphichiral candidates.
AMPHICHIRAL_BASES = {"4_1", "6_3", "8_3", "8_9", "8_12", "12a_1202", "15331"}


# -----------------------------------------------------------------------------
# Geometry evaluation
# -----------------------------------------------------------------------------
def evaluate_fourier_series(coeffs: Dict[str, np.ndarray], s: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate a Fourier-series knot using SSTcore if available, else fseries_compat."""
    if fourier_knot_eval is not None:
        try:
            # Some bindings accept vector s, some only scalar s.
            out = fourier_knot_eval(
                coeffs["a_x"], coeffs["b_x"],
                coeffs["a_y"], coeffs["b_y"],
                coeffs["a_z"], coeffs["b_z"],
                s,
            )
            arr = np.asarray(out, dtype=float)
            if arr.ndim == 2 and arr.shape[1] == 3:
                return arr[:, 0], arr[:, 1], arr[:, 2]
        except Exception:
            pass
        try:
            pts = [
                np.asarray(
                    fourier_knot_eval(
                        coeffs["a_x"], coeffs["b_x"],
                        coeffs["a_y"], coeffs["b_y"],
                        coeffs["a_z"], coeffs["b_z"],
                        float(si),
                    ),
                    dtype=float,
                )
                for si in s
            ]
            arr = np.vstack(pts)
            if arr.ndim == 2 and arr.shape[1] == 3:
                return arr[:, 0], arr[:, 1], arr[:, 2]
        except Exception:
            pass

    return eval_fourier_block(coeffs, s)


# -----------------------------------------------------------------------------
# Biot–Savart and curl
# -----------------------------------------------------------------------------
def compute_biot_savart_velocity(x: np.ndarray, y: np.ndarray, z: np.ndarray, grid_points: np.ndarray) -> np.ndarray:
    """Velocity field on arbitrary points for a closed polyline centerline."""
    if HAVE_SSTCORE and biot_savart_velocity_grid is not None:
        poly = np.stack([x, y, z], axis=1).astype(float)
        return np.asarray(biot_savart_velocity_grid(poly, grid_points.astype(float)), dtype=float)

    # Fallback: midpoint rule for unit-circulation polyline segments.
    n = len(x)
    velocity = np.zeros_like(grid_points, dtype=float)
    for i in range(n):
        r0 = np.array([x[i], y[i], z[i]], dtype=float)
        r1 = np.array([x[(i + 1) % n], y[(i + 1) % n], z[(i + 1) % n]], dtype=float)
        dl = r1 - r0
        r_mid = 0.5 * (r0 + r1)
        R = grid_points - r_mid
        invR3 = 1.0 / (np.linalg.norm(R, axis=1) ** 3 + 1e-18)
        velocity += np.cross(dl, R) * invR3[:, None]
    return velocity * (1.0 / (4.0 * np.pi))


def compute_vorticity_full_grid(velocity: np.ndarray, shape: Tuple[int, int, int], spacing: float) -> np.ndarray:
    """Curl of velocity on a regular 3D grid."""
    if HAVE_SSTCORE and curl3d_central is not None:
        vel3 = velocity.reshape(*shape, 3).astype(float)
        curl3 = curl3d_central(vel3, float(spacing))
        return np.asarray(curl3, dtype=float).reshape(-1, 3)

    # Fallback: periodic central differences. Interior cropping reduces boundary artefacts.
    vx = velocity[:, 0].reshape(shape)
    vy = velocity[:, 1].reshape(shape)
    vz = velocity[:, 2].reshape(shape)
    h2 = 2.0 * spacing
    curl_x = (np.roll(vz, -1, 1) - np.roll(vz, 1, 1)) / h2 - (np.roll(vy, -1, 2) - np.roll(vy, 1, 2)) / h2
    curl_y = (np.roll(vx, -1, 2) - np.roll(vx, 1, 2)) / h2 - (np.roll(vz, -1, 0) - np.roll(vz, 1, 0)) / h2
    curl_z = (np.roll(vy, -1, 0) - np.roll(vy, 1, 0)) / h2 - (np.roll(vx, -1, 1) - np.roll(vx, 1, 1)) / h2
    return np.stack([curl_x, curl_y, curl_z], axis=-1).reshape(-1, 3)


# -----------------------------------------------------------------------------
# Grid helpers
# -----------------------------------------------------------------------------
def build_grid(grid_size: int, spacing: float, interior_cells: int) -> Dict[str, Any]:
    grid_range = spacing * (np.arange(grid_size) - grid_size // 2)
    X, Y, Z = np.meshgrid(grid_range, grid_range, grid_range, indexing="ij")
    grid_points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=-1)

    interior_slice = slice(interior_cells, -interior_cells)
    Xi, Yi, Zi = np.meshgrid(
        grid_range[interior_slice],
        grid_range[interior_slice],
        grid_range[interior_slice],
        indexing="ij",
    )
    r_sq = (Xi**2 + Yi**2 + Zi**2).ravel()
    return {
        "grid_points": grid_points,
        "grid_shape": (grid_size, grid_size, grid_size),
        "interior_slice": interior_slice,
        "r_sq": r_sq,
        "dV": float(spacing**3),
    }


def extract_interior_field(field: np.ndarray, shape: Tuple[int, int, int], interior_slice: slice) -> np.ndarray:
    arr = field.reshape(*shape, 3)
    sub = arr[interior_slice, :, :][:, interior_slice, :][:, :, interior_slice]
    return sub.reshape(-1, 3)


# -----------------------------------------------------------------------------
# Diagnostics
# -----------------------------------------------------------------------------
def compute_balance_index(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    grid_size: int,
    spacing: float,
    interior_cells: int,
) -> Tuple[float, float, float]:
    """
    Compute the SST balance diagnostic.

    Hc and Hm are evaluated in the normalized knot units of the input geometry.
    The returned a_mu is therefore a shape diagnostic under a fixed normalization,
    not an SI observable.
    """
    grid = build_grid(grid_size, spacing, interior_cells)
    vel = compute_biot_savart_velocity(x, y, z, grid["grid_points"])
    vort = compute_vorticity_full_grid(vel, grid["grid_shape"], spacing)

    v_sub = extract_interior_field(vel, grid["grid_shape"], grid["interior_slice"])
    w_sub = extract_interior_field(vort, grid["grid_shape"], grid["interior_slice"])

    dV = grid["dV"]
    Hc = float(np.einsum("ij,ij->", v_sub, w_sub) * dV)
    Hm = float(np.sum(np.linalg.norm(w_sub, axis=1) ** 2 * grid["r_sq"]) * dV)
    if abs(Hm) < 1e-30:
        raise ZeroDivisionError("Hm is numerically zero; balance index undefined.")
    a_mu = 0.5 * (Hc / Hm - 1.0)
    return float(a_mu), Hc, Hm


# -----------------------------------------------------------------------------
# Naming helpers
# -----------------------------------------------------------------------------
def base_id(path: str) -> str:
    """Collapse suffix variants like 4_1z, 3_1p, 12a_1202z6 to a common base."""
    s = os.path.basename(path).replace("knot.", "").replace(".fseries", "")
    m = re.match(r"((?:\d+[an]?_\d+)|15331)", s)
    return m.group(1) if m else s


def choose_primary_block(path: str) -> Tuple[str, Dict[str, np.ndarray]]:
    blocks = parse_fseries_multi(path)
    if not blocks:
        raise ValueError(f"No valid Fourier blocks found in: {path}")
    # Prefer the largest coefficient block if multiple blocks are present.
    return max(blocks, key=lambda b: b[1]["a_x"].size)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    out_dir = get_exports_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = sorted(glob.glob("./**/*.fseries", recursive=True))
    if not paths:
        print("No .fseries files found under ./Knots_FourierSeries/")
        return

    print("\n=== SST helicity-balance scan ===")
    print(f"SSTcore bindings active: {HAVE_SSTCORE}")

    s = np.linspace(0.0, 2.0 * np.pi, NUM_CENTERLINE_SAMPLES, endpoint=False)
    rows = []

    for path in paths:
        fname = os.path.basename(path)
        print(f"\n========== {fname} ===========")
        try:
            _header, coeffs = choose_primary_block(path)
            x, y, z = evaluate_fourier_series(coeffs, s)
        except Exception as exc:
            print(f"{fname}: [parse/eval failed] {exc}")
            continue

        for G, S, I in DEFAULT_RESOLUTIONS:
            try:
                a_mu, Hc, Hm = compute_balance_index(x, y, z, G, S, I)
                print(f"{fname}: a_mu({G}) = {a_mu:.8f}   [Hc={Hc:.3e}, Hm={Hm:.3e}]")
                rows.append(
                    {
                        "file": fname.replace("knot.", "").replace(".fseries", ""),
                        "base": base_id(path),
                        "grid": G,
                        "spacing": S,
                        "interior_cells": I,
                        "a_mu": a_mu,
                        "Hc": Hc,
                        "Hm": Hm,
                    }
                )
            except Exception as exc:
                print(f"{fname}: [grid {G} failed] {exc}")

    if not rows:
        print("No valid results produced.")
        return

    df = pd.DataFrame(rows)
    by_resolution_path = out_dir / "SST_helicity_by_file_and_resolution.csv"
    df.to_csv(by_resolution_path, index=False)
    print(f"\nWrote {by_resolution_path}")

    grouped = (
        df.groupby("base")
        .agg(
            a_mu_mean=("a_mu", "mean"),
            a_mu_std=("a_mu", "std"),
            n_samples=("a_mu", "count"),
            Hc_mean=("Hc", "mean"),
            Hm_mean=("Hm", "mean"),
        )
        .reset_index()
    )
    grouped["is_amphichiral_seed"] = grouped["base"].isin(AMPHICHIRAL_BASES)
    grouped["flag"] = np.where(
        grouped["is_amphichiral_seed"] & (np.abs(grouped["a_mu_mean"] + 0.5) > 0.02),
        "CHECK(balance deviates from -0.5)",
        "",
    )

    grouped_path = out_dir / "SST_helicity_by_base.csv"
    grouped.to_csv(grouped_path, index=False)
    print(f"Wrote {grouped_path}")


if __name__ == "__main__":
    main()