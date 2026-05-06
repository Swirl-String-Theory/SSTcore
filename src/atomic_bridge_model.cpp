#include "atomic_bridge_model.h"
#include <cmath>
#include <stdexcept>

namespace sst {

namespace { constexpr double pi_d = 3.141592653589793238462643383279502884; }

double AtomicBridgeModel::eta0(double v_swirl, double c) { return SSTCanonicalConstants::eta0(v_swirl, c); }

double AtomicBridgeModel::bohr_radius_sst(double r_c, double alpha) {
    if (r_c <= 0.0 || alpha <= 0.0) throw std::invalid_argument("r_c and alpha must be positive.");
    return 2.0 * r_c / (alpha * alpha);
}

double AtomicBridgeModel::rydberg_energy(double hbar, double reduced_mass, double a0) {
    if (hbar <= 0.0 || reduced_mass <= 0.0 || a0 <= 0.0) throw std::invalid_argument("hbar, reduced_mass, and a0 must be positive.");
    return hbar * hbar / (2.0 * reduced_mass * a0 * a0);
}

double AtomicBridgeModel::lambda_sst(double rho_core, double v_swirl, double r_c) {
    if (rho_core <= 0.0 || v_swirl <= 0.0 || r_c <= 0.0) throw std::invalid_argument("rho_core, v_swirl, and r_c must be positive.");
    return 4.0 * pi_d * rho_core * v_swirl * v_swirl * std::pow(r_c, 4);
}

double AtomicBridgeModel::soft_core_potential(double r, double Lambda, double r_c) {
    if (r_c <= 0.0) throw std::invalid_argument("r_c must be positive.");
    return -Lambda / std::sqrt(r * r + r_c * r_c);
}

double AtomicBridgeModel::soft_core_force(double r, double Lambda, double r_c) {
    if (r_c <= 0.0) throw std::invalid_argument("r_c must be positive.");
    return -Lambda * r / std::pow(r * r + r_c * r_c, 1.5);
}

double AtomicBridgeModel::clock_branch_factor(double sigma, double eta0, double gamma) {
    return 1.0 + sigma * eta0 * gamma;
}

double AtomicBridgeModel::scalar_clock_potential_linear(double sigma, double E_R, double eta0, double gamma) {
    return -2.0 * sigma * E_R * eta0 * gamma;
}

double AtomicBridgeModel::orbit_coupling_energy(double sigma, double E_R, double eta0, double anticommutator_value) {
    return 0.5 * E_R * eta0 * sigma * anticommutator_value;
}

double AtomicBridgeModel::frozen_linear_interaction(double sigma, double E_R, double eta0, double gamma, double anticommutator_value) {
    return scalar_clock_potential_linear(sigma, E_R, eta0, gamma) + orbit_coupling_energy(sigma, E_R, eta0, anticommutator_value);
}

double AtomicBridgeModel::omega_z_from_displacement_gradient(double Omega, double dxi_dz) {
    return 2.0 * Omega * dxi_dz;
}

double AtomicBridgeModel::u_theta_uniform_vorticity(double r, double omega_z) {
    return 0.5 * omega_z * r;
}

double AtomicBridgeModel::gamma_from_uniform_vorticity(double r, double omega_z, double Gamma0) {
    if (Gamma0 <= 0.0) throw std::invalid_argument("Gamma0 must be positive.");
    const double Gamma_loc = pi_d * r * r * omega_z;
    return Gamma_loc / Gamma0;
}

double AtomicBridgeModel::helical_packet_gamma(double r, double phi, double z, double t,
                                                double A_gamma, double w_r, double w_z,
                                                double v, int m, double k, double omega) {
    if (w_r <= 0.0 || w_z <= 0.0) throw std::invalid_argument("w_r and w_z must be positive.");
    const double radial = std::exp(-(r * r) / (2.0 * w_r * w_r));
    const double axial_arg = z - v * t;
    const double axial = std::exp(-(axial_arg * axial_arg) / (2.0 * w_z * w_z));
    return A_gamma * radial * axial * std::cos(static_cast<double>(m) * phi + k * z - omega * t);
}

} // namespace sst
