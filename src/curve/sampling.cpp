#include "curve/sampling.h"

#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace sst {
namespace curve {

double CurveSampling::closed_length(const std::vector<Vec3>& points) {
    const std::size_t m = points.size();
    if (m < 2) return 0.0;
    double L = 0.0;
    for (std::size_t i = 0; i < m; ++i) {
        const Vec3& a = points[i];
        const Vec3& b = points[(i + 1) % m];
        L += norm(diff(b, a));
    }
    return L;
}

std::vector<Vec3> CurveSampling::resample_closed_arclength(
    const std::vector<Vec3>& points, std::size_t n) {
    if (n == 0) return {};
    const std::size_t m = points.size();
    std::vector<Vec3> out(n, Vec3{{0, 0, 0}});
    if (m < 2) return out;

    std::vector<double> cum(m + 1, 0.0);
    for (std::size_t i = 0; i < m; ++i) {
        const Vec3& a = points[i];
        const Vec3& b = points[(i + 1) % m];
        cum[i + 1] = cum[i] + norm(diff(b, a));
    }
    const double L = cum[m];
    if (!(L > 0.0)) return out;

    std::size_t seg = 0;
    for (std::size_t k = 0; k < n; ++k) {
        const double target = L * static_cast<double>(k) / static_cast<double>(n);
        while (seg + 1 < m && cum[seg + 1] < target) ++seg;
        const std::size_t j = (seg + 1) % m;
        const double den = std::max(1e-30, cum[seg + 1] - cum[seg]);
        const double u = (target - cum[seg]) / den;
        out[k] = {
            points[seg][0] + u * (points[j][0] - points[seg][0]),
            points[seg][1] + u * (points[j][1] - points[seg][1]),
            points[seg][2] + u * (points[j][2] - points[seg][2]),
        };
    }
    return out;
}

std::vector<Vec3> CurveSampling::reverse_traversal(const std::vector<Vec3>& points) {
    std::vector<Vec3> out = points;
    std::reverse(out.begin(), out.end());
    return out;
}

std::vector<Vec3> CurveSampling::sample_fourier_parametric(
    const std::vector<FourierTerm>& coeffs, std::size_t n) {
    std::vector<Vec3> out(n);
    const double two_pi = 6.28318530717958647692;
    for (std::size_t k = 0; k < n; ++k) {
        const double t = two_pi * static_cast<double>(k) / static_cast<double>(n);
        Vec3 p{{0, 0, 0}};
        for (const auto& c : coeffs) {
            const double ct = std::cos(c.I * t);
            const double st = std::sin(c.I * t);
            for (int d = 0; d < 3; ++d) {
                p[static_cast<std::size_t>(d)] += ct * c.A[static_cast<std::size_t>(d)]
                                                 + st * c.B[static_cast<std::size_t>(d)];
            }
        }
        out[k] = p;
    }
    return out;
}

std::vector<Vec3> CurveSampling::sample_fourier(
    const std::vector<FourierTerm>& coeffs, std::size_t n, bool arclength_uniform) {
    if (!arclength_uniform) return sample_fourier_parametric(coeffs, n);
    double imax = 1.0;
    for (const auto& c : coeffs) imax = std::max(imax, std::abs(c.I));
    const std::size_t n_ref = std::max<std::size_t>(4096, static_cast<std::size_t>(16 * imax));
    return resample_closed_arclength(sample_fourier_parametric(coeffs, n_ref), n);
}

std::vector<Vec3> CurveSampling::sample_circle(std::size_t n, double R, double z) {
    std::vector<Vec3> out(n);
    const double two_pi = 6.28318530717958647692;
    for (std::size_t k = 0; k < n; ++k) {
        const double t = two_pi * static_cast<double>(k) / static_cast<double>(n);
        out[k] = {R * std::cos(t), R * std::sin(t), z};
    }
    return out;
}

}  // namespace curve
}  // namespace sst
