#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compute oriented linking matrix and net chirality/helicity scores
from multi-component link centerlines.

Input
-----
One file per component, each containing an ordered closed polygonal curve:
    x y z
    x y z
    ...

Accepted separators: whitespace, comma, or tab.
If the first and last point are not identical, the script closes the curve automatically.

Main outputs
------------
1. Oriented linking matrix:
       L_ij = Lk(C_i, C_j)

2. Per-component writhe:
       Wr(C_i)

3. Net pairwise helicity score:
       H_link = sum_{i<j} Gamma_i Gamma_j Lk_ij

4. Net chirality/helicity-like score:
       chi_net = sum_i Gamma_i^2 Wr_i + 2 sum_{i<j} Gamma_i Gamma_j Lk_ij

Interpretation
--------------
- Lk changes sign if one component orientation is reversed.
- Wr changes sign if the component orientation is reversed.
- H_link measures pairwise oriented transport coupling.
- chi_net mixes self-chirality (writhe) and pairwise linking.

Usage examples
--------------
Equal circulations:
    python oriented_link_scores.py comp1.txt comp2.txt comp3.txt

Custom circulations:
    python oriented_link_scores.py comp1.txt comp2.txt comp3.txt --gammas 1 1 -1

Reverse one component in-place before running:
    python oriented_link_scores.py A.txt B.txt C_reversed.txt

Optional JSON output:
    python oriented_link_scores.py comp1.txt comp2.txt comp3.txt --json-out scores.json
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import List, Tuple

import numpy as np


def load_curve(path: str) -> np.ndarray:
    text = Path(path).read_text(encoding="utf-8", errors="replace").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    pts = []
    for ln in lines:
        ln = ln.replace(",", " ")
        parts = [p for p in ln.split() if p]
        if len(parts) < 3:
            continue
        pts.append([float(parts[0]), float(parts[1]), float(parts[2])])
    arr = np.asarray(pts, dtype=float)
    if arr.ndim != 2 or arr.shape[0] < 4 or arr.shape[1] != 3:
        raise ValueError(f"{path}: expected at least 4 xyz points")
    # close automatically if needed
    if np.linalg.norm(arr[0] - arr[-1]) > 1e-12:
        arr = np.vstack([arr, arr[0]])
    return arr


