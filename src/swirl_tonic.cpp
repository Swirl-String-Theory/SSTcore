#include "sst_swirl_tonic.h"

#include <cmath>
#include <limits>

namespace sst {

double SwirlTonicAPI::stokes_circulation(
    const std::vector<double>& vx,
    const std::vector<double>& vy,
    const std::vector<double>& vz,
    const std::vector<double>& dx,
    const std::vector<double>& dy,
    const std::vector<double>& dz) {
    const std::size_t n = vx.size();
    if (n == 0 || n != vy.size() || n != vz.size() || n != dx.size() || n != dy.size() || n != dz.size()) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    double gamma = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        gamma += vx[i] * dx[i] + vy[i] * dy[i] + vz[i] * dz[i];
    }
    return gamma;
}

double SwirlTonicAPI::material_holonomy(double circulation, double gamma_0) {
    if (!(gamma_0 > 0.0) || !std::isfinite(circulation)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return circulation / gamma_0;
}

bool SwirlTonicAPI::material_tonic_not_a_eff(bool claimed_identity) {
    return !claimed_identity;
}

SwirlTonicResult SwirlTonicAPI::evaluate(
    const std::vector<double>& vx,
    const std::vector<double>& vy,
    const std::vector<double>& vz,
    const std::vector<double>& dx,
    const std::vector<double>& dy,
    const std::vector<double>& dz,
    double gamma_0,
    bool claimed_identity_with_a_eff) {
    SwirlTonicResult out;
    out.circulation = stokes_circulation(vx, vy, vz, dx, dy, dz);
    out.holonomy = material_holonomy(out.circulation, gamma_0);
    out.material_not_a_eff = material_tonic_not_a_eff(claimed_identity_with_a_eff);
    out.passed = std::isfinite(out.holonomy) && out.material_not_a_eff;
    out.message = out.passed ? "swirl-tonic ok" : "swirl-tonic guard failure";
    return out;
}

} // namespace sst
