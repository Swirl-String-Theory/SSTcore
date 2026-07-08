#ifndef SSTCORE_SST_FITTING_TRACE_H
#define SSTCORE_SST_FITTING_TRACE_H

#pragma once

#include <complex>
#include <cstddef>
#include <vector>

namespace sst {

class TraceFormula {
public:
    static std::vector<std::complex<double>> evaluateSectorLogZ(
        const double* t_values, std::size_t nt, int nu, double theta_nu,
        double ell_trefoil, std::size_t truncation_M);
    static std::vector<std::complex<double>> evaluateSectorDLogZDs(
        const double* t_values, std::size_t nt, int nu, double theta_nu,
        double ell_trefoil, std::size_t truncation_M);
    static std::vector<std::complex<double>> evaluateMultisectorLogZ(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        double ell_trefoil, std::size_t truncation_M);
    static std::vector<std::complex<double>> evaluateMultisectorDLogZDs(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        double ell_trefoil, std::size_t truncation_M);
    static std::vector<double> phaseDerivativeFromXi(
        const double* t_values, std::size_t nt, const std::complex<double>* xi_values);
};

} // namespace sst

#endif // SSTCORE_SST_FITTING_TRACE_H
