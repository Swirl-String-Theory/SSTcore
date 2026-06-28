#!/usr/bin/env python3
"""
sst_schrodinger_gate_constants.py

Gate-1 / Gate-2 numerical audit for the SST Schrödinger--R-phase/Kelvin
Envelope Principle.

Common prefix: sst_schrodinger_

This script checks the numerical identities:

    Gamma_0 = 2*pi*r_c*|v_swirl|
    beta_0  = Gamma_0/(4*pi) = r_c*|v_swirl|/2
    Omega_0 = |v_swirl|/r_c
    lambda_C_bar(SST) = c/Omega_0 = r_c*c/|v_swirl|
    D_e = hbar/(2*m_e)
    D_SST = c^2/(2*Omega_0) = r_c*c^2/(2*|v_swirl|)
    R_SST = D_e/beta_0 = (c/|v_swirl|)^2 = 4/alpha_SST^2

Interpretation:
    If the identities pass numerically, the large Kelvin -> Schrödinger
    coefficient boost is consistent with Compton-core scaling, where r_c is
    treated as the horn-torus flow radius around the knot, not as a bare
    singular-core radius.

Status language:
    PASS here means numerical closure only. It does NOT prove the physical
    mechanism. It supports [DERIVED CONDITIONAL] status for the constants gate.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Constant:
    symbol: str
    value: float
    unit: str
    description: str


# --- Canonical / CODATA constants used by this audit ---
CONSTANTS = {
    "c": Constant("c", 2.99792458e8, "m s^-1", "speed of light"),
    "hbar": Constant("hbar", 1.054571817e-34, "J s", "reduced Planck constant"),
    "m_e": Constant("m_e", 9.1093837015e-31, "kg", "electron mass"),
    "r_c": Constant("r_c", 1.40897017e-15, "m", "SST horn-torus flow radius around knot"),
    "v_swirl": Constant(
        "|v_swirl|",
        1.09384563e6,
        "m s^-1",
        "canonical characteristic swirl speed",
    ),
    "rho_f": Constant("rho_f", 7.0e-7, "kg m^-3", "effective fluid density"),
}


@dataclass(frozen=True)
class AuditRow:
    name: str
    value: float
    unit: str
    reference: float | None = None
    rel_error: float | None = None
    status: str = "INFO"


def rel_error(value: float, reference: float) -> float:
    if reference == 0:
        return math.inf if value != 0 else 0.0
    return abs(value - reference) / abs(reference)


def status_from_error(err: float | None, tolerance: float) -> str:
    if err is None:
        return "INFO"
    return "PASS" if err <= tolerance else "FAIL"


def compute_rows(tolerance: float) -> list[AuditRow]:
    c = CONSTANTS["c"].value
    hbar = CONSTANTS["hbar"].value
    m_e = CONSTANTS["m_e"].value
    r_c = CONSTANTS["r_c"].value
    v = CONSTANTS["v_swirl"].value
    rho_f = CONSTANTS["rho_f"].value

    gamma_0 = 2.0 * math.pi * r_c * v
    beta_0 = gamma_0 / (4.0 * math.pi)
    beta_0_alt = r_c * v / 2.0
    omega_0 = v / r_c
    omega_compton = m_e * c**2 / hbar
    lambda_cbar_sst = c / omega_0
    lambda_cbar_std = hbar / (m_e * c)
    d_e = hbar / (2.0 * m_e)
    d_sst = c**2 / (2.0 * omega_0)
    r_sst = d_e / beta_0
    r_sst_geom = (c / v) ** 2
    alpha_sst = 2.0 * v / c
    r_sst_alpha = 4.0 / alpha_sst**2
    q_swirl = 0.5 * rho_f * v**2
    q_c = 0.5 * rho_f * c**2

    tests = [
        ("Gamma_0", gamma_0, "m^2 s^-1", None),
        ("beta_0 = Gamma_0/(4*pi)", beta_0, "m^2 s^-1", beta_0_alt),
        ("Omega_0 = |v_swirl|/r_c", omega_0, "s^-1", omega_compton),
        ("lambda_Cbar(SST)=c/Omega_0", lambda_cbar_sst, "m", lambda_cbar_std),
        ("D_e = hbar/(2*m_e)", d_e, "m^2 s^-1", None),
        ("D_SST = c^2/(2*Omega_0)", d_sst, "m^2 s^-1", d_e),
        ("R_SST = D_e/beta_0", r_sst, "dimensionless", r_sst_geom),
        ("R_SST = 4/alpha_SST^2", r_sst_alpha, "dimensionless", r_sst_geom),
        ("alpha_SST = 2|v_swirl|/c", alpha_sst, "dimensionless", None),
        ("q_swirl = 0.5*rho_f*|v_swirl|^2", q_swirl, "Pa", None),
        ("q_c = 0.5*rho_f*c^2", q_c, "Pa", None),
    ]

    rows: list[AuditRow] = []
    for name, value, unit, reference in tests:
        err = rel_error(value, reference) if reference is not None else None
        rows.append(
            AuditRow(
                name=name,
                value=value,
                unit=unit,
                reference=reference,
                rel_error=err,
                status=status_from_error(err, tolerance),
            )
        )
    return rows


def format_float(x: float | None) -> str:
    if x is None:
        return ""
    return f"{x:.15e}"


def print_table(rows: Iterable[AuditRow]) -> None:
    header = f"{'status':<8} {'quantity':<42} {'value':>20} {'unit':<14} {'reference':>20} {'rel_error':>12}"
    print(header)
    print("-" * len(header))
    for row in rows:
        err = "" if row.rel_error is None else f"{row.rel_error:.3e}"
        ref = format_float(row.reference)
        print(
            f"{row.status:<8} {row.name:<42} {row.value:>20.12e} {row.unit:<14} {ref:>20} {err:>12}"
        )


def write_csv(rows: Iterable[AuditRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["status", "name", "value", "unit", "reference", "rel_error"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "status": row.status,
                    "name": row.name,
                    "value": row.value,
                    "unit": row.unit,
                    "reference": row.reference,
                    "rel_error": row.rel_error,
                }
            )


def write_markdown(rows: Iterable[AuditRow], path: Path, tolerance: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    overall = "PASS" if all(r.status != "FAIL" for r in rows) else "FAIL"
    with path.open("w", encoding="utf-8") as f:
        f.write("# SST Schrödinger Gate Constants Audit\n\n")
        f.write(f"Tolerance: `{tolerance:.3e}` relative error.\n\n")
        f.write(f"Overall numerical gate status: **{overall}**.\n\n")
        f.write("| status | quantity | value | unit | reference | relative error |\n")
        f.write("|---|---:|---:|---|---:|---:|\n")
        for r in rows:
            f.write(
                f"| {r.status} | {r.name} | `{r.value:.15e}` | {r.unit} | "
                f"`{format_float(r.reference)}` | "
                f"`{'' if r.rel_error is None else f'{r.rel_error:.3e}'}` |\n"
            )
        f.write("\n## Interpretation\n\n")
        f.write(
            "This audit supports the numerical identity\n\n"
            "```tex\n"
            "\\frac{\\hbar}{2m_e}=\\frac{r_c c^2}{2\\lVert\\mathbf{v}_{\\!\\boldsymbol{\\circlearrowleft}}\\rVert}\n"
            "```\n\n"
            "given the stated constants. This closes the constants gate only; the physical origin must still be established by the R-phase envelope and knot-boundary gates.\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="SST Schrödinger constants gate audit.")
    parser.add_argument("--tolerance", type=float, default=2e-8, help="Relative tolerance for PASS/FAIL checks.")
    parser.add_argument("--outdir", type=Path, default=Path("."), help="Directory for CSV/Markdown outputs.")
    parser.add_argument("--no-files", action="store_true", help="Only print; do not write CSV/Markdown outputs.")
    args = parser.parse_args()

    rows = compute_rows(args.tolerance)
    print_table(rows)

    if not args.no_files:
        write_csv(rows, args.outdir / "sst_schrodinger_gate_constants_results.csv")
        write_markdown(rows, args.outdir / "sst_schrodinger_gate_constants_summary.md", args.tolerance)
        print(f"\nWrote: {args.outdir / 'sst_schrodinger_gate_constants_results.csv'}")
        print(f"Wrote: {args.outdir / 'sst_schrodinger_gate_constants_summary.md'}")

    return 0 if all(r.status != "FAIL" for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
