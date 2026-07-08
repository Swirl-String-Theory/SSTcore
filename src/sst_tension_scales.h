#ifndef SSTCORE_SST_TENSION_SCALES_H
#define SSTCORE_SST_TENSION_SCALES_H

#pragma once

#include "sst/particle/scales.h"

namespace sst {

class [[deprecated("Use sst::particle::scales")]] SSTTensionScales {
public:
    [[nodiscard]] static double F_swirl_max(double hbar, double omega_c, double r_c) {
        return particle::scales::F_swirl_max(hbar, omega_c, r_c);
    }
    [[nodiscard]] static double F_gr_max(double c, double G) { return particle::scales::F_gr_max(c, G); }
    [[nodiscard]] static double gravitational_fine_structure(double G, double m_e, double hbar, double c) {
        return particle::scales::gravitational_fine_structure(G, m_e, hbar, c);
    }
    [[nodiscard]] static double tension_ratio_from_couplings(double alpha_g, double alpha) {
        return particle::scales::tension_ratio_from_couplings(alpha_g, alpha);
    }
    [[nodiscard]] static double coulomb_force_at_core(double e_charge, double epsilon_0, double r_c) {
        return particle::scales::coulomb_force_at_core(e_charge, epsilon_0, r_c);
    }
    [[nodiscard]] static double electron_spring_constant(double F_swirl_max, double r_c, double n = 2.0) {
        return particle::scales::electron_spring_constant(F_swirl_max, r_c, n);
    }
    [[nodiscard]] static double electron_spring_frequency(double F_swirl_max, double r_c, double m_e, double n = 2.0) {
        return particle::scales::electron_spring_frequency(F_swirl_max, r_c, m_e, n);
    }
    [[nodiscard]] static double electron_spring_energy(double F_swirl_max, double r_c, double n = 2.0) {
        return particle::scales::electron_spring_energy(F_swirl_max, r_c, n);
    }
    [[nodiscard]] static double rydberg_from_sst(double v_swirl, double r_c, double c) {
        return particle::scales::rydberg_from_sst(v_swirl, r_c, c);
    }
    [[nodiscard]] static double swirl_impedance(double P_K, double v_K) {
        return particle::scales::swirl_impedance(P_K, v_K);
    }
    [[nodiscard]] static double dimensionless_stiffness_ratio(double P_K, double V_K, double hbar, double omega) {
        return particle::scales::dimensionless_stiffness_ratio(P_K, V_K, hbar, omega);
    }
};

} // namespace sst

#endif // SSTCORE_SST_TENSION_SCALES_H
