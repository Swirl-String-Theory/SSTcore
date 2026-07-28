#include "sst_operational_spacetime.h"

#include <cmath>
#include <limits>

namespace sst {

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
    LorentzMapResult out;
    if (!(c > 0.0) || !std::isfinite(v) || std::abs(v) >= c) {
        out.gamma = std::numeric_limits<double>::quiet_NaN();
        out.invariant_residual = std::numeric_limits<double>::quiet_NaN();
        out.transformed_event = {std::numeric_limits<double>::quiet_NaN(),
                                 std::numeric_limits<double>::quiet_NaN(),
                                 std::numeric_limits<double>::quiet_NaN(),
                                 std::numeric_limits<double>::quiet_NaN()};
        return out;
    }
    const double beta = v / c;
    out.gamma = 1.0 / std::sqrt(1.0 - beta * beta);
    const double t = event[0], x = event[1], y = event[2], z = event[3];
    out.transformed_event[0] = out.gamma * (t - beta * x / c);
    out.transformed_event[1] = out.gamma * (x - v * t);
    out.transformed_event[2] = y;
    out.transformed_event[3] = z;

    // Compare s^2 of event vs origin before/after boost (should match).
    const std::array<double, 4> origin{0, 0, 0, 0};
    const double s2 = minkowski_interval2(event, origin, c);
    const double s2p = minkowski_interval2(out.transformed_event, origin, c);
    const double denom = std::abs(s2) + 1.0;
    out.invariant_residual = std::abs(s2p - s2) / denom;
    return out;
}

} // namespace sst
