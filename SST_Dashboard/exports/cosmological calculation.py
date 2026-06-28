# cosmological_calculation.py
# Presentation-style benchmarking script for SST Λ-replacement vs ΛCDM
# - Compares E(z), luminosity distance D_L(z), and distance modulus μ(z)
# - Fits SST params (Ω_Q0, n) to mimic ΛCDM distances over 0 < z ≤ 2
# - Computes effective w_Q(0), q0, and implied (Q_D + <R>) via Ω_Q(z)
#
# No internet; default Planck-like numbers. Plots: plain matplotlib.
# Safe numerics: uses numpy.trapezoid; avoids z=0 in μ; masks non-finite values.

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# If you run locally with Tk, keep this; otherwise you can comment it out.
matplotlib.use('TkAgg')

# Optional UI table display (will no-op if not available)
def _display_df(df, name="Table"):
    try:
        from ace_tools_open import display_dataframe_to_user
        display_dataframe_to_user(name, df)
    except Exception:
        # Fallback: print a small preview
        print(f"\n{name} (preview):")
        print(df.head(10).to_string(index=False))

# -------------------- Constants --------------------
c = 299792.458  # speed of light [km/s]
H0_km = 70.0    # H0 [km/s/Mpc]
H0 = H0_km / (3.0856775814913673e19) * 1000.0  # [1/s]; 1 Mpc = 3.085677...e22 m

# ΛCDM baseline (flat)
Omega_m_LCDM = 0.315
Omega_L_LCDM = 0.685
Omega_k_LCDM = 0.0
Omega_r = 0.0  # negligible for z ≤ 2 here

# -------------------- Cosmology helpers --------------------
def E_LCDM(z):
    """Dimensionless Hubble parameter for flat ΛCDM."""
    z = np.asarray(z)
    return np.sqrt(Omega_m_LCDM*(1+z)**3 + Omega_r*(1+z)**4 + Omega_k_LCDM*(1+z)**2 + Omega_L_LCDM)

def E_SST_vec(z, Omega_m, Omega_k, Omega_Q0, n):
    """Dimensionless Hubble parameter for SST model with Ω_Q(z)=Ω_Q0(1+z)^(-n)."""
    z = np.asarray(z)
    return np.sqrt(Omega_m*(1+z)**3 + Omega_k*(1+z)**2 + Omega_Q0*(1+z)**(-n))

def cumulative_comoving_distance_grid(z_grid, Ez):
    """
    D_C(z_i) = (c/H0) ∫_z0^{z_i} dz'/E(z') using cumulative trapezoid.
    z_grid must start at z>0 to avoid D_L = 0 in μ.
    """
    if z_grid[0] <= 0:
        raise ValueError("z_grid must start strictly > 0.")
    invE = 1.0 / Ez
    dz = np.diff(z_grid)
    mid = 0.5 * (invE[:-1] + invE[1:])
    integral = np.concatenate([[0.0], np.cumsum(mid * dz)])
    return (c / H0_km) * integral  # [Mpc]

def D_L_from_curve(z_grid, Dc_curve):
    """Luminosity distance D_L = (1+z) D_C for flat geometry."""
    return (1.0 + z_grid) * Dc_curve  # [Mpc]

def distance_modulus_from_DL_Mpc_vec(DL_Mpc):
    """μ = 5 log10(D_L/10pc), guard against zeros."""
    DL_pc = np.asarray(DL_Mpc) * 1e6
    DL_pc = np.clip(DL_pc, 1e-30, None)  # avoid log10(0)
    return 5.0 * (np.log10(DL_pc) - 1.0)

