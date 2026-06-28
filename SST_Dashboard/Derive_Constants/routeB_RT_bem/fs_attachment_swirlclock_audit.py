#!/usr/bin/env python3
"""
fs_attachment_swirlclock_audit.py

Research-track numerical audit for an SST Swirl-clock / entanglement-coupling
ansatz and its relevance to the Attachment Lemma.

Model summary
-------------
Let s_ij be the entanglement entropy, A_ij a dimensionless global attachment
amplitude, and lambda_SE the dimensionless swirl-entanglement coupling.

    eps_ij = lambda_SE * s_ij * A_ij

The visible 3D circulation/holonomy partition is modeled as

    Gamma_3 = Gamma_total / (1 + sigma * eps_ij)
    chi_3   = chi_total   / (1 + sigma * eps_ij)
    chi_att = sigma * eps_ij * chi_3

where sigma = +1 is a leakage-like partition and sigma = -1 is a loading-like
partition. The closure residual

    chi_total - (chi_3 + chi_att)

must vanish up to floating-point tolerance.

The Swirl Clock is audited as

    S_t = sqrt(1 - (u_theta0 / (c * (1 + sigma*eps)))^2)

with default u_theta0 = |v_swirl| at r = r_c.

Spectroscopic constraint proxy
------------------------------
If a transition frequency scales like denom^{-kappa}, then

    delta_nu/nu = denom^{-kappa} - 1,
    denom = 1 + sigma*eps.

For a hyperfine/contact-locking proxy, use kappa=3.  Hydrogen spectroscopy
motivates a very conservative default tolerance 1e-12 for such fractional shifts.
If the coupling leaks net electric charge/flux, hydrogen neutrality motivates a
much stronger default bound |eps| <= 1e-20.  Use --neutrality-mode compensated
for a charge-neutral phase-clock coupling.

This script does not prove the Attachment Lemma. It tests whether a proposed
entanglement-weighted global attachment ansatz is internally consistent and not
already excluded by simple hydrogen-like null constraints.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional


# --- SST canonical constants used by default ---
C_LIGHT = 299_792_458.0  # m s^-1
V_SWIRL = 1.09384563e6  # m s^-1, |v_{circlearrowleft}|
R_C = 1.40897017e-15  # m
RHO_F = 7.0e-7  # kg m^-3
GAMMA_CORE = 2.0 * math.pi * R_C * V_SWIRL  # m^2 s^-1


@dataclass
class Scenario:
    name: str = "default_bell_attachment"
    s: float = math.log(2.0)         # Bell-pair entropy, dimensionless
    A: float = 1.0                  # attachment amplitude, dimensionless
    lambda_SE: float = 1e-13        # swirl-entanglement coupling, dimensionless
    sigma: int = +1                 # +1 leakage, -1 loading
    chi_total: float = 1.0 / (2.0 * math.pi)
    r: float = R_C
    u_theta0: float = V_SWIRL


@dataclass
class AuditResult:
    name: str
    s: float
    A: float
    lambda_SE: float
    sigma: int
    epsilon: float
    denom: float
    valid_partition: bool
    valid_clock: bool
    chi_total: float
    chi_3: float
    chi_att: float
    chi_residual: float
    chi_residual_abs: float
    Gamma_total_m2_s: float
    Gamma_3_m2_s: float
    Gamma_att_m2_s: float
    u_theta0_m_s: float
    u_theta3_m_s: float
    beta0: float
    beta3: float
    S_t0: float
    S_t: float
    delta_S_t: float
    frac_delta_S_t: float
    swirl_energy_density0_J_m3: float
    swirl_energy_density3_J_m3: float
    frac_delta_energy_density: float
    kappa: float
    frac_delta_frequency: float
    passes_frequency_bound: bool
    frequency_tolerance: float
    neutrality_mode: str
    neutrality_proxy_abs_epsilon: float
    passes_neutrality_bound: bool
    neutrality_tolerance: float
    status: str


def _safe_float(row: dict, key: str, default: float) -> float:
    value = row.get(key, "")
    if value is None or str(value).strip() == "":
        return default
    return float(value)


def _safe_int(row: dict, key: str, default: int) -> int:
    value = row.get(key, "")
    if value is None or str(value).strip() == "":
        return default
    return int(float(value))


def load_scenarios_csv(path: Path) -> List[Scenario]:
    scenarios: List[Scenario] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            base = Scenario()
            scenarios.append(
                Scenario(
                    name=row.get("name") or f"scenario_{idx}",
                    s=_safe_float(row, "s", base.s),
                    A=_safe_float(row, "A", base.A),
                    lambda_SE=_safe_float(row, "lambda_SE", base.lambda_SE),
                    sigma=_safe_int(row, "sigma", base.sigma),
                    chi_total=_safe_float(row, "chi_total", base.chi_total),
                    r=_safe_float(row, "r", base.r),
                    u_theta0=_safe_float(row, "u_theta0", base.u_theta0),
                )
            )
    return scenarios


def logspace(start_exp: float, stop_exp: float, n: int) -> Iterable[float]:
    if n <= 1:
        yield 10.0 ** start_exp
        return
    for i in range(n):
        t = i / (n - 1)
        yield 10.0 ** (start_exp + t * (stop_exp - start_exp))


def make_scan_scenarios(
    s: float,
    A: float,
    sigma: int,
    lambda_min_exp: float,
    lambda_max_exp: float,
    n: int,
    chi_total: float,
    r: float,
    u_theta0: float,
) -> List[Scenario]:
    return [
        Scenario(
            name=f"scan_lambda_{lam:.3e}",
            s=s,
            A=A,
            lambda_SE=lam,
            sigma=sigma,
            chi_total=chi_total,
            r=r,
            u_theta0=u_theta0,
        )
        for lam in logspace(lambda_min_exp, lambda_max_exp, n)
    ]


def audit_scenario(
    scenario: Scenario,
    *,
    kappa: float,
    frequency_tolerance: float,
    neutrality_mode: str,
    neutrality_tolerance: float,
    closure_tolerance: float,
) -> AuditResult:
    if scenario.sigma not in (-1, +1):
        raise ValueError(f"Scenario {scenario.name!r}: sigma must be +1 or -1.")
    if scenario.r <= 0:
        raise ValueError(f"Scenario {scenario.name!r}: r must be positive.")
    if scenario.u_theta0 < 0:
        raise ValueError(f"Scenario {scenario.name!r}: u_theta0 must be non-negative.")

    epsilon = scenario.lambda_SE * scenario.s * scenario.A
    denom = 1.0 + scenario.sigma * epsilon
    valid_partition = denom > 0.0 and math.isfinite(denom)

    if not valid_partition:
        # Return a mostly populated failed record without taking invalid square roots.
        return AuditResult(
            name=scenario.name,
            s=scenario.s,
            A=scenario.A,
            lambda_SE=scenario.lambda_SE,
            sigma=scenario.sigma,
            epsilon=epsilon,
            denom=denom,
            valid_partition=False,
            valid_clock=False,
            chi_total=scenario.chi_total,
            chi_3=float("nan"),
            chi_att=float("nan"),
            chi_residual=float("nan"),
            chi_residual_abs=float("inf"),
            Gamma_total_m2_s=GAMMA_CORE,
            Gamma_3_m2_s=float("nan"),
            Gamma_att_m2_s=float("nan"),
            u_theta0_m_s=scenario.u_theta0,
            u_theta3_m_s=float("nan"),
            beta0=(scenario.u_theta0 / C_LIGHT) ** 2,
            beta3=float("nan"),
            S_t0=float("nan"),
            S_t=float("nan"),
            delta_S_t=float("nan"),
            frac_delta_S_t=float("nan"),
            swirl_energy_density0_J_m3=0.5 * RHO_F * scenario.u_theta0**2,
            swirl_energy_density3_J_m3=float("nan"),
            frac_delta_energy_density=float("nan"),
            kappa=kappa,
            frac_delta_frequency=float("nan"),
            passes_frequency_bound=False,
            frequency_tolerance=frequency_tolerance,
            neutrality_mode=neutrality_mode,
            neutrality_proxy_abs_epsilon=abs(epsilon),
            passes_neutrality_bound=False,
            neutrality_tolerance=neutrality_tolerance,
            status="FAIL: invalid partition denominator",
        )

    chi_3 = scenario.chi_total / denom
    chi_att = scenario.sigma * epsilon * chi_3
    chi_residual = scenario.chi_total - (chi_3 + chi_att)
    chi_residual_abs = abs(chi_residual)

    Gamma_total = GAMMA_CORE
    Gamma_3 = Gamma_total / denom
    Gamma_att = scenario.sigma * epsilon * Gamma_3

    u_theta3 = scenario.u_theta0 / denom
    beta0 = (scenario.u_theta0 / C_LIGHT) ** 2
    beta3 = (u_theta3 / C_LIGHT) ** 2
    valid_clock = beta0 < 1.0 and beta3 < 1.0

    S_t0 = math.sqrt(max(0.0, 1.0 - beta0)) if beta0 <= 1.0 else float("nan")
    S_t = math.sqrt(max(0.0, 1.0 - beta3)) if beta3 <= 1.0 else float("nan")
    delta_S_t = S_t - S_t0 if valid_clock else float("nan")
    frac_delta_S_t = delta_S_t / S_t0 if valid_clock and S_t0 != 0.0 else float("nan")

    ed0 = 0.5 * RHO_F * scenario.u_theta0**2
    ed3 = 0.5 * RHO_F * u_theta3**2
    frac_delta_ed = (ed3 / ed0) - 1.0 if ed0 != 0.0 else float("nan")

    frac_delta_frequency = denom ** (-kappa) - 1.0
    passes_frequency_bound = abs(frac_delta_frequency) <= frequency_tolerance

    if neutrality_mode == "none" or neutrality_mode == "compensated":
        passes_neutrality_bound = True
    elif neutrality_mode == "charge-leak":
        passes_neutrality_bound = abs(epsilon) <= neutrality_tolerance
    else:
        raise ValueError("neutrality_mode must be one of: none, compensated, charge-leak")

    passes_closure = chi_residual_abs <= closure_tolerance

    status_parts = []
    if not passes_closure:
        status_parts.append("FAIL: holonomy closure")
    if not valid_clock:
        status_parts.append("FAIL: superluminal/invalid clock")
    if not passes_frequency_bound:
        status_parts.append("FAIL: frequency bound")
    if not passes_neutrality_bound:
        status_parts.append("FAIL: neutrality bound")
    status = "PASS" if not status_parts else "; ".join(status_parts)

    return AuditResult(
        name=scenario.name,
        s=scenario.s,
        A=scenario.A,
        lambda_SE=scenario.lambda_SE,
        sigma=scenario.sigma,
        epsilon=epsilon,
        denom=denom,
        valid_partition=valid_partition,
        valid_clock=valid_clock,
        chi_total=scenario.chi_total,
        chi_3=chi_3,
        chi_att=chi_att,
        chi_residual=chi_residual,
        chi_residual_abs=chi_residual_abs,
        Gamma_total_m2_s=Gamma_total,
        Gamma_3_m2_s=Gamma_3,
        Gamma_att_m2_s=Gamma_att,
        u_theta0_m_s=scenario.u_theta0,
        u_theta3_m_s=u_theta3,
        beta0=beta0,
        beta3=beta3,
        S_t0=S_t0,
        S_t=S_t,
        delta_S_t=delta_S_t,
        frac_delta_S_t=frac_delta_S_t,
        swirl_energy_density0_J_m3=ed0,
        swirl_energy_density3_J_m3=ed3,
        frac_delta_energy_density=frac_delta_ed,
        kappa=kappa,
        frac_delta_frequency=frac_delta_frequency,
        passes_frequency_bound=passes_frequency_bound,
        frequency_tolerance=frequency_tolerance,
        neutrality_mode=neutrality_mode,
        neutrality_proxy_abs_epsilon=abs(epsilon),
        passes_neutrality_bound=passes_neutrality_bound,
        neutrality_tolerance=neutrality_tolerance,
        status=status,
    )


def write_csv(results: List[AuditResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(r) for r in results]
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(results: List[AuditResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2, allow_nan=True)


def write_markdown(results: List[AuditResult], path: Path, args: argparse.Namespace) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = len(results)
    n_pass = sum(1 for r in results if r.status == "PASS")
    n_freq_fail = sum(1 for r in results if not r.passes_frequency_bound)
    n_neut_fail = sum(1 for r in results if not r.passes_neutrality_bound)
    max_abs_eps = max((abs(r.epsilon) for r in results), default=float("nan"))
    max_abs_freq = max((abs(r.frac_delta_frequency) for r in results if math.isfinite(r.frac_delta_frequency)), default=float("nan"))
    max_abs_clock = max((abs(r.frac_delta_S_t) for r in results if math.isfinite(r.frac_delta_S_t)), default=float("nan"))

    with path.open("w", encoding="utf-8") as f:
        f.write("# SST Attachment Lemma / Swirl-Clock Entanglement Audit\n\n")
        f.write("## Model\n\n")
        f.write("```text\n")
        f.write("epsilon = lambda_SE * s * A\n")
        f.write("denom   = 1 + sigma * epsilon\n")
        f.write("chi_3   = chi_total / denom\n")
        f.write("chi_att = sigma * epsilon * chi_3\n")
        f.write("S_t     = sqrt(1 - (u_theta0 / (c * denom))^2)\n")
        f.write("delta_nu/nu = denom^(-kappa) - 1\n")
        f.write("```\n\n")
        f.write("## Constants\n\n")
        f.write(f"- c = {C_LIGHT:.12e} m s^-1\n")
        f.write(f"- |v_swirl| = {V_SWIRL:.12e} m s^-1\n")
        f.write(f"- r_c = {R_C:.12e} m\n")
        f.write(f"- rho_f = {RHO_F:.12e} kg m^-3\n")
        f.write(f"- Gamma_core = 2*pi*r_c*|v_swirl| = {GAMMA_CORE:.12e} m^2 s^-1\n\n")
        f.write("## Audit settings\n\n")
        f.write(f"- kappa = {args.kappa}\n")
        f.write(f"- frequency_tolerance = {args.frequency_tolerance:.3e}\n")
        f.write(f"- neutrality_mode = {args.neutrality_mode}\n")
        f.write(f"- neutrality_tolerance = {args.neutrality_tolerance:.3e}\n")
        f.write(f"- closure_tolerance = {args.closure_tolerance:.3e}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- scenarios = {n}\n")
        f.write(f"- pass = {n_pass}\n")
        f.write(f"- frequency_bound_fail = {n_freq_fail}\n")
        f.write(f"- neutrality_bound_fail = {n_neut_fail}\n")
        f.write(f"- max |epsilon| = {max_abs_eps:.12e}\n")
        f.write(f"- max |delta_nu/nu| = {max_abs_freq:.12e}\n")
        f.write(f"- max |delta S_t/S_t0| = {max_abs_clock:.12e}\n\n")
        f.write("## First 25 scenarios\n\n")
        f.write("| name | epsilon | delta_nu/nu | delta S_t/S_t0 | chi_residual_abs | status |\n")
        f.write("|---|---:|---:|---:|---:|---|\n")
        for r in results[:25]:
            f.write(
                f"| {r.name} | {r.epsilon:.3e} | {r.frac_delta_frequency:.3e} | "
                f"{r.frac_delta_S_t:.3e} | {r.chi_residual_abs:.3e} | {r.status} |\n"
            )
        f.write("\n")
        f.write("## Interpretation\n\n")
        f.write("A PASS means this specific parameter point is internally consistent, keeps the holonomy partition closed, and does not exceed the chosen proxy bounds.\n\n")
        f.write("A frequency-bound failure means the entanglement-weighted attachment would produce a transition shift larger than the selected spectroscopic tolerance.\n\n")
        f.write("A neutrality-bound failure only matters if --neutrality-mode charge-leak is selected. For a charge-neutral phase-clock coupling, use --neutrality-mode compensated.\n")


def print_console_summary(results: List[AuditResult]) -> None:
    n = len(results)
    n_pass = sum(1 for r in results if r.status == "PASS")
    print(f"Scenarios audited: {n}")
    print(f"PASS: {n_pass}")
    if results:
        first = results[0]
        print("\nFirst scenario:")
        for key in [
            "name", "epsilon", "denom", "S_t0", "S_t", "frac_delta_S_t",
            "frac_delta_frequency", "chi_residual_abs", "status",
        ]:
            print(f"  {key}: {getattr(first, key)}")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Audit SST Swirl-clock / entanglement coupling for Attachment Lemma consistency."
    )
    p.add_argument("--input", type=Path, default=None, help="Optional CSV of scenarios.")
    p.add_argument("--outdir", type=Path, default=Path("attachment_audit_out"), help="Output directory.")
    p.add_argument("--kappa", type=float, default=3.0, help="Transition scaling exponent; kappa=3 for hyperfine/contact-locking.")
    p.add_argument("--frequency-tolerance", type=float, default=1e-12, help="Allowed |delta_nu/nu|.")
    p.add_argument("--neutrality-mode", choices=["none", "compensated", "charge-leak"], default="compensated")
    p.add_argument("--neutrality-tolerance", type=float, default=1e-20, help="Allowed |epsilon| if neutrality-mode=charge-leak.")
    p.add_argument("--closure-tolerance", type=float, default=1e-14, help="Allowed absolute holonomy closure residual.")

    # Single-scenario defaults
    p.add_argument("--s", type=float, default=math.log(2.0), help="Entanglement entropy.")
    p.add_argument("--A", type=float, default=1.0, help="Attachment amplitude.")
    p.add_argument("--lambda-SE", dest="lambda_SE", type=float, default=1e-13, help="Swirl-entanglement coupling.")
    p.add_argument("--sigma", type=int, choices=[-1, 1], default=1, help="+1 leakage, -1 loading.")
    p.add_argument("--chi-total", type=float, default=1.0 / (2.0 * math.pi), help="Total holonomy chi.")
    p.add_argument("--r", type=float, default=R_C, help="Audit radius in m.")
    p.add_argument("--u-theta0", type=float, default=V_SWIRL, help="Unperturbed tangential swirl speed in m/s.")

    # Scan mode
    p.add_argument("--scan", action="store_true", help="Scan lambda_SE logarithmically instead of one scenario.")
    p.add_argument("--lambda-min-exp", type=float, default=-25.0, help="log10 minimum lambda_SE for scan.")
    p.add_argument("--lambda-max-exp", type=float, default=-5.0, help="log10 maximum lambda_SE for scan.")
    p.add_argument("--scan-n", type=int, default=201, help="Number of scan points.")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.input is not None:
        scenarios = load_scenarios_csv(args.input)
    elif args.scan:
        scenarios = make_scan_scenarios(
            s=args.s,
            A=args.A,
            sigma=args.sigma,
            lambda_min_exp=args.lambda_min_exp,
            lambda_max_exp=args.lambda_max_exp,
            n=args.scan_n,
            chi_total=args.chi_total,
            r=args.r,
            u_theta0=args.u_theta0,
        )
    else:
        scenarios = [
            Scenario(
                name="single",
                s=args.s,
                A=args.A,
                lambda_SE=args.lambda_SE,
                sigma=args.sigma,
                chi_total=args.chi_total,
                r=args.r,
                u_theta0=args.u_theta0,
            )
        ]

    results = [
        audit_scenario(
            s,
            kappa=args.kappa,
            frequency_tolerance=args.frequency_tolerance,
            neutrality_mode=args.neutrality_mode,
            neutrality_tolerance=args.neutrality_tolerance,
            closure_tolerance=args.closure_tolerance,
        )
        for s in scenarios
    ]

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(results, args.outdir / "attachment_swirlclock_audit_results.csv")
    write_json(results, args.outdir / "attachment_swirlclock_audit_results.json")
    write_markdown(results, args.outdir / "attachment_swirlclock_audit_summary.md", args)
    print_console_summary(results)
    print(f"\nWrote: {args.outdir / 'attachment_swirlclock_audit_results.csv'}")
    print(f"Wrote: {args.outdir / 'attachment_swirlclock_audit_results.json'}")
    print(f"Wrote: {args.outdir / 'attachment_swirlclock_audit_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
