#include "sst_spectro_response.h"

#include <cmath>
#include <limits>

namespace sst {

double SpectroResponseAPI::configuration_transition_energy(double E_excited, double E_ground) {
    if (!std::isfinite(E_excited) || !std::isfinite(E_ground)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return E_excited - E_ground;
}

double SpectroResponseAPI::transition_frequency(double delta_E, double h) {
    if (!(h > 0.0) || !std::isfinite(delta_E)) return std::numeric_limits<double>::quiet_NaN();
    return delta_E / h;
}

double SpectroResponseAPI::linear_response_delta_nu(
    double h,
    const std::vector<double>& dDeltaE_dq,
    const std::vector<double>& dq) {
    if (!(h > 0.0) || dDeltaE_dq.size() != dq.size()) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    double sum = 0.0;
    for (std::size_t i = 0; i < dq.size(); ++i) {
        sum += dDeltaE_dq[i] * dq[i];
    }
    return sum / h;
}

bool SpectroResponseAPI::rejects_double_count_with_xi_k(bool xi_k_already_includes_H_K) {
    return xi_k_already_includes_H_K; // true means the forbidden path was detected
}

SpectroResponseResult SpectroResponseAPI::evaluate(
    double E_excited, double E_ground, double h,
    const std::vector<double>& dDeltaE_dq,
    const std::vector<double>& dq,
    bool xi_k_already_includes_H_K) {
    SpectroResponseResult out;
    out.delta_E = configuration_transition_energy(E_excited, E_ground);
    out.nu = transition_frequency(out.delta_E, h);
    out.delta_nu = linear_response_delta_nu(h, dDeltaE_dq, dq);
    out.double_count_with_xi_k = rejects_double_count_with_xi_k(xi_k_already_includes_H_K);
    out.passed = std::isfinite(out.delta_nu) && !out.double_count_with_xi_k;
    out.message = out.passed ? "spectro response ok" : "spectro response guard failure";
    return out;
}

} // namespace sst