def seg_midpoints_and_vectors(curve: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    p0 = curve[:-1]
    p1 = curve[1:]
    mids = 0.5 * (p0 + p1)
    dls = p1 - p0
    return mids, dls


def gauss_linking_integral(curve_a: np.ndarray, curve_b: np.ndarray) -> float:
    """
    Discrete Gauss linking integral for two closed polygonal curves.
    Midpoint rule on segment pairs.
    """
    ma, dla = seg_midpoints_and_vectors(curve_a)
    mb, dlb = seg_midpoints_and_vectors(curve_b)

    total = 0.0
    for i in range(len(dla)):
        ra = ma[i]
        dra = dla[i]
        for j in range(len(dlb)):
            rb = mb[j]
            drb = dlb[j]
            r = ra - rb
            nr = np.linalg.norm(r)
            if nr < 1e-15:
                continue
            total += np.dot(np.cross(dra, drb), r) / (nr ** 3)

    return total / (4.0 * math.pi)


def writhe_discrete(curve: np.ndarray) -> float:
    """
    Discrete writhe approximation using the same Gauss-type integral
    on one curve, excluding identical and adjacent segments.
    """
    mids, dls = seg_midpoints_and_vectors(curve)
    n = len(dls)
    total = 0.0

    for i in range(n):
        ri = mids[i]
        dli = dls[i]
        for j in range(n):
            if i == j:
                continue
            # exclude adjacent pairs for polygonal self-integral stability
            if abs(i - j) == 1 or abs(i - j) == n - 1:
                continue
            rj = mids[j]
            dlj = dls[j]
            r = ri - rj
            nr = np.linalg.norm(r)
            if nr < 1e-15:
                continue
            total += np.dot(np.cross(dli, dlj), r) / (nr ** 3)

    return total / (4.0 * math.pi)


def oriented_linking_matrix(curves: List[np.ndarray]) -> np.ndarray:
    m = len(curves)
    L = np.zeros((m, m), dtype=float)
    for i in range(m):
        for j in range(i + 1, m):
            lk = gauss_linking_integral(curves[i], curves[j])
            L[i, j] = lk
            L[j, i] = lk
    return L


def compute_scores(curves: List[np.ndarray], gammas: np.ndarray) -> dict:
    m = len(curves)
    L = oriented_linking_matrix(curves)
    Wr = np.array([writhe_discrete(c) for c in curves], dtype=float)

    H_link = 0.0
    for i in range(m):
        for j in range(i + 1, m):
            H_link += gammas[i] * gammas[j] * L[i, j]

    chi_net = float(np.sum((gammas ** 2) * Wr) + 2.0 * H_link)

    # cancellation / coherence diagnostics
    abs_pair_sum = 0.0
    signed_pair_sum = 0.0
    for i in range(m):
        for j in range(i + 1, m):
            term = gammas[i] * gammas[j] * L[i, j]
            signed_pair_sum += term
            abs_pair_sum += abs(term)

    pair_coherence = signed_pair_sum / abs_pair_sum if abs_pair_sum > 0 else 0.0

    abs_self_sum = float(np.sum(np.abs((gammas ** 2) * Wr)))
    signed_self_sum = float(np.sum((gammas ** 2) * Wr))
    self_coherence = signed_self_sum / abs_self_sum if abs_self_sum > 0 else 0.0

    return {
        "linking_matrix": L,
        "writhe": Wr,
        "H_link": H_link,
        "chi_net": chi_net,
        "pair_coherence": pair_coherence,
        "self_coherence": self_coherence,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="One xyz/txt/csv polyline file per component")
    ap.add_argument(
        "--gammas",
        nargs="*",
        type=float,
        default=None,
        help="Optional circulation weights Gamma_i, one per component; default all 1",
    )
    ap.add_argument("--json-out", type=str, default=None, help="Optional JSON output")
    args = ap.parse_args()

    curves = [load_curve(p) for p in args.files]
    m = len(curves)

    if args.gammas is None or len(args.gammas) == 0:
        gammas = np.ones(m, dtype=float)
    else:
        if len(args.gammas) != m:
            raise ValueError(f"Need exactly {m} gamma values, got {len(args.gammas)}")
        gammas = np.asarray(args.gammas, dtype=float)

    result = compute_scores(curves, gammas)
    L = result["linking_matrix"]
    Wr = result["writhe"]

    print("\nOriented linking matrix L_ij")
    print("============================")
    for row in L:
        print("  ".join(f"{v: .6f}" for v in row))

    print("\nPer-component writhe Wr_i")
    print("=========================")
    for i, wr in enumerate(Wr):
        print(f"component {i+1}: {wr:.6f}")

    print("\nNet scores")
    print("==========")
    print(f"H_link         = {result['H_link']:.6f}")
    print(f"chi_net        = {result['chi_net']:.6f}")
    print(f"pair_coherence = {result['pair_coherence']:.6f}")
    print(f"self_coherence = {result['self_coherence']:.6f}")

    print("\nInterpretation")
    print("==============")
    print("pair_coherence ~ +1 : pairwise link orientations reinforce")
    print("pair_coherence ~ -1 : pairwise link orientations oppose")
    print("pair_coherence ~  0 : strong internal cancellation")
    print("chi_net sign      : net chirality/helicity-like sign")
    print("If one component is reversed, expect sign flips in its row/column of L_ij.")

    if args.json_out:
        payload = {
            "files": args.files,
            "gammas": gammas.tolist(),
            "linking_matrix": L.tolist(),
            "writhe": Wr.tolist(),
            "H_link": float(result["H_link"]),
            "chi_net": float(result["chi_net"]),
            "pair_coherence": float(result["pair_coherence"]),
            "self_coherence": float(result["self_coherence"]),
        }
        Path(args.json_out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote JSON: {args.json_out}")


if __name__ == "__main__":
    main()