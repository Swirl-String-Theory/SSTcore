#ifndef SSTCORE_SST_SPECTRAL_DENSE_LINALG_H
#define SSTCORE_SST_SPECTRAL_DENSE_LINALG_H

#pragma once

#include "sst/spectral/grid1d.h"
#include <cstddef>
#include <vector>

namespace sst {
namespace spectral {

std::vector<double> assemble_schrodinger_matrix(
    const Grid1D& grid,
    const BoundaryOptions& bc,
    const double* potential,
    double kinetic_prefactor = 1.0);
std::vector<double> apply_diagonal_shift(const double* matrix, std::size_t n, double shift);
std::vector<double> assemble_transfer_kernel(
    const Grid1D& grid,
    const double* potential,
    double diffusion_scale,
    double potential_scale,
    bool normalize_rows);
std::vector<double> generator_from_transfer_kernel(
    const double* kernel,
    std::size_t n,
    double dt,
    bool subtract_identity_first);
std::vector<double> matrix_vector_multiply(const double* matrix, std::size_t n, const double* x);
double rayleigh_quotient(const double* matrix, std::size_t n, const double* x);
void normalize_vector(double* x, std::size_t n);
double residual_norm(const double* matrix, std::size_t n, const double* x, double lambda);

} // namespace spectral
} // namespace sst

#endif // SSTCORE_SST_SPECTRAL_DENSE_LINALG_H
