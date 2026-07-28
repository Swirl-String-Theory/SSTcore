#include "sst_action_phase.h"

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
    return (P * c * c) / H;
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

ActionPhaseResiduals ActionPhaseAPI::action_phase_residuals(double P, double E0, double c, double Omega0) {
    ActionPhaseResiduals out;
    const double H = mass_shell_hamiltonian(P, E0, c);
    if (!std::isfinite(H) || !std::isfinite(Omega0)) {
        out.ok = false;
        return out;
    }
    const double V = velocity_from_mass_shell(P, E0, c);
    const double g = gamma_from_mass_shell(P, E0, c);
    const double dtau = proper_time_rate(P, E0, c);
    const double Om = internal_phase_rate_at_fixed_momentum(P, E0, c, Omega0);

    out.hamiltonian_consistency = std::abs(H * H - (P * P * c * c + E0 * E0));
    out.velocity_consistency = std::abs(V * H - P * c * c);
    out.gamma_consistency = std::abs(g * E0 - H);
    out.proper_time_consistency = std::abs(dtau * H - E0);
    out.phase_rate_consistency = std::abs(Om * g - Omega0);
    out.ok = std::isfinite(out.hamiltonian_consistency) &&
             std::isfinite(out.velocity_consistency) &&
             std::isfinite(out.gamma_consistency) &&
             std::isfinite(out.proper_time_consistency) &&
             std::isfinite(out.phase_rate_consistency);
    return out;
}

} // namespace sst
