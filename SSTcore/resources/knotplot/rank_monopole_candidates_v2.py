#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rank knots as effective coarse-grained monopole candidates from
monopole_batch_summary.txt.

Input:
  - batch summary file produced by test_monopole_from_fseries.py --batch ...

Output:
  - per-knot ranking by:
      (1) cleanliness score
      (2) shape-only score
      (3) robustness metrics across parameter sweeps

Interpretation
--------------
We do NOT treat the pure tensor source as a monopole candidate.
The batch already showed it is systematically suppressed.

We rank the mixed source as an effective coarse-grained monopole candidate,
but penalize dipole and quadrupole contamination.

Main derived scores:
    cleanliness = |Q_mix| / (1 + lambda_d*d + lambda_q*q)
    shape_score = 1 / (1 + lambda_d*d + lambda_q*q)

where:
    d = mix_norm_dipole
    q = mix_norm_quad

The first score rewards strong effective monopole magnitude.
The second score compares geometry more fairly independent of total size.

Usage
-----
python rank_monopole_candidates_v2.py monopole_batch_summary.txt

Optional:
  --top 20
  --lambda-d 1.0
  --lambda-q 1.0
  --min-runs 5
  --out-tsv monopole_ranking.tsv
  --stem TL3.3
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RunRow:
    stem: str
    relpath: str
    grid_n: int
    tube_radius: float
    alpha: float
    beta: float
    bbox_diag: float
    q_tensor: float
    q_mix: float
    tensor_norm_dipole: float
    tensor_norm_quad: float
    mix_norm_dipole: float
    mix_norm_quad: float
    mix_plausible: int
    tensor_monopole_suppressed: int
    scalar_mass: float


def safe_float(s: str) -> float:
    s = s.strip()
    if s == "":
        return float("nan")
    return float(s)


def safe_int(s: str) -> int:
    s = s.strip()
    if s == "":
        return 0
    return int(float(s))


def parse_batch_summary(path: str) -> List[RunRow]:
    """
    Parse the tab-separated section after:
        Per-knot (tab-separated)
    """
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()

    start_idx = None
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Per-knot"):
            start_idx = i
            break
    if start_idx is None:
        raise ValueError("Could not find 'Per-knot (tab-separated)' section.")

    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip().startswith("ok\t"):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("Could not find tab-separated header row.")

    header = lines[header_idx].split("\t")
    rows: List[RunRow] = []

    for i in range(header_idx + 1, len(lines)):
        line = lines[i].rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < len(header):
            # allow truncated tail of file or malformed line
            continue

        rec = dict(zip(header, parts))

        try:
            rows.append(
                RunRow(
                    stem=rec["stem"],
                    relpath=rec["relpath"],
                    grid_n=safe_int(rec["grid_n"]),
                    tube_radius=safe_float(rec["tube_radius"]),
                    alpha=safe_float(rec["alpha"]),
                    beta=safe_float(rec["beta"]),
                    bbox_diag=safe_float(rec["bbox_diag"]),
                    q_tensor=safe_float(rec["Q_tensor"]),
                    q_mix=safe_float(rec["Q_mix"]),
                    tensor_norm_dipole=safe_float(rec["tensor_norm_dipole"]),
                    tensor_norm_quad=safe_float(rec["tensor_norm_quad"]),
                    mix_norm_dipole=safe_float(rec["mix_norm_dipole"]),
                    mix_norm_quad=safe_float(rec["mix_norm_quad"]),
                    mix_plausible=safe_int(rec["mix_plausible"]),
                    tensor_monopole_suppressed=safe_int(rec["tensor_monopole_suppressed"]),
                    scalar_mass=safe_float(rec["scalar_mass"]),
                )
            )
        except KeyError as e:
            raise ValueError(f"Missing expected column: {e}") from e

    if not rows:
        raise ValueError("No usable per-knot rows parsed.")
    return rows


def median(xs: List[float]) -> float:
    xs2 = [x for x in xs if not math.isnan(x)]
    if not xs2:
        return float("nan")
    return statistics.median(xs2)


