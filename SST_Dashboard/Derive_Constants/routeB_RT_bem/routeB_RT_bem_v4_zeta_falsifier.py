#!/usr/bin/env python3
r"""
routeB_RT_bem_v4_zeta_falsifier.py
==================================

BEMv4 Route-B audit: R--T boundary spectral action with raw spectra,
mode-cutoff series, renormalized-action cutoff fit, and blind alpha prediction.

This script is a falsifier / provenance harness. It does NOT compare with CODATA
alpha and it does NOT fit alpha.

New BEMv4 outputs
-----------------
For each run directory:

  raw_spectrum_<knot>.npy
      Positive generalized R--T impedance eigenvalues for that knot.

  cutoff_series.csv
      Mode-cutoff partial sums:
          S_M(K) = -sum_{j<=M} log(lambda_j(K))
      and reference-subtracted series:
          DeltaS_M(K/ref)=S_M(K)-S_M(ref).

  renormalized_action_fit.csv
      Fits tail cutoffs to
          DeltaS_M = S_inf + c1 M^{-1/2} + c2 M^{-1} + c3 M^{-3/2} + ...
      without any observed alpha.

  blind_alpha_prediction.md
      A blind report with
          alpha_inv_pred_blind = 0.5 * S_inf
      for the selected target/reference pair, but no CODATA comparison.

Input
-----
Supports Brian Gilbert XML/Fourier ideal.txt files:

  <AB Id="3:1:1" Conway="3" L="16.371637" D="1.000000">
    <Coeff I="1" A="..." B="..." />
  </AB>

Also supports simple coordinate blocks:

  # Knot: 3_1
  x y z
  ...

Important
---------
Passing this audit does not derive alpha. A true derivation still requires a
canonical theorem-level map alpha^{-1}=F(S_RT^ren(3_1/0_1)) specified before
comparison with data.

Scale-role convention: r_c, R_horn, and a_tube
----------------------------------------------
Route-B BEM is a dimensionless certified-geometry programme.  Its numerical
normalizers use L_cert, M_max, and DeltaF_pair; they do not require inserting a
physical core radius into the BEM score.

When a physical radius is discussed, use

    r_c == R_horn

where R_horn is the horn-torus / return-flow circulation radius.  Do not
silently identify r_c with the local ideal-tube radius.  Use

    a_tube = R_horn / chi_h = r_c / chi_h
    ell_K_phys = 2 * a_tube * L_cert

The dimensionless Route-B normalizer remains

    N_RT = M_max * L_cert**2

while physical reconstruction uses

    L_phys**2 = 4 * a_tube**2 * L_cert**2
              = 4 * r_c**2 * L_cert**2 / chi_h**2

Only if chi_h is later made knot-dependent should a separate horn-effective
scan use M_max * (L_cert / chi_h(K))**2.  BEMv1--BEMv19 default mode is the
certified dimensionless geometry mode.

"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

try:
    from scipy.linalg import eigh
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


# ---------------------------------------------------------------------------
# Parsing: XML/Fourier ideal.txt and coordinate blocks
# ---------------------------------------------------------------------------

_FLOAT_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


def parse_attrs_from_tag(tag: str) -> Dict[str, str]:
    return {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"', tag)}


def parse_vec3_attr(s: str) -> List[float]:
    vals = [float(x.strip()) for x in s.split(",")]
    if len(vals) != 3:
        raise ValueError(f"expected 3-vector, got {s!r}")
    return vals


def is_ideal_xml_fourier_file(path: Path) -> bool:
    if not path.exists():
        return False
    head = path.read_text(encoding="utf-8", errors="replace")[:8192]
    return "<AB " in head and "<Coeff " in head


def ideal_id_to_display_name(bid: str) -> str:
    parts = str(bid).split(":")
    if len(parts) >= 3 and parts[2] == "1":
        return f"{parts[0]}_{parts[1]}"
    return str(bid).replace(":", "_")


def parse_ideal_xml_fourier_file(path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Parse single-component <AB> blocks. Multi-component <Component> blocks are
    marked unsupported for centerline BEM and skipped unless explicitly handled
    in a future multi-boundary version.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks: Dict[str, Dict[str, Any]] = {}

    for m in re.finditer(r"<AB\b([^>]*)>(.*?)</AB>", text, flags=re.S | re.I):
        attrs = parse_attrs_from_tag(m.group(1))
        bid = attrs.get("Id", f"AB_{len(blocks)+1}")
        body = m.group(2)
        ncomp = int(attrs.get("n", "1").strip() or "1")
        has_components = "<Component" in body

        def maybe_float(key: str):
            try:
                return float(str(attrs.get(key, "")).strip())
            except Exception:
                return None

        block: Dict[str, Any] = {
            "id": bid,
            "name": ideal_id_to_display_name(bid),
            "conway": attrs.get("Conway", ""),
            "L": maybe_float("L"),
            "D": maybe_float("D"),
            "n": ncomp,
            "supported": (ncomp == 1 and not has_components),
            "A": {},
            "B": {},
            "max_I": None,
        }

        if block["supported"]:
            A: Dict[int, np.ndarray] = {}
            B: Dict[int, np.ndarray] = {}
            for cm in re.finditer(r"<Coeff\b([^>]*)/?>", body, flags=re.I):
                ca = parse_attrs_from_tag(cm.group(1))
                if not all(k in ca for k in ("I", "A", "B")):
                    continue
                idx = int(ca["I"])
                A[idx] = np.asarray(parse_vec3_attr(ca["A"]), dtype=float)
                B[idx] = np.asarray(parse_vec3_attr(ca["B"]), dtype=float)
            block["A"] = A
            block["B"] = B
            block["max_I"] = max(set(A) | set(B)) if (A and B) else None
            if not A or not B:
                block["supported"] = False

        blocks[bid] = block

    return blocks


def eval_ideal_fourier_block(block: Dict[str, Any], samples: int) -> np.ndarray:
    t = np.linspace(0.0, 2.0 * math.pi, int(samples), endpoint=False)
    pts = np.zeros((len(t), 3), dtype=float)
    A: Dict[int, np.ndarray] = block["A"]
    B: Dict[int, np.ndarray] = block["B"]
    for I in sorted(set(A) | set(B)):
        pts += np.cos(I * t)[:, None] * A.get(I, np.zeros(3))[None, :]
        pts += np.sin(I * t)[:, None] * B.get(I, np.zeros(3))[None, :]
    return pts


def parse_id_csv(s: str) -> List[str]:
    return [x.strip() for x in str(s).split(",") if x.strip()]


def load_knots_from_ideal_xml(path: Path, ids_csv: str, samples: int, max_knots: int) -> Tuple[Dict[str, np.ndarray], Dict[str, Dict[str, Any]]]:
    blocks = parse_ideal_xml_fourier_file(path)
    if not blocks:
        raise ValueError(f"No <AB> Fourier blocks parsed from {path}")

    ids = parse_id_csv(ids_csv)
    selected: List[Tuple[str, Dict[str, Any]]] = []

    if len(ids) == 1 and ids[0].lower() == "all":
        for bid, b in blocks.items():
            if b.get("supported"):
                selected.append((bid, b))
                if len(selected) >= max_knots:
                    break
    else:
        for bid in ids:
            if bid not in blocks:
                raise ValueError(f"AB Id={bid!r} not found in {path}")
            b = blocks[bid]
            if not b.get("supported"):
                raise ValueError(f"AB Id={bid!r} is multi-component or unsupported by centerline BEMv4")
            selected.append((bid, b))

    knots: Dict[str, np.ndarray] = {}
    meta: Dict[str, Dict[str, Any]] = {}
    for bid, b in selected:
        name = b["name"]
        base, k = name, 2
        while name in knots:
            name = f"{base}__{k}"
            k += 1
        knots[name] = eval_ideal_fourier_block(b, samples)
        meta[name] = {k: v for k, v in b.items() if k not in ("A", "B")}
    return knots, meta


def list_ideal_xml_blocks(path: Path, max_knots: int = 60) -> None:
    blocks = parse_ideal_xml_fourier_file(path)
    print(f"ideal XML/Fourier file: {path}")
    print(f"blocks: {len(blocks)}")
    for i, (bid, b) in enumerate(blocks.items()):
        if i >= max_knots:
            print(f"... truncated at {max_knots}")
            break
        sup = "yes" if b.get("supported") else "no"
        print(f"{i:4d} Id={bid:12s} name={b.get('name',''):8s} Conway={str(b.get('conway','')):8s} "
              f"L={b.get('L')} D={b.get('D')} n={b.get('n')} supported={sup} max_I={b.get('max_I')}")


def parse_coordinate_file(path: Path) -> Tuple[Dict[str, np.ndarray], Dict[str, Dict[str, Any]]]:
    knots: Dict[str, List[List[float]]] = {}
    cur_name: Optional[str] = None
    cur_pts: List[List[float]] = []
    anon = 1

    def flush():
        nonlocal cur_name, cur_pts, anon
        if cur_pts:
            nm = cur_name or f"knot_{anon}"
            anon += 1
            base, k = nm, 2
            while nm in knots:
                nm = f"{base}__{k}"
                k += 1
            knots[nm] = cur_pts
        cur_name, cur_pts = None, []

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith(("#", "//", ";")):
            s = line.lstrip("#/;").strip()
            m = re.search(r"(?:knot|name|id)\s*[:=]\s*([A-Za-z0-9_+\-.]+)", s, flags=re.I)
            if m:
                flush()
                cur_name = m.group(1)
            continue
        parts = [p for p in re.split(r"[,;\s]+", line) if p]
        vals = []
        for p in parts:
            try:
                vals.append(float(p))
            except Exception:
                pass
        if len(vals) >= 3:
            cur_pts.append(vals[-3:])
        elif re.match(r"^[A-Za-z0-9_+\-.]+$", line):
            flush()
            cur_name = line
    flush()

    out: Dict[str, np.ndarray] = {}
    meta: Dict[str, Dict[str, Any]] = {}
    for nm, pts in knots.items():
        arr = np.asarray(pts, dtype=float)
        if arr.ndim == 2 and arr.shape[1] == 3 and arr.shape[0] >= 8 and np.isfinite(arr).all():
            out[nm] = arr
            meta[nm] = {"id": nm, "name": nm, "source": "coordinate"}
    return out, meta


def write_sampled_coordinate_file(path: Path, knots: Dict[str, np.ndarray], meta: Dict[str, Dict[str, Any]], note: str) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write("# Sampled coordinate file generated by routeB_RT_bem_v4_zeta_falsifier.py\n")
        f.write(f"# Source: {note}\n\n")
        for name, P in knots.items():
            m = meta.get(name, {})
            f.write(f"# Knot: {name}  Id={m.get('id','')}  L={m.get('L','')}  Conway={m.get('conway','')}\n")
            for x, y, z in np.asarray(P, dtype=float):
                f.write(f"{x:.12g} {y:.12g} {z:.12g}\n")
            f.write("\n")


# ---------------------------------------------------------------------------
# Geometry / mesh
# ---------------------------------------------------------------------------

def close_curve(P: np.ndarray) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    if np.linalg.norm(P[0] - P[-1]) > 1e-12:
        return np.vstack([P, P[0]])
    return P


def arclength(P: np.ndarray) -> float:
    C = close_curve(P)
    return float(np.sum(np.linalg.norm(np.diff(C, axis=0), axis=1)))


def resample_closed_curve(P: np.ndarray, n: int, normalize_length: bool = True) -> np.ndarray:
    C = close_curve(P)
    seg = np.linalg.norm(np.diff(C, axis=0), axis=1)
    total = float(np.sum(seg))
    if total <= 0:
        raise ValueError("zero-length curve")
    s = np.r_[0.0, np.cumsum(seg)]
    targets = np.linspace(0.0, total, int(n), endpoint=False)
    Q = np.column_stack([np.interp(targets, s, C[:, j]) for j in range(3)])
    Q -= Q.mean(axis=0)
    if normalize_length:
        Q /= max(arclength(Q), 1e-30)
    return Q


def tangents(P: np.ndarray) -> np.ndarray:
    T = np.roll(P, -1, axis=0) - np.roll(P, 1, axis=0)
    return T / np.maximum(np.linalg.norm(T, axis=1)[:, None], 1e-30)


def rotate_about(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    axis = axis / max(np.linalg.norm(axis), 1e-30)
    return v * math.cos(angle) + np.cross(axis, v) * math.sin(angle) + axis * np.dot(axis, v) * (1 - math.cos(angle))


def parallel_transport_frames(P: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    T = tangents(P)
    n = len(P)
    N1 = np.zeros_like(P)
    N2 = np.zeros_like(P)
    axes = np.eye(3)
    ref = axes[np.argmin(np.abs(axes @ T[0]))]
    N1[0] = ref - np.dot(ref, T[0]) * T[0]
    N1[0] /= max(np.linalg.norm(N1[0]), 1e-30)
    N2[0] = np.cross(T[0], N1[0])
    N2[0] /= max(np.linalg.norm(N2[0]), 1e-30)

    for i in range(n - 1):
        a, b = T[i], T[i + 1]
        ax = np.cross(a, b)
        an = np.linalg.norm(ax)
        if an < 1e-14:
            v = N1[i].copy()
        else:
            v = rotate_about(N1[i], ax, math.atan2(an, np.clip(np.dot(a, b), -1, 1)))
        v -= np.dot(v, b) * b
        v /= max(np.linalg.norm(v), 1e-30)
        N1[i + 1] = v
        N2[i + 1] = np.cross(b, v)
        N2[i + 1] /= max(np.linalg.norm(N2[i + 1]), 1e-30)

    # Holonomy correction.
    a, b = T[-1], T[0]
    ax = np.cross(a, b)
    an = np.linalg.norm(ax)
    if an < 1e-14:
        vclose = N1[-1].copy()
    else:
        vclose = rotate_about(N1[-1], ax, math.atan2(an, np.clip(np.dot(a, b), -1, 1)))
    vclose -= np.dot(vclose, T[0]) * T[0]
    vclose /= max(np.linalg.norm(vclose), 1e-30)
    hol = math.atan2(np.dot(T[0], np.cross(vclose, N1[0])), np.dot(vclose, N1[0]))
    for i in range(n):
        N1[i] = rotate_about(N1[i], T[i], hol * i / n)
        N1[i] -= np.dot(N1[i], T[i]) * T[i]
        N1[i] /= max(np.linalg.norm(N1[i]), 1e-30)
        N2[i] = np.cross(T[i], N1[i])
        N2[i] /= max(np.linalg.norm(N2[i]), 1e-30)
    return T, N1, N2


def reach_radius(P: np.ndarray, neighbor_skip: int) -> float:
    n = len(P)
    dmin = float("inf")
    for i in range(n):
        d = np.linalg.norm(P[i] - P, axis=1)
        mask = np.ones(n, dtype=bool)
        for k in range(-neighbor_skip, neighbor_skip + 1):
            mask[(i + k) % n] = False
        if np.any(mask):
            dmin = min(dmin, float(d[mask].min()))
    if not np.isfinite(dmin):
        dmin = 1.0 / n
    return max(0.5 * dmin, 1e-5)


def fibonacci_sphere(n: int, radius: float) -> Tuple[np.ndarray, np.ndarray]:
    pts = np.zeros((n, 3), dtype=float)
    gr = (1.0 + math.sqrt(5.0)) / 2.0
    for i in range(n):
        z = 1.0 - 2.0 * (i + 0.5) / n
        phi = 2.0 * math.pi * (i / gr)
        rr = math.sqrt(max(0.0, 1.0 - z * z))
        pts[i] = radius * np.array([rr * math.cos(phi), rr * math.sin(phi), z])
    areas = np.full(n, 4.0 * math.pi * radius * radius / n)
    return pts, areas


def make_mesh(P_raw: np.ndarray, n_center: int, n_theta: int, n_sphere: int, tube_fraction: float, outer_factor: float) -> Dict[str, Any]:
    C = resample_closed_curve(P_raw, n_center, normalize_length=True)
    _, N1, N2 = parallel_transport_frames(C)
    ds = 1.0 / n_center
    a = max(tube_fraction * reach_radius(C, max(3, int(0.04 * n_center))), 1e-5)

    pts: List[np.ndarray] = []
    areas: List[float] = []
    labels: List[str] = []
    for i in range(n_center):
        for j in range(n_theta):
            phi = 2.0 * math.pi * j / n_theta
            radial = math.cos(phi) * N1[i] + math.sin(phi) * N2[i]
            pts.append(C[i] + a * radial)
            areas.append(2.0 * math.pi * a * ds / n_theta)
            labels.append("tube")

    tube = np.asarray(pts, dtype=float)
    R = outer_factor * max(float(np.linalg.norm(tube, axis=1).max()), 1e-6)
    sph, sph_a = fibonacci_sphere(n_sphere, R)

    X = np.vstack([tube, sph])
    A = np.r_[np.asarray(areas, dtype=float), sph_a]
    labels_arr = np.asarray(labels + ["sphere"] * len(sph), dtype=object)
    return {
        "points": X,
        "areas": A,
        "labels": labels_arr,
        "tube_radius": float(a),
        "outer_radius": float(R),
        "centerline_points": int(n_center),
        "n_theta": int(n_theta),
        "n_sphere": int(n_sphere),
    }


# ---------------------------------------------------------------------------
# BEM / Steklov spectrum
# ---------------------------------------------------------------------------

def self_term(A: np.ndarray, mu: float, self_scale: float) -> np.ndarray:
    rp = np.sqrt(np.maximum(A, 1e-300) / math.pi)
    if abs(mu) < 1e-14:
        val = 0.5 * rp
    else:
        val = (1.0 - np.exp(-mu * rp)) / (2.0 * mu)
    return self_scale * val


def single_layer_sym(X: np.ndarray, A: np.ndarray, mu: float, self_scale: float) -> np.ndarray:
    D = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=2)
    G = np.exp(-mu * np.maximum(D, 0.0)) / (4.0 * math.pi * np.maximum(D, 1e-300))
    sA = np.sqrt(np.maximum(A, 1e-300))
    S = (sA[:, None] * G) * sA[None, :]
    np.fill_diagonal(S, self_term(A, mu, self_scale))
    return 0.5 * (S + S.T)


def spd_inv(S: np.ndarray, ridge_rel: float) -> np.ndarray:
    w, V = np.linalg.eigh(0.5 * (S + S.T))
    ridge = ridge_rel * max(float(np.max(np.abs(w))), 1.0)
    w = np.maximum(w, ridge)
    inv = (V / w) @ V.T
    return 0.5 * (inv + inv.T)


def remove_constant(A: np.ndarray, B: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    n = A.shape[0]
    c = np.ones((n, 1)) / math.sqrt(n)
    M = np.eye(n)
    M[:, 0:1] = c
    Q, _ = np.linalg.qr(M)
    Q = Q[:, 1:]
    return Q.T @ A @ Q, Q.T @ B @ Q


def select_boundary(mesh: Dict[str, Any], subspace: str) -> Tuple[np.ndarray, np.ndarray]:
    X = mesh["points"]
    A = mesh["areas"]
    labels = mesh["labels"]
    if subspace == "all":
        return X, A
    idx = np.where(labels == subspace)[0]
    return X[idx], A[idx]


def compute_spectrum(P_raw: np.ndarray, args) -> Tuple[np.ndarray, Dict[str, Any]]:
    mesh = make_mesh(P_raw, args.n_center, args.n_theta, args.n_sphere, args.tube_fraction, args.outer_factor)
    X, A = select_boundary(mesh, args.boundary_subspace)

    a = mesh["tube_radius"]
    R = mesh["outer_radius"]
    if args.mu_mode == "inverse_tube_radius":
        mu = 1.0 / max(a, 1e-30)
    elif args.mu_mode == "inverse_outer_radius":
        mu = 1.0 / max(R, 1e-30)
    elif args.mu_mode == "fixed":
        mu = args.mu_value
    else:
        mu = 0.0

    SR = single_layer_sym(X, A, 0.0, args.self_scale)
    ST = single_layer_sym(X, A, mu, args.self_scale)
    LR = spd_inv(SR, args.ridge_rel)
    LT = spd_inv(ST, args.ridge_rel)

    if not args.keep_constant:
        LR, LT = remove_constant(LR, LT)

    if HAVE_SCIPY:
        ev = eigh(LR, LT, eigvals_only=True)
    else:
        ev = np.linalg.eigvals(np.linalg.solve(LT + args.ridge_rel * np.eye(LT.shape[0]), LR)).real

    ev = np.sort(np.real(ev[np.isfinite(ev)]))
    ev = ev[ev > args.eig_floor]
    if len(ev) == 0:
        raise ValueError("no positive generalized eigenvalues")

    if args.max_raw_modes > 0:
        ev = ev[:min(args.max_raw_modes, len(ev))]

    meta = {
        "boundary_nodes": int(len(mesh["points"])),
        "selected_nodes": int(len(X)),
        "tube_radius": float(a),
        "outer_radius": float(R),
        "screening_mu": float(mu),
        "n_center": int(args.n_center),
        "n_theta": int(args.n_theta),
        "n_sphere": int(args.n_sphere),
        "boundary_subspace": args.boundary_subspace,
        "operator_backend": "BEM_V4_AREA_SYMMETRIC_ZETA_CUTOFF",
        "scipy": bool(HAVE_SCIPY),
    }
    return ev, meta


# ---------------------------------------------------------------------------
# Cutoff series and renormalized-action fits
# ---------------------------------------------------------------------------

def partial_action(ev: np.ndarray) -> np.ndarray:
    return -np.cumsum(np.log(np.maximum(ev, 1e-300)))


def design_matrix(M: np.ndarray, model: str) -> Tuple[np.ndarray, List[str]]:
    cols = [np.ones_like(M, dtype=float)]
    names = ["S_inf"]
    if "sqrt" in model:
        cols.append(M ** -0.5); names.append("c_sqrt")
    if "inv" in model:
        cols.append(M ** -1.0); names.append("c_inv")
    if "threehalf" in model:
        cols.append(M ** -1.5); names.append("c_threehalf")
    if "two" in model:
        cols.append(M ** -2.0); names.append("c_two")
    return np.column_stack(cols), names


def fit_cutoff(M: np.ndarray, Y: np.ndarray, model: str) -> Dict[str, Any]:
    X, names = design_matrix(M.astype(float), model)
    if len(M) < X.shape[1] + 1:
        return {"model": model, "status": "SKIP_TOO_FEW_POINTS"}
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    pred = X @ beta
    resid = Y - pred
    dof = max(1, len(Y) - X.shape[1])
    rms = float(math.sqrt(np.mean(resid * resid)))
    sigma2 = float(np.sum(resid * resid) / dof)
    try:
        cov = sigma2 * np.linalg.inv(X.T @ X)
        se = np.sqrt(np.maximum(np.diag(cov), 0.0))
    except Exception:
        se = np.full_like(beta, np.nan, dtype=float)

    out: Dict[str, Any] = {
        "model": model,
        "status": "PASS_FIT",
        "n_points": int(len(M)),
        "M_min": int(np.min(M)),
        "M_max": int(np.max(M)),
        "rms": rms,
        "S_inf": float(beta[0]),
        "S_inf_se": float(se[0]) if len(se) else float("nan"),
        "alpha_inv_pred_blind": float(0.5 * beta[0]),
    }
    for name, val, err in zip(names[1:], beta[1:], se[1:]):
        out[name] = float(val)
        out[name + "_se"] = float(err)
    return out


def resolve_name(name_or_id: str, names: List[str], meta: Dict[str, Dict[str, Any]]) -> str:
    if name_or_id in names:
        return name_or_id
    # Accept AB Ids like 3:1:1.
    for nm in names:
        if str(meta.get(nm, {}).get("id", "")) == name_or_id:
            return nm
    # Accept normalized AB IDs.
    norm = ideal_id_to_display_name(name_or_id)
    if norm in names:
        return norm
    raise ValueError(f"Could not resolve knot {name_or_id!r}; available={names}")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    keys: List[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(rows)


def make_cutoff_and_fits(outdir: Path, spectra: Dict[str, np.ndarray], meta: Dict[str, Dict[str, Any]], args) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    names = list(spectra.keys())
    ref = resolve_name(args.reference, names, meta)
    target = resolve_name(args.target, names, meta)

    S = {k: partial_action(v) for k, v in spectra.items()}
    Sref = S[ref]
    max_common_ref = len(Sref)

    cutoff_rows: List[Dict[str, Any]] = []
    fit_rows: List[Dict[str, Any]] = []

    for name in names:
        if name == ref:
            continue
        maxM = min(len(S[name]), max_common_ref)
        for M in range(1, maxM + 1):
            delta = float(S[name][M - 1] - Sref[M - 1])
            cutoff_rows.append({
                "knot": name,
                "reference": ref,
                "M": M,
                "S_M_knot": float(S[name][M - 1]),
                "S_M_reference": float(Sref[M - 1]),
                "DeltaS_M": delta,
                "alpha_inv_pred_blind_M": 0.5 * delta,
            })

        # Tail fit.
        start = max(args.fit_min_M, int(math.ceil((1.0 - args.fit_tail_frac) * maxM)))
        start = min(start, maxM)
        M_tail = np.arange(start, maxM + 1, dtype=int)
        Y_tail = np.asarray([S[name][m - 1] - Sref[m - 1] for m in M_tail], dtype=float)

        for model in args.fit_models.split(","):
            model = model.strip()
            if not model:
                continue
            fit = fit_cutoff(M_tail, Y_tail, model)
            fit.update({
                "knot": name,
                "reference": ref,
                "target_selected": bool(name == target),
                "fit_tail_frac": float(args.fit_tail_frac),
                "max_common_modes": int(maxM),
            })
            fit_rows.append(fit)

    write_csv(outdir / "cutoff_series.csv", cutoff_rows)
    write_csv(outdir / "renormalized_action_fit.csv", fit_rows)

    # Choose best/default fit for target: prefer full requested first model order with PASS and lowest rms.
    target_fits = [r for r in fit_rows if r.get("knot") == target and r.get("status") == "PASS_FIT"]
    if target_fits:
        # Prefer most complex listed last? Better choose lowest RMS among valid, but keep it explicit.
        best = sorted(target_fits, key=lambda r: (float(r.get("rms", 1e99)), -len(str(r.get("model", "")))))[0]
    else:
        best = {"status": "NO_VALID_TARGET_FIT", "knot": target, "reference": ref}

    return cutoff_rows, fit_rows, best


def write_blind_prediction(outdir: Path, best: Dict[str, Any], spectra: Dict[str, np.ndarray], meta: Dict[str, Dict[str, Any]], args, input_path: Path, source_note: str) -> None:
    sha = hashlib.sha256(input_path.read_bytes()).hexdigest() if input_path.exists() else "missing"
    target = best.get("knot", args.target)
    reference = best.get("reference", args.reference)

    lines: List[str] = []
    lines.append("# Blind Route-B alpha prediction audit")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("This file is alpha-blind. It does not contain or compare against CODATA alpha.")
    lines.append("The printed quantity is a candidate prediction under the provisional map")
    lines.append("")
    lines.append(r"\[")
    lines.append(r"\alpha_{\rm inv,pred}^{\rm blind}=\frac12 S_{\rm ren}(K/{\rm ref}).")
    lines.append(r"\]")
    lines.append("")
    lines.append("This map is a Route-B working hypothesis, not yet a theorem.")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    lines.append(f"- input path: `{input_path}`")
    lines.append(f"- input sha256: `{sha}`")
    lines.append(f"- source: `{source_note}`")
    lines.append(f"- target: `{target}`")
    lines.append(f"- reference/vacuum subtraction: `{reference}`")
    lines.append(f"- BEM backend: `BEM_V4_AREA_SYMMETRIC_ZETA_CUTOFF`")
    lines.append(f"- scipy generalized eigensolver: `{HAVE_SCIPY}`")
    lines.append("")
    lines.append("## Mesh/operator parameters")
    lines.append("")
    for key in ["n_center", "n_theta", "n_sphere", "boundary_subspace", "tube_fraction", "outer_factor", "mu_mode", "mu_value", "ridge_rel", "self_scale", "keep_constant", "max_raw_modes"]:
        lines.append(f"- `{key}`: `{getattr(args, key)}`")
    lines.append("")
    lines.append("## Selected renormalized cutoff fit")
    lines.append("")
    for k in ["model", "status", "n_points", "M_min", "M_max", "rms", "S_inf", "S_inf_se", "alpha_inv_pred_blind"]:
        if k in best:
            lines.append(f"- `{k}`: `{best[k]}`")
    for k in best:
        if k.startswith("c_") and not k.endswith("_se"):
            lines.append(f"- `{k}`: `{best[k]}`")
            if k + "_se" in best:
                lines.append(f"- `{k}_se`: `{best[k + '_se']}`")
    lines.append("")
    lines.append("## Raw spectra saved")
    lines.append("")
    for name, ev in spectra.items():
        lines.append(f"- `{name}`: `raw_spectrum_{safe_name(name)}.npy`, modes={len(ev)}, Id={meta.get(name, {}).get('id', '')}, L={meta.get(name, {}).get('L', '')}")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("If the target fit is unstable under mesh refinement, tube-radius extrapolation, outer-boundary extrapolation, or model choice, Route B is not yet a derivation.")
    lines.append("Only after a canonical theorem-level map and stable continuum/renormalized limit exist should this blind number be compared with observed alpha.")
    (outdir / "blind_alpha_prediction.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(outdir: Path, spectra: Dict[str, np.ndarray], meta: Dict[str, Dict[str, Any]], spec_meta: Dict[str, Dict[str, Any]], args, source_note: str) -> None:
    rows = []
    for name, ev in spectra.items():
        rows.append({
            "knot": name,
            "id": meta.get(name, {}).get("id", ""),
            "conway": meta.get(name, {}).get("conway", ""),
            "L_database": meta.get(name, {}).get("L", ""),
            "D_database": meta.get(name, {}).get("D", ""),
            "raw_spectrum_file": f"raw_spectrum_{safe_name(name)}.npy",
            "n_eigenvalues": int(len(ev)),
            "min_eig": float(np.min(ev)),
            "max_eig": float(np.max(ev)),
            "S_all": float(partial_action(ev)[-1]),
            **spec_meta.get(name, {}),
        })
    write_csv(outdir / "raw_spectrum_manifest.csv", rows)

    config = {
        "source_note": source_note,
        "args": vars(args),
        "have_scipy": HAVE_SCIPY,
    }
    (outdir / "run_config.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_input(args, outdir: Path) -> Tuple[Dict[str, np.ndarray], Dict[str, Dict[str, Any]], Path, str]:
    input_path = Path(args.ideal)
    if args.list_ideal_xml_knots:
        list_ideal_xml_blocks(input_path, args.max_list)
        raise SystemExit(0)

    if is_ideal_xml_fourier_file(input_path):
        knots, meta = load_knots_from_ideal_xml(input_path, args.ideal_xml_knot_ids, args.ideal_xml_samples, args.max_knots)
        sampled = outdir / "idealxml_sampled_ideal_used.txt"
        write_sampled_coordinate_file(sampled, knots, meta, f"XML/Fourier ideal.txt={input_path}; ids={args.ideal_xml_knot_ids}; samples={args.ideal_xml_samples}")
        return knots, meta, sampled, f"XML/Fourier ideal.txt={input_path}"
    knots, meta = parse_coordinate_file(input_path)
    return knots, meta, input_path, f"coordinate file={input_path}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt", help="Brian Gilbert XML/Fourier ideal.txt or coordinate-block file")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v4")
    ap.add_argument("--ideal-xml-knot-ids", default="0:1:1,3:1:1,4:1:1", help="AB Id list or all")
    ap.add_argument("--ideal-xml-samples", type=int, default=1600)
    ap.add_argument("--max-knots", type=int, default=20)
    ap.add_argument("--list-ideal-xml-knots", action="store_true")
    ap.add_argument("--max-list", type=int, default=60)

    ap.add_argument("--reference", default="0_1", help="reference/vacuum subtraction knot name or AB Id")
    ap.add_argument("--target", default="3_1", help="target knot name or AB Id for blind report")

    ap.add_argument("--n-center", type=int, default=32)
    ap.add_argument("--n-theta", type=int, default=6)
    ap.add_argument("--n-sphere", type=int, default=144)
    ap.add_argument("--boundary-subspace", choices=["all", "tube", "sphere"], default="all")
    ap.add_argument("--tube-fraction", type=float, default=0.30)
    ap.add_argument("--outer-factor", type=float, default=2.6)
    ap.add_argument("--mu-mode", choices=["inverse_tube_radius", "inverse_outer_radius", "fixed", "zero"], default="inverse_outer_radius")
    ap.add_argument("--mu-value", type=float, default=1.0)
    ap.add_argument("--ridge-rel", type=float, default=1e-9)
    ap.add_argument("--self-scale", type=float, default=1.0)
    ap.add_argument("--keep-constant", action="store_true")
    ap.add_argument("--eig-floor", type=float, default=1e-14)
    ap.add_argument("--max-raw-modes", type=int, default=0, help="0 means all positive modes")

    ap.add_argument("--fit-tail-frac", type=float, default=0.60, help="fraction of large-M tail used for cutoff fit")
    ap.add_argument("--fit-min-M", type=int, default=6)
    ap.add_argument("--fit-models", default="sqrt,sqrt+inv,sqrt+inv+threehalf", help="comma models using terms sqrt, inv, threehalf, two")

    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    knots, meta, used_input_path, source_note = load_input(args, outdir)
    if not knots:
        raise SystemExit("No supported knots loaded")

    spectra: Dict[str, np.ndarray] = {}
    spec_meta: Dict[str, Dict[str, Any]] = {}
    for name, P in knots.items():
        ev, sm = compute_spectrum(P, args)
        spectra[name] = ev
        spec_meta[name] = sm
        np.save(outdir / f"raw_spectrum_{safe_name(name)}.npy", ev)

    cutoff_rows, fit_rows, best = make_cutoff_and_fits(outdir, spectra, meta, args)
    write_blind_prediction(outdir, best, spectra, meta, args, used_input_path, source_note)
    write_manifest(outdir, spectra, meta, spec_meta, args, source_note)

    print("=" * 78)
    print("Route B BEMv4 zeta/cutoff audit complete")
    print("=" * 78)
    print(f"source: {source_note}")
    print(f"outdir: {outdir}")
    print(f"knots: {', '.join(spectra.keys())}")
    for name, ev in spectra.items():
        print(f"{name:14s} raw_modes={len(ev):4d} S_all={partial_action(ev)[-1]: .12g} file=raw_spectrum_{safe_name(name)}.npy")
    print(f"cutoff rows: {len(cutoff_rows)}")
    print(f"fit rows: {len(fit_rows)}")
    print(f"blind selected fit: {best}")
    print("wrote: raw_spectrum_*.npy, cutoff_series.csv, renormalized_action_fit.csv, blind_alpha_prediction.md")


if __name__ == "__main__":
    main()
