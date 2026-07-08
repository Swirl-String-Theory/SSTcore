#ifndef SSTCORE_SST_SPECTRAL_FINITE_DIFFERENCE_H
#define SSTCORE_SST_SPECTRAL_FINITE_DIFFERENCE_H

#pragma once

#include "sst/spectral/grid1d.h"
#include <cstddef>
#include <vector>

namespace sst {
namespace spectral {

std::vector<double> build_uniform_grid(const Grid1D& grid);
std::vector<double> build_identity(std::size_t n);
std::vector<double> build_second_difference(const Grid1D& grid, const BoundaryOptions& bc);
std::vector<double> build_laplacian_schrodinger_kinetic(
    const Grid1D& grid,
    const BoundaryOptions& bc,
    double kinetic_prefactor = 1.0);

} // namespace spectral
} // namespace sst

#endif // SSTCORE_SST_SPECTRAL_FINITE_DIFFERENCE_H
