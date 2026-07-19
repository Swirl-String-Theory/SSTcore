#include "analysis/intrinsic_frame.h"

#include <algorithm>
#include <cmath>
#include <vector>

namespace sst {
namespace analysis {
namespace {

Vec3 vnorm(const Vec3& a) {
    const double n = norm(a);
    if (n > 1e-30) return {a[0] / n, a[1] / n, a[2] / n};
    return {{0, 0, 1}};
}

Vec3 deterministic_axis_sign(const Vec3& v) {
    int j = 0;
    if (std::abs(v[1]) > std::abs(v[j])) j = 1;
    if (std::abs(v[2]) > std::abs(v[j])) j = 2;
    if (v[static_cast<std::size_t>(j)] < 0.0) {
        return {{-v[0], -v[1], -v[2]}};
    }
    return v;
}

}  // namespace

Vec3 IntrinsicFrame::weighted_centroid(
    const std::vector<Vec3>& points,
    const std::vector<double>* weights) {
    double x = 0, y = 0, z = 0, w = 0;
    for (std::size_t k = 0; k < points.size(); ++k) {
        const double q = (weights && weights->size() == points.size())
            ? (*weights)[k]
            : 1.0;
        x += q * points[k][0];
        y += q * points[k][1];
        z += q * points[k][2];
        w += q;
    }
    w = std::max(w, 1e-30);
    return {{x / w, y / w, z / w}};
}

void IntrinsicFrame::symmetric_eigen3(
    const double m[9],
    double eigenvalues[3],
    double eigenvectors[9]) {
    double a[9];
    for (int i = 0; i < 9; ++i) a[i] = m[i];
    double V[9] = {1, 0, 0, 0, 1, 0, 0, 0, 1};

    for (int it = 0; it < 48; ++it) {
        int p = 0, q = 1;
        double maxv = std::abs(a[1]);
        const int pairs[2][2] = {{0, 2}, {1, 2}};
        for (const auto& pr : pairs) {
            const double x = std::abs(a[3 * pr[0] + pr[1]]);
            if (x > maxv) {
                maxv = x;
                p = pr[0];
                q = pr[1];
            }
        }
        if (maxv < 1e-14 * std::max({1.0, std::abs(a[0]), std::abs(a[4]), std::abs(a[8])})) {
            break;
        }
        const double app = a[3 * p + p];
        const double aqq = a[3 * q + q];
        const double apq = a[3 * p + q];
        const double phi = 0.5 * std::atan2(2.0 * apq, aqq - app);
        const double c = std::cos(phi);
        const double sn = std::sin(phi);
        for (int k = 0; k < 3; ++k) {
            const double aik = a[3 * p + k];
            const double aqk = a[3 * q + k];
            a[3 * p + k] = c * aik - sn * aqk;
            a[3 * q + k] = sn * aik + c * aqk;
        }
        for (int k = 0; k < 3; ++k) {
            const double akp = a[3 * k + p];
            const double akq = a[3 * k + q];
            a[3 * k + p] = c * akp - sn * akq;
            a[3 * k + q] = sn * akp + c * akq;
        }
        a[3 * p + q] = a[3 * q + p] = 0.0;
        for (int k = 0; k < 3; ++k) {
            const double vip = V[3 * k + p];
            const double viq = V[3 * k + q];
            V[3 * k + p] = c * vip - sn * viq;
            V[3 * k + q] = sn * vip + c * viq;
        }
    }

    struct Eig {
        double value;
        Vec3 vector;
    };
    Eig eig[3];
    for (int j = 0; j < 3; ++j) {
        eig[j].value = a[3 * j + j];
        eig[j].vector = deterministic_axis_sign(
            vnorm(Vec3{{V[j], V[3 + j], V[6 + j]}}));
    }
    std::sort(eig, eig + 3, [](const Eig& x, const Eig& y) { return x.value < y.value; });
    for (int j = 0; j < 3; ++j) {
        eigenvalues[j] = eig[j].value;
        eigenvectors[3 * j + 0] = eig[j].vector[0];
        eigenvectors[3 * j + 1] = eig[j].vector[1];
        eigenvectors[3 * j + 2] = eig[j].vector[2];
    }
}

IntrinsicFrameResult IntrinsicFrame::compute(
    const std::vector<Vec3>& points,
    const std::vector<double>* weights) {
    IntrinsicFrameResult out;
    if (points.empty()) return out;

    const Vec3 c = weighted_centroid(points, weights);
    out.centroid = c;
    double W = 0.0;
    double C[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};
    for (std::size_t k = 0; k < points.size(); ++k) {
        const double q = (weights && weights->size() == points.size())
            ? (*weights)[k]
            : 1.0;
        const double x = points[k][0] - c[0];
        const double y = points[k][1] - c[1];
        const double z = points[k][2] - c[2];
        W += q;
        C[0] += q * x * x;
        C[1] += q * x * y;
        C[2] += q * x * z;
        C[3] += q * y * x;
        C[4] += q * y * y;
        C[5] += q * y * z;
        C[6] += q * z * x;
        C[7] += q * z * y;
        C[8] += q * z * z;
    }
    W = std::max(W, 1e-30);
    for (double& v : C) v /= W;

    double evals[3];
    double evecs[9];
    symmetric_eigen3(C, evals, evecs);
    // evecs rows are eigenvectors sorted ascending: row0 = smallest
    Vec3 ez{{evecs[0], evecs[1], evecs[2]}};
    Vec3 ex{{evecs[6], evecs[7], evecs[8]}};  // largest
    // Gram-Schmidt / right-handed
    const double proj = dot(ex, ez);
    ex = vnorm(Vec3{{ex[0] - proj * ez[0], ex[1] - proj * ez[1], ex[2] - proj * ez[2]}});
    Vec3 ey = vnorm(cross(ez, ex));
    ex = vnorm(cross(ey, ez));

    out.axis_x = ex;
    out.axis_y = ey;
    out.axis_z = ez;
    out.eigenvalues = {{evals[0], evals[1], evals[2]}};
    return out;
}

}  // namespace analysis
}  // namespace sst
