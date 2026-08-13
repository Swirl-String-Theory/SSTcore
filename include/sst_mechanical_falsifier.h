#pragma once

#include <string>

namespace sst {

struct MechanicalFalsifierResult {
    double delta_p_omega = 0.0;
    double C_blind = 0.0;
    bool scaling_ok = false; // Δp_ω ∝ rho_f^1 v^2 L^0
    std::string message;
};

class MechanicalFalsifierAPI {
public:
    // Coarse Reynolds axis pressure difference diagnostic.
    // Δp_ω = p_⊥ - p_∥ (caller supplies pressures).
    [[nodiscard]] static double delta_p_omega(double p_perp, double p_parallel);

    // C_blind = median(Δp_ω) / (rho_f v_ref²) — single-sample form
    [[nodiscard]] static double C_blind(double delta_p, double rho_f, double v_ref);

    // Scaling check: expected power of rho_f is 1, of v_ref is 2, of L is 0.
    [[nodiscard]] static bool blind_scaling_gate(int power_rho_f, int power_v, int power_L);

    [[nodiscard]] static MechanicalFalsifierResult evaluate(
        double p_perp, double p_parallel, double rho_f, double v_ref);
};

} // namespace sst
