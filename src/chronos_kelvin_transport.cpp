#include "chronos_kelvin_transport.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace sst {

double ChronosKelvinTransport::kelvin_invariant(double R, double omega) {
    if (R <= 0.0) throw std::invalid_argument("R must be positive.");
    return R * R * omega;
}

double ChronosKelvinTransport::omega_from_invariant(double invariant, double R) {
    if (R <= 0.0) throw std::invalid_argument("R must be positive.");
    return invariant / (R * R);
}

double ChronosKelvinTransport::omega_from_swirl_clock(double S_t, double r_c, double c) {
    if (S_t < 0.0 || S_t > 1.0 || r_c <= 0.0 || c <= 0.0) {
        throw std::invalid_argument("Require 0 <= S_t <= 1 and positive r_c, c.");
    }
    return (c / r_c) * std::sqrt(std::max(0.0, 1.0 - S_t * S_t));
}

double ChronosKelvinTransport::vorticity_from_swirl_clock(double S_t, double r_c, double c) {
    // Canon Sec. 2.9 chronos-Kelvin vorticity. Rigid local rotation has
    // vorticity = 2 * angular frequency, hence omega = 2 * omega_from_swirl_clock.
    return 2.0 * omega_from_swirl_clock(S_t, r_c, c);
}

double ChronosKelvinTransport::swirl_clock_from_omega(double omega, double r_c, double c) {
    if (r_c <= 0.0 || c <= 0.0) throw std::invalid_argument("r_c and c must be positive.");
    const double x = 1.0 - (omega * r_c) * (omega * r_c) / (c * c);
    return std::sqrt(x > 0.0 ? x : 0.0);
}

double ChronosKelvinTransport::chronos_kelvin_invariant(double R, double S_t, double r_c, double c) {
    return kelvin_invariant(R, omega_from_swirl_clock(S_t, r_c, c));
}

double ChronosKelvinTransport::clock_radius_derivative(double S_t, double R, double dR_dt) {
    if (S_t <= 0.0 || R <= 0.0) throw std::invalid_argument("S_t and R must be positive.");
    return (2.0 * (1.0 - S_t * S_t) / S_t) * (dR_dt / R);
}

double ChronosKelvinTransport::radius_from_clock_invariant(double invariant, double S_t, double r_c, double c) {
    const double omega = omega_from_swirl_clock(S_t, r_c, c);
    if (omega <= 0.0) throw std::invalid_argument("omega is zero; radius is not determined by invariant.");
    return std::sqrt(invariant / omega);
}

} // namespace sst
