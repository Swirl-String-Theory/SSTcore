#ifndef SSTCORE_CHRONOS_KELVIN_TRANSPORT_H
#define SSTCORE_CHRONOS_KELVIN_TRANSPORT_H
#pragma once

#include "../include/SST_Constants.h"

namespace sst {

class ChronosKelvinTransport {
public:
    [[nodiscard]] static double kelvin_invariant(double R, double omega);
    [[nodiscard]] static double omega_from_invariant(double invariant, double R);
    // Returns the ANGULAR-FREQUENCY convention Omega (= vorticity / 2):
    //   Omega = (c / r_c) * sqrt(1 - S_t^2).
    [[nodiscard]] static double omega_from_swirl_clock(double S_t, double r_c, double c = static_cast<double>(SST::Constants::C_VACUUM));
    // Returns the canon chronos-Kelvin VORTICITY omega = 2 * Omega (Canon Sec. 2.9):
    //   omega = (2c / r_c) * sqrt(1 - S_t^2).
    [[nodiscard]] static double vorticity_from_swirl_clock(double S_t, double r_c, double c = static_cast<double>(SST::Constants::C_VACUUM));
    // Inverse of vorticity_from_swirl_clock for the canon vorticity convention.
    [[nodiscard]] static double swirl_clock_from_omega(double omega, double r_c, double c = static_cast<double>(SST::Constants::C_VACUUM));
    [[nodiscard]] static double chronos_kelvin_invariant(double R, double S_t, double r_c, double c = static_cast<double>(SST::Constants::C_VACUUM));
    [[nodiscard]] static double clock_radius_derivative(double S_t, double R, double dR_dt);
    [[nodiscard]] static double radius_from_clock_invariant(double invariant, double S_t, double r_c, double c = static_cast<double>(SST::Constants::C_VACUUM));
};

} // namespace sst

#endif // SSTCORE_CHRONOS_KELVIN_TRANSPORT_H
