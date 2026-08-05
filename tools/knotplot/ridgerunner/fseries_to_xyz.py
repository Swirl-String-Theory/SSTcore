#!/usr/bin/env python3
"""
Sample a KnotPlot Fourier .fseries file to KnotPlot-style XYZ .txt.

.fseries rows are Ax Bx Ay By Az Bz for harmonics n=1..N (comment lines skipped).
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

TAU = 2.0 * math.pi

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None  # type: ignore


def load_fseries_matrix(path: Path) -> list[tuple[float, float, float, float, float, float]]:
    """Load 6-column harmonic rows from a .fseries file."""
    rows: list[tuple[float, float, float, float, float, float]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("%") or s.startswith("#"):
            continue
        parts = s.replace(",", " ").split()
        try:
            vals = [float(x) for x in parts]
        except ValueError:
            continue
        if len(vals) >= 6:
            rows.append(
                (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5])
            )
    if not rows:
        raise ValueError(f"no fseries coefficients in {path}")
    return rows


def sample_fseries(
    coeffs: list[tuple[float, float, float, float, float, float]],
    n: int,
) -> list[tuple[float, float, float]]:
    """Evaluate Fourier series at n equally spaced parameters on [0, 2π)."""
    if n < 3:
        raise ValueError("points must be >= 3")
    if np is not None:
        t = np.linspace(0.0, TAU, n, endpoint=False)
        p = np.zeros((n, 3), dtype=float)
        for k, (ax, bx, ay, by, az, bz) in enumerate(coeffs, start=1):
            c = np.cos(k * t)
            s = np.sin(k * t)
            p[:, 0] += c * ax + s * bx
            p[:, 1] += c * ay + s * by
            p[:, 2] += c * az + s * bz
        return [tuple(map(float, row)) for row in p]

    points: list[tuple[float, float, float]] = []
    for i in range(n):
        t = TAU * i / n
        x = y = z = 0.0
        for k, (ax, bx, ay, by, az, bz) in enumerate(coeffs, start=1):
            c = math.cos(k * t)
            s = math.sin(k * t)
            x += c * ax + s * bx
            y += c * ay + s * by
            z += c * az + s * bz
        points.append((x, y, z))
    return points


def points_to_xyz_txt(points: list[tuple[float, float, float]]) -> str:
    lines = [f"{p[0]:.17g} {p[1]:.17g} {p[2]:.17g}" for p in points]
    return "\n".join(lines) + "\n"


def parse_fseries_stem(stem: str) -> tuple[str, str]:
    """Return (folder_base, full_stem) for catalog lookup.

    Examples: 3_1p → (3_1, 3_1p); 12a_1202z6 → (12a_1202, 12a_1202z6);
    15331 → (15331, 15331).
    """
    m = re.fullmatch(
        r"^((?:\d+[a-z]?(?:_\d+)+|\d+))([a-z]*\d*)$", stem, re.IGNORECASE
    )
    if not m:
        raise ValueError(f"invalid fseries stem {stem!r}")
    return m.group(1), stem


def fseries_path_for_stem(
    stem: str, *, fseries_root: Path
) -> Path:
    """Map stem like 3_1 / 3_1p / 12a_1202 → Knots_FourierSeries/<base>/knot.<stem>.fseries."""
    base, full = parse_fseries_stem(stem)
    return fseries_root / base / f"knot.{full}.fseries"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "fseries",
        type=Path,
        nargs="?",
        default=None,
        help="path to .fseries (or use --stem)",
    )
    ap.add_argument(
        "--stem",
        default=None,
        help="catalog stem e.g. 3_1 / 3_1p (looks under --fseries-root)",
    )
    ap.add_argument(
        "--fseries-root",
        type=Path,
        default=None,
        help="default: ../Knots_FourierSeries next to this bundle",
    )
    ap.add_argument(
        "--points",
        type=int,
        default=300,
        help="sample points (default: 300)",
    )
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="output XYZ .txt path",
    )
    args = ap.parse_args(argv)

    bundle = Path(__file__).resolve().parent
    root = args.fseries_root or (bundle.parent / "Knots_FourierSeries")
    if args.fseries is not None:
        path = args.fseries
    elif args.stem:
        path = fseries_path_for_stem(args.stem, fseries_root=root)
    else:
        print("error: provide fseries path or --stem", file=sys.stderr)
        return 1
    if not path.is_file():
        print(f"error: fseries not found: {path}", file=sys.stderr)
        return 1

    try:
        coeffs = load_fseries_matrix(path)
        points = sample_fseries(coeffs, args.points)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(points_to_xyz_txt(points), encoding="utf-8")
    print(f"Wrote: {args.output}", flush=True)
    print(f"  fseries={path}  points={args.points}  harmonics={len(coeffs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
