#!/usr/bin/env python3
import os
import re
import math
import glob
import argparse
import csv
from datetime import datetime

import numpy as np
import pandas as pd


# ============================================================
# Constants: user-provided SST/VAM parameters
# ============================================================
C_e = 1_093_845.63             # m/s
r_c = 1.40897017e-15           # m
rho_fluid = 7.0e-7             # kg/m^3
rho_energy = 3.49924562e35     # J/m^3
c = 299_792_458.0              # m/s
alpha = 1 / 137.035999084
phi = (1 + 5**0.5) / 2
VOL_BASELINE_VALUE = 2.029883212819307  # Vol(4_1)

# Derived per-meter coefficients (kg/m)
E_density_fluid = 0.5 * rho_fluid * C_e**2
tube_area = math.pi * r_c**2
K_fluid = (4 / (alpha * phi)) * (E_density_fluid / c**2) * tube_area
K_energy = (4 / (alpha * phi)) * (rho_energy / c**2) * tube_area


# ============================================================
# File parsing
# ============================================================
def load_fseries_matrix(path):
    """
    Load plain numeric .fseries:
      columns [Ax, Bx, Ay, By, Az, Bz]
      row j corresponds to harmonic j = 1..N
    Skips comment/non-numeric lines.
    """
    rows = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("%") or s.startswith("#"):
                continue
            try:
                vals = [float(x) for x in s.replace(",", " ").split()]
            except ValueError:
                continue
            if len(vals) >= 6:
                rows.append(vals[:6])

    if not rows:
        return np.zeros((0, 6), dtype=float)

    return np.array(rows, dtype=float)


def load_ideal_matrix(path):
    """
    Load ideal-like XML-ish format with lines such as:
      <Coeff I="  1" A=" ax, ay, az" B=" bx, by, bz" />
    Returns numeric array of shape (N,6):
      [Ax, Bx, Ay, By, Az, Bz]
    sorted by harmonic I
    """
    coeffs = []
    patt = re.compile(
        r'<Coeff\s+I="([^"]+)"\s+A="([^"]+)"\s+B="([^"]+)"'
    )

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = patt.search(line)
            if not m:
                continue

            i_raw, a_raw, b_raw = m.groups()
            try:
                idx = int(str(i_raw).strip())
                A = [float(x.strip()) for x in a_raw.split(",")]
                B = [float(x.strip()) for x in b_raw.split(",")]
            except Exception:
                continue

            if len(A) != 3 or len(B) != 3:
                continue

            ax, ay, az = A
            bx, by, bz = B
            coeffs.append((idx, [ax, bx, ay, by, az, bz]))

    if not coeffs:
        return np.zeros((0, 6), dtype=float)

    coeffs.sort(key=lambda x: x[0])

    max_idx = coeffs[-1][0]
    arr = np.zeros((max_idx, 6), dtype=float)

    for idx, row in coeffs:
        if idx >= 1:
            arr[idx - 1, :] = row

    return arr


def load_coeff_matrix(path, input_format="auto"):
    ext = os.path.splitext(path)[1].lower()
    base = os.path.basename(path).lower()

    if input_format == "fseries":
        return load_fseries_matrix(path), "fseries"

    if input_format == "ideal":
        return load_ideal_matrix(path), "ideal"

    # auto
    if ext == ".fseries":
        return load_fseries_matrix(path), "fseries"

    if ext == ".txt" and base.endswith("_ideal.txt"):
        return load_ideal_matrix(path), "ideal"

    # fallback attempt
    coeffs = load_ideal_matrix(path)
    if coeffs.size > 0:
        return coeffs, "ideal"

    coeffs = load_fseries_matrix(path)
    if coeffs.size > 0:
        return coeffs, "fseries"

    return np.zeros((0, 6), dtype=float), "unknown"


