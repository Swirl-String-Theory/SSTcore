#include "sst_value_origin.h"
#include "canonical_constants.h"

#include <cmath>
#include <limits>

namespace sst {
namespace {
constexpr double pi_d = 3.141592653589793238462643383279502884;
}

const char* ValueOriginAPI::origin_name(ValueOrigin o) {
    switch (o) {
        case ValueOrigin::CanonicalSnapshot: return "CanonicalSnapshot";
        case ValueOrigin::Recomputed: return "Recomputed";
        case ValueOrigin::CalibratedInput: return "CalibratedInput";
    }
    return "CanonicalSnapshot";
}

double ValueOriginAPI::fmax_snapshot() {
    return static_cast<double>(SST::Constants::F_SWIRL_MAX);
}

double ValueOriginAPI::fmax_recompute_from_primitives() {
    return SSTCanonicalConstants::values().F_swirl_max;
}

double ValueOriginAPI::fmax_rydberg_16pi2(double hbar, double R_infty, double c, double alpha) {
    if (!(hbar > 0.0) || !(R_infty > 0.0) || !(c > 0.0) || !(alpha > 0.0)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    const double a5 = alpha * alpha * alpha * alpha * alpha;
    return 16.0 * pi_d * pi_d * hbar * R_infty * R_infty * c / a5;
}

double ValueOriginAPI::fmax_rydberg_32pi2(double hbar, double R_infty, double c, double alpha) {
    return 2.0 * fmax_rydberg_16pi2(hbar, R_infty, c, alpha);
}

SnapshotCompareResult ValueOriginAPI::compare_fmax_snapshot_to_recomputed() {
    SnapshotCompareResult out;
    out.snapshot = fmax_snapshot();
    out.recomputed = fmax_recompute_from_primitives();
    out.residual = std::abs(out.recomputed - out.snapshot);
    // Snapshot constant itself is never mutated by recompute.
    out.snapshot_unchanged = (out.snapshot == static_cast<double>(SST::Constants::F_SWIRL_MAX));
    return out;
}

double ValueOriginAPI::bare_mass_ratio_from_dimensionless_length(double L_tot) {
    if (!std::isfinite(L_tot)) return std::numeric_limits<double>::quiet_NaN();
    return L_tot / 4.0;
}

double ValueOriginAPI::bare_mass_from_dimensionless_length(double L_tot, double m_e) {
    if (!(m_e > 0.0) || !std::isfinite(L_tot)) return std::numeric_limits<double>::quiet_NaN();
    return bare_mass_ratio_from_dimensionless_length(L_tot) * m_e;
}

double ValueOriginAPI::rho_f_two_sigfig(double rho_f) {
    if (!(rho_f > 0.0) || !std::isfinite(rho_f)) return std::numeric_limits<double>::quiet_NaN();
    const double exp10 = std::floor(std::log10(rho_f));
    const double scale = std::pow(10.0, exp10 - 1.0); // 2 sig figs
    return std::round(rho_f / scale) * scale;
}

CanonicalValue ValueOriginAPI::make_canonical_value(
    const std::string& name, double value, ValueOrigin origin, int significant_figures) {
    return CanonicalValue{name, value, origin, significant_figures};
}

} // namespace sst
