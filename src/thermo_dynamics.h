#ifndef SSTCORE_THERMO_DYNAMICS_H
#define SSTCORE_THERMO_DYNAMICS_H

#pragma once

#include "sst/continuum/thermo.h"

namespace sst {

class [[deprecated("Use sst::continuum::thermo")]] ThermoDynamics {
public:
    static double potential_temperature(double T, double p0, double p, double R, double cp) {
        return continuum::thermo::potential_temperature(T, p0, p, R, cp);
    }
    static double entropy_from_theta(double cp, double theta, double dtheta) {
        return continuum::thermo::entropy_from_theta(cp, theta, dtheta);
    }
    static double entropy_from_pv(double N, double R, double p, double V, double gamma) {
        return continuum::thermo::entropy_from_pv(N, R, p, V, gamma);
    }
    static double enthalpy(double internal_energy, double p, double V) {
        return continuum::thermo::enthalpy(internal_energy, p, V);
    }
};

} // namespace sst

#endif // SSTCORE_THERMO_DYNAMICS_H
