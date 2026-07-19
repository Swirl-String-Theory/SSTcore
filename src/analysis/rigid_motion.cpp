#include "analysis/rigid_motion.h"

#include "analysis/intrinsic_frame.h"

#include <algorithm>
#include <cmath>
#include <vector>

namespace sst {
namespace analysis {
namespace {

void solve3(double m[9], double b[3], double x[3]) {
    double a[9];
    for (int i = 0; i < 9; ++i) a[i] = m[i];
    for (int i = 0; i < 3; ++i) x[i] = b[i];
    for (int k = 0; k < 3; ++k) {
        int p = k;
        for (int i = k + 1; i < 3; ++i) {
            if (std::abs(a[3 * i + k]) > std::abs(a[3 * p + k])) p = i;
        }
        if (std::abs(a[3 * p + k]) < 1e-30) {
            x[0] = x[1] = x[2] = 0.0;
            return;
        }
        if (p != k) {
            for (int j = k; j < 3; ++j) {
                const double t = a[3 * k + j];
                a[3 * k + j] = a[3 * p + j];
                a[3 * p + j] = t;
            }
            const double t = x[k];
            x[k] = x[p];
            x[p] = t;
        }
        const double d = a[3 * k + k];
        for (int j = k; j < 3; ++j) a[3 * k + j] /= d;
        x[k] /= d;
        for (int i = 0; i < 3; ++i) {
            if (i == k) continue;
            const double f = a[3 * i + k];
            for (int j = k; j < 3; ++j) a[3 * i + j] -= f * a[3 * k + j];
            x[i] -= f * x[k];
        }
    }
}

}  // namespace

RigidMotionResult RigidMotion::fit(
    const std::vector<Vec3>& points,
    const std::vector<Vec3>& velocity,
    const std::vector<double>* weights) {
    RigidMotionResult out;
    const std::size_t n = std::min(points.size(), velocity.size());
    if (n == 0) return out;

    out.translation_field.assign(n, Vec3{{0, 0, 0}});
    out.rotation_field.assign(n, Vec3{{0, 0, 0}});
    out.deformation_field.assign(n, Vec3{{0, 0, 0}});

    const Vec3 c = IntrinsicFrame::weighted_centroid(points, weights);
    out.centroid = c;

    double W = 0.0, ux = 0, uy = 0, uz = 0;
    for (std::size_t k = 0; k < n; ++k) {
        const double w = (weights && weights->size() >= n) ? (*weights)[k] : 1.0;
        W += w;
        ux += w * velocity[k][0];
        uy += w * velocity[k][1];
        uz += w * velocity[k][2];
    }
    W = std::max(W, 1e-30);
    const Vec3 U{{ux / W, uy / W, uz / W}};
    out.translation = U;

    double I[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};
    double b[3] = {0, 0, 0};
    for (std::size_t k = 0; k < n; ++k) {
        const double w = (weights && weights->size() >= n) ? (*weights)[k] : 1.0;
        const double rx = points[k][0] - c[0];
        const double ry = points[k][1] - c[1];
        const double rz = points[k][2] - c[2];
        const double vx = velocity[k][0] - U[0];
        const double vy = velocity[k][1] - U[1];
        const double vz = velocity[k][2] - U[2];
        const double r2 = rx * rx + ry * ry + rz * rz;
        I[0] += w * (r2 - rx * rx);
        I[1] -= w * rx * ry;
        I[2] -= w * rx * rz;
        I[3] -= w * ry * rx;
        I[4] += w * (r2 - ry * ry);
        I[5] -= w * ry * rz;
        I[6] -= w * rz * rx;
        I[7] -= w * rz * ry;
        I[8] += w * (r2 - rz * rz);
        b[0] += w * (ry * vz - rz * vy);
        b[1] += w * (rz * vx - rx * vz);
        b[2] += w * (rx * vy - ry * vx);
    }

    double Om[3];
    solve3(I, b, Om);
    out.omega = {{Om[0], Om[1], Om[2]}};

    double err = 0.0, vnorm2 = 0.0;
    for (std::size_t k = 0; k < n; ++k) {
        const double rx = points[k][0] - c[0];
        const double ry = points[k][1] - c[1];
        const double rz = points[k][2] - c[2];
        const double ox = Om[1] * rz - Om[2] * ry;
        const double oy = Om[2] * rx - Om[0] * rz;
        const double oz = Om[0] * ry - Om[1] * rx;
        out.translation_field[k] = U;
        out.rotation_field[k] = {{ox, oy, oz}};
        out.deformation_field[k] = {{
            velocity[k][0] - U[0] - ox,
            velocity[k][1] - U[1] - oy,
            velocity[k][2] - U[2] - oz
        }};
        const double ex = velocity[k][0]
            - (out.translation_field[k][0] + out.rotation_field[k][0]
               + out.deformation_field[k][0]);
        const double ey = velocity[k][1]
            - (out.translation_field[k][1] + out.rotation_field[k][1]
               + out.deformation_field[k][1]);
        const double ez = velocity[k][2]
            - (out.translation_field[k][2] + out.rotation_field[k][2]
               + out.deformation_field[k][2]);
        const double w = (weights && weights->size() >= n) ? (*weights)[k] : 1.0;
        err += w * (ex * ex + ey * ey + ez * ez);
        vnorm2 += w * (velocity[k][0] * velocity[k][0]
                       + velocity[k][1] * velocity[k][1]
                       + velocity[k][2] * velocity[k][2]);
    }

    out.reconstruction_relative_error = std::sqrt(err / std::max(vnorm2, 1e-300));
    const double rot_energy = b[0] * Om[0] + b[1] * Om[1] + b[2] * Om[2];
    out.deformation_relative_norm =
        std::sqrt(std::max(0.0, vnorm2 - rot_energy) / std::max(vnorm2, 1e-300));
    return out;
}

}  // namespace analysis
}  // namespace sst
