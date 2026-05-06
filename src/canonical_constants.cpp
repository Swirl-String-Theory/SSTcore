#include "canonical_constants.h"
#include <cmath>
#include <stdexcept>

namespace sst {

namespace {
    constexpr double pi_d = 3.141592653589793238462643383279502884;
}

double SSTCanonicalConstants::speed_of_light() { return static_cast<double>(SST::Constants::C_VACUUM); }
double SSTCanonicalConstants::hbar() { return static_cast<double>(SST::Constants::H_BAR); }
double SSTCanonicalConstants::alpha() { return static_cast<double>(SST::Constants::ALPHA); }
double SSTCanonicalConstants::electron_mass() { return static_cast<double>(SST::Constants::M_ELECTRON); }
double SSTCanonicalConstants::elementary_charge() { return static_cast<double>(SST::Constants::E_CHARGE); }
double SSTCanonicalConstants::epsilon_0() { return static_cast<double>(SST::Constants::EPSILON_0); }
double SSTCanonicalConstants::phi() { return static_cast<double>(SST::Constants::PHI); }

double SSTCanonicalConstants::compton_angular_frequency(double m_e, double c, double hbar) {
    if (m_e <= 0.0 || c <= 0.0 || hbar <= 0.0) throw std::invalid_argument("m_e, c, and hbar must be positive.");
    return m_e * c * c / hbar;
}

double SSTCanonicalConstants::reduced_compton_wavelength(double hbar, double m_e, double c) {
    if (hbar <= 0.0 || m_e <= 0.0 || c <= 0.0) throw std::invalid_argument("hbar, m_e, and c must be positive.");
    return hbar / (m_e * c);
}

double SSTCanonicalConstants::full_compton_wavelength(double hbar, double m_e, double c) {
    return 2.0 * pi_d * reduced_compton_wavelength(hbar, m_e, c);
}

double SSTCanonicalConstants::core_radius_from_compton_anchor(double v_swirl, double omega_c) {
    if (v_swirl <= 0.0 || omega_c <= 0.0) throw std::invalid_argument("v_swirl and omega_c must be positive.");
    return v_swirl / omega_c;
}

double SSTCanonicalConstants::circulation_quantum(double r_c, double v_swirl) {
    if (r_c <= 0.0 || v_swirl <= 0.0) throw std::invalid_argument("r_c and v_swirl must be positive.");
    return 2.0 * pi_d * r_c * v_swirl;
}

double SSTCanonicalConstants::circulation_quantum_from_v_omega(double v_swirl, double omega_c) {
    return 2.0 * pi_d * v_swirl * v_swirl / omega_c;
}

double SSTCanonicalConstants::eta0(double v_swirl, double c) {
    if (c <= 0.0) throw std::invalid_argument("c must be positive.");
    return v_swirl / c;
}

double SSTCanonicalConstants::swirl_clock(double v_norm, double c) {
    if (c <= 0.0) throw std::invalid_argument("c must be positive.");
    const double x = 1.0 - (v_norm * v_norm) / (c * c);
    return std::sqrt(x > 0.0 ? x : 0.0);
}

double SSTCanonicalConstants::swirl_energy_density(double rho_f, double v_norm) {
    if (rho_f < 0.0) throw std::invalid_argument("rho_f must be non-negative.");
    return 0.5 * rho_f * v_norm * v_norm;
}

double SSTCanonicalConstants::mass_equivalent_density(double rho_E, double c) {
    if (c <= 0.0) throw std::invalid_argument("c must be positive.");
    return rho_E / (c * c);
}

double SSTCanonicalConstants::core_density_closure(double m_e, double c, double v_swirl, double r_c) {
    if (m_e <= 0.0 || c <= 0.0 || v_swirl <= 0.0 || r_c <= 0.0) {
        throw std::invalid_argument("m_e, c, v_swirl, and r_c must be positive.");
    }
    return (m_e * c * c) / (2.0 * pi_d * v_swirl * v_swirl * r_c * r_c * r_c);
}

double SSTCanonicalConstants::geometric_gate(double lambda_c, double r_c) {
    if (lambda_c <= 0.0 || r_c <= 0.0) throw std::invalid_argument("lambda_c and r_c must be positive.");
    return lambda_c / (pi_d * r_c);
}

double SSTCanonicalConstants::f_swirl_max(double hbar, double omega_c, double r_c) {
    if (hbar <= 0.0 || omega_c <= 0.0 || r_c <= 0.0) throw std::invalid_argument("hbar, omega_c, and r_c must be positive.");
    return hbar * omega_c / (2.0 * r_c);
}

double SSTCanonicalConstants::rydberg_sst(double v_swirl, double r_c, double c) {
    if (v_swirl <= 0.0 || r_c <= 0.0 || c <= 0.0) throw std::invalid_argument("v_swirl, r_c, and c must be positive.");
    return (v_swirl * v_swirl * v_swirl) / (pi_d * r_c * c * c * c);
}

double SSTCanonicalConstants::bare_master_mass_scale(double rho_m, double r_c) {
    if (rho_m < 0.0 || r_c <= 0.0) throw std::invalid_argument("rho_m must be non-negative and r_c positive.");
    return rho_m * r_c * r_c * r_c;
}

SSTCanonicalValues SSTCanonicalConstants::values(double rho_f, double v_swirl) {
    SSTCanonicalValues out;
    out.rho_f = rho_f;
    out.v_swirl = v_swirl;
    out.omega_c = compton_angular_frequency(out.m_e, out.c, out.hbar);
    out.r_c = core_radius_from_compton_anchor(v_swirl, out.omega_c);
    out.gamma_0 = circulation_quantum(out.r_c, v_swirl);
    out.lambda_bar_c = reduced_compton_wavelength(out.hbar, out.m_e, out.c);
    out.lambda_c = full_compton_wavelength(out.hbar, out.m_e, out.c);
    out.rho_E = swirl_energy_density(rho_f, v_swirl);
    out.rho_m = mass_equivalent_density(out.rho_E, out.c);
    out.rho_core = core_density_closure(out.m_e, out.c, v_swirl, out.r_c);
    out.eta_0 = eta0(v_swirl, out.c);
    out.geometric_gate = geometric_gate(out.lambda_c, out.r_c);
    out.swirl_clock = swirl_clock(v_swirl, out.c);
    out.F_swirl_max = f_swirl_max(out.hbar, out.omega_c, out.r_c);
    out.R_infty_sst = rydberg_sst(v_swirl, out.r_c, out.c);
    return out;
}

} // namespace sst
