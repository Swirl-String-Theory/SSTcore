#!/usr/bin/env python3
# SST invariant-kernel mass benchmarks (exact_closure)
# Derives from the canonical Lagrangian mass sector:
#   M = (4/alpha_fs) * b^{-3/2} * phi^{-g} * n^{-1/phi} * [ u * (pi r_c^3 L_tot) / c^2 ],
#   u = 1/2 * rho_core * v_swirl^2.
# Calibration mode: exact_closure — solves (s_u, s_d) so that p and n are exact;
# leptons exact by solving L_tot; composites as constituent sums (no binding).
#
# Output:
#   - CSV/Excel with species, known mass, predicted mass, error %
#   - Prints a LaTeX table
#
# Caption suggestion:
#   (Errors in atoms/molecules = missing binding energy contribution, not model failure.)

import math
import pandas as pd

# ---- Canon constants ----
phi = (1 + 5**0.5)/2
alpha_fs = 7.2973525643e-3
c = 299_792_458.0
v_swirl = 1.09384563e6
r_c = 1.40897017e-15
rho_core = 3.8934358266918687e18
pi = math.pi

# ---- Known masses (kg) ----
M_e_actual = 9.1093837015e-31
M_mu_actual = 1.883531627e-28
M_tau_actual = 3.16754e-27
M_p_actual = 1.67262192369e-27
M_n_actual = 1.67492749804e-27

u = 1.66053906660e-27  # atomic mass unit

# Atoms (atomic masses include electrons)
M_H1_atom = 1.00782503223*u
M_He4_atom = 4.00260325413*u
M_C12_atom = 12.0*u
M_O16_atom = 15.99491461957*u

# Molecules
M_H2 = 2.01588*u
M_H2O = 18.01056*u
M_CO2 = 44.0095*u

def u_energy():
    return 0.5 * rho_core * v_swirl**2  # J/m^3

def master_mass_invariant(b,g,n,L_tot):
    pref = (4.0/alpha_fs) * (b**-1.5) * (phi**(-g)) * (n ** (-1.0/phi))
    V = pi * r_c**3 * L_tot
    return pref * (u_energy() * V) / (c**2)

def solve_L_tot_from_mass(M_target, b,g,n):
    pref = (4.0/alpha_fs) * (b**-1.5) * (phi**(-g)) * (n ** (-1.0/phi))
    denom = pref * u_energy() * pi * r_c**3 / (c**2)
    return M_target / denom

def baryon_prefactor(b,g,n):
    return (4.0/alpha_fs) * (b**-1.5) * (phi**(-g)) * (n ** (-1.0/phi)) * (u_energy() * pi * r_c**3) / (c**2)

def fit_su_sd_exact_closure():
    b_b, g_b, n_b = 3, 2, 3
    kappa_R = 2.0
    scaling = 2.0 * (pi**2) * kappa_R
    A = baryon_prefactor(b_b, g_b, n_b)
    K = A * scaling
    s_u = (2.0*M_p_actual - M_n_actual) / (3.0*K)
    s_d = (M_p_actual / K) - 2.0*s_u
    lam_b = 1.0
    return s_u, s_d, lam_b, scaling, A, K

def constituent_sum(M_p, M_n, M_e, Z, N, include_electrons=True):
    mass = Z*M_p + N*M_n
    if include_electrons:
        mass += Z*M_e
    return mass

