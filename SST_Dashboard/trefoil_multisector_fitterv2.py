from __future__ import annotations

"""
Fast Python replacement for the original multisector fitter.

This version keeps the high-level fitting / CSV / reporting logic in Python,
but offloads the heavy multisector product evaluation to the compiled pybind11
kernel:

    sst.MultisectorFitter

Expected compiled API
---------------------
The extension module must expose:

    sst.MultisectorFitter.evaluate_multisector(...)
    sst.MultisectorFitter.evaluate_multisector_abs(...)
    sst.MultisectorFitter.objective_near_nodes(...)

as defined in the C++ bundle.
"""

from dataclasses import dataclass, field
from pathlib import Path
import json
import math
from typing import Callable

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution, minimize
from scipy.signal import find_peaks


# -----------------------------------------------------------------------------
# Data classes
# -----------------------------------------------------------------------------

@dataclass
class MultisectorConfig:
    sectors: list[int] = field(default_factory=lambda: [2, 3, 5])
    a_nc_over_rc: float = 1.00039865
    truncation_M: int = 120
    completion_mode: str = "none"  # none | exp_linear
    t_min: float | None = None
    t_max: float | None = None
    target_near_nodes: list[float] = field(default_factory=list)
    node_weights: list[float] | None = None
    use_global_then_local: bool = True
    random_seed: int = 1234
    match_count: int = 6
    fit_sector_weights: bool = False

    @property
    def ell_trefoil(self) -> float:
        return math.log(self.a_nc_over_rc)

    @property
    def completion_mode_code(self) -> int:
        mapping = {"none": 0, "exp_linear": 1}
        if self.completion_mode not in mapping:
            raise ValueError(f"Unsupported completion_mode for fast fitter: {self.completion_mode}")
        return mapping[self.completion_mode]


@dataclass
class FitResult:
    success: bool
    objective_value: float
    fitted_params: dict
    predicted_minima: list[float]
    target_near_nodes: list[float]
    config: dict


# -----------------------------------------------------------------------------
# Loader
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
# Near-node extraction
# -----------------------------------------------------------------------------

def infer_near_nodes(df: pd.DataFrame, t_min: float | None, t_max: float | None, max_count: int) -> list[float]:
    w = df.copy()
    if t_min is not None:
        w = w[w["t"] >= t_min]
    if t_max is not None:
        w = w[w["t"] <= t_max]

    y = w["phi_abs"].to_numpy(dtype=float)
    t = w["t"].to_numpy(dtype=float)
    if len(y) < 5:
        return []

    peaks, _ = find_peaks(-y)
    if len(peaks) == 0:
        return []

    candidates = [(t[p], y[p]) for p in peaks]
    candidates.sort(key=lambda z: z[1])
    nodes = [x for x, _ in candidates[:max_count]]
    return sorted(nodes)


def predicted_near_nodes(t: np.ndarray, phi_abs: np.ndarray, max_count: int) -> list[float]:
    peaks, _ = find_peaks(-phi_abs)
    if len(peaks) == 0:
        return []
    candidates = [(t[p], phi_abs[p]) for p in peaks]
    candidates.sort(key=lambda z: z[1])
    nodes = [x for x, _ in candidates[:max_count]]
    return sorted(nodes)


# -----------------------------------------------------------------------------
# Parameter packing
# -----------------------------------------------------------------------------

def build_fit_param_dict(x: np.ndarray, config: MultisectorConfig) -> dict:
    idx = 0
    params: dict = {}

    thetas = []
    for _ in config.sectors:
        thetas.append(float(x[idx]))
        idx += 1
    params["thetas"] = thetas

    if config.fit_sector_weights:
        ws = []
        for _ in config.sectors:
            ws.append(float(x[idx]))
            idx += 1
        params["sector_weights"] = ws

    if config.completion_mode == "exp_linear":
        params["alpha"] = float(x[idx])
        idx += 1
        params["beta"] = float(x[idx])
        idx += 1
    else:
        params["alpha"] = 0.0
        params["beta"] = 0.0

    return params


