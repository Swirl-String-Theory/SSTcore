#include "sst_operational_spacetime.h"

#include <cmath>
#include <limits>

namespace sst {
namespace {

double invariant_residual_normalized(double s2, double s2p, double c) {
    // Dimensionless: divide by max(|s2|, c^4) so units cancel (time^2*c^2 style scale).
    const double scale = std::max(std::abs(s2), std::pow(c, 4.0));
    return std::abs(s2p - s2) / (scale + 1e-300);
}

} // namespace

RadarInterval OperationalSpacetimeAPI::radar_interval(double emission_time, double reception_time, double c) {
    RadarInterval out;
    out.emission_time = emission_time;
    out.reception_time = reception_time;
    if (!(c > 0.0) || !std::isfinite(emission_time) || !std::isfinite(reception_time)) {
        out.causal = false;
        out.radar_time = std::numeric_limits<double>::quiet_NaN();
        out.radar_distance = std::numeric_limits<double>::quiet_NaN();
        return out;
    }
    out.causal = reception_time >= emission_time;
    if (!out.causal) {
        out.radar_time = std::numeric_limits<double>::quiet_NaN();
        out.radar_distance = std::numeric_limits<double>::quiet_NaN();
        return out;
    }
    out.radar_time = 0.5 * (reception_time + emission_time);
    out.radar_distance = 0.5 * c * (reception_time - emission_time);
    return out;
}

double OperationalSpacetimeAPI::minkowski_interval2(const std::array<double, 4>& a, const std::array<double, 4>& b, double c) {
    const double dt = a[0] - b[0];
    const double dx = a[1] - b[1];
    const double dy = a[2] - b[2];
    const double dz = a[3] - b[3];
    return c * c * dt * dt - (dx * dx + dy * dy + dz * dz);
}

LorentzMapResult OperationalSpacetimeAPI::lorentz_boost_x(const std::array<double, 4>& event, double v, double c) {
    return lorentz_boost(event, {v, 0.0, 0.0}, c);
}

LorentzMapResult OperationalSpacetimeAPI::lorentz_boost(
    const std::array<double, 4>& event,
    const std::array<double, 3>& velocity,
    double c) {
    LorentzMapResult out;
    const double vx = velocity[0], vy = velocity[1], vz = velocity[2];
    const double v2 = vx * vx + vy * vy + vz * vz;
    const double v = std::sqrt(v2);
    if (!(c > 0.0) || !std::isfinite(v) || !(v < c) || !std::isfinite(vx) || !std::isfinite(vy) || !std::isfinite(vz)) {
        out.gamma = std::numeric_limits<double>::quiet_NaN();
        out.invariant_residual = std::numeric_limits<double>::quiet_NaN();
        out.transformed_event = {std::numeric_limits<double>::quiet_NaN(),
                                 std::numeric_limits<double>::quiet_NaN(),
                                 std::numeric_limits<double>::quiet_NaN(),
                                 std::numeric_limits<double>::quiet_NaN()};
        return out;
    }
    if (v == 0.0) {
        out.gamma = 1.0;
        out.transformed_event = event;
        out.invariant_residual = 0.0;
        return out;
    }
    const double beta = v / c;
    out.gamma = 1.0 / std::sqrt(1.0 - beta * beta);
    const double t = event[0];
    const double x = event[1], y = event[2], z = event[3];
    const double nx = vx / v, ny = vy / v, nz = vz / v;
    const double x_par = x * nx + y * ny + z * nz;
    const double x_perp_x = x - x_par * nx;
    const double x_perp_y = y - x_par * ny;
    const double x_perp_z = z - x_par * nz;

    const double t_p = out.gamma * (t - beta * x_par / c);
    const double x_par_p = out.gamma * (x_par - v * t);
    out.transformed_event[0] = t_p;
    out.transformed_event[1] = x_perp_x + x_par_p * nx;
    out.transformed_event[2] = x_perp_y + x_par_p * ny;
    out.transformed_event[3] = x_perp_z + x_par_p * nz;

    const std::array<double, 4> origin{0, 0, 0, 0};
    const double s2 = minkowski_interval2(event, origin, c);
    const double s2p = minkowski_interval2(out.transformed_event, origin, c);
    out.invariant_residual = invariant_residual_normalized(s2, s2p, c);
    return out;
}

} // namespace sst
