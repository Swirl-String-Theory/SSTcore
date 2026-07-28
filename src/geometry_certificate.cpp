#include "geometry_certificate.h"

#include "sst/tube/geometry_core.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <limits>
#include <sstream>
#include <stdexcept>

namespace sst {
namespace {

// FNV-1a 64-bit folded to hex (stable geometry fingerprint; not cryptographic SHA-256).
std::string fnv1a_hex(const std::vector<Vec3>& pts) {
    std::uint64_t h = 14695981039346656037ull;
    for (const auto& p : pts) {
        for (std::size_t k = 0; k < 3; ++k) {
            const double c = p[k];
            const auto* bytes = reinterpret_cast<const unsigned char*>(&c);
            for (std::size_t i = 0; i < sizeof(double); ++i) {
                h ^= bytes[i];
                h *= 1099511628211ull;
            }
        }
    }
    std::ostringstream oss;
    oss << std::hex << std::setfill('0') << std::setw(16) << h;
    return oss.str();
}

} // namespace

std::string GeometryCertificateAPI::sha256_hex_of_points(const std::vector<Vec3>& pts) {
    // Name retained for API stability; implementation is a deterministic FNV-1a fingerprint.
    return fnv1a_hex(pts);
}

GeometryCertificate GeometryCertificateAPI::evaluate_tube_geometry(
    const std::vector<Vec3>& pts,
    double tube_radius,
    double separation_tol,
    double curvature_tol) {
    GeometryCertificate out;
    out.tube_radius = tube_radius;
    out.geometry_hash = sha256_hex_of_points(pts);

    if (pts.size() < 3 || !(tube_radius > 0.0) || !(separation_tol >= 0.0) || !(curvature_tol >= 0.0)) {
        out.status = CertificateStatus::Indeterminate;
        return out;
    }

    try {
        const auto metrics = ResolvedTubeGeometry::analyze(pts, /*skip_neighbors=*/2, /*contact_tol=*/1e-3, /*equilateral_tol=*/1e-3);
        out.minimum_separation = metrics.min_dcsd;
        out.minimum_radius_of_curvature = metrics.minrad;
        out.thickness_margin = metrics.min_dcsd - 2.0 * tube_radius;
        out.discretization_error = metrics.edge_length_max_rel_dev;

        const bool sep_ok = metrics.min_dcsd > 2.0 * tube_radius + separation_tol;
        const double kappa_max = (metrics.minrad > 0.0) ? (1.0 / metrics.minrad) : std::numeric_limits<double>::infinity();
        const bool curv_ok = tube_radius * kappa_max <= 1.0 + curvature_tol;

        if (!std::isfinite(metrics.min_dcsd) || !std::isfinite(metrics.minrad)) {
            out.status = CertificateStatus::Indeterminate;
        } else if (sep_ok && curv_ok) {
            out.status = CertificateStatus::Pass;
        } else {
            out.status = CertificateStatus::Fail;
        }
    } catch (const std::exception&) {
        out.status = CertificateStatus::Indeterminate;
    }
    return out;
}

ContactSaturationResult GeometryCertificateAPI::evaluate_contact_saturation(
    const std::vector<double>& contact_pressures,
    double saturation_pressure,
    double epsilon) {
    ContactSaturationResult out;
    out.saturation_pressure = saturation_pressure;

    if (!(saturation_pressure > 0.0) || !(epsilon >= 0.0)) {
        out.status = CertificateStatus::Indeterminate;
        return out;
    }
    if (contact_pressures.empty()) {
        out.status = CertificateStatus::Indeterminate;
        return out;
    }

    double peak = 0.0;
    std::size_t active = 0;
    for (double p : contact_pressures) {
        if (!std::isfinite(p)) {
            out.status = CertificateStatus::Indeterminate;
            return out;
        }
        peak = std::max(peak, p);
        if (p > epsilon) ++active;
    }
    out.peak_contact_pressure = peak;
    out.active_contact_count = active;
    out.saturation_ratio = peak / saturation_pressure;

    if (out.saturation_ratio < 1.0 - epsilon) {
        out.status = CertificateStatus::Pass; // under saturation
    } else if (std::abs(out.saturation_ratio - 1.0) <= epsilon) {
        out.status = CertificateStatus::Pass; // on threshold
    } else {
        out.status = CertificateStatus::Fail; // above saturation
    }
    return out;
}

ChronosFirstHittingResult GeometryCertificateAPI::chronos_first_hitting(
    const std::vector<double>& times,
    const std::vector<double>& observable,
    double threshold) {
    ChronosFirstHittingResult out;
    out.threshold = threshold;

    if (times.size() < 2 || times.size() != observable.size() || !std::isfinite(threshold)) {
        out.status = CertificateStatus::Indeterminate;
        return out;
    }

    for (std::size_t i = 0; i < times.size(); ++i) {
        if (!std::isfinite(times[i]) || !std::isfinite(observable[i])) {
            out.status = CertificateStatus::Indeterminate;
            return out;
        }
        if (i > 0 && !(times[i] >= times[i - 1])) {
            out.status = CertificateStatus::Indeterminate;
            return out;
        }
    }

    if (observable[0] >= threshold) {
        out.status = CertificateStatus::Pass;
        out.first_hitting_time = times[0];
        out.event_index = 0;
        return out;
    }

    for (std::size_t i = 1; i < times.size(); ++i) {
        const double g0 = observable[i - 1];
        const double g1 = observable[i];
        if (g0 < threshold && g1 >= threshold) {
            const double dg = g1 - g0;
            const double alpha = (std::abs(dg) < 1e-30) ? 0.0 : (threshold - g0) / dg;
            out.first_hitting_time = times[i - 1] + alpha * (times[i] - times[i - 1]);
            out.event_index = i;
            out.status = CertificateStatus::Pass;
            return out;
        }
    }

    // No hit
    out.status = CertificateStatus::Fail;
    out.first_hitting_time = std::numeric_limits<double>::infinity();
    out.event_index = times.size();
    return out;
}

Rank9ChannelDiagnostics GeometryCertificateAPI::rank9_from_singular_values(
    const std::array<double, 9>& singular_values,
    double tau_rank) {
    Rank9ChannelDiagnostics out;
    out.singular_values = singular_values;

    if (!(tau_rank > 0.0)) {
        out.status = CertificateStatus::Indeterminate;
        return out;
    }

    double sigma_max = 0.0;
    for (double s : singular_values) {
        if (!std::isfinite(s) || s < 0.0) {
            out.status = CertificateStatus::Indeterminate;
            return out;
        }
        sigma_max = std::max(sigma_max, s);
    }

    if (sigma_max == 0.0) {
        out.numerical_rank = 0;
        out.conditioning = std::numeric_limits<double>::infinity();
        out.status = CertificateStatus::Fail;
        return out;
    }

    int rank = 0;
    double sigma_min_pos = sigma_max;
    for (double s : singular_values) {
        if (s / sigma_max > tau_rank) {
            ++rank;
            sigma_min_pos = std::min(sigma_min_pos, s);
        }
    }
    out.numerical_rank = rank;
    out.conditioning = sigma_max / sigma_min_pos;

    // rank==9 is a numerical diagnosis, not automatic physical closure.
    if (rank == 9) {
        out.status = CertificateStatus::Pass;
    } else if (rank >= 0) {
        out.status = CertificateStatus::Fail;
    } else {
        out.status = CertificateStatus::Indeterminate;
    }
    return out;
}

} // namespace sst
