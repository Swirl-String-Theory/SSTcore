#include "sst/particle/scales.h"
#include "canonical_constants.h"
#include <cmath>
#include <stdexcept>

namespace sst::particle::scales {

namespace { constexpr double pi_d = 3.141592653589793238462643383279502884; }

double F_swirl_max(double hbar, double omega_c, double r_c) {
    return SSTCanonicalConstants::f_swirl_max(hbar, omega_c, r_c);
}

double F_gr_max(double c, double G) {
    if (c <= 0.0 || G <= 0.0) throw std::invalid_argument("c and G must be positive.");
    return std::pow(c, 4) / (4.0 * G);
}

double gravitational_fine_structure(double G, double m_e, double hbar, double c) {
    if (G <= 0.0 || m_e <= 0.0 || hbar <= 0.0 || c <= 0.0) throw std::invalid_argument("arguments must be positive.");
    return G * m_e * m_e / (hbar * c);
}

double tension_ratio_from_couplings(double alpha_g, double alpha) {
    if (alpha <= 0.0) throw std::invalid_argument("alpha must be positive.");
    return 4.0 * alpha_g / alpha;
}

double coulomb_force_at_core(double e_charge, double epsilon_0, double r_c) {
    if (epsilon_0 <= 0.0 || r_c <= 0.0) throw std::invalid_argument("epsilon_0 and r_c must be positive.");
    return e_charge * e_charge / (4.0 * pi_d * epsilon_0 * r_c * r_c);
}

double electron_spring_constant(double F_swirl_max, double r_c, double n) {
    if (F_swirl_max <= 0.0 || r_c <= 0.0 || n <= 0.0) throw std::invalid_argument("F_swirl_max, r_c, and n must be positive.");
    return F_swirl_max / (n * r_c);
}

double electron_spring_frequency(double F_swirl_max, double r_c, double m_e, double n) {
    if (m_e <= 0.0) throw std::invalid_argument("m_e must be positive.");
    return std::sqrt(electron_spring_constant(F_swirl_max, r_c, n) / m_e);
}

double electron_spring_energy(double F_swirl_max, double r_c, double n) {
    return 0.5 * electron_spring_constant(F_swirl_max, r_c, n) * r_c * r_c;
}

double rydberg_from_sst(double v_swirl, double r_c, double c) {
    return SSTCanonicalConstants::rydberg_sst(v_swirl, r_c, c);
}

double swirl_impedance(double P_K, double v_K) {
    if (v_K <= 0.0) throw std::invalid_argument("v_K must be positive.");
    return P_K / v_K;
}

double dimensionless_stiffness_ratio(double P_K, double V_K, double hbar, double omega) {
    if (V_K < 0.0 || hbar <= 0.0 || omega <= 0.0) {
        throw std::invalid_argument("V_K must be non-negative; hbar and omega must be positive.");
    }
    return (P_K * V_K) / (hbar * omega);
}

} // namespace sst::particle::scales
