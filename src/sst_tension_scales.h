#ifndef SSTCORE_SST_TENSION_SCALES_H
#define SSTCORE_SST_TENSION_SCALES_H
#pragma once

#include "canonical_constants.h"

namespace sst {

class SSTTensionScales {
public:
    [[nodiscard]] static double F_swirl_max(double hbar, double omega_c, double r_c);
    [[nodiscard]] static double F_gr_max(double c, double G);
    [[nodiscard]] static double gravitational_fine_structure(double G, double m_e, double hbar, double c);
    [[nodiscard]] static double tension_ratio_from_couplings(double alpha_g, double alpha);
    [[nodiscard]] static double coulomb_force_at_core(double e_charge, double epsilon_0, double r_c);
    [[nodiscard]] static double electron_spring_constant(double F_swirl_max, double r_c, double n = 2.0);
    [[nodiscard]] static double electron_spring_frequency(double F_swirl_max, double r_c, double m_e, double n = 2.0);
    [[nodiscard]] static double electron_spring_energy(double F_swirl_max, double r_c, double n = 2.0);
    [[nodiscard]] static double rydberg_from_sst(double v_swirl, double r_c, double c);
};

} // namespace sst

#endif // SSTCORE_SST_TENSION_SCALES_H
