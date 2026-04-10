from __future__ import annotations

"""
Week 1 + 2 combined runner for the SST trefoil multisector program.

What this script does
---------------------
1. Runs robustness scans over:
   - truncation M values
   - optimizer seeds
   - fitting windows
   - target-node subsets

2. Uses an objective with:
   - target-node matching
   - extra-minima suppression
   - optional sector-weight regularization

3. Writes machine-readable outputs:
   - one CSV with every run
   - one grouped summary CSV
   - one JSON summary

4. Optionally renders quick stability plots.

Expected compiled backend
-------------------------
The pybind11 module must expose:
    sst.MultisectorFitter.evaluate_multisector_abs(...)

The script tries to import either:
    import sst
or:
    import swirl_string_core as sst
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
import argparse
import json
import math
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution, minimize
from scipy.signal import find_peaks


# -----------------------------------------------------------------------------
# Backend import
# -----------------------------------------------------------------------------

def _get_kernel_module():
    try:
        import sstcore as sst  # type: ignore
        return sst
    except ImportError:
        try:
            import swirl_string_core as sst  # type: ignore
            return sst
        except ImportError as exc:
            raise ImportError(
                "Could not import compiled SST pybind11 module. Tried 'sst' and 'swirl_string_core'."
            ) from exc


# -----------------------------------------------------------------------------
# Data / config
# -----------------------------------------------------------------------------

@dataclass
class Week12Config:
    sectors: list[int] = field(default_factory=lambda: [2, 3, 5])
    a_nc_over_rc: float = 1.00039865
    completion_mode: str = "none"  # none | exp_linear
    fit_sector_weights: bool = False

    # Week 1 stability scan
    M_values: list[int] = field(default_factory=lambda: [100, 150, 200, 250, 300, 400])
    seeds: list[int] = field(default_factory=lambda: [1001, 1002, 1003, 1004, 1005])
    windows: list[tuple[float, float]] = field(default_factory=lambda: [(20.0, 35.0), (23.0, 34.0), (24.0, 33.0)])
    target_sets: list[list[float]] = field(default_factory=lambda: [[25.18, 26.75, 32.80], [25.18, 26.75]])

    # Week 2 suppression objective
    lambda_extra: float = 0.5
    sigma_extra: float = 0.05
    lambda_reg: float = 0.01

    # Fit settings
    use_global_then_local: bool = True
    de_maxiter: int = 50
    de_popsize: int = 10
    local_method: str = "L-BFGS-B"

    # Forbidden-zone control.
    # If None, neighborhoods are auto-generated from the active target list.
    # Width applies symmetrically around each target.
    target_neighborhood_halfwidth: float = 0.35

    # Evaluation grid cropping for output summary only
    keep_top_minima: int = 8

    @property
    def ell_trefoil(self) -> float:
        return math.log(self.a_nc_over_rc)

    @property
    def completion_mode_code(self) -> int:
        mapping = {"none": 0, "exp_linear": 1}
        if self.completion_mode not in mapping:
            raise ValueError(f"Unsupported completion_mode: {self.completion_mode}")
        return mapping[self.completion_mode]


# -----------------------------------------------------------------------------
# CSV loader
# -----------------------------------------------------------------------------

def load_phi_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}

    if "t" not in cols:
        raise ValueError(f"CSV {path} must contain a 't' column.")

    t_col = cols["t"]
    real_col = next((cols[c] for c in ("phi_real", "real") if c in cols), None)
    imag_col = next((cols[c] for c in ("phi_imag", "imag") if c in cols), None)
    abs_col = next((cols[c] for c in ("phi_abs", "abs") if c in cols), None)

    out = pd.DataFrame()
    out["t"] = df[t_col].astype(float)

    if real_col is not None and imag_col is not None:
        out["phi_real"] = df[real_col].astype(float)
        out["phi_imag"] = df[imag_col].astype(float)
        out["phi_abs"] = np.sqrt(out["phi_real"] ** 2 + out["phi_imag"] ** 2)
    elif abs_col is not None:
        out["phi_real"] = np.nan
        out["phi_imag"] = np.nan
        out["phi_abs"] = df[abs_col].astype(float)
    else:
        raise ValueError(
            f"CSV {path} must contain either real/imag columns or an abs column."
        )

    return out.sort_values("t").reset_index(drop=True)


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def predicted_near_nodes(t: np.ndarray, phi_abs: np.ndarray, max_count: int) -> list[float]:
    peaks, _ = find_peaks(-phi_abs)
    if len(peaks) == 0:
        return []
    candidates = [(t[p], phi_abs[p]) for p in peaks]
    candidates.sort(key=lambda z: z[1])
    nodes = [x for x, _ in candidates[:max_count]]
    return sorted(nodes)


def build_neighborhoods(targets: list[float], halfwidth: float) -> list[tuple[float, float]]:
    return [(t - halfwidth, t + halfwidth) for t in targets]


def in_any_interval(x: float, intervals: list[tuple[float, float]]) -> bool:
    for a, b in intervals:
        if a <= x <= b:
            return True
    return False


def phase_invariants(thetas: Iterable[float]) -> tuple[float, float, float]:
    vals = list(thetas)
    if len(vals) < 3:
        return float("nan"), float("nan"), float("nan")
    d23 = vals[0] - vals[1]
    d35 = vals[1] - vals[2]
    tsum = (vals[0] + vals[1] + vals[2]) % (2 * math.pi)
    return d23, d35, tsum


# -----------------------------------------------------------------------------
# Backend bridge
# -----------------------------------------------------------------------------

def evaluate_abs(
    t_grid: np.ndarray,
    sectors: list[int],
    thetas: list[float],
    sector_weights: list[float] | None,
    ell_trefoil: float,
    truncation_M: int,
    completion_mode_code: int,
    alpha: float,
    beta: float,
) -> np.ndarray:
    sst = _get_kernel_module()
    return np.asarray(
        sst.MultisectorFitter.evaluate_multisector_abs(
            np.asarray(t_grid, dtype=np.float64),
            np.asarray(sectors, dtype=np.int32),
            np.asarray(thetas, dtype=np.float64),
            None if sector_weights is None else np.asarray(sector_weights, dtype=np.float64),
            ell_trefoil=float(ell_trefoil),
            truncation_M=int(truncation_M),
            completion_mode=int(completion_mode_code),
            alpha=float(alpha),
            beta=float(beta),
        )
    )


# -----------------------------------------------------------------------------
# Parameter packing
# -----------------------------------------------------------------------------

def build_fit_param_dict(x: np.ndarray, cfg: Week12Config) -> dict:
    idx = 0
    params: dict = {}

    thetas = []
    for _ in cfg.sectors:
        thetas.append(float(x[idx]))
        idx += 1
    params["thetas"] = thetas

    if cfg.fit_sector_weights:
        ws = []
        for _ in cfg.sectors:
            ws.append(float(x[idx]))
            idx += 1
        params["sector_weights"] = ws
    else:
        params["sector_weights"] = None

    if cfg.completion_mode == "exp_linear":
        params["alpha"] = float(x[idx])
        idx += 1
        params["beta"] = float(x[idx])
        idx += 1
    else:
        params["alpha"] = 0.0
        params["beta"] = 0.0

    return params


def parameter_bounds(cfg: Week12Config) -> list[tuple[float, float]]:
    bounds: list[tuple[float, float]] = []
    for _ in cfg.sectors:
        bounds.append((0.0, math.pi))

    if cfg.fit_sector_weights:
        for _ in cfg.sectors:
            bounds.append((0.25, 2.0))

    if cfg.completion_mode == "exp_linear":
        bounds.extend([(-2.0, 2.0), (-10.0, 10.0)])

    return bounds


# -----------------------------------------------------------------------------
# Week 1 + 2 objective
# -----------------------------------------------------------------------------

def objective_factory_week12(
    t_grid: np.ndarray,
    target_nodes: list[float],
    cfg: Week12Config,
    truncation_M: int,
) -> callable:
    target_set = np.array(target_nodes, dtype=float)
    neighborhoods = build_neighborhoods(target_nodes, cfg.target_neighborhood_halfwidth)

    def objective(x: np.ndarray) -> float:
        p = build_fit_param_dict(x, cfg)
        phi_abs = evaluate_abs(
            t_grid=t_grid,
            sectors=cfg.sectors,
            thetas=p["thetas"],
            sector_weights=p["sector_weights"],
            ell_trefoil=cfg.ell_trefoil,
            truncation_M=truncation_M,
            completion_mode_code=cfg.completion_mode_code,
            alpha=p["alpha"],
            beta=p["beta"],
        )

        peaks, _ = find_peaks(-phi_abs)
        if len(peaks) == 0:
            return 1e12

        minima_t = t_grid[peaks]
        minima_val = phi_abs[peaks]

        order = np.argsort(minima_val)
        minima_t = minima_t[order]
        minima_val = minima_val[order]

        if len(minima_t) < len(target_set):
            return 1e12

        # Target mismatch from the deepest minima.
        chosen_t = np.sort(minima_t[: len(target_set)])
        mismatch = float(np.sum((chosen_t - target_set) ** 2))

        # Extra-minima suppression inside the active window but outside target neighborhoods.
        extra_penalty = 0.0
        for tj, vj in zip(minima_t, minima_val):
            if not in_any_interval(float(tj), neighborhoods):
                extra_penalty += math.exp(-float(vj) / cfg.sigma_extra)

        # Sector-weight regularization.
        reg = 0.0
        if cfg.fit_sector_weights and p["sector_weights"] is not None:
            ws = np.asarray(p["sector_weights"], dtype=float)
            reg = float(np.sum((ws - 1.0) ** 2))

        return mismatch + cfg.lambda_extra * extra_penalty + cfg.lambda_reg * reg

    return objective


# -----------------------------------------------------------------------------
# Single run
# -----------------------------------------------------------------------------

def run_single_fit(
    df: pd.DataFrame,
    cfg: Week12Config,
    truncation_M: int,
    seed: int,
    t_min: float,
    t_max: float,
    target_nodes: list[float],
) -> dict:
    w = df.copy()
    w = w[(w["t"] >= t_min) & (w["t"] <= t_max)].copy()
    t_grid = w["t"].to_numpy(dtype=float)

    objective = objective_factory_week12(t_grid, target_nodes, cfg, truncation_M)
    bounds = parameter_bounds(cfg)
    rng = np.random.default_rng(seed)

    if cfg.use_global_then_local:
        de = differential_evolution(
            objective,
            bounds=bounds,
            seed=seed,
            polish=False,
            updating="deferred",
            workers=1,
            maxiter=cfg.de_maxiter,
            popsize=cfg.de_popsize,
        )
        x0 = de.x
    else:
        x0 = np.array([rng.uniform(lo, hi) for lo, hi in bounds], dtype=float)

    local = minimize(objective, x0=x0, bounds=bounds, method=cfg.local_method)
    params = build_fit_param_dict(local.x, cfg)

    phi_abs = evaluate_abs(
        t_grid=t_grid,
        sectors=cfg.sectors,
        thetas=params["thetas"],
        sector_weights=params["sector_weights"],
        ell_trefoil=cfg.ell_trefoil,
        truncation_M=truncation_M,
        completion_mode_code=cfg.completion_mode_code,
        alpha=params["alpha"],
        beta=params["beta"],
    )

    minima = predicted_near_nodes(t_grid, phi_abs, max_count=max(len(target_nodes), cfg.keep_top_minima))
    d23, d35, tsum = phase_invariants(params["thetas"])

    row = {
        "M": truncation_M,
        "seed": seed,
        "t_min": t_min,
        "t_max": t_max,
        "targets": "|".join(f"{x:.2f}" for x in target_nodes),
        "success": bool(local.success),
        "objective": float(local.fun),
        "theta2": params["thetas"][0] if len(params["thetas"]) > 0 else np.nan,
        "theta3": params["thetas"][1] if len(params["thetas"]) > 1 else np.nan,
        "theta5": params["thetas"][2] if len(params["thetas"]) > 2 else np.nan,
        "delta23": d23,
        "delta35": d35,
        "theta_sum_mod": tsum,
        "alpha": params["alpha"],
        "beta": params["beta"],
        "sector_weights": json.dumps(params["sector_weights"]) if params["sector_weights"] is not None else "",
        "predicted_minima": json.dumps(minima),
        "target_count": len(target_nodes),
    }

    # Store first few minima into scalar columns for easier grouping.
    for i in range(cfg.keep_top_minima):
        row[f"min{i+1}"] = minima[i] if i < len(minima) else np.nan

    return row


# -----------------------------------------------------------------------------
# Batch driver
# -----------------------------------------------------------------------------

def run_week12(df: pd.DataFrame, cfg: Week12Config) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    rows: list[dict] = []

    for M in cfg.M_values:
        for seed in cfg.seeds:
            for t_min, t_max in cfg.windows:
                for targets in cfg.target_sets:
                    row = run_single_fit(
                        df=df,
                        cfg=cfg,
                        truncation_M=M,
                        seed=seed,
                        t_min=t_min,
                        t_max=t_max,
                        target_nodes=targets,
                    )
                    rows.append(row)
                    print(
                        f"M={M:>4} seed={seed} window=[{t_min:.1f},{t_max:.1f}] "
                        f"targets={targets} objective={row['objective']:.6f} success={row['success']}"
                    )

    all_df = pd.DataFrame(rows)

    group_cols = ["M", "t_min", "t_max", "targets"]
    summary = (
        all_df.groupby(group_cols, dropna=False)
        .agg(
            n_runs=("objective", "size"),
            success_rate=("success", "mean"),
            objective_mean=("objective", "mean"),
            objective_std=("objective", "std"),
            theta2_mean=("theta2", "mean"),
            theta2_std=("theta2", "std"),
            theta3_mean=("theta3", "mean"),
            theta3_std=("theta3", "std"),
            theta5_mean=("theta5", "mean"),
            theta5_std=("theta5", "std"),
            delta23_mean=("delta23", "mean"),
            delta23_std=("delta23", "std"),
            delta35_mean=("delta35", "mean"),
            delta35_std=("delta35", "std"),
            theta_sum_mod_mean=("theta_sum_mod", "mean"),
            theta_sum_mod_std=("theta_sum_mod", "std"),
            min1_mean=("min1", "mean"),
            min1_std=("min1", "std"),
            min2_mean=("min2", "mean"),
            min2_std=("min2", "std"),
            min3_mean=("min3", "mean"),
            min3_std=("min3", "std"),
        )
        .reset_index()
    )

    summary_payload = {
        "config": asdict(cfg),
        "n_total_runs": int(len(all_df)),
        "best_run": all_df.loc[all_df["objective"].idxmin()].to_dict() if len(all_df) else {},
    }

    return all_df, summary, summary_payload


# -----------------------------------------------------------------------------
# Optional plots
# -----------------------------------------------------------------------------

def render_basic_plots(summary_df: pd.DataFrame, output_dir: Path) -> None:
    import matplotlib.pyplot as plt

    # Use only the full 3-target set when available for cleaner plots.
    target_mask = summary_df["targets"].str.contains("25.18\|26.75\|32.80", regex=True)
    s = summary_df[target_mask].copy()
    if s.empty:
        s = summary_df.copy()

    # Prefer the widest window when available.
    s = s.sort_values(["t_min", "t_max", "M"]).copy()

    plt.figure(figsize=(10, 6))
    for (t_min, t_max), g in s.groupby(["t_min", "t_max"]):
        g = g.sort_values("M")
        plt.plot(g["M"], g["objective_mean"], marker="o", label=f"[{t_min:.0f},{t_max:.0f}]")
    plt.title("Week 1+2 Objective Stability vs Truncation M")
    plt.xlabel("M")
    plt.ylabel("Mean Objective")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "week12_objective_stability.png", dpi=180)
    plt.close()

    plt.figure(figsize=(10, 6))
    for col, label in [("theta2_mean", "theta2"), ("theta3_mean", "theta3"), ("theta5_mean", "theta5")]:
        g = s.groupby("M", as_index=False)[col].mean()
        plt.plot(g["M"], g[col], marker="o", label=label)
    plt.title("Week 1+2 Phase Means vs Truncation M")
    plt.xlabel("M")
    plt.ylabel("theta")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "week12_phase_stability.png", dpi=180)
    plt.close()


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def parse_int_list(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def parse_seed_list(text: str) -> list[int]:
    return parse_int_list(text)


def parse_windows(text: str) -> list[tuple[float, float]]:
    # format: 20:35,23:34,24:33
    out = []
    for block in text.split(","):
        block = block.strip()
        if not block:
            continue
        a, b = block.split(":")
        out.append((float(a), float(b)))
    return out


def parse_target_sets(text: str) -> list[list[float]]:
    # format: 25.18|26.75|32.80;25.18|26.75
    out = []
    for block in text.split(";"):
        block = block.strip()
        if not block:
            continue
        out.append([float(x) for x in block.split("|") if x])
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Week 1 + 2 combined trefoil multisector runner.")
    parser.add_argument("input_csv", help="CSV with t and Phi_3_1 transform columns")
    parser.add_argument("--output-dir", default="week12_outputs")
    parser.add_argument("--sectors", default="2,3,5")
    parser.add_argument("--a-nc-over-rc", type=float, default=1.00039865)
    parser.add_argument("--completion", choices=["none", "exp_linear"], default="none")
    parser.add_argument("--fit-sector-weights", action="store_true")
    parser.add_argument("--M-values", default="100,150,200,250,300,400")
    parser.add_argument("--seeds", default="1001,1002,1003,1004,1005")
    parser.add_argument("--windows", default="20:35,23:34,24:33")
    parser.add_argument("--target-sets", default="25.18|26.75|32.80;25.18|26.75")
    parser.add_argument("--lambda-extra", type=float, default=0.5)
    parser.add_argument("--sigma-extra", type=float, default=0.05)
    parser.add_argument("--lambda-reg", type=float, default=0.01)
    parser.add_argument("--target-halfwidth", type=float, default=0.35)
    parser.add_argument("--de-maxiter", type=int, default=50)
    parser.add_argument("--de-popsize", type=int, default=10)
    parser.add_argument("--no-global", action="store_true")
    parser.add_argument("--plots", action="store_true")

    args = parser.parse_args()

    df = load_phi_csv(args.input_csv)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    cfg = Week12Config(
        sectors=parse_int_list(args.sectors),
        a_nc_over_rc=args.a_nc_over_rc,
        completion_mode=args.completion,
        fit_sector_weights=args.fit_sector_weights,
        M_values=parse_int_list(args.M_values),
        seeds=parse_seed_list(args.seeds),
        windows=parse_windows(args.windows),
        target_sets=parse_target_sets(args.target_sets),
        lambda_extra=args.lambda_extra,
        sigma_extra=args.sigma_extra,
        lambda_reg=args.lambda_reg,
        target_neighborhood_halfwidth=args.target_halfwidth,
        use_global_then_local=not args.no_global,
        de_maxiter=args.de_maxiter,
        de_popsize=args.de_popsize,
    )

    all_df, summary_df, summary_payload = run_week12(df, cfg)

    all_csv = outdir / "week12_all_runs.csv"
    summary_csv = outdir / "week12_summary.csv"
    summary_json = outdir / "week12_summary.json"

    all_df.to_csv(all_csv, index=False)
    summary_df.to_csv(summary_csv, index=False)
    summary_json.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    if args.plots:
        render_basic_plots(summary_df, outdir)

    print(f"Saved all runs: {all_csv}")
    print(f"Saved summary:  {summary_csv}")
    print(f"Saved json:     {summary_json}")
    print(json.dumps(summary_payload, indent=2))


if __name__ == "__main__":
    main()
