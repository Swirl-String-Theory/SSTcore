#!/usr/bin/env python3
"""
sst_schrodinger_knot_boundary_locking_spectral.py

Gate-4 exploratory spectral audit for knot-boundary locking on a horn-torus
surface around a trefoil-like knot.

Purpose:
    Test whether a horn-torus boundary can select/lock allowed phase windings
    and whether it can plausibly explain the Schrödinger coefficient gate.

Important honesty constraint:
    This script is a reduced spectral/holonomy audit, not a full BEM/FEM solver.
    It should be treated as [RESEARCH GATE] tooling. Its most important failure
    mode is meaningful: if n_core=1 is not selected without an imposed core-cycle
    constraint, knot-boundary locking is a quantization/selection mechanism, not
    the source of the large Compton/R-phase renormalization factor.

Model:
    A trefoil centerline R(t) is sampled. A horn-torus tube of radius r_c is
    represented by coordinates (s, phi). A phase field is approximated by

        theta(s,phi) = 2*pi*n_s*s/L + n_core*phi

    with a geometric connection A_s from integrated frame twist. The reduced
    boundary stiffness energy is approximated as

        E ~ 1/2 * ∫ [ (d_s theta - A_s)^2 + (1/r_c^2)(d_phi theta)^2 ] dA.

    The script scans integer (n_s, n_core) and reports the unconstrained minimum
    and the minimum under n_core=1.

Interpretation:
    - If unconstrained minimum is n_core=0, boundary locking alone does NOT
      derive n_core=1.
    - If constrained n_core=1 has a clear longitudinal mode minimum, the boundary
      can select compatible longitudinal holonomy once the core cycle is imposed.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class Candidate:
    n_s: int
    n_core: int
    energy_norm: float
    longitudinal_energy: float
    meridional_energy: float
    holonomy_mismatch: float


def trefoil_centerline(t: np.ndarray, family: str = "torus_2_3") -> np.ndarray:
    """Return Nx3 trefoil-like centerline samples."""
    if family == "torus_2_3":
        # Standard torus knot T(2,3): two poloidal / three toroidal winding convention.
        # Units are dimensionless; later scaled by arclength normalization.
        R = 2.0
        a = 0.7
        x = (R + a * np.cos(3.0 * t)) * np.cos(2.0 * t)
        y = (R + a * np.cos(3.0 * t)) * np.sin(2.0 * t)
        z = a * np.sin(3.0 * t)
        return np.column_stack([x, y, z])
    if family == "classic_param":
        x = np.sin(t) + 2.0 * np.sin(2.0 * t)
        y = np.cos(t) - 2.0 * np.cos(2.0 * t)
        z = -np.sin(3.0 * t)
        return np.column_stack([x, y, z])
    raise ValueError(f"Unknown family: {family}")


def periodic_derivative(arr: np.ndarray, dt: float) -> np.ndarray:
    return (np.roll(arr, -1, axis=0) - np.roll(arr, 1, axis=0)) / (2.0 * dt)


def geometry_invariants(points: np.ndarray) -> dict[str, np.ndarray | float]:
    """Compute arclength, curvature, torsion, and total twist proxy."""
    n = len(points)
    dt = 2.0 * math.pi / n
    r1 = periodic_derivative(points, dt)
    r2 = periodic_derivative(r1, dt)
    r3 = periodic_derivative(r2, dt)

    speed = np.linalg.norm(r1, axis=1)
    ds = speed * dt
    length = float(np.sum(ds))

    cross12 = np.cross(r1, r2)
    cross_norm = np.linalg.norm(cross12, axis=1)
    curvature = cross_norm / np.maximum(speed**3, 1e-30)
    torsion = np.einsum("ij,ij->i", cross12, r3) / np.maximum(cross_norm**2, 1e-30)
    total_twist_proxy = float(np.sum(torsion * ds) / (2.0 * math.pi))

    return {
        "ds": ds,
        "length": length,
        "curvature": curvature,
        "torsion": torsion,
        "total_twist_proxy": total_twist_proxy,
    }


def reduced_energy(
    n_s: int,
    n_core: int,
    length: float,
    tube_radius: float,
    total_twist_proxy: float,
    connection_mode: str = "frenet_twist_average",
) -> Candidate:
    """Reduced horn-torus stiffness energy in dimensionless K_R units."""
    # Effective longitudinal phase gradient.
    dtheta_ds = 2.0 * math.pi * n_s / length

    if connection_mode == "none":
        a_s = 0.0
    elif connection_mode == "frenet_twist_average":
        # If the meridional phase is attached to a rotating frame, n_core samples
        # the geometric frame twist along s.
        a_s = 2.0 * math.pi * n_core * total_twist_proxy / length
    else:
        raise ValueError(f"Unknown connection_mode: {connection_mode}")

    # Surface area element approximated as r_c dphi ds for a thin tube. The common
    # factor 2*pi*r_c*L is retained so energies can be compared across tube radii.
    area = 2.0 * math.pi * tube_radius * length
    longitudinal_density = (dtheta_ds - a_s) ** 2
    meridional_density = (n_core / tube_radius) ** 2

    longitudinal_energy = 0.5 * area * longitudinal_density
    meridional_energy = 0.5 * area * meridional_density
    energy = longitudinal_energy + meridional_energy

    holonomy_mismatch = n_s - n_core * total_twist_proxy
    return Candidate(
        n_s=n_s,
        n_core=n_core,
        energy_norm=float(energy),
        longitudinal_energy=float(longitudinal_energy),
        meridional_energy=float(meridional_energy),
        holonomy_mismatch=float(holonomy_mismatch),
    )


def scan_candidates(
    n_s_range: range,
    n_core_range: range,
    length: float,
    tube_radius: float,
    total_twist_proxy: float,
    connection_mode: str,
) -> list[Candidate]:
    out = []
    for n_core in n_core_range:
        for n_s in n_s_range:
            out.append(
                reduced_energy(
                    n_s=n_s,
                    n_core=n_core,
                    length=length,
                    tube_radius=tube_radius,
                    total_twist_proxy=total_twist_proxy,
                    connection_mode=connection_mode,
                )
            )
    return sorted(out, key=lambda c: c.energy_norm)


def write_csv(candidates: Iterable[Candidate], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "n_s",
                "n_core",
                "energy_norm",
                "longitudinal_energy",
                "meridional_energy",
                "holonomy_mismatch",
            ],
        )
        writer.writeheader()
        for c in candidates:
            writer.writerow(c.__dict__)


def write_summary(
    path: Path,
    family: str,
    length: float,
    total_twist_proxy: float,
    tube_radius: float,
    unconstrained: Candidate,
    constrained_core1: Candidate | None,
    top: list[Candidate],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("# SST Knot-Boundary Locking Spectral Gate\n\n")
        f.write(f"Trefoil family: `{family}`\n\n")
        f.write(f"Dimensionless centerline length: `{length:.12e}`\n\n")
        f.write(f"Tube radius used in reduced audit: `{tube_radius:.12e}`\n\n")
        f.write(f"Total Frenet-twist proxy: `{total_twist_proxy:.12e}` turns\n\n")
        f.write("## Main result\n\n")
        f.write(
            f"Unconstrained minimum: `n_s={unconstrained.n_s}`, "
            f"`n_core={unconstrained.n_core}`, "
            f"`E={unconstrained.energy_norm:.12e}`.\n\n"
        )
        if constrained_core1 is not None:
            f.write(
                f"Minimum under imposed `n_core=1`: `n_s={constrained_core1.n_s}`, "
                f"`E={constrained_core1.energy_norm:.12e}`, "
                f"`holonomy_mismatch={constrained_core1.holonomy_mismatch:.12e}`.\n\n"
            )
        f.write("## Interpretation\n\n")
        if unconstrained.n_core == 1:
            f.write(
                "The reduced model selects `n_core=1` without imposing the core-cycle constraint. "
                "This is a candidate positive signal for knot-boundary locking.\n\n"
            )
        else:
            f.write(
                "The reduced model does **not** select `n_core=1` without imposing the core-cycle constraint. "
                "This means boundary locking alone should not yet be canonized as the source of the core cycle. "
                "It can still select compatible longitudinal holonomy once `n_core=1` is imposed by a separate core-cycle/attachment lemma.\n\n"
            )
        f.write("## Top candidates\n\n")
        f.write("| rank | n_s | n_core | E | E_long | E_merid | holonomy mismatch |\n")
        f.write("|---:|---:|---:|---:|---:|---:|---:|\n")
        for i, c in enumerate(top, start=1):
            f.write(
                f"| {i} | {c.n_s} | {c.n_core} | `{c.energy_norm:.6e}` | "
                f"`{c.longitudinal_energy:.6e}` | `{c.meridional_energy:.6e}` | "
                f"`{c.holonomy_mismatch:.6e}` |\n"
            )


def print_top(candidates: list[Candidate], n: int = 12) -> None:
    print(f"{'rank':>4} {'n_s':>5} {'n_core':>7} {'E':>16} {'E_long':>16} {'E_merid':>16} {'hol_mismatch':>16}")
    print("-" * 90)
    for i, c in enumerate(candidates[:n], start=1):
        print(
            f"{i:4d} {c.n_s:5d} {c.n_core:7d} {c.energy_norm:16.8e} "
            f"{c.longitudinal_energy:16.8e} {c.meridional_energy:16.8e} {c.holonomy_mismatch:16.8e}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="SST knot-boundary locking spectral gate.")
    parser.add_argument("--samples", type=int, default=2048, help="Centerline samples.")
    parser.add_argument("--family", choices=["torus_2_3", "classic_param"], default="torus_2_3")
    parser.add_argument("--tube-radius", type=float, default=0.08, help="Dimensionless horn-torus tube radius for reduced spectral audit.")
    parser.add_argument("--n-s-max", type=int, default=8, help="Scan n_s in [-N,N].")
    parser.add_argument("--n-core-max", type=int, default=4, help="Scan n_core in [-N,N].")
    parser.add_argument("--connection-mode", choices=["none", "frenet_twist_average"], default="frenet_twist_average")
    parser.add_argument("--outdir", type=Path, default=Path("."), help="Directory for CSV/Markdown outputs.")
    parser.add_argument("--no-files", action="store_true", help="Only print; do not write outputs.")
    args = parser.parse_args()

    t = np.linspace(0.0, 2.0 * math.pi, args.samples, endpoint=False)
    pts = trefoil_centerline(t, family=args.family)
    geom = geometry_invariants(pts)
    length = float(geom["length"])
    total_twist_proxy = float(geom["total_twist_proxy"])

    candidates = scan_candidates(
        n_s_range=range(-args.n_s_max, args.n_s_max + 1),
        n_core_range=range(-args.n_core_max, args.n_core_max + 1),
        length=length,
        tube_radius=args.tube_radius,
        total_twist_proxy=total_twist_proxy,
        connection_mode=args.connection_mode,
    )
    unconstrained = candidates[0]
    constrained = [c for c in candidates if c.n_core == 1]
    constrained_core1 = constrained[0] if constrained else None

    print("SST knot-boundary locking reduced spectral audit")
    print("=" * 58)
    print(f"family                      : {args.family}")
    print(f"samples                     : {args.samples}")
    print(f"dimensionless length         : {length:.12e}")
    print(f"tube radius                  : {args.tube_radius:.12e}")
    print(f"total twist proxy            : {total_twist_proxy:.12e} turns")
    print(f"connection mode              : {args.connection_mode}")
    print()
    print("Top candidates:")
    print_top(candidates, n=12)
    print()
    print(
        f"Unconstrained minimum: n_s={unconstrained.n_s}, n_core={unconstrained.n_core}, "
        f"E={unconstrained.energy_norm:.12e}"
    )
    if constrained_core1 is not None:
        print(
            f"Constrained n_core=1 minimum: n_s={constrained_core1.n_s}, "
            f"E={constrained_core1.energy_norm:.12e}, "
            f"holonomy_mismatch={constrained_core1.holonomy_mismatch:.12e}"
        )

    if unconstrained.n_core == 1:
        print("\nGATE SIGNAL: boundary locking selects n_core=1 in this reduced model.")
    else:
        print("\nGATE SIGNAL: boundary locking does NOT select n_core=1 without an imposed core-cycle constraint.")
        print("Interpretation: use as quantization/holonomy selector, not as sole origin of the Compton/R-phase factor.")

    if not args.no_files:
        csv_path = args.outdir / "sst_schrodinger_knot_boundary_locking_spectral_results.csv"
        md_path = args.outdir / "sst_schrodinger_knot_boundary_locking_spectral_summary.md"
        write_csv(candidates, csv_path)
        write_summary(
            md_path,
            family=args.family,
            length=length,
            total_twist_proxy=total_twist_proxy,
            tube_radius=args.tube_radius,
            unconstrained=unconstrained,
            constrained_core1=constrained_core1,
            top=candidates[:12],
        )
        print(f"\nWrote: {csv_path}")
        print(f"Wrote: {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
