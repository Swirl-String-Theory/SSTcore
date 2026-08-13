#pragma once

#include <string>

namespace sst {

struct MaxwellKineticResult {
    bool coupling_nonzero = false;
    bool drive_above_gap = false;
    bool lifetime_observable = false;
    bool three_gate_ok = false;
    double tau_inv = 0.0;
    std::string message;
};

class MaxwellKineticAPI {
public:
    // Three-gate activation: G≠0, E_drive≥Δ, τ≲t_obs
    [[nodiscard]] static bool three_gate_condition(
        double coupling_G, double E_drive, double gap_Delta, double tau, double t_obs);

    // τ^{-1}_{K,a} = Σ_L n_L ⟨v_rel σ^KL_{a,inel}⟩  (single-term scaffold)
    [[nodiscard]] static double collision_rate_inv(double n_L, double v_rel, double sigma_inel);

    [[nodiscard]] static MaxwellKineticResult evaluate(
        double coupling_G, double E_drive, double gap_Delta, double tau, double t_obs,
        double n_L, double v_rel, double sigma_inel);
};

} // namespace sst
