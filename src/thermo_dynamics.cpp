#include "sst/continuum/thermo.h"
#include <cmath>

namespace sst::continuum::thermo {

double potential_temperature(double T, double p0, double p, double R, double cp) {
    const double k = R / cp;
    return T * std::pow(p0 / p, k);
}

double entropy_from_theta(double cp, double theta, double dtheta) {
    return cp * dtheta / theta;
}

double entropy_from_pv(double N, double R, double p, double V, double gamma) {
    return (N * R / (gamma - 1)) * (std::log(p) + std::log(V));
}

double enthalpy(double internal_energy, double p, double V) {
    return internal_energy + p * V;
}

} // namespace sst::continuum::thermo
