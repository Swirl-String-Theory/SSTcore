#pragma once

#include <string>

namespace sst {

enum class KnotRegime {
    Compact,
    Slender,
    Indeterminate
};

struct IdealKnotRegimeResult {
    double epsilon_kappa = 0.0;
    double epsilon_sep = 0.0;
    KnotRegime regime = KnotRegime::Indeterminate;
    double helicity_moffatt_ricca = 0.0; // Γ² (Wr + Tw)
    double kkt_residual = 0.0;
    bool lia_kam_excluded = false;
    std::string message;
};

class IdealKnotRegimeAPI {
public:
    [[nodiscard]] static double epsilon_kappa(double a_core, double kappa_max);
    [[nodiscard]] static double epsilon_sep(double a_core, double d_sep);

    [[nodiscard]] static KnotRegime classify_regime(double eps_kappa, double eps_sep, double order_one = 0.3);

    // H = Γ² (Wr + Tw) = Γ² SL  [Moffatt–Ricca single-tube]
    [[nodiscard]] static double moffatt_ricca_helicity(double gamma, double writhe, double twist);

    [[nodiscard]] static IdealKnotRegimeResult evaluate(
        double a_core, double kappa_max, double d_sep,
        double gamma, double writhe, double twist,
        double kkt_residual = 0.0);

    [[nodiscard]] static const char* regime_name(KnotRegime r);
};

} // namespace sst