def parameter_bounds(config: MultisectorConfig) -> list[tuple[float, float]]:
    bounds: list[tuple[float, float]] = []
    for _ in config.sectors:
        bounds.append((0.0, math.pi))

    if config.fit_sector_weights:
        for _ in config.sectors:
            bounds.append((0.25, 2.0))

    if config.completion_mode == "exp_linear":
        bounds.extend([(-2.0, 2.0), (-10.0, 10.0)])

    return bounds


# -----------------------------------------------------------------------------
# Fast kernel bridge
# -----------------------------------------------------------------------------

def _get_kernel_module():
    try:
        import sstcore as sst # type: ignore
        return sst
    except ImportError:
        try:
            import swirl_string_core as sst  # type: ignore
            return sst
        except ImportError as exc:
            raise ImportError(
                "Could not import compiled SST pybind11 module. Tried 'sst' and 'swirl_string_core'."
            ) from exc


def phi_pc_at_t_fast(t: np.ndarray, config: MultisectorConfig, fit_params: dict) -> np.ndarray:
    sst = _get_kernel_module()

    sectors = np.asarray(config.sectors, dtype=np.int32)
    thetas = np.asarray(fit_params["thetas"], dtype=np.float64)
    weights = None
    if config.fit_sector_weights:
        weights = np.asarray(fit_params["sector_weights"], dtype=np.float64)

    alpha = float(fit_params.get("alpha", 0.0))
    beta = float(fit_params.get("beta", 0.0))

    return np.asarray(
        sst.MultisectorFitter.evaluate_multisector(
            np.asarray(t, dtype=np.float64),
            sectors,
            thetas,
            weights,
            ell_trefoil=float(config.ell_trefoil),
            truncation_M=int(config.truncation_M),
            completion_mode=int(config.completion_mode_code),
            alpha=alpha,
            beta=beta,
        )
    )


def phi_pc_abs_at_t_fast(t: np.ndarray, config: MultisectorConfig, fit_params: dict) -> np.ndarray:
    sst = _get_kernel_module()

    sectors = np.asarray(config.sectors, dtype=np.int32)
    thetas = np.asarray(fit_params["thetas"], dtype=np.float64)
    weights = None
    if config.fit_sector_weights:
        weights = np.asarray(fit_params["sector_weights"], dtype=np.float64)

    alpha = float(fit_params.get("alpha", 0.0))
    beta = float(fit_params.get("beta", 0.0))

    return np.asarray(
        sst.MultisectorFitter.evaluate_multisector_abs(
            np.asarray(t, dtype=np.float64),
            sectors,
            thetas,
            weights,
            ell_trefoil=float(config.ell_trefoil),
            truncation_M=int(config.truncation_M),
            completion_mode=int(config.completion_mode_code),
            alpha=alpha,
            beta=beta,
        )
    )


# -----------------------------------------------------------------------------
# Objective
# -----------------------------------------------------------------------------

