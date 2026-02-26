#pragma once

#include <cmath>

namespace sst {
    // Portable mathematical constants for the library.
    // Prefer using this instead of M_PI (which is non-standard and
    // requires _USE_MATH_DEFINES on MSVC).
    inline constexpr const double pi = 3.141592653589793238462643383279502884L;
}