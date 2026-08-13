#pragma once

#include <string>
#include <array>

namespace sst {

struct TorsionMassResult {
    double mass = 0.0;
    double dimensional_residual = 0.0;
    std::string convention;
    bool ok = false;
};

struct AnisotropyResiduals {
    double chi_hat = 0.0;
    double delta_aniso = 0.0;
    double normalization = 0.0;
    bool ok = false;
    std::string epistemic_status; // OPEN_RESEARCH_GATE until CheckKind retrofit
};

class CoreTorsionAPI {
public:
    // M = E0 * I / c_T^2  (I has dimensions of length^2 / energy^0 — document as moment factor)
    [[nodiscard]] static TorsionMassResult torsion_inertial_mass(double E0, double I, double c_T);

    // Deprecated factor-2 route for regression guards only.
    [[nodiscard]] static TorsionMassResult torsion_inertial_mass_legacy_factor2(double E0, double I, double c_T);

    // chi_hat = c_T^2 * tr(M) / (3 E0); M is 3x3 row-major; delta_aniso = rms off-isotropy.
    [[nodiscard]] static AnisotropyResiduals anisotropy_residuals(
        const std::array<double, 9>& M_row_major, double E0, double c_T);
};

} // namespace sst