def objective_factory(df: pd.DataFrame, config: MultisectorConfig):
    if config.target_near_nodes:
        targets = list(config.target_near_nodes)
    else:
        targets = infer_near_nodes(
            df, config.t_min, config.t_max, config.match_count
        )

    if not targets:
        raise ValueError("No target near-nodes available.")

    target_set = np.array(targets, dtype=float)
    node_weights = np.array(
        config.node_weights or [1.0] * len(targets), dtype=float
    )

    # Hyperparameters
    lambda_extra = 0.5
    lambda_reg = 0.01
    sigma = 0.05

    w = df.copy()
    if config.t_min is not None:
        w = w[w["t"] >= config.t_min]
    if config.t_max is not None:
        w = w[w["t"] <= config.t_max]

    t_grid = w["t"].to_numpy(dtype=float)

    def objective(x: np.ndarray) -> float:
        p = build_fit_param_dict(x, config)

        # Gebruik de snelle C++ kernel
        phi_abs = phi_pc_abs_at_t_fast(t_grid, config, p)

        # Vind alle minima
        peaks, _ = find_peaks(-phi_abs)
        if len(peaks) == 0:
            return 1e9

        minima_t = t_grid[peaks]
        minima_val = phi_abs[peaks]

        # Sorteer op diepte van minima
        order = np.argsort(minima_val)
        minima_t = minima_t[order]
        minima_val = minima_val[order]

        if len(minima_t) < len(target_set):
            return 1e9

        # Doelminima
        chosen_t = np.sort(minima_t[: len(target_set)])
        mismatch = np.sum(
            node_weights * (chosen_t - target_set) ** 2
        )

        # Straf extra minima
        extra_penalty = 0.0
        if len(minima_val) > len(target_set):
            extras = minima_val[len(target_set):]
            extra_penalty = np.sum(np.exp(-extras / sigma))

        # Regularisatie van sectorgewichten
        reg = 0.0
        if config.fit_sector_weights:
            ws = np.array(p["sector_weights"], dtype=float)
            reg = np.sum((ws - 1.0) ** 2)

        return float(
            mismatch
            + lambda_extra * extra_penalty
            + lambda_reg * reg
        )

    objective.targets = targets  # type: ignore[attr-defined]
    return objective


# -----------------------------------------------------------------------------
# Fitter
# -----------------------------------------------------------------------------

def fit_multisector(df: pd.DataFrame, config: MultisectorConfig) -> FitResult:
    objective = objective_factory(df, config)
    bounds = parameter_bounds(config)
    rng = np.random.default_rng(config.random_seed)

    if config.use_global_then_local:
        de = differential_evolution(
            objective,
            bounds=bounds,
            seed=config.random_seed,
            polish=False,
            updating="deferred",
            workers=1,
            maxiter=80,
            popsize=12,
        )
        x0 = de.x
    else:
        x0 = np.array([rng.uniform(lo, hi) for lo, hi in bounds], dtype=float)

    local = minimize(objective, x0=x0, bounds=bounds, method="L-BFGS-B")
    x_best = local.x
    params = build_fit_param_dict(x_best, config)

    w = df.copy()
    if config.t_min is not None:
        w = w[w["t"] >= config.t_min]
    if config.t_max is not None:
        w = w[w["t"] <= config.t_max]
    t_grid = w["t"].to_numpy(dtype=float)
    phi_abs = phi_pc_abs_at_t_fast(t_grid, config, params)
    mins = predicted_near_nodes(t_grid, phi_abs, max_count=max(config.match_count, 8))

    return FitResult(
        success=bool(local.success),
        objective_value=float(local.fun),
        fitted_params=params,
        predicted_minima=mins,
        target_near_nodes=list(objective.targets),  # type: ignore[attr-defined]
        config={
            "sectors": config.sectors,
            "a_nc_over_rc": config.a_nc_over_rc,
            "ell_trefoil": config.ell_trefoil,
            "truncation_M": config.truncation_M,
            "completion_mode": config.completion_mode,
            "t_min": config.t_min,
            "t_max": config.t_max,
            "match_count": config.match_count,
            "fit_sector_weights": config.fit_sector_weights,
        },
    )


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def output_path_for_truncation_m(base: str | Path, m: int, multi_m: bool) -> Path:
    """Single path, or per-M path when running a multi-M batch."""
    p = Path(base)
    if not multi_m:
        return p
    if "{M}" in p.name:
        return p.parent / p.name.replace("{M}", str(m))
    return p.parent / f"{p.stem}_M{m}{p.suffix}"


