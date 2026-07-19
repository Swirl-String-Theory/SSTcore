#include "knot/polygonal_gauss.h"

#include <cmath>

namespace sst {
namespace knot {
namespace {

inline double clampf(double v, double lo, double hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

}  // namespace

double PolygonalGaussInvariants::segment_pair_omega(
    const Vec3& p1, const Vec3& p2, const Vec3& p3, const Vec3& p4) {
    const Vec3 r13 = diff(p3, p1);
    const Vec3 r14 = diff(p4, p1);
    const Vec3 r23 = diff(p3, p2);
    const Vec3 r24 = diff(p4, p2);

    Vec3 n1 = cross(r13, r14);
    Vec3 n2 = cross(r14, r24);
    Vec3 n3 = cross(r24, r23);
    Vec3 n4 = cross(r23, r13);

    const double m1 = dot(n1, n1), m2 = dot(n2, n2), m3 = dot(n3, n3), m4 = dot(n4, n4);
    if (m1 < 1e-60 || m2 < 1e-60 || m3 < 1e-60 || m4 < 1e-60) return 0.0;

    const double s1 = 1.0 / std::sqrt(m1);
    const double s2 = 1.0 / std::sqrt(m2);
    const double s3 = 1.0 / std::sqrt(m3);
    const double s4 = 1.0 / std::sqrt(m4);
    n1 = {n1[0] * s1, n1[1] * s1, n1[2] * s1};
    n2 = {n2[0] * s2, n2[1] * s2, n2[2] * s2};
    n3 = {n3[0] * s3, n3[1] * s3, n3[2] * s3};
    n4 = {n4[0] * s4, n4[1] * s4, n4[2] * s4};

    double om = std::asin(clampf(dot(n1, n2), -1.0, 1.0))
              + std::asin(clampf(dot(n2, n3), -1.0, 1.0))
              + std::asin(clampf(dot(n3, n4), -1.0, 1.0))
              + std::asin(clampf(dot(n4, n1), -1.0, 1.0));

    const Vec3 r12 = diff(p2, p1);
    const Vec3 r34 = diff(p4, p3);
    const Vec3 c = cross(r34, r12);
    if (dot(c, r13) < 0.0) om = -om;
    return om;
}

PolygonalGaussResult PolygonalGaussInvariants::evaluate(
    const std::vector<Vec3>& curve_a,
    const std::vector<Vec3>& curve_b,
    bool same_curve) {
    PolygonalGaussResult out;
    const std::size_t N1 = curve_a.size();
    const std::size_t N2 = curve_b.size();
    if (N1 < 3 || N2 < 3) return out;

    double S = 0.0, A = 0.0;
    if (same_curve) {
        for (std::size_t i = 0; i < N1; ++i) {
            const std::size_t i2 = (i + 1) % N1;
            for (std::size_t j = i + 2; j < N1; ++j) {
                if (i == 0 && j == N1 - 1) continue;
                const double om = segment_pair_omega(
                    curve_a[i], curve_a[i2], curve_a[j], curve_a[(j + 1) % N1]);
                S += om;
                A += std::abs(om);
            }
        }
        out.signed_integral = S / (2.0 * 3.14159265358979323846);
        out.absolute_integral = A / (2.0 * 3.14159265358979323846);
    } else {
        for (std::size_t i = 0; i < N1; ++i) {
            const std::size_t i2 = (i + 1) % N1;
            for (std::size_t j = 0; j < N2; ++j) {
                const double om = segment_pair_omega(
                    curve_a[i], curve_a[i2], curve_b[j], curve_b[(j + 1) % N2]);
                S += om;
                A += std::abs(om);
            }
        }
        out.signed_integral = S / (4.0 * 3.14159265358979323846);
        out.absolute_integral = A / (4.0 * 3.14159265358979323846);
    }
    out.linking_integer_audit = static_cast<int>(std::llround(out.signed_integral));
    return out;
}

PolygonalGaussResult PolygonalGaussInvariants::writhe(const std::vector<Vec3>& curve) {
    return evaluate(curve, curve, true);
}

PolygonalGaussResult PolygonalGaussInvariants::linking(
    const std::vector<Vec3>& curve_a, const std::vector<Vec3>& curve_b) {
    return evaluate(curve_a, curve_b, false);
}

}  // namespace knot
}  // namespace sst
