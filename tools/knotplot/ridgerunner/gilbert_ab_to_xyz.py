#!/usr/bin/env python3
"""
Sample a Brian Gilbert <AB> Fourier block to KnotPlot-style XYZ .txt.

Default ideal DB: SST-Workbench/knots_ideal_favorites.txt

Example:
  python gilbert_ab_to_xyz.py --id 3:1:1 --points 300 -o out/3_1_1/n300.txt
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None  # type: ignore[assignment]

TAU = 2.0 * math.pi

BUNDLE = Path(__file__).resolve().parent
WORKBENCH = BUNDLE.parents[1]  # .../SST-Workbench
DEFAULT_IDEAL = WORKBENCH / "knots_ideal_favorites.txt"

if str(WORKBENCH) not in sys.path:
    sys.path.insert(0, str(WORKBENCH))

from sst_gilbert_usability import (  # noqa: E402
    DEFAULT_MIN_C_CONT,
    CurvatureOnlyIdealError,
    usability_from_coeffs,
)

# Diameter-normalized acceptance target for trefoil after Ridgerunner polish.
TARGET_L_3_1_DIAM = 16.357467488
TARGET_ROP_RADIUS = 2.0 * TARGET_L_3_1_DIAM  # 32.714934976


def parse_ideal_ab_block(
    text: str, knot_id: str
) -> tuple[list[tuple[int, tuple[float, float, float], tuple[float, float, float]]], dict[str, str]]:
    """Parse a single-component Brian Gilbert <AB> block."""
    escaped = re.escape(knot_id)
    match = re.search(
        rf'<AB\s+Id="{escaped}"(?P<attrs>[^>]*)>(?P<body>.*?)</AB>',
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise KeyError(f"ideal AB block not found: {knot_id}")
    body = match.group("body")
    if "<Component" in body:
        raise ValueError(
            f"multi-component AB block is not supported: {knot_id}"
        )
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', match.group("attrs")))
    coeffs: list[
        tuple[int, tuple[float, float, float], tuple[float, float, float]]
    ] = []
    coeff_re = re.compile(
        r'<Coeff\s+I="\s*(?P<i>-?\d+)"\s+A="(?P<a>[^"]+)"\s+B="(?P<b>[^"]+)"\s*/>'
    )
    for cm in coeff_re.finditer(body):
        idx = int(cm.group("i"))
        avec = tuple(float(x.strip()) for x in cm.group("a").split(","))
        bvec = tuple(float(x.strip()) for x in cm.group("b").split(","))
        if len(avec) != 3 or len(bvec) != 3:
            raise ValueError(
                f"invalid coefficient vector in {knot_id}, harmonic {idx}"
            )
        coeffs.append((idx, avec, bvec))  # type: ignore[arg-type]
    if not coeffs:
        raise ValueError(f"no coefficients found in AB block {knot_id}")
    return coeffs, attrs


def reconstruct_ideal_ab(
    text: str, knot_id: str, n: int, *, mirror: bool = False
) -> list[tuple[float, float, float]]:
    """Evaluate Gilbert Fourier series at n equally spaced parameters."""
    if n < 3:
        raise ValueError("points must be >= 3")
    coeffs, _ = parse_ideal_ab_block(text, knot_id)
    if np is not None:
        t = np.linspace(0.0, TAU, n, endpoint=False)
        p = np.zeros((n, 3), dtype=float)
        for idx, avec, bvec in coeffs:
            a = np.asarray(avec, dtype=float)
            b = np.asarray(bvec, dtype=float)
            if idx == 0:
                p += a
            else:
                p += np.cos(idx * t)[:, None] * a[None, :]
                p += np.sin(idx * t)[:, None] * b[None, :]
        if mirror:
            p[:, 2] *= -1.0
        return [tuple(map(float, row)) for row in p]

    points: list[tuple[float, float, float]] = []
    for k in range(n):
        t = TAU * k / n
        x = y = z = 0.0
        for idx, avec, bvec in coeffs:
            if idx == 0:
                x += avec[0]
                y += avec[1]
                z += avec[2]
            else:
                c = math.cos(idx * t)
                s = math.sin(idx * t)
                x += c * avec[0] + s * bvec[0]
                y += c * avec[1] + s * bvec[1]
                z += c * avec[2] + s * bvec[2]
        if mirror:
            z = -z
        points.append((x, y, z))
    return points


def polygonal_length(points: list[tuple[float, float, float]]) -> float:
    """Closed polygonal length (last edge connects last → first)."""
    if len(points) < 2:
        return 0.0
    total = 0.0
    for i in range(len(points)):
        a = points[i]
        b = points[(i + 1) % len(points)]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        dz = b[2] - a[2]
        total += math.sqrt(dx * dx + dy * dy + dz * dz)
    return total


def points_to_xyz_txt(points: list[tuple[float, float, float]]) -> str:
    lines = [f"{p[0]:.17g} {p[1]:.17g} {p[2]:.17g}" for p in points]
    return "\n".join(lines) + "\n"


def l_diam_from_metrics(
    *,
    ropelength: float | None = None,
    length: float | None = None,
    thickness: float | None = None,
) -> float:
    """Convert Ridgerunner metrics to diameter-normalized length."""
    if ropelength is not None and math.isfinite(ropelength):
        return float(ropelength) / 2.0
    if (
        length is not None
        and thickness is not None
        and math.isfinite(length)
        and math.isfinite(thickness)
        and thickness > 0.0
    ):
        return float(length) / (2.0 * float(thickness))
    raise ValueError("need ropelength or (length and thickness)")


def compare_to_target(
    polish_l_diam: float,
    *,
    target: float = TARGET_L_3_1_DIAM,
    rel_tol: float = 1e-4,
) -> dict[str, float | bool]:
    delta = polish_l_diam - target
    rel = abs(delta) / target if target != 0.0 else float("inf")
    return {
        "target_L_diam": target,
        "polish_L_diam": polish_l_diam,
        "delta": delta,
        "rel_err": rel,
        "within_tol": rel <= rel_tol,
        "rel_tol": rel_tol,
    }


def compare_metrics_file(
    metrics_path: Path, *, rel_tol: float = 1e-4, target: float | None = None
) -> dict[str, float | bool | str]:
    """Load polish *.metrics.json and compare L_diam to target."""
    import json

    data = json.loads(metrics_path.read_text(encoding="utf-8"))
    ropelength = data.get("ropelength")
    length = data.get("length")
    thickness = data.get("thickness")
    residual = data.get("residual")
    l_diam = l_diam_from_metrics(
        ropelength=ropelength if ropelength is not None else None,
        length=length if length is not None else None,
        thickness=thickness if thickness is not None else None,
    )
    tgt = TARGET_L_3_1_DIAM if target is None else target
    result = compare_to_target(l_diam, target=tgt, rel_tol=rel_tol)
    result["metrics_path"] = str(metrics_path)
    if residual is not None:
        result["residual"] = float(residual)
    if ropelength is not None:
        result["ropelength"] = float(ropelength)
    return result


def print_compare_report(
    cmp: dict[str, float | bool | str], *, label: str = "polish"
) -> None:
    print("============================================================")
    print(f"Ideal AB polish vs acceptance target ({label})")
    print("============================================================")
    print(f"metrics:        {cmp.get('metrics_path', '')}")
    print(f"target_L_diam = {cmp['target_L_diam']}")
    print(f"polish_L_diam = {cmp['polish_L_diam']}")
    print(f"delta         = {cmp['delta']}")
    print(f"rel_err       = {cmp['rel_err']}")
    print(f"rel_tol       = {cmp['rel_tol']}")
    if "ropelength" in cmp:
        print(f"ropelength    = {cmp['ropelength']}  (radius units)")
    if "residual" in cmp:
        print(f"residual      = {cmp['residual']}")
    if cmp["within_tol"]:
        print("RESULT: WITHIN TOLERANCE")
    else:
        print("RESULT: ABOVE TOLERANCE (see residual / extend polish if needed)")


def default_ideal_path() -> Path:
    return DEFAULT_IDEAL


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sample Gilbert AB Fourier block to XYZ .txt"
    )
    parser.add_argument(
        "--ideal",
        type=Path,
        default=None,
        help=f"path to ideal favorites (default: {DEFAULT_IDEAL})",
    )
    parser.add_argument("--id", default="3:1:1", help="AB Id (default: 3:1:1)")
    parser.add_argument(
        "--points",
        type=int,
        default=300,
        help="number of sample points (default: 300)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="output XYZ .txt path (required unless --compare-metrics)",
    )
    parser.add_argument(
        "--mirror",
        action="store_true",
        help="mirror z → -z after reconstruction",
    )
    parser.add_argument(
        "--compare-metrics",
        type=Path,
        default=None,
        metavar="METRICS_JSON",
        help="compare polish *.metrics.json L_diam to TARGET_L_3_1_DIAM",
    )
    parser.add_argument(
        "--rel-tol",
        type=float,
        default=1e-4,
        help="relative tolerance for --compare-metrics (default: 1e-4)",
    )
    parser.add_argument(
        "--allow-curvature-only",
        action="store_true",
        help="skip C_cont>0.05 usability gate (diagnostics only)",
    )
    parser.add_argument(
        "--min-c-cont",
        type=float,
        default=DEFAULT_MIN_C_CONT,
        help=f"minimum C_cont to accept as ideal (default: {DEFAULT_MIN_C_CONT})",
    )
    args = parser.parse_args(argv)

    if args.compare_metrics is not None:
        if not args.compare_metrics.is_file():
            print(
                f"error: metrics not found: {args.compare_metrics}",
                file=sys.stderr,
            )
            return 1
        try:
            cmp = compare_metrics_file(
                args.compare_metrics, rel_tol=args.rel_tol
            )
        except (OSError, ValueError, KeyError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print_compare_report(cmp)
        return 0 if cmp["within_tol"] else 2

    if args.output is None:
        print(
            "error: -o/--output is required unless --compare-metrics",
            file=sys.stderr,
        )
        return 1

    ideal_path = args.ideal or default_ideal_path()
    if not ideal_path.is_file():
        print(f"error: ideal file not found: {ideal_path}", file=sys.stderr)
        return 1

    text = ideal_path.read_text(encoding="utf-8", errors="replace")
    try:
        coeffs, attrs = parse_ideal_ab_block(text, args.id)
        D = float(attrs.get("D", "1").strip())
        if not args.allow_curvature_only:
            _pts, report = usability_from_coeffs(
                coeffs, D=D, samples=max(128, args.points), min_c_cont=args.min_c_cont
            )
            if not report["usable"]:
                raise CurvatureOnlyIdealError(
                    f"Gilbert {args.id} fails C_cont gate: "
                    f"C_cont={report['C_cont']:.6g} <= {args.min_c_cont} "
                    f"(kappa_hat_max={report['kappa_hat_max']:.6g}). "
                    f"Pass --allow-curvature-only only for diagnostics."
                )
            print(
                f"  C_cont={report['C_cont']:.6g}  "
                f"kappa_hat_max={report['kappa_hat_max']:.6g}  (usable)"
            )
        points = reconstruct_ideal_ab(
            text, args.id, args.points, mirror=args.mirror
        )
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    length = polygonal_length(points)
    gilbert_l = attrs.get("L")
    gilbert_d = attrs.get("D")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(points_to_xyz_txt(points), encoding="utf-8")

    print(f"Wrote: {args.output}")
    print(f"  id={args.id}  points={args.points}  harmonics={len(coeffs)}")
    print(f"  Gilbert L={gilbert_l}  D={gilbert_d}  (seed attrs)")
    print(f"  sampled polygonal L={length:.9f}  (seed, not polish target)")
    print(
        f"  polish target L_diam={TARGET_L_3_1_DIAM}  "
        f"(Rop_radius={TARGET_ROP_RADIUS})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
