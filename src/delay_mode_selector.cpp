#include "delay_mode_selector.h"
#include <cmath>
#include <stdexcept>

namespace sst {

namespace { constexpr double pi_d = 3.141592653589793238462643383279502884; }

double DelayModeSelector::circulation_delay(double length, double v_swirl) {
    if (length < 0.0 || v_swirl <= 0.0) throw std::invalid_argument("length must be non-negative and v_swirl positive.");
    return length / v_swirl;
}

double DelayModeSelector::core_turnover_delay(double r_c, double v_swirl) {
    if (r_c <= 0.0 || v_swirl <= 0.0) throw std::invalid_argument("r_c and v_swirl must be positive.");
    return 2.0 * pi_d * r_c / v_swirl;
}

double DelayModeSelector::discrete_mode_frequency(int n, double tau) {
    if (tau <= 0.0) throw std::invalid_argument("tau must be positive.");
    return 2.0 * pi_d * static_cast<double>(n) / tau;
}

double DelayModeSelector::phase_lock_residual(double Omega, double omega0, double kappa, double tau) {
    return Omega - omega0 - kappa * std::sin(Omega * tau);
}

double DelayModeSelector::phase_lock_stability_slope(double Omega, double kappa, double tau) {
    return kappa * tau * std::cos(Omega * tau);
}

DelayModeResult DelayModeSelector::solve_phase_locked_frequency(
    double omega0, double kappa, double tau, double initial_guess, int max_iter, double tol)
{
    if (tau <= 0.0 || max_iter <= 0 || tol <= 0.0) throw std::invalid_argument("tau, max_iter, and tol must be positive.");
    DelayModeResult out;
    out.tau = tau;
    double Omega = (initial_guess != 0.0) ? initial_guess : omega0;
    for (int i = 0; i < max_iter; ++i) {
        const double f = phase_lock_residual(Omega, omega0, kappa, tau);
        const double df = 1.0 - kappa * tau * std::cos(Omega * tau);
        if (std::abs(df) < 1e-30) break;
        const double step = f / df;
        Omega -= step;
        out.iterations = i + 1;
        if (std::abs(step) <= tol * std::max(1.0, std::abs(Omega))) {
            out.converged = true;
            break;
        }
    }
    out.omega = Omega;
    out.residual = phase_lock_residual(Omega, omega0, kappa, tau);
    return out;
}

} // namespace sst
