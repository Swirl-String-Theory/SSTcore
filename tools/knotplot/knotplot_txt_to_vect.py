#!/usr/bin/env python3
"""
Convert KnotPlot plain-text XYZ exports to Geomview/plCurve VECT files
suitable as Ridgerunner input.

Input conventions
-----------------
- Each non-empty line starts with: x y z
- Blank lines separate link components.
- Components are treated as closed polygons.
- If a file has multiple components but no blank separators, use
  --component-size N or --component-count K.

Examples
--------
Single trefoil:
    python knotplot_txt_to_vect.py T_2_3_trial_005k.txt

Three-component link:
    python knotplot_txt_to_vect.py Tlink_6_9_D1_040k.txt

Batch:
    python knotplot_txt_to_vect.py --scan . --glob "*.txt"

Explicit output:
    python knotplot_txt_to_vect.py input.txt --output output.vect
"""

from __future__ import annotations

from pathlib import Path
import argparse
import math
import sys
from typing import Iterable

Point = tuple[float, float, float]

DEFAULT_COLORS: tuple[tuple[float, float, float, float], ...] = (
    (0.20, 0.65, 1.00, 1.00),
    (1.00, 0.45, 0.25, 1.00),
    (0.35, 0.85, 0.45, 1.00),
    (0.80, 0.45, 1.00, 1.00),
    (1.00, 0.80, 0.20, 1.00),
    (0.25, 0.90, 0.85, 1.00),
)


def parse_xyz_lines(path: Path) -> list[list[Point]]:
    """Parse blank-line-separated components."""
    components: list[list[Point]] = []
    current: list[Point] = []

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        line = raw_line.strip()

        if not line:
            if current:
                components.append(current)
                current = []
            continue

        # Allow comments in source files.
        if line.startswith("#"):
            continue

        fields = line.replace(",", " ").split()
        if len(fields) < 3:
            raise ValueError(
                f"{path}:{line_number}: expected at least three numeric fields"
            )

        try:
            point = tuple(float(value) for value in fields[:3])
        except ValueError as exc:
            raise ValueError(
                f"{path}:{line_number}: invalid XYZ coordinate: {raw_line!r}"
            ) from exc

        if not all(math.isfinite(value) for value in point):
            raise ValueError(
                f"{path}:{line_number}: coordinates must be finite"
            )

        current.append(point)  # type: ignore[arg-type]

    if current:
        components.append(current)

    if not components:
        raise ValueError(f"{path}: no XYZ coordinates found")

    return components


def split_components(
    components: list[list[Point]],
    *,
    component_size: int | None,
    component_count: int | None,
) -> list[list[Point]]:
    """
    Optionally split a single unseparated coordinate stream.
    Blank-line-separated files need no extra arguments.
    """
    if component_size is not None and component_count is not None:
        raise ValueError("use either --component-size or --component-count, not both")

    if len(components) != 1:
        if component_size is not None or component_count is not None:
            raise ValueError(
                "component splitting options are only valid when the input "
                "contains no blank-line component separators"
            )
        return components

    points = components[0]

    if component_size is not None:
        if component_size < 3:
            raise ValueError("--component-size must be at least 3")
        if len(points) % component_size != 0:
            raise ValueError(
                f"{len(points)} vertices cannot be divided into components "
                f"of size {component_size}"
            )
        return [
            points[start : start + component_size]
            for start in range(0, len(points), component_size)
        ]

    if component_count is not None:
        if component_count < 1:
            raise ValueError("--component-count must be at least 1")
        if len(points) % component_count != 0:
            raise ValueError(
                f"{len(points)} vertices cannot be divided evenly over "
                f"{component_count} components"
            )
        size = len(points) // component_count
        if size < 3:
            raise ValueError("each component must contain at least 3 vertices")
        return [
            points[index * size : (index + 1) * size]
            for index in range(component_count)
        ]

    return components


def remove_duplicate_closure(
    components: list[list[Point]], tolerance: float
) -> list[list[Point]]:
    """
    VECT closes a component using a negative vertex count, so an explicitly
    repeated final copy of the first point is unnecessary and undesirable.
    """
    cleaned: list[list[Point]] = []

    for index, component in enumerate(components, start=1):
        points = list(component)

        if len(points) >= 2:
            first = points[0]
            last = points[-1]
            distance = math.dist(first, last)
            if distance <= tolerance:
                points.pop()

        if len(points) < 3:
            raise ValueError(
                f"component {index} has fewer than 3 distinct vertices"
            )

        cleaned.append(points)

    return cleaned


