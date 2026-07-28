#pragma once

#include <cmath>
#include <limits>
#include <string>

namespace sst {

struct ActionPhaseResiduals {
    double hamiltonian_consistency = 0.0;
    double velocity_consistency = 0.0;
    double gamma_consistency = 0.0;
    double proper_time_consistency = 0.0;
    double phase_rate_consistency = 0.0;
    bool ok = false;
};

class ActionPhaseAPI {
public:
    // H = hypot(P*c, E0)
    [[nodiscard]] static double mass_shell_hamiltonian(double P, double E0, double c);
    [[nodiscard]] static double velocity_from_mass_shell(double P, double E0, double c);
    [[nodiscard]] static double gamma_from_mass_shell(double P, double E0, double c);
    [[nodiscard]] static double proper_time_rate(double P, double E0, double c);
    // Ω = Ω0 * E0 / H  (fixed-P internal phase rate)
    [[nodiscard]] static double internal_phase_rate_at_fixed_momentum(double P, double E0, double c, double Omega0);
    [[nodiscard]] static ActionPhaseResiduals action_phase_residuals(double P, double E0, double c, double Omega0);
};

} // namespace sst