def save_result(result: FitResult, output_path: str | Path) -> None:
    output_path = Path(output_path)
    payload = {
        "success": result.success,
        "objective_value": result.objective_value,
        "fitted_params": result.fitted_params,
        "predicted_minima": result.predicted_minima,
        "target_near_nodes": result.target_near_nodes,
        "config": result.config,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def evaluate_model_grid(df: pd.DataFrame, config: MultisectorConfig, fit_params: dict) -> pd.DataFrame:
    w = df.copy()
    if config.t_min is not None:
        w = w[w["t"] >= config.t_min]
    if config.t_max is not None:
        w = w[w["t"] <= config.t_max]
    t_grid = w["t"].to_numpy(dtype=float)
    phi_model = phi_pc_at_t_fast(t_grid, config, fit_params)
    return pd.DataFrame(
        {
            "t": t_grid,
            "phi_model_real": np.real(phi_model),
            "phi_model_imag": np.imag(phi_model),
            "phi_model_abs": np.abs(phi_model),
        }
    )


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Fast multisector trefoil fitter using compiled pybind11 kernel."
    )
    parser.add_argument("input_csv", help="CSV with t and Phi_3_1 transform columns")
    parser.add_argument("--output-json", default="multisector_fit_result.json")
    parser.add_argument("--output-model-csv", default="multisector_fit_model.csv")
    parser.add_argument("--sectors", nargs="*", type=int, default=[2, 3, 5])
    parser.add_argument("--a-nc-over-rc", type=float, default=1.00039865)
    parser.add_argument(
        "--M",
        type=int,
        nargs="+",
        default=[120],
        metavar="M",
        help="Truncation M (one value, or several for batch: e.g. --M 150 200 300 400). "
        "With multiple M, outputs get _M<value> before the extension unless the path contains {M}.",
    )
    parser.add_argument("--t-min", type=float, default=None)
    parser.add_argument("--t-max", type=float, default=None)
    parser.add_argument("--match-count", type=int, default=6)
    parser.add_argument("--targets", nargs="*", type=float, default=[])
    parser.add_argument("--completion", choices=["none", "exp_linear"], default="none")
    parser.add_argument("--fit-sector-weights", action="store_true")
    parser.add_argument("--no-global", action="store_true")

    args = parser.parse_args()

    df = load_phi_csv(args.input_csv)
    M_list = list(args.M)
    multi_m = len(M_list) > 1
    batch_summary: list[dict] = []

    for m in M_list:
        cfg = MultisectorConfig(
            sectors=list(args.sectors),
            a_nc_over_rc=args.a_nc_over_rc,
            truncation_M=int(m),
            completion_mode=args.completion,
            t_min=args.t_min,
            t_max=args.t_max,
            target_near_nodes=list(args.targets),
            use_global_then_local=not args.no_global,
            match_count=args.match_count,
            fit_sector_weights=args.fit_sector_weights,
        )

        result = fit_multisector(df, cfg)
        out_json = output_path_for_truncation_m(args.output_json, m, multi_m)
        out_csv = output_path_for_truncation_m(args.output_model_csv, m, multi_m)
        save_result(result, out_json)

        model_df = evaluate_model_grid(df, cfg, result.fitted_params)
        model_df.to_csv(out_csv, index=False)

        one = {
            "truncation_M": m,
            "success": result.success,
            "objective_value": result.objective_value,
            "fitted_params": result.fitted_params,
            "target_near_nodes": result.target_near_nodes,
            "predicted_minima": result.predicted_minima,
            "ell_trefoil": cfg.ell_trefoil,
            "output_json": str(out_json),
            "output_model_csv": str(out_csv),
        }
        batch_summary.append(one)

        print(f"Fit complete (M={m}) -> {out_json}, {out_csv}")
        print(json.dumps({k: v for k, v in one.items() if k not in ("output_json", "output_model_csv")}, indent=2))

    if multi_m:
        print("\nBatch summary (M values):")
        for row in batch_summary:
            print(f"  M={row['truncation_M']}: objective={row['objective_value']:.6g} success={row['success']}")


if __name__ == "__main__":
    main()