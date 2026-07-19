#ifndef SSTCORE_POLYGONAL_GAUSS_H
#define SSTCORE_POLYGONAL_GAUSS_H

#pragma once

#include "sst/types.h"
#include "vortexlab/types.h"

#include <vector>

namespace sst {
namespace knot {

class PolygonalGaussInvariants {
public:
    // Exact polygonal solid-angle pair (VortexLab segPairOmega).
    static double segment_pair_omega(
        const Vec3& p1, const Vec3& p2, const Vec3& p3, const Vec3& p4);

    // same_curve: Wr/ACN with 2π normalization; else Lk/cross-ACN with 4π.
    static PolygonalGaussResult evaluate(
        const std::vector<Vec3>& curve_a,
        const std::vector<Vec3>& curve_b,
        bool same_curve);

    static PolygonalGaussResult writhe(const std::vector<Vec3>& curve);
    static PolygonalGaussResult linking(
        const std::vector<Vec3>& curve_a, const std::vector<Vec3>& curve_b);
};

}  // namespace knot
}  // namespace sst

#endif
