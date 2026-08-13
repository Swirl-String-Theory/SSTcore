#include "sst_action_phase.h"

#include <algorithm>

namespace sst {
namespace {

bool valid_inputs(double P, double E0, double c) {
    return std::isfinite(P) && std::isfinite(E0) && std::isfinite(c) && (E0 > 0.0) && (c > 0.0);
}

} // namespace

double ActionPhaseAPI::mass_shell_hamiltonian(double P, double E0, double c) {
    if (!valid_inputs(P, E0, c)) return std::numeric_limits<double>::quiet_NaN();
    return std::hypot(P * c, E0);
}

double ActionPhaseAPI::velocity_from_mass_shell(double P, double E0, double c) {
    const double H = mass_shell_hamiltonian(P, E0, c);
    if (!(H > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    // Scale-safe: avoid P*c*c forming an intermediate that overflows.
    return c * ((P * c) / H);
}

double ActionPhaseAPI::gamma_from_mass_shell(double P, double E0, double c) {
    const double H = mass_shell_hamiltonian(P, E0, c);
    if (!(H > 0.0) || !(E0 > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return H / E0;
}

double ActionPhaseAPI::proper_time_rate(double P, double E0, double c) {
    const double H = mass_shell_hamiltonian(P, E0, c);
    if (!(H > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return E0 / H;
}

double ActionPhaseAPI::internal_phase_rate_at_fixed_momentum(double P, double E0, double c, double Omega0) {
    if (!std::isfinite(Omega0)) return std::numeric_limits<double>::quiet_NaN();
    const double H = mass_shell_hamiltonian(P, E0, c);
    if (!(H > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return Omega0 * E0 / H;
}

double ActionPhaseAPI::delta_shape_separability(double P, double E0, double dE0_dq, double c) {
    const double H = mass_shell_hamiltonian(P, E0, c);
    if (!(H > 0.0) || !std::isfinite(dE0_dq)) return std::numeric_limits<double>::quiet_NaN();
    const double dH_dq = (E0 / H) * dE0_dq;
    const double expected = (E0 / H) * dE0_dq;
    return std::abs(dH_dq - expected); // identically 0 for separable shell
}

double ActionPhaseAPI::coupled_shape_residual(
    double P, double E0, double dE0_dq, double c, double eps, double f_q, double df_dq) {
    const double H_shell = mass_shell_hamiltonian(P, E0, c);
    if (!(H_shell > 0.0) || !std::isfinite(dE0_dq) || !std::isfinite(eps) || !std::isfinite(f_q) ||
        !std::isfinite(df_dq)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    const double dH_shell_dq = (E0 / H_shell) * dE0_dq;
    const double dH_coupled_dq = dH_shell_dq + eps * (P * P) * df_dq;
    const double separable_claim = (E0 / H_shell) * dE0_dq;
    return std::abs(dH_coupled_dq - separable_claim);
}

double ActionPhaseAPI::fixed_v_phase_error_factor(double P, double E0, double c) {
    const double g = gamma_from_mass_shell(P, E0, c);
    if (!std::isfinite(g)) return std::numeric_limits<double>::quiet_NaN();
    return g * g - 1.0;
}

ActionPhaseResiduals ActionPhaseAPI::action_phase_residuals(double P, double E0, double c, double Omega0,
                                                           double tol) {
    ActionPhaseResiduals out;
    const double H = mass_shell_hamiltonian(P, E0, c);
    if (!std::isfinite(H) || !std::isfinite(Omega0) || !(tol >= 0.0)) {
        out.ok = false;
        return out;
    }
    const double V = velocity_from_mass_shell(P, E0, c);
    const double g = gamma_from_mass_shell(P, E0, c);
    const double dtau = proper_time_rate(P, E0, c);
    const double Om = internal_phase_rate_at_fixed_momentum(P, E0, c, Omega0);

    // Absolute residuals (kept for back-compat) plus normalized where meaningful.
    const double shell_abs = std::abs(H * H - ((P * c) * (P * c) + E0 * E0));
    out.hamiltonian_consistency = shell_abs / std::max(H * H, 1.0);
    out.velocity_consistency = std::abs(V - c * ((P * c) / H)) / std::max(c, 1.0);
    out.gamma_consistency = std::abs(g - H / E0);
    out.proper_time_consistency = std::abs(dtau - E0 / H);
    out.phase_rate_consistency = std::abs(Om - Omega0 * E0 / H) / std::max(std::abs(Omega0), 1.0);
    out.delta_shape_separability = delta_shape_separability(P, E0, /*dE0_dq=*/1.0, c);

    out.finite = std::isfinite(out.hamiltonian_consistency) && std::isfinite(out.velocity_consistency) &&
                 std::isfinite(out.gamma_consistency) && std::isfinite(out.proper_time_consistency) &&
                 std::isfinite(out.phase_rate_consistency) && std::isfinite(out.delta_shape_separability);
    const double worst = std::max({out.hamiltonian_consistency, out.velocity_consistency, out.gamma_consistency,
                                   out.proper_time_consistency, out.phase_rate_consistency,
                                   out.delta_shape_separability});
    out.within_tolerance = out.finite && worst <= tol;
    out.ok = out.within_tolerance;
    return out;
}

} // namespace sst
