#ifndef SSTCORE_SST_CONTINUUM_RADIATION_H
#define SSTCORE_SST_CONTINUUM_RADIATION_H

#pragma once

namespace sst::continuum::radiation {

double radiation_force(double I0, double Qm, double lambda1, double lambda2, double lambda_g);
double dxdt(double x, double y);
double dydt(double x, double y, double mu);

} // namespace sst::continuum::radiation

#endif // SSTCORE_SST_CONTINUUM_RADIATION_H
