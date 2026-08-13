#pragma once

#include <string>
#include <vector>

namespace sst {

struct SwirlTonicResult {
    double circulation = 0.0;
    double holonomy = 0.0;
    bool material_not_a_eff = false;
    bool passed = false;
    std::string message;
};

class SwirlTonicAPI {
public:
    // Stokes: Γ_C = ∮ v·dℓ (polygonal polyline, closed)
    [[nodiscard]] static double stokes_circulation(
        const std::vector<double>& vx,
        const std::vector<double>& vy,
        const std::vector<double>& vz,
        const std::vector<double>& dx,
        const std::vector<double>& dy,
        const std::vector<double>& dz);

    // h_C^(m) = Γ_C / Γ₀
    [[nodiscard]] static double material_holonomy(double circulation, double gamma_0);

    // Guard: A_st^(m) ≢ A_eff
    [[nodiscard]] static bool material_tonic_not_a_eff(bool claimed_identity);

    [[nodiscard]] static SwirlTonicResult evaluate(
        const std::vector<double>& vx,
        const std::vector<double>& vy,
        const std::vector<double>& vz,
        const std::vector<double>& dx,
        const std::vector<double>& dy,
        const std::vector<double>& dz,
        double gamma_0,
        bool claimed_identity_with_a_eff);
};

} // namespace sst