# ============================================================
# Knot id parsing
# ============================================================
def parse_knot_id_from_filename(fname):
    """
    Examples:
      knot_3.1.fseries    -> 3_1
      knot_3.1_ideal.txt  -> 3_1
      knot.3_1.fseries    -> 3_1
    """
    base = os.path.basename(fname)

    m = re.search(r'knot_(\d+)\.(\d+)(?:_ideal)?(?:\.[^.]+)?$', base)
    if m:
        return f"{m.group(1)}_{m.group(2)}"

    m = re.search(r'knot\.(\d+)_(\d+)(?:\.[^.]+)?$', base)
    if m:
        return f"{m.group(1)}_{m.group(2)}"

    stem = os.path.splitext(base)[0]
    return stem


def discover_ids(files):
    seen = set()
    out = []
    for f in files:
        kid = parse_knot_id_from_filename(f)
        if kid not in seen:
            seen.add(kid)
            out.append(kid)
    return out


# ============================================================
# Fourier geometry
# ============================================================
def eval_series(coeffs, t):
    """
    Return r(t) and r'(t) from Fourier coefficients.
    coeffs shape: (N,6) columns [Ax, Bx, Ay, By, Az, Bz]
    row j-1 corresponds to harmonic j.
    """
    t = np.asarray(t, dtype=float)

    if coeffs.size == 0:
        return np.zeros((t.size, 3)), np.zeros((t.size, 3))

    N = coeffs.shape[0]
    n = np.arange(1, N + 1, dtype=float).reshape(-1, 1)  # critical fix
    nt = n * t.reshape(1, -1)

    cos_nt = np.cos(nt)
    sin_nt = np.sin(nt)

    Ax, Bx, Ay, By, Az, Bz = [coeffs[:, i].reshape(-1, 1) for i in range(6)]

    x = (Ax * cos_nt + Bx * sin_nt).sum(axis=0)
    y = (Ay * cos_nt + By * sin_nt).sum(axis=0)
    z = (Az * cos_nt + Bz * sin_nt).sum(axis=0)
    r = np.stack([x, y, z], axis=1)

    x_t = ((-n * Ax) * sin_nt + (n * Bx) * cos_nt).sum(axis=0)
    y_t = ((-n * Ay) * sin_nt + (n * By) * cos_nt).sum(axis=0)
    z_t = ((-n * Az) * sin_nt + (n * Bz) * cos_nt).sum(axis=0)
    r_t = np.stack([x_t, y_t, z_t], axis=1)

    return r, r_t


def curve_length(r_t, dt):
    return float(np.sum(np.linalg.norm(r_t, axis=1)) * dt)


def true_closure_error(coeffs):
    r0, _ = eval_series(coeffs, np.array([0.0]))
    r2pi, _ = eval_series(coeffs, np.array([2 * math.pi]))
    return float(np.linalg.norm(r0[0] - r2pi[0]))


# ============================================================
# Invariants
# ============================================================
def writhe_gauss(r, r_t, dt, maxM=500):
    """
    Discretized Gauss writhe integral, O(M^2).
    Downsamples if needed.
    """
    M = r.shape[0]
    if M > maxM:
        idx = np.linspace(0, M - 1, maxM, dtype=int)
        r = r[idx]
        r_t = r_t[idx]
        M = maxM
        dt = 2 * math.pi / M

    Ri = r[:, None, :]
    Rj = r[None, :, :]
    dR = Ri - Rj
    dist = np.linalg.norm(dR, axis=2)

    # scale-aware threshold
    bbox_min = np.min(r, axis=0)
    bbox_max = np.max(r, axis=0)
    bbox_diag = float(np.linalg.norm(bbox_max - bbox_min))
    eps = max(1e-12, 1e-9 * max(bbox_diag, 1.0))

    mask = dist > eps

    Ti = r_t[:, None, :]
    Tj = r_t[None, :, :]
    cross = np.cross(Ti, Tj)
    num = (cross * dR).sum(axis=2)

    kernel = np.zeros_like(num)
    kernel[mask] = num[mask] / (dist[mask] ** 3)

    Wr = (dt * dt) * kernel.sum() / (4 * math.pi)
    return float(Wr)


