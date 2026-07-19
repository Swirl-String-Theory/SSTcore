#include "geometry/periodic_spline.h"

#include <cmath>
#include <stdexcept>

namespace sst {
namespace geometry {

double PeriodicCubicSpline3D::wrap01(double u, double L) {
    if (!(L > 0.0)) return 0.0;
    u = std::fmod(u, L);
    if (u < 0.0) u += L;
    return u;
}

bool PeriodicCubicSpline3D::cyclic_solve(
    const std::vector<double>& a,
    const std::vector<double>& b,
    const std::vector<double>& c,
    double corner,
    const std::vector<double>& r,
    std::vector<double>& out) {
    const std::size_t n = r.size();
    if (n < 2) return false;
    std::vector<double> aa = a, bb = b, cc = c, rr = r;
    // Sherman-Morrison style cyclic tridiagonal (VortexLab vlCyclicSolve)
    std::vector<double> u(n, 0.0), z(n, 0.0), y(n, 0.0);
    u[0] = corner;
    u[n - 1] = corner;
    bb[0] -= corner;
    bb[n - 1] -= corner;

    // forward elimination for M y = r and M z = u
    for (std::size_t i = 1; i < n; ++i) {
        if (std::abs(bb[i - 1]) < 1e-30) return false;
        const double m = aa[i] / bb[i - 1];
        bb[i] -= m * cc[i - 1];
        rr[i] -= m * rr[i - 1];
        u[i] -= m * u[i - 1];
    }
    if (std::abs(bb[n - 1]) < 1e-30) return false;
    y[n - 1] = rr[n - 1] / bb[n - 1];
    z[n - 1] = u[n - 1] / bb[n - 1];
    for (std::size_t i = n - 1; i-- > 0;) {
        y[i] = (rr[i] - cc[i] * y[i + 1]) / bb[i];
        z[i] = (u[i] - cc[i] * z[i + 1]) / bb[i];
    }
    const double fact = (y[0] + y[n - 1]) / (1.0 + z[0] + z[n - 1]);
    out.resize(n);
    for (std::size_t i = 0; i < n; ++i) out[i] = y[i] - fact * z[i];
    return true;
}

PeriodicCubicSpline3D::PeriodicCubicSpline3D(const std::vector<Vec3>& points) {
    n_ = points.size();
    if (n_ < 4) throw std::invalid_argument("PeriodicCubicSpline3D requires >= 4 points");
    points_ = points;
    h_.assign(n_, 0.0);
    s_.assign(n_ + 1, 0.0);
    for (std::size_t i = 0; i < n_; ++i) {
        const Vec3 d = diff(points_[(i + 1) % n_], points_[i]);
        h_[i] = std::max(1e-12, norm(d));
        s_[i + 1] = s_[i] + h_[i];
    }
    L_ = s_[n_];

    std::vector<double> a(n_, 0.0), b(n_, 0.0), c(n_, 0.0);
    for (std::size_t i = 0; i < n_; ++i) {
        const double hm = h_[(i + n_ - 1) % n_];
        const double hp = h_[i];
        a[i] = (i == 0) ? 0.0 : hm;
        b[i] = 2.0 * (hm + hp);
        c[i] = (i + 1 < n_) ? hp : 0.0;
    }

    second_.assign(3, {});
    for (int d = 0; d < 3; ++d) {
        std::vector<double> r(n_, 0.0);
        for (std::size_t i = 0; i < n_; ++i) {
            const std::size_t im = (i + n_ - 1) % n_;
            const std::size_t ip = (i + 1) % n_;
            r[i] = 6.0 * ((points_[ip][static_cast<std::size_t>(d)] - points_[i][static_cast<std::size_t>(d)]) / h_[i]
                        - (points_[i][static_cast<std::size_t>(d)] - points_[im][static_cast<std::size_t>(d)]) / h_[im]);
        }
        if (!cyclic_solve(a, b, c, h_[n_ - 1], r, second_[static_cast<std::size_t>(d)])) {
            throw std::runtime_error("PeriodicCubicSpline3D singular cyclic solve");
        }
    }
}

SplineEval PeriodicCubicSpline3D::eval(double u) const {
    SplineEval ev;
    u = wrap01(u, L_);
    ev.u = u;
    std::size_t lo = 0, hi = n_;
    while (lo + 1 < hi) {
        const std::size_t m = (lo + hi) >> 1;
        if (s_[m] <= u) lo = m;
        else hi = m;
    }
    const std::size_t i = std::min(n_ - 1, lo);
    const std::size_t j = (i + 1) % n_;
    const double hh = h_[i];
    const double A = (s_[i + 1] - u) / hh;
    const double B = (u - s_[i]) / hh;
    for (int d = 0; d < 3; ++d) {
        const double yi = points_[i][static_cast<std::size_t>(d)];
        const double yj = points_[j][static_cast<std::size_t>(d)];
        const double Mi = second_[static_cast<std::size_t>(d)][i];
        const double Mj = second_[static_cast<std::size_t>(d)][j];
        ev.p[static_cast<std::size_t>(d)] =
            A * yi + B * yj + ((A * A * A - A) * Mi + (B * B * B - B) * Mj) * hh * hh / 6.0;
        ev.d1[static_cast<std::size_t>(d)] =
            (yj - yi) / hh + hh * (-(3 * A * A - 1) * Mi + (3 * B * B - 1) * Mj) / 6.0;
        ev.d2[static_cast<std::size_t>(d)] = A * Mi + B * Mj;
    }
    return ev;
}

}  // namespace geometry
}  // namespace sst
