#pragma once

#include <string>

namespace sst {

enum class ValueOrigin {
    CanonicalSnapshot,
    Recomputed,
    CalibratedInput
};

struct CanonicalValue {
    std::string name;
    double value = 0.0;
    ValueOrigin origin = ValueOrigin::CanonicalSnapshot;
    int significant_figures = -1; // -1 => full precision
};

struct SnapshotCompareResult {
    double snapshot = 0.0;
    double recomputed = 0.0;
    double residual = 0.0;
    bool snapshot_unchanged = true;
};

class ValueOriginAPI {
public:
    [[nodiscard]] static const char* origin_name(ValueOrigin o);

    // Canonical Fmax snapshot (must remain 29.053507).
    [[nodiscard]] static double fmax_snapshot();

    // Recompute from SSTCanonicalConstants::values().F_swirl_max (may differ slightly).
    [[nodiscard]] static double fmax_recompute_from_primitives();

    // F ~ 16 π² ħ R_∞² c / α⁵
    [[nodiscard]] static double fmax_rydberg_16pi2(double hbar, double R_infty, double c, double alpha);
    // Intentional wrong factor for regression (must not match snapshot).
    [[nodiscard]] static double fmax_rydberg_32pi2(double hbar, double R_infty, double c, double alpha);

    [[nodiscard]] static SnapshotCompareResult compare_fmax_snapshot_to_recomputed();

    // M0/m_e = L_tot / 4 (dimensionless L_tot).
    [[nodiscard]] static double bare_mass_ratio_from_dimensionless_length(double L_tot);
    [[nodiscard]] static double bare_mass_from_dimensionless_length(double L_tot, double m_e);

    // Round rho_f to 2 significant figures (canonical display policy).
    [[nodiscard]] static double rho_f_two_sigfig(double rho_f);

    [[nodiscard]] static CanonicalValue make_canonical_value(
        const std::string& name, double value, ValueOrigin origin, int significant_figures = -1);
};

} // namespace sst
