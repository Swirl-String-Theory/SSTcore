#ifndef SSTCORE_DELAY_MODE_SELECTOR_H
#define SSTCORE_DELAY_MODE_SELECTOR_H
#pragma once

namespace sst {

struct DelayModeResult {
    double omega = 0.0;
    double residual = 0.0;
    double tau = 0.0;
    bool converged = false;
    int iterations = 0;
};

class DelayModeSelector {
public:
    [[nodiscard]] static double circulation_delay(double length, double v_swirl);
    [[nodiscard]] static double core_turnover_delay(double r_c, double v_swirl);
    [[nodiscard]] static double discrete_mode_frequency(int n, double tau);
    [[nodiscard]] static double phase_lock_residual(double Omega, double omega0, double kappa, double tau);
    [[nodiscard]] static double phase_lock_stability_slope(double Omega, double kappa, double tau);
    [[nodiscard]] static DelayModeResult solve_phase_locked_frequency(
        double omega0, double kappa, double tau, double initial_guess = 0.0,
        int max_iter = 64, double tol = 1e-12);
};

} // namespace sst

#endif // SSTCORE_DELAY_MODE_SELECTOR_H
