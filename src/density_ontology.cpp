#include "sst_density_ontology.h"

#include <cmath>

namespace sst {

const char* DensityOntologyAPI::symbol_name(DensitySymbol s) {
    switch (s) {
        case DensitySymbol::RhoSub: return "rho_sub";
        case DensitySymbol::RhoEff: return "rho_eff";
        case DensitySymbol::JOmega: return "J_omega";
        case DensitySymbol::MuL: return "mu_l";
    }
    return "unknown";
}

const char* DensityOntologyAPI::symbol_unit(DensitySymbol s) {
    switch (s) {
        case DensitySymbol::RhoSub: return "kg/m^3";
        case DensitySymbol::RhoEff: return "kg/m^3";
        case DensitySymbol::JOmega: return "kg/m";
        case DensitySymbol::MuL: return "kg/m";
    }
    return "";
}

bool DensityOntologyAPI::rho_sub_differs_from_rho_f(double rho_sub, double rho_f, double abs_tol) {
    if (!std::isfinite(rho_sub) || !std::isfinite(rho_f)) return true;
    return std::abs(rho_sub - rho_f) > abs_tol;
}

bool DensityOntologyAPI::j_omega_differs_from_mu_l(double j_omega, double mu_l, double abs_tol) {
    if (!std::isfinite(j_omega) || !std::isfinite(mu_l)) return true;
    return std::abs(j_omega - mu_l) > abs_tol;
}

DimensionalCheckResult DensityOntologyAPI::validate_energy_density_form(EnergyDensityForm form) {
    DimensionalCheckResult out;
    switch (form) {
        case EnergyDensityForm::HalfRhoEffDtASquared:
            out.allowed = true;
            out.reason = "u_disp = 1/2 rho_eff |d_t A|^2 with [A]=m is dimensionally valid";
            break;
        case EnergyDensityForm::HalfJOmegaOmegaSquared:
            out.allowed = true;
            out.reason = "u_rot = 1/2 J_omega |omega|^2 is dimensionally valid";
            break;
        case EnergyDensityForm::HalfRhoFOmegaSquaredNoLength:
            out.allowed = false;
            out.reason = "forbidden: 1/2 rho_f |omega|^2 without derived length^2";
            break;
        default:
            out.allowed = false;
            out.reason = "unknown energy-density form";
            break;
    }
    return out;
}

bool DensityOntologyAPI::reject_j_omega_equals_rho_f_ell2_without_bridge(
    double j_omega, double rho_f, double ell2) {
    (void)j_omega;
    (void)rho_f;
    (void)ell2;
    // Without an explicit bridge declaration, identification is rejected.
    return true;
}

} // namespace sst
