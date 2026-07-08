#ifndef SSTCORE_SST_SPECTRAL_EIGENSOLVER_JACOBI_H
#define SSTCORE_SST_SPECTRAL_EIGENSOLVER_JACOBI_H

#pragma once

#include "sst/spectral/grid1d.h"
#include <cstddef>
#include <vector>

namespace sst {
namespace spectral {

SpectralResult jacobi_eigen_solve_symmetric(
    const double* matrix,
    std::size_t n,
    bool compute_eigenvectors = true,
    std::size_t max_sweeps = 100,
    double tol = 1e-12,
    bool sort_ascending = true);

std::vector<double> eigenvalues(
    const double* matrix,
    std::size_t n,
    std::size_t max_sweeps = 100,
    double tol = 1e-12,
    bool sort_ascending = true);

} // namespace spectral
} // namespace sst

#endif // SSTCORE_SST_SPECTRAL_EIGENSOLVER_JACOBI_H
