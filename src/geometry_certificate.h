#pragma once

#include "sst/certificate_status.h"
#include "sst/types.h"
#include <array>
#include <cstddef>
#include <string>
#include <vector>

namespace sst {

struct GeometryCertificate {
    CertificateStatus status = CertificateStatus::NotEvaluated;
    double minimum_separation = 0.0;
    double minimum_radius_of_curvature = 0.0;
    double tube_radius = 0.0;
    double thickness_margin = 0.0;
    double discretization_error = 0.0;
    std::string geometry_hash;
};

struct ContactSaturationResult {
    CertificateStatus status = CertificateStatus::NotEvaluated;
    double peak_contact_pressure = 0.0;
    double saturation_pressure = 0.0;
    double saturation_ratio = 0.0;
    std::size_t active_contact_count = 0;
};

struct ChronosFirstHittingResult {
    CertificateStatus status = CertificateStatus::NotEvaluated;
    double first_hitting_time = 0.0;
    std::size_t event_index = 0;
    double threshold = 0.0;
};

struct Rank9ChannelDiagnostics {
    CertificateStatus status = CertificateStatus::NotEvaluated;
    int numerical_rank = 0;
    std::array<double, 9> singular_values{};
    double conditioning = 0.0;
};

class GeometryCertificateAPI {
public:
    // Gate: d_min > 2a and a*kappa_max <= 1 (with explicit tolerances).
    [[nodiscard]] static GeometryCertificate evaluate_tube_geometry(
        const std::vector<Vec3>& pts,
        double tube_radius,
        double separation_tol = 1e-9,
        double curvature_tol = 1e-9);

    [[nodiscard]] static ContactSaturationResult evaluate_contact_saturation(
        const std::vector<double>& contact_pressures,
        double saturation_pressure,
        double epsilon = 1e-9);

    // First hitting time t* = inf{t>=0: g(t) >= g_*}; linear interpolation between samples.
    [[nodiscard]] static ChronosFirstHittingResult chronos_first_hitting(
        const std::vector<double>& times,
        const std::vector<double>& observable,
        double threshold);

    // Rank via singular values with relative threshold tau_rank.
    [[nodiscard]] static Rank9ChannelDiagnostics rank9_from_singular_values(
        const std::array<double, 9>& singular_values,
        double tau_rank = 1e-12);

    [[nodiscard]] static std::string sha256_hex_of_points(const std::vector<Vec3>& pts);
};

} // namespace sst
