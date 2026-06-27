#ifndef SSTCORE_ATOMIC_BRIDGE_MODEL_H
#define SSTCORE_ATOMIC_BRIDGE_MODEL_H
#pragma once

#include "canonical_constants.h"

namespace sst {

class AtomicBridgeModel {
public:
    [[nodiscard]] static double eta0(double v_swirl, double c = static_cast<double>(SST::Constants::C_VACUUM));
    [[nodiscard]] static double bohr_radius_sst(double r_c, double alpha);
    [[nodiscard]] static double rydberg_energy(double hbar, double reduced_mass, double a0);
    [[nodiscard]] static double lambda_sst(double rho_core, double v_swirl, double r_c);
    [[nodiscard]] static double soft_core_potential(double r, double Lambda, double r_c);
    [[nodiscard]] static double soft_core_force(double r, double Lambda, double r_c);
    [[nodiscard]] static double clock_branch_factor(double sigma, double eta0, double gamma);
    [[nodiscard]] static double scalar_clock_potential_linear(double sigma, double E_R, double eta0, double gamma);
    [[nodiscard]] static double orbit_coupling_energy(double sigma, double E_R, double eta0, double anticommutator_value);
    [[nodiscard]] static double frozen_linear_interaction(double sigma, double E_R, double eta0, double gamma, double anticommutator_value);

    // Hydrodynamic Pauli benchmark scale:
    // V_max = rho_f Gamma0^2/(4*pi) * (L/a_cut) * shape_factor.
    // a_cut is a UV regularization cutoff and must not be identified with a_core unless
    // an explicit resolved-core model is supplied.
    [[nodiscard]] static double pauli_barrier_scale(double rho_f, double Gamma0, double L, double a_cut, double shape_factor = 1.0);
    [[nodiscard]] static double omega_z_from_displacement_gradient(double Omega, double dxi_dz);
    [[nodiscard]] static double u_theta_uniform_vorticity(double r, double omega_z);
    [[nodiscard]] static double gamma_from_uniform_vorticity(double r, double omega_z, double Gamma0);
    [[nodiscard]] static double helical_packet_gamma(double r, double phi, double z, double t,
                                                     double A_gamma, double w_r, double w_z,
                                                     double v, int m, double k, double omega);
};

} // namespace sst

#endif // SSTCORE_ATOMIC_BRIDGE_MODEL_H
