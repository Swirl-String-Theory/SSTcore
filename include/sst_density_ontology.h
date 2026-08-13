#pragma once

#include <string>

namespace sst {

enum class DensitySymbol {
    RhoSub,   // material substrate [kg/m^3], unfixed
    RhoEff,   // quasi-static effective inertia ≡ rho_f [kg/m^3]
    JOmega,   // rotational microinertia density [kg/m]
    MuL       // line inertia coefficient [kg/m]
};

enum class EnergyDensityForm {
    HalfRhoEffDtASquared,  // 1/2 rho_eff |∂_t A|^2 with [A]=m  — allowed
    HalfJOmegaOmegaSquared, // 1/2 J_ω |ω|^2                     — allowed
    HalfRhoFOmegaSquaredNoLength, // 1/2 rho_f |ω|^2 without ℓ² — forbidden
    Unknown
};

struct DimensionalCheckResult {
    bool allowed = false;
    std::string reason;
};

class DensityOntologyAPI {
public:
    [[nodiscard]] static const char* symbol_name(DensitySymbol s);
    [[nodiscard]] static const char* symbol_unit(DensitySymbol s);

    // Non-identification guards.
    [[nodiscard]] static bool rho_sub_differs_from_rho_f(double rho_sub, double rho_f, double abs_tol = 0.0);
    [[nodiscard]] static bool j_omega_differs_from_mu_l(double j_omega, double mu_l, double abs_tol = 0.0);

    // Alias: rho_f ≡ rho_eff as constant quasi-static response coefficient.
    [[nodiscard]] static bool rho_f_aliases_rho_eff() { return true; }

    [[nodiscard]] static DimensionalCheckResult validate_energy_density_form(EnergyDensityForm form);

    // Forbidden: treat J_ω as rho_f * ℓ² without an explicit bridge length.
    [[nodiscard]] static bool reject_j_omega_equals_rho_f_ell2_without_bridge(
        double j_omega, double rho_f, double ell2);
};

} // namespace sst
