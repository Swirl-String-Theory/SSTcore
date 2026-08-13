#include "sst_mechanical_falsifier.h"

#include <cmath>
#include <limits>

namespace sst {

double MechanicalFalsifierAPI::delta_p_omega(double p_perp, double p_parallel) {
    if (!std::isfinite(p_perp) || !std::isfinite(p_parallel)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return p_perp - p_parallel;
}

double MechanicalFalsifierAPI::C_blind(double delta_p, double rho_f, double v_ref) {
    if (!(rho_f > 0.0) || !(v_ref > 0.0) || !std::isfinite(delta_p)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return delta_p / (rho_f * v_ref * v_ref);
}

bool MechanicalFalsifierAPI::blind_scaling_gate(int power_rho_f, int power_v, int power_L) {
    return power_rho_f == 1 && power_v == 2 && power_L == 0;
}

MechanicalFalsifierResult MechanicalFalsifierAPI::evaluate(
    double p_perp, double p_parallel, double rho_f, double v_ref) {
    MechanicalFalsifierResult out;
    out.delta_p_omega = delta_p_omega(p_perp, p_parallel);
    out.C_blind = C_blind(out.delta_p_omega, rho_f, v_ref);
    out.scaling_ok = blind_scaling_gate(1, 2, 0) && std::isfinite(out.C_blind);
    out.message = out.scaling_ok ? "blind mechanical falsifier ok" : "blind mechanical falsifier failure";
    return out;
}

} // namespace sst
