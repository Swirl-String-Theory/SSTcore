#include "geometry/periodic_spline.h"

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <vector>

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

namespace {

// 7-point Gauss / 15-point Kronrod on [-1,1] (Piessens et al. / QUADPACK).
constexpr double kKgNodes[8] = {
    0.0,
    0.2077844261475285,
    0.4058451513773972,
    0.5860872354673711,
    0.7415311855993945,
    0.8648644233597691,
    0.9491079123427585,
    0.9914553711208126,
};
constexpr double kKronrodW[8] = {
    0.2094821410847278,
    0.2044329400752989,
    0.1903505780647854,
    0.1690047266392679,
    0.1406532597155259,
    0.1047900103222502,
    0.06309209262997855,
    0.02293532201052922,
};
// Gauss-7 weights at Kronrod nodes 0, ±x2, ±x4, ±x6 (indices 0,2,4,6).
constexpr double kGaussW[4] = {
    0.4179591836734694,
    0.3818300505051189,
    0.2797053914892767,
    0.1294849661688697,
};

struct QuadPiece {
    double a = 0.0;
    double b = 0.0;
    double gk = 0.0;
    double err = 0.0;
};

double speed_at(const PeriodicCubicSpline3D& sp, double u) {
    return norm(sp.eval(u).d1);
}

QuadPiece gk15_speed(const PeriodicCubicSpline3D& sp, double a, double b) {
    const double mid = 0.5 * (a + b);
    const double half = 0.5 * (b - a);
    double f[8];
    f[0] = speed_at(sp, mid);
    for (int i = 1; i < 8; ++i) {
        f[i] = speed_at(sp, mid + half * kKgNodes[i])
             + speed_at(sp, mid - half * kKgNodes[i]);
    }
    double kronrod = kKronrodW[0] * f[0];
    for (int i = 1; i < 8; ++i) kronrod += kKronrodW[i] * f[i];
    double gauss = kGaussW[0] * f[0];
    gauss += kGaussW[1] * f[2];
    gauss += kGaussW[2] * f[4];
    gauss += kGaussW[3] * f[6];
    kronrod *= half;
    gauss *= half;
    QuadPiece q;
    q.a = a;
    q.b = b;
    q.gk = kronrod;
    q.err = std::abs(kronrod - gauss);
    return q;
}

}  // namespace

SplineLengthResult PeriodicCubicSpline3D::integrated_arclength(
    double abs_tol,
    double rel_tol) const {
    SplineLengthResult out;
    if (n_ < 4 || !(L_ > 0.0)) {
        out.converged = false;
        return out;
    }
    if (!(abs_tol > 0.0)) abs_tol = 1e-10;
    if (!(rel_tol > 0.0)) rel_tol = 1e-10;

    constexpr std::size_t kMaxDepth = 64;
    constexpr std::size_t kMaxIntervals = 200000;
    std::vector<QuadPiece> stack;
    stack.reserve(n_ * 4);
    for (std::size_t i = 0; i < n_; ++i) {
        stack.push_back(gk15_speed(*this, s_[i], s_[i + 1]));
    }

    double total = 0.0;
    double total_err = 0.0;
    std::size_t finished = 0;
    std::size_t splits = 0;
    bool converged = true;

    while (!stack.empty()) {
        if (finished + stack.size() > kMaxIntervals || splits > kMaxDepth * n_) {
            for (const QuadPiece& q : stack) {
                total += q.gk;
                total_err += q.err;
                ++finished;
            }
            converged = false;
            break;
        }
        QuadPiece q = stack.back();
        stack.pop_back();
        const double local_tol =
            abs_tol * (q.b - q.a) / L_ + rel_tol * std::max(std::abs(q.gk), 1e-30);
        if (q.err <= local_tol || (q.b - q.a) < 1e-15 * L_) {
            total += q.gk;
            total_err += q.err;
            ++finished;
            continue;
        }
        const double mid = 0.5 * (q.a + q.b);
        stack.push_back(gk15_speed(*this, q.a, mid));
        stack.push_back(gk15_speed(*this, mid, q.b));
        ++splits;
    }

    out.length = total;
    out.absolute_error_estimate = total_err;
    out.interval_count = finished;
    out.converged =
        converged && total_err <= abs_tol + rel_tol * std::max(std::abs(total), 1e-30);
    return out;
}

}  // namespace geometry
}  // namespace sst
