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
    /** Normalized |∂q H - (E0/H) ∂q E0| for separable shell (0 when shape-separable). */
    double delta_shape_separability = 0.0;
    bool finite = false;
    bool within_tolerance = false;
    bool ok = false;
};

class ActionPhaseAPI {
public:
    // H = hypot(P*c, E0)
    [[nodiscard]] static double mass_shell_hamiltonian(double P, double E0, double c);
    /** Scale-safe: V = c * ((P*c)/H). */
    [[nodiscard]] static double velocity_from_mass_shell(double P, double E0, double c);
    [[nodiscard]] static double gamma_from_mass_shell(double P, double E0, double c);
    [[nodiscard]] static double proper_time_rate(double P, double E0, double c);
    // Ω = Ω0 * E0 / H  (fixed-P internal phase rate)
    [[nodiscard]] static double internal_phase_rate_at_fixed_momentum(double P, double E0, double c, double Omega0);
    [[nodiscard]] static ActionPhaseResiduals action_phase_residuals(double P, double E0, double c, double Omega0,
                                                                    double tol = 1e-12);

    /**
     * Shape-separability residual for H=sqrt(P^2 c^2 + E0(q)^2):
     * |∂q H - (E0/H) ∂q E0|. Separable ⇒ 0.
     */
    [[nodiscard]] static double delta_shape_separability(double P, double E0, double dE0_dq, double c);

    /**
     * Coupled countermodel H = hypot(P c, E0) + eps * P^2 * f_q.
     * Returns |∂q H_coupled - (E0/H_shell) ∂q E0| which stays O(|eps|) when eps≠0.
     */
    [[nodiscard]] static double coupled_shape_residual(
        double P, double E0, double dE0_dq, double c, double eps, double f_q, double df_dq);

    /**
     * Wrong fixed-V phase rate uses Ω_wrong = Ω0 / γ^2 vs correct Ω = Ω0 / γ.
     * Returns Ω_wrong/Ω_correct - 1 = γ^2 - 1.
     */
    [[nodiscard]] static double fixed_v_phase_error_factor(double P, double E0, double c);
};

} // namespace sst
