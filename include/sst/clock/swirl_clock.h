#ifndef SSTCORE_SST_CLOCK_SWIRL_CLOCK_H
#define SSTCORE_SST_CLOCK_SWIRL_CLOCK_H

#pragma once

#include "sst/types.h"
#include "SST_Constants.h"
#include <cmath>
#include <vector>

namespace sst::clock {

[[nodiscard]] inline double factor_from_speed(double speed_squared, double c = static_cast<double>(SST::Constants::C_VACUUM)) {
    const double c2 = c * c;
    double arg = 1.0 - speed_squared / c2;
    if (arg < 0.0) arg = 0.0;
    return std::sqrt(arg);
}

[[nodiscard]] inline std::vector<double> map_from_velocity_field(
    const std::vector<Vec3>& v_swirl_field,
    double c = static_cast<double>(SST::Constants::C_VACUUM))
{
    std::vector<double> st_map(v_swirl_field.size());
    for (std::size_t i = 0; i < v_swirl_field.size(); ++i) {
        const Vec3& v = v_swirl_field[i];
        const double v2 = v[0] * v[0] + v[1] * v[1] + v[2] * v[2];
        st_map[i] = factor_from_speed(v2, c);
    }
    return st_map;
}

} // namespace sst::clock

#endif // SSTCORE_SST_CLOCK_SWIRL_CLOCK_H
