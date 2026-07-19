#include "filament/velocity_solver.h"

#include "sst/types.h"

#include <cmath>
#include <vector>

namespace sst {
namespace filament {
namespace {

Vec3 add3(const Vec3& a, const Vec3& b) {
    return {a[0] + b[0], a[1] + b[1], a[2] + b[2]};
}

Vec3 scale3(const Vec3& a, double s) {
    return {a[0] * s, a[1] * s, a[2] * s};
}

}  // namespace

VelocityFieldResult FilamentVelocitySolver::evaluate(
    const FilamentSystemState& filaments,
    const VelocityOptions& options) {
    VelocityFieldResult out;
    const std::size_t nf = filaments.filaments.size();
    out.velocity.resize(nf);
    out.maximum_speed = 0.0;

    // Midpoint / dl caches
    std::vector<std::vector<Vec3>> mids(nf), dls(nf);
    for (std::size_t f = 0; f < nf; ++f) {
        const auto& fil = filaments.filaments[f];
        const std::size_t N = fil.points.size();
        mids[f].resize(N);
        dls[f].resize(N);
        out.velocity[f].assign(N, Vec3{{0, 0, 0}});
        for (std::size_t k = 0; k < N; ++k) {
            const std::size_t k2 = (k + 1) % N;
            dls[f][k] = diff(fil.points[k2], fil.points[k]);
            mids[f][k] = scale3(add3(fil.points[k], fil.points[k2]), 0.5);
        }
    }

    const double a = std::max(options.core_radius, 1e-30);
    const double eD = std::exp(options.core_delta);
    const double a_sim2 = options.a_sim * options.a_sim;
    const bool lia_only = options.lia_only;
    // include_external / include_mutual_friction ignored in v1

    double umax2 = 0.0;
    for (std::size_t ft = 0; ft < nf; ++ft) {
        const auto& target = filaments.filaments[ft];
        const std::size_t N = target.points.size();
        if (target.ghost) {
            // zero velocity already assigned
            continue;
        }
        const double pref = target.circulation / (4.0 * 3.14159265358979323846);
        for (std::size_t i = 0; i < N; ++i) {
            const std::size_t im = (i + N - 1) % N;
            const std::size_t ip = i;
            const Vec3& p = target.points[i];
            const Vec3& dm = dls[ft][im];
            const Vec3& dp = dls[ft][ip];
            const double lm = std::max(norm(dm), 1e-30);
            const double lp = std::max(norm(dp), 1e-30);
            const Vec3 cxv = cross(dm, dp);

            const double lf = pref
                * (std::log(2.0 * std::sqrt(lm * lp) / (eD * a)) + options.lia_constant)
                * 2.0 / (lm * lp * (lm + lp));
            Vec3 u = scale3(cxv, lf);

            if (!lia_only) {
                for (std::size_t fs = 0; fs < nf; ++fs) {
                    const auto& source = filaments.filaments[fs];
                    if (source.ghost || !source.source) continue;
                    const std::size_t M = source.points.size();
                    const double pref_source = source.circulation / (4.0 * 3.14159265358979323846);
                    const double reg = (fs == ft) ? 0.0 : a_sim2;
                    for (std::size_t j = 0; j < M; ++j) {
                        if (fs == ft && (j == im || j == ip)) continue;
                        const Vec3 r = diff(p, mids[fs][j]);
                        const double r2 = r[0] * r[0] + r[1] * r[1] + r[2] * r[2] + reg;
                        const double inv = pref_source / (r2 * std::sqrt(r2));
                        const Vec3& dl = dls[fs][j];
                        u[0] += (dl[1] * r[2] - dl[2] * r[1]) * inv;
                        u[1] += (dl[2] * r[0] - dl[0] * r[2]) * inv;
                        u[2] += (dl[0] * r[1] - dl[1] * r[0]) * inv;
                    }
                }
            }

            out.velocity[ft][i] = u;
            const double um = u[0] * u[0] + u[1] * u[1] + u[2] * u[2];
            if (um > umax2) umax2 = um;
        }
    }
    out.maximum_speed = std::sqrt(umax2);
    return out;
}

}  // namespace filament
}  // namespace sst
