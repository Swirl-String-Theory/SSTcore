#ifndef SSTCORE_SST_TYPES_H
#define SSTCORE_SST_TYPES_H

#pragma once

#include <array>
#include <cmath>

namespace sst {

using Vec3 = std::array<double, 3>;
using Vec2f = std::array<float, 2>;

inline Vec3 cross(const Vec3& a, const Vec3& b) {
    return {
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    };
}

inline Vec3 diff(const Vec3& a, const Vec3& b) {
    return {a[0] - b[0], a[1] - b[1], a[2] - b[2]};
}

inline double dot(const Vec3& a, const Vec3& b) {
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

inline double norm(const Vec3& v) {
    return std::sqrt(dot(v, v));
}

} // namespace sst

#endif // SSTCORE_SST_TYPES_H