def run():
    # Solve leptons
    L_e = solve_L_tot_from_mass(M_e_actual, b=2, g=1, n=1)
    L_mu = solve_L_tot_from_mass(M_mu_actual, b=5, g=2, n=1)
    L_tau = solve_L_tot_from_mass(M_tau_actual, b=7, g=3, n=1)
    M_e_pred  = master_mass_invariant(2,1,1,L_e)
    M_mu_pred = master_mass_invariant(5,2,1,L_mu)
    M_tau_pred= master_mass_invariant(7,3,1,L_tau)

    # Fit baryons
    s_u, s_d, lam_b, scaling, A_bary, K = fit_su_sd_exact_closure()
    L_p = lam_b * (2.0*s_u + 1.0*s_d) * scaling
    L_n = lam_b * (1.0*s_u + 2.0*s_d) * scaling
    M_p_pred = master_mass_invariant(3,2,3,L_p)
    M_n_pred = master_mass_invariant(3,2,3,L_n)

    # Table rows
    rows = []
    def add_row(name, M_act, M_pred):
        err = 100.0*(M_pred - M_act)/M_act if M_act>0 else None
        rows.append({"species": name, "known_mass_kg": M_act, "pred_mass_kg": M_pred, "error_percent": err})

    add_row("electron e-", M_e_actual, M_e_pred)
    add_row("muon μ-", M_mu_actual, M_mu_pred)
    add_row("tau τ-", M_tau_actual, M_tau_pred)
    add_row("proton p", M_p_actual, M_p_pred)
    add_row("neutron n", M_n_actual, M_n_pred)

    # Composites (no binding)
    add_row("Hydrogen-1 atom", M_H1_atom, constituent_sum(M_p_pred, M_n_pred, M_e_pred, Z=1, N=0, include_electrons=True))
    add_row("Helium-4 atom",   M_He4_atom, constituent_sum(M_p_pred, M_n_pred, M_e_pred, Z=2, N=2, include_electrons=True))
    add_row("Carbon-12 atom",  M_C12_atom, constituent_sum(M_p_pred, M_n_pred, M_e_pred, Z=6, N=6, include_electrons=True))
    add_row("Oxygen-16 atom",  M_O16_atom, constituent_sum(M_p_pred, M_n_pred, M_e_pred, Z=8, N=8, include_electrons=True))

    add_row("H2 molecule",     M_H2, 2*constituent_sum(M_p_pred, M_n_pred, M_e_pred, Z=1, N=0, include_electrons=True))
    add_row("H2O molecule",    M_H2O, constituent_sum(M_p_pred, M_n_pred, M_e_pred, 1,0,True)*2 + constituent_sum(M_p_pred, M_n_pred, M_e_pred, 8,8,True))
    add_row("CO2 molecule",    M_CO2, constituent_sum(M_p_pred, M_n_pred, M_e_pred, 6,6,True) + 2*constituent_sum(M_p_pred, M_n_pred, M_e_pred, 8,8,True))

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = run()
    xlsx = "figures/SST_invariant_kernel_benchmarks_exact_closure.xlsx"
    csv  = "figures/SST_invariant_kernel_benchmarks_exact_closure.csv"
    df.to_excel(xlsx, index=False)
    df.to_csv(csv, index=False)
    # Print LaTeX table
    cols = ["species","known_mass_kg","pred_mass_kg","error_percent"]
    fmt = df[cols].copy()
    # Compact scientific notation
    def sci(x):
        if pd.isna(x): return ""
        return "{:.6e}".format(x)
    fmt["known_mass_kg"] = fmt["known_mass_kg"].apply(sci)
    fmt["pred_mass_kg"]  = fmt["pred_mass_kg"].apply(sci)
    fmt["error_percent"] = fmt["error_percent"].apply(lambda x: "" if pd.isna(x) else "{:.4f}".format(x))
    print("\\begin{table}[H]")
    print("\\centering")
    print("\\caption{Invariant-kernel mass benchmarks (exact\\_closure). \\emph{Errors in atoms/molecules = missing binding energy contribution, not model failure.}}")
    print("\\begin{tabular}{lccc}")
    print("\\toprule")
    print("Species & Known mass (kg) & Predicted mass (kg) & Error (\\%)\\\\")
    print("\\midrule")
    for _, r in fmt.iterrows():
        print(f"{r['species']} & {r['known_mass_kg']} & {r['pred_mass_kg']} & {r['error_percent']}\\\\")
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{table}")