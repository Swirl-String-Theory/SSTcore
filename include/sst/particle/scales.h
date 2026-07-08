#ifndef SSTCORE_SST_PARTICLE_SCALES_H
#define SSTCORE_SST_PARTICLE_SCALES_H

#pragma once

#include "canonical_constants.h"

namespace sst::particle::scales {

double F_swirl_max(double hbar, double omega_c, double r_c);
double F_gr_max(double c, double G);
double gravitational_fine_structure(double G, double m_e, double hbar, double c);
double tension_ratio_from_couplings(double alpha_g, double alpha);
double coulomb_force_at_core(double e_charge, double epsilon_0, double r_c);
double electron_spring_constant(double F_swirl_max, double r_c, double n = 2.0);
double electron_spring_frequency(double F_swirl_max, double r_c, double m_e, double n = 2.0);
double electron_spring_energy(double F_swirl_max, double r_c, double n = 2.0);
double rydberg_from_sst(double v_swirl, double r_c, double c);
double swirl_impedance(double P_K, double v_K);
double dimensionless_stiffness_ratio(double P_K, double V_K, double hbar, double omega);

} // namespace sst::particle::scales

#endif // SSTCORE_SST_PARTICLE_SCALES_H
