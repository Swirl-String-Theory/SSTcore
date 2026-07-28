#pragma once

#include <array>
#include <cmath>
#include <string>

namespace sst {

struct RadarInterval {
    double emission_time = 0.0;
    double reception_time = 0.0;
    double radar_time = 0.0;
    double radar_distance = 0.0;
    bool causal = false;
};

struct LorentzMapResult {
    std::array<double, 4> transformed_event{};
    double gamma = 1.0;
    double invariant_residual = 0.0;
};

class OperationalSpacetimeAPI {
public:
    // T_radar = (T+ + T-)/2, R_radar = c(T+ - T-)/2; requires T+ >= T-.
    [[nodiscard]] static RadarInterval radar_interval(double emission_time, double reception_time, double c = 1.0);

    // Boost along +x with velocity v (|v|<c). Events are (t,x,y,z).
    [[nodiscard]] static LorentzMapResult lorentz_boost_x(const std::array<double, 4>& event, double v, double c = 1.0);

    [[nodiscard]] static double minkowski_interval2(const std::array<double, 4>& a, const std::array<double, 4>& b, double c = 1.0);
};

} // namespace sst