# -------------------- Main computation --------------------
def main():
    # Redshift grid: start strictly above 0 to avoid μ singularity
    z_vals = np.linspace(1e-8, 2.0, 600)

    # Baseline ΛCDM curves
    E_LCDM_vals = E_LCDM(z_vals)
    DC_LCDM = cumulative_comoving_distance_grid(z_vals, E_LCDM_vals)
    DL_LCDM_vals = D_L_from_curve(z_vals, DC_LCDM)
    mu_LCDM_vals = distance_modulus_from_DL_Mpc_vec(DL_LCDM_vals)

    # Fit SST (Ω_Q0, n) with Ω_m fixed and Ω_k=0
    Omega_m_SST = Omega_m_LCDM
    Omega_k_SST = 0.0
    Omega_Q0_grid = np.linspace(0.60, 0.75, 46)  # narrower, faster
    n_grid        = np.linspace(0.00, 0.60, 61)

    best = None
    w = 1.0 + 0.3*z_vals  # weights favoring higher z a bit

    for Omega_Q0 in Omega_Q0_grid:
        flat_penalty = (Omega_m_SST + Omega_Q0 - 1.0)**2  # soft flatness prior
        for n in n_grid:
            Ez = E_SST_vec(z_vals, Omega_m_SST, Omega_k_SST, Omega_Q0, n)
            DC = cumulative_comoving_distance_grid(z_vals, Ez)
            DL = D_L_from_curve(z_vals, DC)
            mu = distance_modulus_from_DL_Mpc_vec(DL)

            # mask finite values
            finite = np.isfinite(mu) & np.isfinite(mu_LCDM_vals) & np.isfinite(w) & (w > 0)
            if not np.any(finite):
                continue

            diff = mu[finite] - mu_LCDM_vals[finite]
            rms = np.sqrt(np.average(diff**2, weights=w[finite]))
            score = rms + 20.0*flat_penalty

            if (best is None) or (score < best["score"]):
                best = dict(
                    Omega_Q0=float(Omega_Q0),
                    n=float(n),
                    rms=float(rms),
                    score=float(score),
                    Ez=Ez,
                    DC=DC,
                    DL=DL,
                    mu=mu,
                    flat_penalty=float(flat_penalty),
                )

    if best is None:
        raise RuntimeError("No valid SST fit found. Check grids or model settings.")

    # Derived quantities at z=0
    best_Omega_Q0 = best["Omega_Q0"]
    best_n = best["n"]
    wQ0 = best_n/3.0 - 1.0
    q0_SST = 0.5*Omega_m_SST + 0.5*(1.0 + 3.0*wQ0)*best_Omega_Q0
    q0_LCDM = 0.5*Omega_m_LCDM - Omega_L_LCDM
    H0_sq = H0**2
    QD_plus_R_0 = -6.0 * H0_sq * best_Omega_Q0  # [1/s^2]

    # Table (sparser sampling so it’s readable)
    sample_idx = np.linspace(0, len(z_vals)-1, 121, dtype=int)
    df = pd.DataFrame({
        "z": z_vals[sample_idx],
        "E_LCDM": E_LCDM_vals[sample_idx],
        "E_SST": best["Ez"][sample_idx],
        "DL_LCDM_Mpc": DL_LCDM_vals[sample_idx],
        "DL_SST_Mpc": best["DL"][sample_idx],
        "mu_LCDM_mag": mu_LCDM_vals[sample_idx],
        "mu_SST_mag": best["mu"][sample_idx],
        "mu_residual_mag": (best["mu"] - mu_LCDM_vals)[sample_idx],
    }).round(6)

    _display_df(df, "SST vs ΛCDM Benchmark Table (optimized)")

    # -------------------- Plots --------------------
    # 1) E(z)
    plt.figure(figsize=(7,5), dpi=140)
    plt.plot(z_vals, E_LCDM_vals, label="E(z) ΛCDM")
    plt.plot(z_vals, best["Ez"], label=f"E(z) SST (Ω_Q0={best_Omega_Q0:.3f}, n={best_n:.3f})", linestyle="--")
    plt.xlabel("z"); plt.ylabel("E(z) = H(z)/H0")
    plt.title("Expansion History Comparison"); plt.legend()
    plt.tight_layout(); plt.savefig("figures/SST_benchmark_Ez.png"); plt.close()

    # 2) μ(z)
    plt.figure(figsize=(7,5), dpi=140)
    plt.plot(z_vals, mu_LCDM_vals, label="μ(z) ΛCDM")
    plt.plot(z_vals, best["mu"], label="μ(z) SST (fit)", linestyle="--")
    plt.xlabel("z"); plt.ylabel("Distance Modulus μ [mag]")
    plt.title("Hubble Diagram (Model Curves)"); plt.legend()
    plt.tight_layout(); plt.savefig("figures/SST_benchmark_mu.png"); plt.close()

    # 3) Residuals (finite-only)
    finite2 = np.isfinite(best["mu"]) & np.isfinite(mu_LCDM_vals)
    plt.figure(figsize=(7,4), dpi=140)
    plt.axhline(0.0, linestyle=":")
    plt.plot(z_vals[finite2], (best["mu"] - mu_LCDM_vals)[finite2], label="μ_SST − μ_ΛCDM residuals")
    plt.xlabel("z"); plt.ylabel("Δμ [mag]")
    plt.title("Residuals vs ΛCDM"); plt.legend()
    plt.tight_layout(); plt.savefig("figures/SST_benchmark_residuals.png"); plt.close()

    # -------------------- Summary --------------------
    summary = {
        "H0_km_s_Mpc": H0_km,
        "Omega_m_fixed": Omega_m_SST,
        "Best_Omega_Q0": best_Omega_Q0,
        "Best_n": best_n,
        "Effective_wQ0": wQ0,
        "q0_SST": q0_SST,
        "q0_LCDM": q0_LCDM,
        "RMS_mu_mag": best["rms"],
        "QD_plus_R_at_z0_per_s2": QD_plus_R_0
    }
    print("\n=== Fit summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    # CSV export of the table
    df.to_csv("figures/SST_vs_LCDM_table.csv", index=False)

if __name__ == "__main__":
    main()