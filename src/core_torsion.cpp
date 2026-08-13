#include "sst_core_torsion.h"

#include <algorithm>
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
    // Dimensionless residual of the defining identity M * c_T^2 - E0 * I = 0.
    const double scale = std::max({std::abs(out.mass) * c_T * c_T, std::abs(E0 * I), 1.0});
    out.dimensional_residual = std::abs(out.mass * c_T * c_T - E0 * I) / scale;
    out.ok = true;
    return out;
}

TorsionMassResult CoreTorsionAPI::torsion_inertial_mass_legacy_factor2(double E0, double I, double c_T) {
    auto r = torsion_inertial_mass(E0, I, c_T);
    if (r.ok) {
        r.mass *= 2.0;
        r.convention = "legacy_2*E0*I/c_T^2";
        const double scale = std::max({std::abs(r.mass) * c_T * c_T, std::abs(2.0 * E0 * I), 1.0});
        r.dimensional_residual = std::abs(r.mass * c_T * c_T - 2.0 * E0 * I) / scale;
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
    for (double v : M) {
        if (!std::isfinite(v)) {
            out.ok = false;
            return out;
        }
    }
    // Symmetry: require |M_ij - M_ji| small relative to Frobenius norm.
    double fro2 = 0.0;
    for (double v : M) fro2 += v * v;
    const double fro = std::sqrt(fro2);
    double asym = 0.0;
    asym += std::abs(M[1] - M[3]);
    asym += std::abs(M[2] - M[6]);
    asym += std::abs(M[5] - M[7]);
    if (asym > 1e-12 * (fro + 1.0)) {
        out.ok = false;
        out.epistemic_status = "OPEN_RESEARCH_GATE";
        out.delta_aniso = std::numeric_limits<double>::quiet_NaN();
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
    // Full off-diagonal (upper + lower) contribution.
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            if (i == j) continue;
            const double v = M[i * 3 + j];
            acc += v * v;
        }
    }
    out.delta_aniso = std::sqrt(acc / 8.0) / (std::abs(mean) + 1e-30);
    out.ok = std::isfinite(out.chi_hat) && std::isfinite(out.delta_aniso);
    return out;
}

} // namespace sst