def random_unit_vectors(k, seed=12345):
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(k, 3))
    v /= np.linalg.norm(v, axis=1, keepdims=True) + 1e-15
    return v


def estimate_crossing_number(r, directions=24, maxM=280, seed=12345):
    """
    Projection-based crossing estimator.
    Not an exact invariant; fast surrogate.
    """
    M = r.shape[0]
    if M > maxM:
        idx = np.linspace(0, M - 1, maxM, dtype=int)
        r = r[idx]
        M = maxM

    P = r
    Q = np.roll(r, -1, axis=0)

    min_cross = None

    for d in random_unit_vectors(directions, seed=seed):
        w = d / (np.linalg.norm(d) + 1e-15)
        tmp = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(tmp, w)) > 0.9:
            tmp = np.array([0.0, 1.0, 0.0])

        u = np.cross(w, tmp)
        u /= np.linalg.norm(u) + 1e-15
        v = np.cross(w, u)

        P2 = np.stack([P @ u, P @ v], axis=1)
        Q2 = np.stack([Q @ u, Q @ v], axis=1)

        count = 0

        for i in range(M):
            p1, p2 = P2[i], Q2[i]
            pminx, pmaxx = min(p1[0], p2[0]), max(p1[0], p2[0])
            pminy, pmaxy = min(p1[1], p2[1]), max(p1[1], p2[1])

            for j in range(i + 2, M):
                if j == (i - 1) % M:
                    continue

                q1, q2 = P2[j], Q2[j]

                if (
                        pmaxx < min(q1[0], q2[0])
                        or max(q1[0], q2[0]) < pminx
                        or pmaxy < min(q1[1], q2[1])
                        or max(q1[1], q2[1]) < pminy
                ):
                    continue

                def orient(a, b, c):
                    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

                o1 = orient(p1, p2, q1)
                o2 = orient(p1, p2, q2)
                o3 = orient(q1, q2, p1)
                o4 = orient(q1, q2, p2)

                if o1 == 0 and o2 == 0 and o3 == 0 and o4 == 0:
                    continue

                if (o1 * o2 < 0) and (o3 * o4 < 0):
                    count += 1

        if min_cross is None or count < min_cross:
            min_cross = count

    return int(min_cross if min_cross is not None else 0)


# ============================================================
# Reconstruction diagnostics
# ============================================================
def reconstruction_metrics(coeffs, samples=1500):
    t = np.linspace(0, 2 * math.pi, samples, endpoint=False)
    dt = 2 * math.pi / samples
    r, r_t = eval_series(coeffs, t)

    # Reconstruct again from same coeffs: algebraically exact at machine precision.
    # Here diagnostic mostly captures numerical scale/geometry summaries.
    r2, _ = eval_series(coeffs, t)
    err = np.linalg.norm(r - r2, axis=1)

    rms = float(np.sqrt(np.mean(err**2)))
    mx = float(np.max(err))

    bbox_min = np.min(r, axis=0)
    bbox_max = np.max(r, axis=0)
    bbox_diag = float(np.linalg.norm(bbox_max - bbox_min))

    rms_radius = float(np.sqrt(np.mean(np.sum(r**2, axis=1))))
    length_series = curve_length(r_t, dt)

    return {
        "recon_rms_error": rms,
        "recon_max_error": mx,
        "bbox_diag": bbox_diag,
        "rms_radius": rms_radius,
        "length_series_units": length_series,
    }


# ============================================================
# Metadata
# ============================================================
def load_meta_table(meta_path):
    if not meta_path or not os.path.exists(meta_path):
        return None

    meta = pd.read_csv(meta_path)
    cols = {c.lower(): c for c in meta.columns}

    def pick(name):
        key = name.lower()
        return meta[cols[key]] if key in cols else None

    std = pd.DataFrame()
    std["knot_id"] = pick("knot_id").astype(str) if pick("knot_id") is not None else ""
    std["chiral"] = pick("chiral").astype(str).str.lower() if pick("chiral") is not None else ""
    std["sigma"] = pick("sigma") if pick("sigma") is not None else np.nan
    std["type"] = pick("type") if pick("type") is not None else ""
    std["hyperbolic_volume"] = pick("hyperbolic_volume") if pick("hyperbolic_volume") is not None else np.nan
    return std.set_index("knot_id")


