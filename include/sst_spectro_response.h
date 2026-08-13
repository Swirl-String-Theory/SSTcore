#pragma once

#include <string>
#include <vector>

namespace sst {

struct SpectroResponseResult {
    double delta_E = 0.0;
    double nu = 0.0;
    double delta_nu = 0.0;
    bool double_count_with_xi_k = false;
    bool passed = false;
    std::string message;
};

class SpectroResponseAPI {
public:
    // ΔE_i^(K) = E_{i,e}^(K) - E_{i,g}^(K)
    [[nodiscard]] static double configuration_transition_energy(double E_excited, double E_ground);

    // ν = ΔE / h
    [[nodiscard]] static double transition_frequency(double delta_E, double h);

    // δν = (1/h) Σ (∂ΔE/∂q_A) δq_A
    [[nodiscard]] static double linear_response_delta_nu(
        double h,
        const std::vector<double>& dDeltaE_dq,
        const std::vector<double>& dq);

    // Guard: do not double-count H_K inside Ξ_K.
    [[nodiscard]] static bool rejects_double_count_with_xi_k(bool xi_k_already_includes_H_K);

    [[nodiscard]] static SpectroResponseResult evaluate(
        double E_excited, double E_ground, double h,
        const std::vector<double>& dDeltaE_dq,
        const std::vector<double>& dq,
        bool xi_k_already_includes_H_K);
};

} // namespace sst
