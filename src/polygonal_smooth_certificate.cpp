#include "polygonal_smooth_certificate.h"
#include "sst_sha256.h"

#include "sst/tube/geometry_core.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <limits>
#include <vector>

namespace sst {
namespace {

void append_le_f64(std::vector<std::uint8_t>& out, double c) {
    std::uint64_t u = 0;
    std::memcpy(&u, &c, sizeof(u));
    for (int i = 0; i < 8; ++i) {
        out.push_back(static_cast<std::uint8_t>((u >> (8 * i)) & 0xffu));
    }
}

std::string points_sha256_hex(const std::vector<Vec3>& pts) {
    std::vector<std::uint8_t> bytes;
    bytes.reserve(pts.size() * 24);
    for (const auto& p : pts) {
        for (std::size_t k = 0; k < 3; ++k) append_le_f64(bytes, p[k]);
    }
    return sha256_hex(bytes);
}

double dist2(const Vec3& a, const Vec3& b) {
    const double dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
    return dx * dx + dy * dy + dz * dz;
}

double point_polyline_distance(const Vec3& p, const std::vector<Vec3>& poly) {
    double best = std::numeric_limits<double>::infinity();
    const std::size_t n = poly.size();
    for (std::size_t i = 0; i < n; ++i) {
        const Vec3& a = poly[i];
        const Vec3& b = poly[(i + 1) % n];
        const double abx = b[0] - a[0], aby = b[1] - a[1], abz = b[2] - a[2];
        const double apx = p[0] - a[0], apy = p[1] - a[1], apz = p[2] - a[2];
        const double ab2 = abx * abx + aby * aby + abz * abz;
        double t = (ab2 > 0.0) ? ((apx * abx + apy * aby + apz * abz) / ab2) : 0.0;
        t = std::clamp(t, 0.0, 1.0);
        const Vec3 q{a[0] + t * abx, a[1] + t * aby, a[2] + t * abz};
        best = std::min(best, std::sqrt(dist2(p, q)));
    }
    return best;
}

double directed_hausdorff(const std::vector<Vec3>& a, const std::vector<Vec3>& b) {
    double m = 0.0;
    for (const auto& p : a) m = std::max(m, point_polyline_distance(p, b));
    return m;
}

Vec3 unit_edge(const Vec3& a, const Vec3& b) {
    const double dx = b[0] - a[0], dy = b[1] - a[1], dz = b[2] - a[2];
    const double n = std::sqrt(dx * dx + dy * dy + dz * dz);
    if (!(n > 0.0)) return Vec3{0.0, 0.0, 0.0};
    return Vec3{dx / n, dy / n, dz / n};
}

double max_tangent_error(const std::vector<Vec3>& poly, const std::vector<Vec3>& smooth) {
    const std::size_t n = std::min(poly.size(), smooth.size());
    if (n < 2) return std::numeric_limits<double>::infinity();
    double err = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        const auto tp = unit_edge(poly[i], poly[(i + 1) % poly.size()]);
        const auto ts = unit_edge(smooth[i % smooth.size()], smooth[(i + 1) % smooth.size()]);
        const double dx = tp[0] - ts[0], dy = tp[1] - ts[1], dz = tp[2] - ts[2];
        err = std::max(err, std::sqrt(dx * dx + dy * dy + dz * dz));
    }
    return err;
}

} // namespace

std::string PolygonalSmoothCertificateAPI::fingerprint_points(const std::vector<Vec3>& pts) {
    return points_sha256_hex(pts);
}

PolygonalSmoothCertificate PolygonalSmoothCertificateAPI::evaluate(
    const std::vector<Vec3>& polygon_pts,
    const std::vector<Vec3>& smooth_pts,
    double tube_radius,
    double hausdorff_tol,
    double tangent_tol,
    double curvature_tol) {
    PolygonalSmoothCertificate out;
    out.polygon_hash = fingerprint_points(polygon_pts);
    out.smooth_hash = fingerprint_points(smooth_pts);

    if (polygon_pts.size() < 3 || smooth_pts.size() < 3 || !(tube_radius > 0.0) ||
        !(hausdorff_tol >= 0.0) || !(tangent_tol >= 0.0) || !(curvature_tol >= 0.0)) {
        out.status = CertificateStatus::Indeterminate;
        return out;
    }

    try {
        const auto poly_m = ResolvedTubeGeometry::analyze(polygon_pts, 2, 1e-3, 1e-3);
        const auto sm_m = ResolvedTubeGeometry::analyze(smooth_pts, 2, 1e-3, 1e-3);

        out.hausdorff_bound = std::max(directed_hausdorff(polygon_pts, smooth_pts),
                                       directed_hausdorff(smooth_pts, polygon_pts));
        out.tangent_error = max_tangent_error(polygon_pts, smooth_pts);
        const double kappa_p = (poly_m.minrad > 0.0) ? (1.0 / poly_m.minrad) : std::numeric_limits<double>::infinity();
        const double kappa_s = (sm_m.minrad > 0.0) ? (1.0 / sm_m.minrad) : std::numeric_limits<double>::infinity();
        out.curvature_error = std::abs(kappa_p - kappa_s);
        out.thickness_lower_bound = std::min(poly_m.minrad, sm_m.minrad);

        if (!std::isfinite(out.hausdorff_bound) || !std::isfinite(out.tangent_error) ||
            !std::isfinite(out.curvature_error) || !std::isfinite(out.thickness_lower_bound)) {
            out.status = CertificateStatus::Indeterminate;
            return out;
        }

        // Conservative thickness claim: lower bound must exceed tube radius.
        const bool thick_ok = out.thickness_lower_bound > tube_radius;
        const bool geom_ok = out.hausdorff_bound <= hausdorff_tol &&
                             out.tangent_error <= tangent_tol &&
                             out.curvature_error <= curvature_tol;
        // Diagnostic-only: sampled Hausdorff/tangent/curvature do not prove reach/isotopy.
        // Never return Pass here (audit H-004); reserve Pass for future rigorous guards.
        if (thick_ok && geom_ok) {
            out.status = CertificateStatus::Indeterminate;
        } else {
            out.status = CertificateStatus::Fail;
        }
    } catch (const std::exception&) {
        out.status = CertificateStatus::Indeterminate;
    }
    return out;
}

} // namespace sst