# ============================================================
# Main
# ============================================================
def main():
    ap = argparse.ArgumentParser(
        description="Recursive Fourier-knot analyzer: invariants.csv + masses.csv from .fseries and/or _ideal.txt"
    )
    ap.add_argument("--dir", type=str, default=".", help="Root directory to scan recursively")
    ap.add_argument("--input-format", type=str, default="auto", choices=["auto", "fseries", "ideal"])
    ap.add_argument("--invariants-out", type=str, default="invariants.csv")
    ap.add_argument("--masses-out", type=str, default="masses.csv")
    ap.add_argument("--scale", type=float, default=1.0, help="Meters per series unit")
    ap.add_argument("--xi", type=float, default=1.0, help="Coherence factor")
    ap.add_argument("--b0", type=float, default=3.0, help="Crossing baseline offset")
    ap.add_argument("--samples", type=int, default=1500, help="Samples along curve")
    ap.add_argument("--wr-maxM", type=int, default=520, help="Max points for writhe integral")
    ap.add_argument("--cr-dirs", type=int, default=28, help="Random directions for crossing estimate")
    ap.add_argument("--cr-maxM", type=int, default=260, help="Downsample points for crossing estimate")
    ap.add_argument("--sigma-mode", type=str, default="meta", choices=["meta", "writhe"])
    ap.add_argument("--meta", type=str, default="", help="Optional CSV with knot_id,chiral,sigma,type,hyperbolic_volume")
    ap.add_argument("--wr-tol", type=float, default=5e-3, help="If sigma_mode=writhe and |Wr|<=tol => sigma=0")
    ap.add_argument("--emit-meta", type=str, default="", help="Optional path to write a meta skeleton CSV")
    args = ap.parse_args()

    root = os.path.abspath(args.dir)

    candidate_files = []
    if args.input_format in ("auto", "fseries"):
        candidate_files.extend(glob.glob(os.path.join(args.dir, "**", "*.fseries"), recursive=True))
    if args.input_format in ("auto", "ideal"):
        candidate_files.extend(glob.glob(os.path.join(args.dir, "**", "*_ideal.txt"), recursive=True))

    files = sorted(set(candidate_files))

    if not files:
        print("No matching input files found under", args.dir)
        return

    if args.emit_meta:
        ids = discover_ids(files)
        with open(args.emit_meta, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["knot_id", "chiral", "sigma", "type", "hyperbolic_volume"])
            for kid in ids:
                w.writerow([kid, "", "", "", ""])
        print("Wrote meta skeleton:", args.emit_meta)

    meta = load_meta_table(args.meta)

    t = np.linspace(0, 2 * math.pi, args.samples, endpoint=False)
    dt = 2 * math.pi / args.samples

    inv_rows = []
    mass_rows = []

    for path in files:
        coeffs, detected_format = load_coeff_matrix(path, input_format=args.input_format)

        if coeffs.size == 0:
            continue

        r, r_t = eval_series(coeffs, t)

        closure = true_closure_error(coeffs)
        L_series = curve_length(r_t, dt)
        Wr = writhe_gauss(r, r_t, dt, maxM=args.wr_maxM)
        cr_est = estimate_crossing_number(r, directions=args.cr_dirs, maxM=args.cr_maxM)
        recon = reconstruction_metrics(coeffs, samples=min(args.samples, 2000))

        relpath = os.path.relpath(path, root)
        knot_id = parse_knot_id_from_filename(path)

        sigma_meta = np.nan
        chiral_meta = ""
        vol_meta = np.nan
        type_meta = ""

        if meta is not None and knot_id in meta.index:
            rowm = meta.loc[knot_id]
            chiral_meta = str(rowm.get("chiral", ""))
            type_meta = str(rowm.get("type", ""))
            try:
                sigma_meta = float(rowm.get("sigma", np.nan))
            except Exception:
                sigma_meta = np.nan
            try:
                vol_meta = float(rowm.get("hyperbolic_volume", np.nan))
            except Exception:
                vol_meta = np.nan

        if args.sigma_mode == "meta":
            if isinstance(sigma_meta, float) and np.isnan(sigma_meta):
                sigma = 0.0 if abs(Wr) <= args.wr_tol else (1.0 if Wr > 0 else -1.0)
                sigma_source = "writhe_fallback"
            else:
                try:
                    sigma = float(sigma_meta)
                    sigma_source = "meta"
                except Exception:
                    sigma = 0.0 if abs(Wr) <= args.wr_tol else (1.0 if Wr > 0 else -1.0)
                    sigma_source = "writhe_fallback"
        else:
            sigma = 0.0 if abs(Wr) <= args.wr_tol else (1.0 if Wr > 0 else -1.0)
            sigma_source = "writhe"

        HvX = sigma * max(cr_est - args.b0, 0.0)
        HvVol = np.nan
        if not np.isnan(vol_meta) and sigma != 0.0:
            HvVol = sigma * (vol_meta / VOL_BASELINE_VALUE)

        H_used = HvX if np.isnan(HvVol) else HvVol

        L_phys = args.scale * L_series
        xi = args.xi

        M_fluid = xi * H_used * K_fluid * L_phys
        M_energy = xi * H_used * K_energy * L_phys

        inv_rows.append({
            "file": os.path.basename(path),
            "relative_path": relpath,
            "input_format_detected": detected_format,
            "knot_id": knot_id,
            "harmonics_N": int(coeffs.shape[0]),
            "closure_error": closure,
            "length_series_units": L_series,
            "writhe": Wr,
            "crossing_est": int(cr_est),
            "sigma": sigma,
            "sigma_source": sigma_source,
            "hyperbolic_volume_meta": vol_meta,
            "type_meta": type_meta,
            "chiral_meta": chiral_meta,
            "recon_rms_error": recon["recon_rms_error"],
            "recon_max_error": recon["recon_max_error"],
            "bbox_diag": recon["bbox_diag"],
            "rms_radius": recon["rms_radius"],
        })

        mass_rows.append({
            "file": os.path.basename(path),
            "relative_path": relpath,
            "input_format_detected": detected_format,
            "knot_id": knot_id,
            "harmonics_N": int(coeffs.shape[0]),
            "scale_m_per_unit": args.scale,
            "length_series_units": L_series,
            "length_m": L_phys,
            "writhe": Wr,
            "crossing_est": int(cr_est),
            "sigma": sigma,
            "sigma_source": sigma_source,
            f"Hvortex_X(b0={args.b0:.3f})": HvX,
            "hyperbolic_volume_meta": vol_meta,
            "Hvortex_Vol(Vol/Vol(4_1))": HvVol,
            "H_used": H_used,
            "xi": xi,
            "K_fluid_kg_per_m": K_fluid,
            "K_energy_kg_per_m": K_energy,
            "mass_fluid_kg": M_fluid,
            "mass_energy_kg": M_energy,
            "type_meta": type_meta,
            "chiral_meta": chiral_meta,
        })

    inv_df = pd.DataFrame(inv_rows)
    mass_df = pd.DataFrame(mass_rows)

    inv_df.to_csv(args.invariants_out, index=False)
    mass_df.to_csv(args.masses_out, index=False)

    print("Wrote:", args.invariants_out)
    print("Wrote:", args.masses_out)
    print("Files processed:", len(inv_df))
    print(f"K_fluid = {K_fluid:.6e} kg/m")
    print(f"K_energy = {K_energy:.6e} kg/m")


if __name__ == "__main__":
    main()