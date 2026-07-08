#ifndef SSTCORE_SST_SPECTRAL_GRID1D_H
#define SSTCORE_SST_SPECTRAL_GRID1D_H

#pragma once

#include <cstddef>
#include <vector>

namespace sst {

struct Grid1D {
    double u_min = -1.0;
    double u_max = 1.0;
    std::size_t n = 201;

    double spacing() const {
        return (n > 1) ? (u_max - u_min) / static_cast<double>(n - 1) : 0.0;
    }
};

struct BoundaryOptions {
    int mode = 0;
    bool force_center_dirichlet = true;
};

struct PotentialGaussianWell {
    double center = 0.0;
    double amplitude = -1.0;
    double sigma = 0.1;
};

struct PotentialOptions {
    double harmonic_coeff = 0.0;
    double quartic_coeff = 0.0;
    double constant_shift = 0.0;
    std::vector<PotentialGaussianWell> gaussians;
};

struct SpectralResult {
    std::vector<double> eigenvalues;
    std::vector<double> eigenvectors;
    std::size_t n = 0;
};

} // namespace sst

#endif // SSTCORE_SST_SPECTRAL_GRID1D_H
