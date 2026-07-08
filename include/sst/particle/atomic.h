#ifndef SSTCORE_SST_PARTICLE_ATOMIC_H
#define SSTCORE_SST_PARTICLE_ATOMIC_H

#pragma once

#include "canonical_constants.h"
#include "sst/particle/scales.h"

namespace sst::particle::atomic {

double kelvin_gap_joule(double hbar, double v_swirl, double r_c, double multiplier = 1.0);
double joule_to_ev(double E_joule);
double ev_to_joule(double E_ev);
double kelvin_gap_ev(double hbar, double v_swirl, double r_c, double multiplier = 1.0);
double boltzmann_suppression(double gap_joule, double temperature_K, double k_B = 1.380649e-23);
bool is_decoupled_from_atomic_transition(double transition_ev, double gap_ev, double safety_factor = 10.0);
double gap_ratio(double transition_ev, double gap_ev);

double eta0(double v_swirl, double c = static_cast<double>(SST::Constants::C_VACUUM));
double bohr_radius_sst(double r_c, double alpha);
double rydberg_energy(double hbar, double reduced_mass, double a0);
double lambda_sst(double rho_core, double v_swirl, double r_c);
double soft_core_potential(double r, double Lambda, double r_c);
double soft_core_force(double r, double Lambda, double r_c);
double clock_branch_factor(double sigma, double eta0, double gamma);
double scalar_clock_potential_linear(double sigma, double E_R, double eta0, double gamma);
double orbit_coupling_energy(double sigma, double E_R, double eta0, double anticommutator_value);
double frozen_linear_interaction(double sigma, double E_R, double eta0, double gamma, double anticommutator_value);
double pauli_barrier_scale(double rho_f, double Gamma0, double L, double a_cut, double shape_factor = 1.0);
double omega_z_from_displacement_gradient(double Omega, double dxi_dz);
double u_theta_uniform_vorticity(double r, double omega_z);
double gamma_from_uniform_vorticity(double r, double omega_z, double Gamma0);
double helical_packet_gamma(double r, double phi, double z, double t,
                           double A_gamma, double w_r, double w_z,
                           double v, int m, double k, double omega);

} // namespace sst::particle::atomic

#endif // SSTCORE_SST_PARTICLE_ATOMIC_H
