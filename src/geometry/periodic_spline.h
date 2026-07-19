#ifndef SSTCORE_PERIODIC_SPLINE_H
#define SSTCORE_PERIODIC_SPLINE_H

#pragma once

#include "sst/types.h"

#include <cstddef>
#include <vector>

namespace sst {
namespace geometry {

struct SplineEval {
    Vec3 p{{0, 0, 0}};
    Vec3 d1{{0, 0, 0}};
    Vec3 d2{{0, 0, 0}};
    double u = 0.0;
};

class PeriodicCubicSpline3D {
public:
    PeriodicCubicSpline3D() = default;
    explicit PeriodicCubicSpline3D(const std::vector<Vec3>& points);

    std::size_t n() const { return n_; }
    double length() const { return L_; }
    /** Arc-length knot at index i ∈ [0, n]; parameter_at(n) == length(). */
    double parameter_at(std::size_t i) const {
        if (n_ == 0) return 0.0;
        if (i >= n_) return L_;
        return s_[i];
    }
    SplineEval eval(double u) const;

private:
    std::size_t n_ = 0;
    double L_ = 0.0;
    std::vector<Vec3> points_;
    std::vector<double> s_;
    std::vector<double> h_;
    std::vector<std::vector<double>> second_;  // 3 x n

    static double wrap01(double u, double L);
    static bool cyclic_solve(
        const std::vector<double>& a,
        const std::vector<double>& b,
        const std::vector<double>& c,
        double corner,
        const std::vector<double>& r,
        std::vector<double>& out);
};

}  // namespace geometry
}  // namespace sst

#endif
