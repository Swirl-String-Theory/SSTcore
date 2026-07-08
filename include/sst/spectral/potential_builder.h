#ifndef SSTCORE_SST_SPECTRAL_POTENTIAL_BUILDER_H
#define SSTCORE_SST_SPECTRAL_POTENTIAL_BUILDER_H

#pragma once

#include "sst/spectral/grid1d.h"
#include <cstddef>
#include <vector>

namespace sst {
namespace spectral {

std::vector<double> build_potential_from_options(const Grid1D& grid, const PotentialOptions& opts);
std::vector<double> build_potential_from_nodes(
    const Grid1D& grid,
    const double* target_nodes,
    std::size_t n_targets,
    double well_amplitude,
    double well_sigma,
    double harmonic_coeff,
    double quartic_coeff,
    double constant_shift);
std::vector<double> build_potential_from_trace_density(
    const double* trace_density,
    std::size_t n,
    double scale,
    double constant_shift);
std::vector<double> build_potential_from_phi_abs(
    const double* phi_abs,
    std::size_t n,
    double scale,
    double smooth_strength,
    double constant_shift);
std::vector<double> smooth_potential_box(const double* v, std::size_t n, int radius);

} // namespace spectral
} // namespace sst

#endif // SSTCORE_SST_SPECTRAL_POTENTIAL_BUILDER_H
