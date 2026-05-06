#include "clock_field_eft.h"
#include <cmath>
#include <stdexcept>

namespace sst {

namespace { constexpr double pi_d = 3.141592653589793238462643383279502884; }

double ClockFieldEFT::c13(double c1, double c3) { return c1 + c3; }

double ClockFieldEFT::tensor_speed(double c13_value, double c) {
    if (c <= 0.0) throw std::invalid_argument("c must be positive.");
    const double denom = 1.0 - c13_value;
    if (denom <= 0.0) throw std::invalid_argument("Require 1 - c13 > 0.");
    return c / std::sqrt(denom);
}

double ClockFieldEFT::tensor_speed_fractional_offset(double c13_value) {
    const double denom = 1.0 - c13_value;
    if (denom <= 0.0) throw std::invalid_argument("Require 1 - c13 > 0.");
    return 1.0 / std::sqrt(denom) - 1.0;
}

bool ClockFieldEFT::satisfies_gw170817(double c13_value, double tolerance) {
    if (tolerance < 0.0) throw std::invalid_argument("tolerance must be non-negative.");
    return std::abs(tensor_speed_fractional_offset(c13_value)) <= tolerance;
}

ClockSectorConstraints ClockFieldEFT::constraints(double c1, double c3, double tolerance) {
    ClockSectorConstraints out;
    out.c13 = c13(c1, c3);
    out.tensor_speed = tensor_speed(out.c13, 1.0);
    out.tensor_speed_fractional_offset = tensor_speed_fractional_offset(out.c13);
    out.gw170817_ok = satisfies_gw170817(out.c13, tolerance);
    return out;
}

double ClockFieldEFT::poisson_source(double rho_matter, double G_eff) {
    if (G_eff < 0.0) throw std::invalid_argument("G_eff must be non-negative.");
    return 4.0 * pi_d * G_eff * rho_matter;
}

double ClockFieldEFT::effective_gravity_from_potential_gradient(double grad_chi) {
    return -grad_chi;
}

Vec4 ClockFieldEFT::unit_timelike_from_gradient_minkowski(const Vec4& grad_chi) {
    // Metric signature (-,+,+,+). For timelike gradient: norm2 = -g^{ab} grad_a grad_b > 0.
    const double norm2 = grad_chi[0]*grad_chi[0] - grad_chi[1]*grad_chi[1] - grad_chi[2]*grad_chi[2] - grad_chi[3]*grad_chi[3];
    if (norm2 <= 0.0) throw std::invalid_argument("gradient must be timelike in (-,+,+,+) signature.");
    const double inv_norm = 1.0 / std::sqrt(norm2);
    return {grad_chi[0]*inv_norm, grad_chi[1]*inv_norm, grad_chi[2]*inv_norm, grad_chi[3]*inv_norm};
}

} // namespace sst