def vect_text(
    components: list[list[Point]],
    *,
    source_name: str,
    include_colors: bool,
) -> str:
    component_count = len(components)
    total_vertices = sum(len(component) for component in components)

    # In Geomview VECT, negative counts mark closed polylines.
    vertex_counts = [-len(component) for component in components]

    if include_colors:
        color_counts = [1] * component_count
        total_colors = component_count
    else:
        color_counts = [0] * component_count
        total_colors = 0

    lines: list[str] = [
        "VECT",
        f"# Converted from KnotPlot XYZ: {source_name}",
        f"# {component_count} closed component(s), {total_vertices} vertices",
        f"{component_count} {total_vertices} {total_colors}",
        " ".join(str(value) for value in vertex_counts),
        " ".join(str(value) for value in color_counts),
    ]

    for component_index, component in enumerate(components):
        lines.append(f"# component {component_index}")
        for x, y, z in component:
            lines.append(f"{x:.17g} {y:.17g} {z:.17g}")

    if include_colors:
        lines.append("# one RGBA color per component")
        for index in range(component_count):
            r, g, b, a = DEFAULT_COLORS[index % len(DEFAULT_COLORS)]
            lines.append(f"{r:.6g} {g:.6g} {b:.6g} {a:.6g}")

    return "\n".join(lines) + "\n"


def validate_vect_text(text: str) -> dict[str, object]:
    """
    Lightweight structural validation of the VECT emitted by this script.
    Comments are removed before tokenization.
    """
    tokens: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line:
            tokens.extend(line.split())

    if not tokens or tokens[0] != "VECT":
        raise ValueError("generated output does not start with VECT")

    cursor = 1
    component_count = int(tokens[cursor])
    total_vertices = int(tokens[cursor + 1])
    total_colors = int(tokens[cursor + 2])
    cursor += 3

    vertex_counts = [int(tokens[cursor + i]) for i in range(component_count)]
    cursor += component_count

    color_counts = [int(tokens[cursor + i]) for i in range(component_count)]
    cursor += component_count

    if sum(abs(value) for value in vertex_counts) != total_vertices:
        raise ValueError("VECT vertex-count header is inconsistent")
    if sum(color_counts) != total_colors:
        raise ValueError("VECT color-count header is inconsistent")
    if any(value >= 0 for value in vertex_counts):
        raise ValueError("all emitted components must be marked closed")

    coordinate_token_count = 3 * total_vertices
    cursor += coordinate_token_count

    color_token_count = 4 * total_colors
    cursor += color_token_count

    if cursor != len(tokens):
        raise ValueError(
            f"unexpected token count: consumed {cursor}, found {len(tokens)}"
        )

    return {
        "components": component_count,
        "vertices": total_vertices,
        "colors": total_colors,
        "verticesPerComponent": [abs(value) for value in vertex_counts],
    }


def convert_one(
    input_path: Path,
    output_path: Path,
    *,
    component_size: int | None,
    component_count: int | None,
    closure_tolerance: float,
    include_colors: bool,
    overwrite: bool,
) -> dict[str, object]:
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"{output_path} already exists; use --overwrite to replace it"
        )

    components = parse_xyz_lines(input_path)
    components = split_components(
        components,
        component_size=component_size,
        component_count=component_count,
    )
    components = remove_duplicate_closure(components, closure_tolerance)

    text = vect_text(
        components,
        source_name=input_path.name,
        include_colors=include_colors,
    )
    report = validate_vect_text(text)

    output_path.write_text(text, encoding="utf-8", newline="\n")
    return report


def collect_inputs(
    positional: Iterable[Path],
    scan_directory: Path | None,
    glob_pattern: str,
) -> list[Path]:
    candidates = list(positional)

    if scan_directory is not None:
        candidates.extend(sorted(scan_directory.glob(glob_pattern)))

    unique: list[Path] = []
    seen: set[Path] = set()

    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            unique.append(candidate)
            seen.add(resolved)

    return unique


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert KnotPlot XYZ text files to closed Geomview/plCurve "
            "VECT files for Ridgerunner."
        )
    )
    parser.add_argument("inputs", nargs="*", type=Path)
    parser.add_argument("--scan", type=Path, help="scan a directory")
    parser.add_argument(
        "--glob",
        default="*.txt",
        help="glob used with --scan (default: *.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output path; valid only for one input",
    )
    parser.add_argument(
        "--component-size",
        type=int,
        help="split an unseparated stream every N vertices",
    )
    parser.add_argument(
        "--component-count",
        type=int,
        help="split an unseparated stream into K equal components",
    )
    parser.add_argument(
        "--closure-tolerance",
        type=float,
        default=1e-12,
        help="remove repeated last=first point within this tolerance",
    )
    parser.add_argument(
        "--no-colors",
        action="store_true",
        help="write no component colors",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace existing .vect outputs",
    )

    args = parser.parse_args()

    inputs = collect_inputs(args.inputs, args.scan, args.glob)
    if not inputs:
        parser.error("provide input files or use --scan")
    if args.output is not None and len(inputs) != 1:
        parser.error("--output is valid only with exactly one input")
    if args.closure_tolerance < 0:
        parser.error("--closure-tolerance must be non-negative")

    for input_path in inputs:
        output_path = args.output or input_path.with_suffix(".vect")
        report = convert_one(
            input_path,
            output_path,
            component_size=args.component_size,
            component_count=args.component_count,
            closure_tolerance=args.closure_tolerance,
            include_colors=not args.no_colors,
            overwrite=args.overwrite,
        )
        print(
            f"{input_path.name} -> {output_path.name}: "
            f"{report['components']} component(s), "
            f"{report['vertices']} vertices, "
            f"per component {report['verticesPerComponent']}"
        )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
