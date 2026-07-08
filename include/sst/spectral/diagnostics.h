#ifndef SSTCORE_SST_SPECTRAL_DIAGNOSTICS_H
#define SSTCORE_SST_SPECTRAL_DIAGNOSTICS_H

#pragma once

#include <cstddef>
#include <vector>

namespace sst {
namespace spectral {

double trace_from_diagonal(const double* matrix, std::size_t n);
double log_det_from_eigenvalues(const double* eigenvalues, std::size_t n, double regularization = 1e-15);
std::vector<double> spectral_density_histogram(
    const double* eigenvalues,
    std::size_t n,
    double x_min,
    double x_max,
    std::size_t n_bins);
std::vector<double> nearest_eigenvalues_to_targets(
    const double* eigenvalues,
    std::size_t n,
    const double* targets,
    std::size_t n_targets);

} // namespace spectral
} // namespace sst

#endif // SSTCORE_SST_SPECTRAL_DIAGNOSTICS_H
