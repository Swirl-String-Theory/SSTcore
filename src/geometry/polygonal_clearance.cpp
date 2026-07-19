#include "geometry/polygonal_clearance.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace sst {
namespace geometry {
double segment_segment_distance2(
    const Vec3& a,
    const Vec3& b,
    const Vec3& c,
    const Vec3& d) {
    const double ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2];
    const double vx = d[0] - c[0], vy = d[1] - c[1], vz = d[2] - c[2];
    const double wx = a[0] - c[0], wy = a[1] - c[1], wz = a[2] - c[2];
    const double A = ux * ux + uy * uy + uz * uz;
    const double B = ux * vx + uy * vy + uz * vz;
    const double C = vx * vx + vy * vy + vz * vz;
    const double D = ux * wx + uy * wy + uz * wz;
    const double E = vx * wx + vy * wy + vz * wz;
    const double den = A * C - B * B;
    double sN, sD = den, tN, tD = den;
    if (den < 1e-30) {
        sN = 0.0;
        sD = 1.0;
        tN = E;
        tD = C;
    } else {
        sN = B * E - C * D;
        tN = A * E - B * D;
        if (sN < 0.0) {
            sN = 0.0;
            tN = E;
            tD = C;
        } else if (sN > sD) {
            sN = sD;
            tN = E + B;
            tD = C;
        }
    }
    if (tN < 0.0) {
        tN = 0.0;
        if (-D < 0.0) sN = 0.0;
        else if (-D > A) sN = sD;
        else {
            sN = -D;
            sD = A;
        }
    } else if (tN > tD) {
        tN = tD;
        const double nD = -D + B;
        if (nD < 0.0) sN = 0.0;
        else if (nD > A) sN = sD;
        else {
            sN = nD;
            sD = A;
        }
    }
    const double sc = (std::abs(sD) < 1e-30) ? 0.0 : sN / sD;
    const double tc = (std::abs(tD) < 1e-30) ? 0.0 : tN / tD;
    const double px = wx + sc * ux - tc * vx;
    const double py = wy + sc * uy - tc * vy;
    const double pz = wz + sc * uz - tc * vz;
    return px * px + py * py + pz * pz;
}

double segment_segment_distance(
    const Vec3& a,
    const Vec3& b,
    const Vec3& c,
    const Vec3& d) {
    return std::sqrt(segment_segment_distance2(a, b, c, d));
}

double self_clearance(const std::vector<Vec3>& curve, int skip_neighbors) {
    const std::size_t n = curve.size();
    if (n < 4) return std::numeric_limits<double>::infinity();
    const int skip = std::max(2, skip_neighbors);
    double m2 = std::numeric_limits<double>::infinity();
    for (std::size_t i = 0; i < n; ++i) {
        const std::size_t i2 = (i + 1) % n;
        const Vec3& A = curve[i];
        const Vec3& B = curve[i2];
        const double mx = 0.5 * (A[0] + B[0]);
        const double my = 0.5 * (A[1] + B[1]);
        const double mz = 0.5 * (A[2] + B[2]);
        const double li = norm(diff(B, A));
        for (std::size_t j = i + 1; j < n; ++j) {
            const int dd = static_cast<int>(std::min(j - i, n - (j - i)));
            if (dd < skip) continue;
            const std::size_t j2 = (j + 1) % n;
            const Vec3& C = curve[j];
            const Vec3& D = curve[j2];
            const double nx = 0.5 * (C[0] + D[0]) - mx;
            const double ny = 0.5 * (C[1] + D[1]) - my;
            const double nz = 0.5 * (C[2] + D[2]) - mz;
            const double lj = norm(diff(D, C));
            const double bound = std::sqrt(nx * nx + ny * ny + nz * nz) - 0.5 * (li + lj);
            if (bound > 0.0 && bound * bound >= m2) continue;
            const double d2 = segment_segment_distance2(A, B, C, D);
            if (d2 < m2) m2 = d2;
        }
    }
    return std::sqrt(m2);
}

double inter_clearance(const std::vector<Vec3>& a, const std::vector<Vec3>& b) {
    if (a.size() < 2 || b.size() < 2) return std::numeric_limits<double>::infinity();
    double m2 = std::numeric_limits<double>::infinity();
    const std::size_t na = a.size(), nb = b.size();
    for (std::size_t i = 0; i < na; ++i) {
        const std::size_t i2 = (i + 1) % na;
        const Vec3& A = a[i];
        const Vec3& B = a[i2];
        const double mx = 0.5 * (A[0] + B[0]);
        const double my = 0.5 * (A[1] + B[1]);
        const double mz = 0.5 * (A[2] + B[2]);
        const double li = norm(diff(B, A));
        for (std::size_t j = 0; j < nb; ++j) {
            const std::size_t j2 = (j + 1) % nb;
            const Vec3& C = b[j];
            const Vec3& D = b[j2];
            const double nx = 0.5 * (C[0] + D[0]) - mx;
            const double ny = 0.5 * (C[1] + D[1]) - my;
            const double nz = 0.5 * (C[2] + D[2]) - mz;
            const double lj = norm(diff(D, C));
            const double bound = std::sqrt(nx * nx + ny * ny + nz * nz) - 0.5 * (li + lj);
            if (bound > 0.0 && bound * bound >= m2) continue;
            const double d2 = segment_segment_distance2(A, B, C, D);
            if (d2 < m2) m2 = d2;
        }
    }
    return std::sqrt(m2);
}

TopologyClearanceResult multi_component_clearance(
    const std::vector<std::vector<Vec3>>& curves,
    double core_radius,
    int default_skip_neighbors) {
    TopologyClearanceResult out;
    out.self_min = std::numeric_limits<double>::infinity();
    out.inter_min = std::numeric_limits<double>::infinity();
    out.clearance = std::numeric_limits<double>::infinity();

    for (const auto& curve : curves) {
        int skip = default_skip_neighbors;
        if (core_radius > 0.0 && curve.size() >= 2) {
            double L = 0.0;
            const std::size_t n = curve.size();
            for (std::size_t k = 0; k < n; ++k) {
                L += norm(diff(curve[(k + 1) % n], curve[k]));
            }
            const double lmean = L / static_cast<double>(std::max<std::size_t>(1, n));
            skip = std::max(2, static_cast<int>(std::ceil(6.0 * core_radius / std::max(lmean, 1e-12))));
        }
        out.self_min = std::min(out.self_min, self_clearance(curve, skip));
    }

    for (std::size_t i = 0; i < curves.size(); ++i) {
        for (std::size_t j = i + 1; j < curves.size(); ++j) {
            out.inter_min = std::min(out.inter_min, inter_clearance(curves[i], curves[j]));
        }
    }

    out.clearance = std::min(out.self_min, out.inter_min);
    return out;
}

}  // namespace geometry
}  // namespace sst
