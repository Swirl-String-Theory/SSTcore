#include "sst_maxwell_kinetic.h"

#include <cmath>
#include <limits>

namespace sst {

bool MaxwellKineticAPI::three_gate_condition(
    double coupling_G, double E_drive, double gap_Delta, double tau, double t_obs) {
    if (!std::isfinite(coupling_G) || !std::isfinite(E_drive) || !std::isfinite(gap_Delta)
        || !std::isfinite(tau) || !std::isfinite(t_obs)) {
        return false;
    }
    return (coupling_G != 0.0) && (E_drive >= gap_Delta) && (tau <= t_obs);
}

double MaxwellKineticAPI::collision_rate_inv(double n_L, double v_rel, double sigma_inel) {
    if (!std::isfinite(n_L) || !std::isfinite(v_rel) || !std::isfinite(sigma_inel)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return n_L * v_rel * sigma_inel;
}

MaxwellKineticResult MaxwellKineticAPI::evaluate(
    double coupling_G, double E_drive, double gap_Delta, double tau, double t_obs,
    double n_L, double v_rel, double sigma_inel) {
    MaxwellKineticResult out;
    out.coupling_nonzero = (coupling_G != 0.0);
    out.drive_above_gap = (E_drive >= gap_Delta);
    out.lifetime_observable = (tau <= t_obs);
    out.three_gate_ok = three_gate_condition(coupling_G, E_drive, gap_Delta, tau, t_obs);
    out.tau_inv = collision_rate_inv(n_L, v_rel, sigma_inel);
    out.message = out.three_gate_ok ? "three-gate activation ok" : "three-gate not satisfied";
    return out;
}

} // namespace sst
