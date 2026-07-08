#include "sst/continuum/radiation.h"
#include <cmath>

namespace sst::continuum::radiation {

double radiation_force(double I0, double Qm, double lambda1, double lambda2, double lambda_g) {
    const double factor = (lambda1 / lambda_g) * (lambda2 / lambda_g);
    const double denom = 1.0 - std::pow(lambda1 / lambda_g, 2);
    return (2.0 * I0 / 3e8) * Qm * factor / denom;
}

double dxdt(double x, double y) { return y; }
double dydt(double x, double y, double mu) { return mu * (1 - x * x) * y - x; }

} // namespace sst::continuum::radiation