def mean(xs: List[float]) -> float:
    xs2 = [x for x in xs if not math.isnan(x)]
    if not xs2:
        return float("nan")
    return statistics.fmean(xs2)


def stdev(xs: List[float]) -> float:
    xs2 = [x for x in xs if not math.isnan(x)]
    if len(xs2) < 2:
        return 0.0
    return statistics.pstdev(xs2)


def quantile(xs: List[float], q: float) -> float:
    xs2 = sorted(x for x in xs if not math.isnan(x))
    if not xs2:
        return float("nan")
    if len(xs2) == 1:
        return xs2[0]
    pos = (len(xs2) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs2[lo]
    frac = pos - lo
    return xs2[lo] * (1 - frac) + xs2[hi] * frac


def summarize_stem(
        stem: str,
        runs: List[RunRow],
        lambda_d: float,
        lambda_q: float,
) -> Dict[str, float | str | int]:
    qmix_vals = [abs(r.q_mix) for r in runs]
    d_vals = [r.mix_norm_dipole for r in runs]
    q_vals = [r.mix_norm_quad for r in runs]
    sm_vals = [r.scalar_mass for r in runs]
    qt_vals = [abs(r.q_tensor) for r in runs]

    cleanliness_vals = []
    shape_vals = []
    scalar_norm_vals = []

    for r in runs:
        penalty = 1.0 + lambda_d * r.mix_norm_dipole + lambda_q * r.mix_norm_quad
        cleanliness_vals.append(abs(r.q_mix) / penalty)
        shape_vals.append(1.0 / penalty)
        if r.scalar_mass != 0.0 and not math.isnan(r.scalar_mass):
            scalar_norm_vals.append(abs(r.q_mix) / abs(r.scalar_mass))

    mix_plausible_rate = mean([float(r.mix_plausible) for r in runs])
    tensor_supp_rate = mean([float(r.tensor_monopole_suppressed) for r in runs])

    # robustness: lower spread is better
    shape_med = median(shape_vals)
    shape_spread = quantile(shape_vals, 0.75) - quantile(shape_vals, 0.25)
    clean_med = median(cleanliness_vals)
    clean_spread = quantile(cleanliness_vals, 0.75) - quantile(cleanliness_vals, 0.25)

    # dimensionless robustness score
    robustness = shape_med / (1.0 + shape_spread)

    return {
        "stem": stem,
        "n_runs": len(runs),
        "qmix_med": median(qmix_vals),
        "qmix_mean": mean(qmix_vals),
        "qtensor_med": median(qt_vals),
        "scalar_mass_med": median(sm_vals),
        "scalar_ratio_med": median(scalar_norm_vals),
        "dipole_med": median(d_vals),
        "dipole_q75": quantile(d_vals, 0.75),
        "quad_med": median(q_vals),
        "quad_q75": quantile(q_vals, 0.75),
        "cleanliness_med": clean_med,
        "cleanliness_q25": quantile(cleanliness_vals, 0.25),
        "cleanliness_q75": quantile(cleanliness_vals, 0.75),
        "shape_score_med": shape_med,
        "shape_score_q25": quantile(shape_vals, 0.25),
        "shape_score_q75": quantile(shape_vals, 0.75),
        "robustness": robustness,
        "mix_plausible_rate": mix_plausible_rate,
        "tensor_suppressed_rate": tensor_supp_rate,
        "cleanliness_spread": clean_spread,
        "shape_spread": shape_spread,
    }


def print_table(title: str, rows: List[Dict[str, float | str | int]], top: int) -> None:
    print()
    print(title)
    print("=" * len(title))
    print(
        f"{'rank':>4}  {'stem':<28} {'runs':>4}  {'shape_med':>11}  {'dip_med':>10}  "
        f"{'quad_med':>10}  {'Qmix_med':>12}  {'robust':>10}"
    )
    for i, row in enumerate(rows[:top], start=1):
        print(
            f"{i:>4}  "
            f"{str(row['stem']):<28} "
            f"{int(row['n_runs']):>4}  "
            f"{float(row['shape_score_med']):>11.6e}  "
            f"{float(row['dipole_med']):>10.6e}  "
            f"{float(row['quad_med']):>10.6e}  "
            f"{float(row['qmix_med']):>12.6e}  "
            f"{float(row['robustness']):>10.6e}"
        )


def main():
    parser = argparse.ArgumentParser(description="Rank coarse-grained monopole candidates from monopole_batch_summary.txt")
    parser.add_argument("summary_path", help="Path to monopole_batch_summary.txt")
    parser.add_argument("--top", type=int, default=20, help="How many top entries to print")
    parser.add_argument("--lambda-d", type=float, default=1.0, help="Penalty weight for normalized dipole")
    parser.add_argument("--lambda-q", type=float, default=1.0, help="Penalty weight for normalized quadrupole")
    parser.add_argument("--min-runs", type=int, default=5, help="Minimum runs required per stem")
    parser.add_argument("--out-tsv", type=str, default=None, help="Optional TSV output path")
    parser.add_argument("--stem", type=str, default=None, help="Optional substring filter for a specific stem")
    args = parser.parse_args()

    rows = parse_batch_summary(args.summary_path)

    grouped: Dict[str, List[RunRow]] = {}
    for r in rows:
        if args.stem and args.stem.lower() not in r.stem.lower():
            continue
        grouped.setdefault(r.stem, []).append(r)

    summaries = []
    for stem, runs in grouped.items():
        if len(runs) < args.min_runs:
            continue
        summaries.append(
            summarize_stem(
                stem=stem,
                runs=runs,
                lambda_d=args.lambda_d,
                lambda_q=args.lambda_q,
            )
        )

    if not summaries:
        print("No stems passed the filters.")
        return

    # ranking 1: best shape-only candidate
    by_shape = sorted(
        summaries,
        key=lambda r: (
            -float(r["shape_score_med"]),
            float(r["quad_med"]),
            float(r["dipole_med"]),
            -float(r["robustness"]),
        ),
    )

    # ranking 2: best absolute effective monopole candidate
    by_cleanliness = sorted(
        summaries,
        key=lambda r: (
            -float(r["cleanliness_med"]),
            float(r["quad_med"]),
            float(r["dipole_med"]),
            -float(r["robustness"]),
        ),
    )

    # ranking 3: most robust shape-only
    by_robustness = sorted(
        summaries,
        key=lambda r: (
            -float(r["robustness"]),
            -float(r["shape_score_med"]),
        ),
    )

    print(f"Parsed stems: {len(summaries)}")
    print(f"Penalty weights: lambda_d={args.lambda_d}, lambda_q={args.lambda_q}")
    print_table("Top shape-only coarse-grained monopole candidates", by_shape, args.top)
    print_table("Top absolute-cleanliness candidates", by_cleanliness, args.top)
    print_table("Top robustness candidates", by_robustness, args.top)

    if args.out_tsv:
        fieldnames = [
            "stem", "n_runs",
            "qmix_med", "qmix_mean", "qtensor_med", "scalar_mass_med", "scalar_ratio_med",
            "dipole_med", "dipole_q75", "quad_med", "quad_q75",
            "cleanliness_med", "cleanliness_q25", "cleanliness_q75",
            "shape_score_med", "shape_score_q25", "shape_score_q75",
            "robustness", "mix_plausible_rate", "tensor_suppressed_rate",
            "cleanliness_spread", "shape_spread",
            "rank_shape", "rank_cleanliness", "rank_robustness",
        ]

        rank_shape = {row["stem"]: i + 1 for i, row in enumerate(by_shape)}
        rank_clean = {row["stem"]: i + 1 for i, row in enumerate(by_cleanliness)}
        rank_rob = {row["stem"]: i + 1 for i, row in enumerate(by_robustness)}

        with open(args.out_tsv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            for row in summaries:
                out = dict(row)
                out["rank_shape"] = rank_shape[row["stem"]]
                out["rank_cleanliness"] = rank_clean[row["stem"]]
                out["rank_robustness"] = rank_rob[row["stem"]]
                writer.writerow(out)

        print()
        print(f"Wrote TSV: {args.out_tsv}")


if __name__ == "__main__":
    main()