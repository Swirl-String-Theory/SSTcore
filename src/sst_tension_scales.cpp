#include "sst_tension_scales.h"
#include <cmath>
#include <stdexcept>

namespace sst {

namespace { constexpr double pi_d = 3.141592653589793238462643383279502884; }

double SSTTensionScales::F_swirl_max(double hbar, double omega_c, double r_c) {
    return SSTCanonicalConstants::f_swirl_max(hbar, omega_c, r_c);
}

double SSTTensionScales::F_gr_max(double c, double G) {
    if (c <= 0.0 || G <= 0.0) throw std::invalid_argument("c and G must be positive.");
    return std::pow(c, 4) / (4.0 * G);
}

double SSTTensionScales::gravitational_fine_structure(double G, double m_e, double hbar, double c) {
    if (G <= 0.0 || m_e <= 0.0 || hbar <= 0.0 || c <= 0.0) throw std::invalid_argument("arguments must be positive.");
    return G * m_e * m_e / (hbar * c);
}

double SSTTensionScales::tension_ratio_from_couplings(double alpha_g, double alpha) {
    if (alpha <= 0.0) throw std::invalid_argument("alpha must be positive.");
    return 4.0 * alpha_g / alpha;
}

double SSTTensionScales::coulomb_force_at_core(double e_charge, double epsilon_0, double r_c) {
    if (epsilon_0 <= 0.0 || r_c <= 0.0) throw std::invalid_argument("epsilon_0 and r_c must be positive.");
    return e_charge * e_charge / (4.0 * pi_d * epsilon_0 * r_c * r_c);
}

double SSTTensionScales::electron_spring_constant(double F_swirl_max, double r_c, double n) {
    if (F_swirl_max <= 0.0 || r_c <= 0.0 || n <= 0.0) throw std::invalid_argument("F_swirl_max, r_c, and n must be positive.");
    return F_swirl_max / (n * r_c);
}

double SSTTensionScales::electron_spring_frequency(double F_swirl_max, double r_c, double m_e, double n) {
    if (m_e <= 0.0) throw std::invalid_argument("m_e must be positive.");
    return std::sqrt(electron_spring_constant(F_swirl_max, r_c, n) / m_e);
}

double SSTTensionScales::electron_spring_energy(double F_swirl_max, double r_c, double n) {
    // E = 1/2 K r_c^2 = F_swirl_max r_c/(2n); Canon n=2 gives F r_c/4.
    return 0.5 * electron_spring_constant(F_swirl_max, r_c, n) * r_c * r_c;
}

double SSTTensionScales::rydberg_from_sst(double v_swirl, double r_c, double c) {
    return SSTCanonicalConstants::rydberg_sst(v_swirl, r_c, c);
}

} // namespace sst
