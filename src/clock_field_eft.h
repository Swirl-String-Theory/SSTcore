#ifndef SSTCORE_CLOCK_FIELD_EFT_H
#define SSTCORE_CLOCK_FIELD_EFT_H
#pragma once

#include <array>
#include "../include/SST_Constants.h"

namespace sst {

using Vec4 = std::array<double, 4>;

struct ClockSectorConstraints {
    double c13 = 0.0;
    double tensor_speed = 1.0;
    double tensor_speed_fractional_offset = 0.0;
    bool gw170817_ok = true;
};

class ClockFieldEFT {
public:
    [[nodiscard]] static double c13(double c1, double c3);
    [[nodiscard]] static double tensor_speed(double c13, double c = static_cast<double>(SST::Constants::C_VACUUM));
    [[nodiscard]] static double tensor_speed_fractional_offset(double c13);
    [[nodiscard]] static bool satisfies_gw170817(double c13, double tolerance = 1e-15);
    [[nodiscard]] static ClockSectorConstraints constraints(double c1, double c3, double tolerance = 1e-15);
    [[nodiscard]] static double poisson_source(double rho_matter, double G_eff);
    [[nodiscard]] static double effective_gravity_from_potential_gradient(double grad_chi);
    [[nodiscard]] static Vec4 unit_timelike_from_gradient_minkowski(const Vec4& grad_chi);
};

} // namespace sst

#endif // SSTCORE_CLOCK_FIELD_EFT_H
