#include "sst_core_torsion.h"

#include <cmath>
#include <limits>

namespace sst {

TorsionMassResult CoreTorsionAPI::torsion_inertial_mass(double E0, double I, double c_T) {
    TorsionMassResult out;
    out.convention = "E0*I/c_T^2";
    if (!(E0 >= 0.0) || !(I >= 0.0) || !(c_T > 0.0) || !std::isfinite(E0) || !std::isfinite(I) || !std::isfinite(c_T)) {
        out.ok = false;
        out.mass = std::numeric_limits<double>::quiet_NaN();
        out.dimensional_residual = std::numeric_limits<double>::quiet_NaN();
        return out;
    }
    out.mass = E0 * I / (c_T * c_T);
    out.dimensional_residual = 0.0;
    out.ok = true;
    return out;
}

TorsionMassResult CoreTorsionAPI::torsion_inertial_mass_legacy_factor2(double E0, double I, double c_T) {
    auto r = torsion_inertial_mass(E0, I, c_T);
    if (r.ok) {
        r.mass *= 2.0;
        r.convention = "legacy_2*E0*I/c_T^2";
    }
    return r;
}

AnisotropyResiduals CoreTorsionAPI::anisotropy_residuals(
    const std::array<double, 9>& M, double E0, double c_T) {
    AnisotropyResiduals out;
    out.epistemic_status = "OPEN_RESEARCH_GATE";
    if (!(E0 > 0.0) || !(c_T > 0.0)) {
        out.ok = false;
        return out;
    }
    const double tr = M[0] + M[4] + M[8];
    out.normalization = 3.0 * E0;
    out.chi_hat = (c_T * c_T) * tr / out.normalization;
    const double mean = tr / 3.0;
    double acc = 0.0;
    for (int i = 0; i < 3; ++i) {
        const double d = M[i * 3 + i] - mean;
        acc += d * d;
    }
    // off-diagonal contribution
    acc += 2.0 * (M[1] * M[1] + M[2] * M[2] + M[5] * M[5]);
    out.delta_aniso = std::sqrt(acc / 6.0) / (std::abs(mean) + 1e-30);
    out.ok = std::isfinite(out.chi_hat) && std::isfinite(out.delta_aniso);
    return out;
}

} // namespace sst
