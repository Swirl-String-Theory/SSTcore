#ifndef SSTCORE_ATOMIC_BRIDGE_MODEL_H
#define SSTCORE_ATOMIC_BRIDGE_MODEL_H

#pragma once

#include "sst/particle/atomic.h"

namespace sst {

class [[deprecated("Use sst::particle::atomic")]] AtomicBridgeModel {
public:
    [[nodiscard]] static double eta0(double v_swirl, double c = static_cast<double>(SST::Constants::C_VACUUM)) {
        return particle::atomic::eta0(v_swirl, c);
    }
    [[nodiscard]] static double bohr_radius_sst(double r_c, double alpha) {
        return particle::atomic::bohr_radius_sst(r_c, alpha);
    }
    [[nodiscard]] static double rydberg_energy(double hbar, double reduced_mass, double a0) {
        return particle::atomic::rydberg_energy(hbar, reduced_mass, a0);
    }
    [[nodiscard]] static double lambda_sst(double rho_core, double v_swirl, double r_c) {
        return particle::atomic::lambda_sst(rho_core, v_swirl, r_c);
    }
    [[nodiscard]] static double soft_core_potential(double r, double Lambda, double r_c) {
        return particle::atomic::soft_core_potential(r, Lambda, r_c);
    }
    [[nodiscard]] static double soft_core_force(double r, double Lambda, double r_c) {
        return particle::atomic::soft_core_force(r, Lambda, r_c);
    }
    [[nodiscard]] static double clock_branch_factor(double sigma, double eta0, double gamma) {
        return particle::atomic::clock_branch_factor(sigma, eta0, gamma);
    }
    [[nodiscard]] static double scalar_clock_potential_linear(double sigma, double E_R, double eta0, double gamma) {
        return particle::atomic::scalar_clock_potential_linear(sigma, E_R, eta0, gamma);
    }
    [[nodiscard]] static double orbit_coupling_energy(double sigma, double E_R, double eta0, double anticommutator_value) {
        return particle::atomic::orbit_coupling_energy(sigma, E_R, eta0, anticommutator_value);
    }
    [[nodiscard]] static double frozen_linear_interaction(double sigma, double E_R, double eta0, double gamma, double anticommutator_value) {
        return particle::atomic::frozen_linear_interaction(sigma, E_R, eta0, gamma, anticommutator_value);
    }
    [[nodiscard]] static double pauli_barrier_scale(double rho_f, double Gamma0, double L, double a_cut, double shape_factor = 1.0) {
        return particle::atomic::pauli_barrier_scale(rho_f, Gamma0, L, a_cut, shape_factor);
    }
    [[nodiscard]] static double omega_z_from_displacement_gradient(double Omega, double dxi_dz) {
        return particle::atomic::omega_z_from_displacement_gradient(Omega, dxi_dz);
    }
    [[nodiscard]] static double u_theta_uniform_vorticity(double r, double omega_z) {
        return particle::atomic::u_theta_uniform_vorticity(r, omega_z);
    }
    [[nodiscard]] static double gamma_from_uniform_vorticity(double r, double omega_z, double Gamma0) {
        return particle::atomic::gamma_from_uniform_vorticity(r, omega_z, Gamma0);
    }
    [[nodiscard]] static double helical_packet_gamma(double r, double phi, double z, double t,
                                                     double A_gamma, double w_r, double w_z,
                                                     double v, int m, double k, double omega) {
        return particle::atomic::helical_packet_gamma(r, phi, z, t, A_gamma, w_r, w_z, v, m, k, omega);
    }
};

} // namespace sst

#endif // SSTCORE_ATOMIC_BRIDGE_MODEL_H
