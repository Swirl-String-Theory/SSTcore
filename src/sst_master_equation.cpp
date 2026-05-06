#include "sst_master_equation.h"
#include <cmath>
#include <stdexcept>

namespace sst {

namespace { constexpr double pi_d = 3.141592653589793238462643383279502884; }

double SSTMasterEquation::topological_kernel(const SSTTopologyKernelInput& in) {
    if (in.phi <= 0.0) throw std::invalid_argument("phi must be positive.");
    const double additive = in.alpha_C * in.crossing + in.beta_L * in.ropelength + in.gamma_H * in.helicity;
    return additive * std::pow(in.phi, -2.0 * static_cast<double>(in.golden_layer));
}

double SSTMasterEquation::geometric_gate_factor(double lambda_c, double r_c, int gate) {
    if (lambda_c <= 0.0 || r_c <= 0.0) throw std::invalid_argument("lambda_c and r_c must be positive.");
    if (gate < 0) throw std::invalid_argument("gate must be non-negative.");
    return std::pow(lambda_c / (pi_d * r_c), static_cast<double>(gate));
}

double SSTMasterEquation::clock_impedance(double swirl_clock) {
    if (swirl_clock <= 0.0) throw std::invalid_argument("swirl_clock must be positive.");
    return 1.0 / (swirl_clock * swirl_clock);
}

double SSTMasterEquation::weak_swirl_clock_impedance(double v_norm, double c) {
    if (c <= 0.0) throw std::invalid_argument("c must be positive.");
    const double x = (v_norm * v_norm) / (c * c);
    return 1.0 + x;
}

double SSTMasterEquation::geometric_baseline_mass(double rho_m, double r_c, double lambda_c, double L_tot) {
    if (rho_m < 0.0 || r_c <= 0.0 || lambda_c <= 0.0) {
        throw std::invalid_argument("rho_m must be non-negative; r_c and lambda_c must be positive.");
    }
    return 2.0 * pi_d * pi_d * pi_d * rho_m * std::pow(r_c, 5) / (lambda_c * lambda_c) * L_tot;
}

SSTMasterEquationOutput SSTMasterEquation::evaluate(const SSTMasterEquationInput& in) {
    if (in.rho_f < 0.0 || in.r_c <= 0.0 || in.c <= 0.0) {
        throw std::invalid_argument("rho_f must be non-negative; r_c and c must be positive.");
    }
    SSTMasterEquationOutput out;
    const double lambda_c = (in.lambda_c > 0.0)
        ? in.lambda_c
        : SSTCanonicalConstants::full_compton_wavelength();

    out.rho_E = SSTCanonicalConstants::swirl_energy_density(in.rho_f, in.v_norm);
    out.rho_m = SSTCanonicalConstants::mass_equivalent_density(out.rho_E, in.c);
    out.swirl_clock = (in.explicit_swirl_clock > 0.0)
        ? in.explicit_swirl_clock
        : SSTCanonicalConstants::swirl_clock(in.v_norm, in.c);
    out.clock_impedance = clock_impedance(out.swirl_clock);
    out.geometric_gate = geometric_gate_factor(lambda_c, in.r_c, in.gate);
    out.topological_kernel = topological_kernel(in.topology);
    out.bare_mass_scale_kg = SSTCanonicalConstants::bare_master_mass_scale(out.rho_m, in.r_c);
    out.mass_kg = out.bare_mass_scale_kg * out.geometric_gate * out.topological_kernel * out.clock_impedance;
    return out;
}

} // namespace sst
