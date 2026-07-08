#ifndef SSTCORE_SST_KNOT_FOURIER_TYPES_H
#define SSTCORE_SST_KNOT_FOURIER_TYPES_H

#pragma once

#include <array>
#include <map>
#include <string>
#include <vector>

namespace sst {

// Fourier block definition (mode-indexed coefficients, dense vector format)
struct FourierBlock {
    std::string header;  // optional metadata/comment line
    std::vector<double> a_x, b_x;
    std::vector<double> a_y, b_y;
    std::vector<double> a_z, b_z;
};

// Optional sparse Fourier representation (for ideal.txt / AB parsing / conversions)
struct FourierBlockSparse {
    std::string name;
    std::map<int, std::array<double, 3>> A;  // cosine coeffs by harmonic index j>=1
    std::map<int, std::array<double, 3>> B;  // sine coeffs by harmonic index j>=1
};

} // namespace sst

#endif // SSTCORE_SST_KNOT_FOURIER_TYPES_H
