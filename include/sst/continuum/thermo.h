#ifndef SSTCORE_SST_CONTINUUM_THERMO_H
#define SSTCORE_SST_CONTINUUM_THERMO_H

#pragma once

namespace sst::continuum::thermo {

double potential_temperature(double T, double p0, double p, double R, double cp);
double entropy_from_theta(double cp, double theta, double dtheta);
double entropy_from_pv(double N, double R, double p, double V, double gamma);
double enthalpy(double internal_energy, double p, double V);

} // namespace sst::continuum::thermo

#endif // SSTCORE_SST_CONTINUUM_THERMO_H
