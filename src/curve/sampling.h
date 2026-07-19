#ifndef SSTCORE_CURVE_SAMPLING_H
#define SSTCORE_CURVE_SAMPLING_H

#pragma once

#include "sst/types.h"
#include "vortexlab/types.h"

#include <cstddef>
#include <vector>

namespace sst {
namespace curve {

struct FourierTerm {
    double I = 0.0;
    Vec3 A{{0, 0, 0}};
    Vec3 B{{0, 0, 0}};
};

class CurveSampling {
public:
    static std::vector<Vec3> resample_closed_arclength(
        const std::vector<Vec3>& points, std::size_t n);

    static std::vector<Vec3> reverse_traversal(const std::vector<Vec3>& points);

    static std::vector<Vec3> sample_fourier_parametric(
        const std::vector<FourierTerm>& coeffs, std::size_t n);

    static std::vector<Vec3> sample_fourier(
        const std::vector<FourierTerm>& coeffs,
        std::size_t n,
        bool arclength_uniform);

    static std::vector<Vec3> sample_circle(
        std::size_t n, double R = 1.0, double z = 0.0);

    static double closed_length(const std::vector<Vec3>& points);
};

}  // namespace curve
}  // namespace sst

#endif
