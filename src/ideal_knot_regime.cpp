#include "sst_ideal_knot_regime.h"

#include <cmath>
#include <limits>

namespace sst {

double IdealKnotRegimeAPI::epsilon_kappa(double a_core, double kappa_max) {
    if (!(a_core > 0.0) || !(kappa_max >= 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return a_core * kappa_max;
}

double IdealKnotRegimeAPI::epsilon_sep(double a_core, double d_sep) {
    if (!(a_core > 0.0) || !(d_sep > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return a_core / d_sep;
}

KnotRegime IdealKnotRegimeAPI::classify_regime(double eps_kappa, double eps_sep, double order_one) {
    if (!std::isfinite(eps_kappa) || !std::isfinite(eps_sep)) return KnotRegime::Indeterminate;
    const bool compact = (eps_kappa >= order_one) || (eps_sep >= order_one);
    const bool slender = (eps_kappa < order_one) && (eps_sep < order_one);
    if (compact) return KnotRegime::Compact;
    if (slender) return KnotRegime::Slender;
    return KnotRegime::Indeterminate;
}

double IdealKnotRegimeAPI::moffatt_ricca_helicity(double gamma, double writhe, double twist) {
    if (!std::isfinite(gamma) || !std::isfinite(writhe) || !std::isfinite(twist)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return gamma * gamma * (writhe + twist);
}

IdealKnotRegimeResult IdealKnotRegimeAPI::evaluate(
    double a_core, double kappa_max, double d_sep,
    double gamma, double writhe, double twist,
    double kkt_residual) {
    IdealKnotRegimeResult out;
    out.epsilon_kappa = epsilon_kappa(a_core, kappa_max);
    out.epsilon_sep = epsilon_sep(a_core, d_sep);
    out.regime = classify_regime(out.epsilon_kappa, out.epsilon_sep);
    out.helicity_moffatt_ricca = moffatt_ricca_helicity(gamma, writhe, twist);
    out.kkt_residual = kkt_residual;
    out.lia_kam_excluded = (out.regime == KnotRegime::Compact);
    out.message = out.lia_kam_excluded
        ? "compact ideal state: LIA/KAM excluded"
        : "regime diagnostic complete";
    return out;
}

const char* IdealKnotRegimeAPI::regime_name(KnotRegime r) {
    switch (r) {
        case KnotRegime::Compact: return "compact";
        case KnotRegime::Slender: return "slender";
        case KnotRegime::Indeterminate: return "indeterminate";
    }
    return "indeterminate";
}

} // namespace sst
