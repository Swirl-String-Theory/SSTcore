#include "filament/integrator.h"

#include "filament/velocity_solver.h"
#include "sst/types.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>

namespace sst {
namespace filament {
namespace {

Vec3 add_scaled(const Vec3& a, const Vec3& b, double s) {
    return {a[0] + s * b[0], a[1] + s * b[1], a[2] + s * b[2]};
}

void apply_velocity(
    FilamentSystemState& state,
    const VelocityFieldResult& vel,
    double scale) {
    for (std::size_t f = 0; f < state.filaments.size(); ++f) {
        auto& fil = state.filaments[f];
        if (fil.ghost || !fil.dynamic) continue;
        for (std::size_t i = 0; i < fil.points.size(); ++i) {
            fil.points[i] = add_scaled(fil.points[i], vel.velocity[f][i], scale);
        }
    }
}

FilamentSystemState blend_stages(
    const FilamentSystemState& y0,
    const VelocityFieldResult& k1,
    const VelocityFieldResult& k2,
    const VelocityFieldResult& k3,
    const VelocityFieldResult& k4,
    double dt) {
    FilamentSystemState out = y0;
    for (std::size_t f = 0; f < out.filaments.size(); ++f) {
        auto& fil = out.filaments[f];
        if (fil.ghost || !fil.dynamic) continue;
        for (std::size_t i = 0; i < fil.points.size(); ++i) {
            const Vec3& a = k1.velocity[f][i];
            const Vec3& b = k2.velocity[f][i];
            const Vec3& c = k3.velocity[f][i];
            const Vec3& d = k4.velocity[f][i];
            fil.points[i][0] += (dt / 6.0) * (a[0] + 2.0 * b[0] + 2.0 * c[0] + d[0]);
            fil.points[i][1] += (dt / 6.0) * (a[1] + 2.0 * b[1] + 2.0 * c[1] + d[1]);
            fil.points[i][2] += (dt / 6.0) * (a[2] + 2.0 * b[2] + 2.0 * c[2] + d[2]);
        }
    }
    return out;
}

double min_segment_length(const FilamentSystemState& state) {
    double m = std::numeric_limits<double>::infinity();
    for (const auto& fil : state.filaments) {
        if (fil.ghost || !fil.dynamic) continue;
        const std::size_t N = fil.points.size();
        for (std::size_t k = 0; k < N; ++k) {
            m = std::min(m, norm(diff(fil.points[(k + 1) % N], fil.points[k])));
        }
    }
    return m;
}

}  // namespace

IntegratorStepResult FilamentIntegrator::rk4_step(
    const FilamentSystemState& state,
    double dt,
    const VelocityOptions& options) {
    IntegratorStepResult result;
    const VelocityFieldResult k1 = FilamentVelocitySolver::evaluate(state, options);

    FilamentSystemState y2 = state;
    apply_velocity(y2, k1, 0.5 * dt);
    const VelocityFieldResult k2 = FilamentVelocitySolver::evaluate(y2, options);

    FilamentSystemState y3 = state;
    apply_velocity(y3, k2, 0.5 * dt);
    const VelocityFieldResult k3 = FilamentVelocitySolver::evaluate(y3, options);

    FilamentSystemState y4 = state;
    apply_velocity(y4, k3, dt);
    const VelocityFieldResult k4 = FilamentVelocitySolver::evaluate(y4, options);

    result.state = blend_stages(state, k1, k2, k3, k4, dt);
    result.maximum_stage_speed = std::max({
        k1.maximum_speed,
        k2.maximum_speed,
        k3.maximum_speed,
        k4.maximum_speed
    });
    return result;
}

double FilamentIntegrator::estimate_cfl_dt(
    const FilamentSystemState& state,
    const VelocityOptions& options,
    double cfl) {
    const VelocityFieldResult vel = FilamentVelocitySolver::evaluate(state, options);
    const double lm = min_segment_length(state);
    const double speed = std::max(vel.maximum_speed, 1e-12);
    if (!std::isfinite(lm) || lm <= 0.0) return 1e-6;
    return std::max(1e-6, cfl * lm / speed);
}

}  // namespace filament
}  // namespace sst
