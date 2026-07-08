#ifndef SSTCORE_RADIATION_FLOW_H
#define SSTCORE_RADIATION_FLOW_H

#pragma once

#include "sst/continuum/radiation.h"

namespace sst {

class [[deprecated("Use sst::continuum::radiation")]] RadiationFlow {
public:
    static double radiation_force(double I0, double Qm, double lambda1, double lambda2, double lambda_g) {
        return continuum::radiation::radiation_force(I0, Qm, lambda1, lambda2, lambda_g);
    }
    static double dxdt(double x, double y) { return continuum::radiation::dxdt(x, y); }
    static double dydt(double x, double y, double mu) { return continuum::radiation::dydt(x, y, mu); }
};

} // namespace sst

#endif // SSTCORE_RADIATION_FLOW_H
