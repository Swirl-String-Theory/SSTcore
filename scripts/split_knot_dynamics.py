#!/usr/bin/env python3
"""One-shot splitter: knot_dynamics.cpp -> modular src files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "knot_dynamics.cpp"
lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)


def chunk(start: int, end: int) -> str:
    return "".join(lines[start - 1 : end])


def write(rel: str, text: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {rel} ({path.stat().st_size} bytes)")


write(
    "src/knot/resource_loader.cpp",
    """#include "sst/knot/resource_loader.h"

#include <cctype>
#include <cstdlib>
#include <fstream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <vector>

#include "knot_files_embedded.h"

namespace sst {

"""
    + chunk(26, 41)
    + chunk(1167, 1502)
    + "\n} // namespace sst\n",
)

write(
    "src/particle/knot_particle_model.cpp",
    """#include "sst/particle/knot_particle_model.h"

#include "SST_Constants.h"
#include "canonical_constants.h"
#include "sst/knot/invariants.h"

#include <algorithm>
#include <cmath>

namespace sst {

"""
    + chunk(43, 99)
    + chunk(329, 381)
    + "\n} // namespace sst\n",
)

write(
    "src/particle/xi_model.cpp",
    """#include "sst/particle/xi_model.h"

#include "SST_Constants.h"

#include <cmath>

namespace sst {

"""
    + chunk(101, 142)
    + "\n} // namespace sst\n",
)

write(
    "src/particle/mass_functional.cpp",
    """#include "sst/particle/mass_functional.h"

#include "canonical_constants.h"
#include "sst_master_equation.h"

#include <cmath>
#include <stdexcept>

namespace sst {

"""
    + chunk(144, 244)
    + "\n} // namespace sst\n",
)

write(
    "src/knot/invariants.cpp",
    """#include "sst/knot.h"

#include "biot_savart.h"
#include "sst/knot/invariants_bridge.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <optional>
#include <random>
#include <stdexcept>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

"""
    + chunk(246, 327)
    + chunk(383, 837)
    + "\n} // namespace sst\n",
)

write(
    "src/knot/fourier_parser.cpp",
    """#include "sst/knot/fourier_parser.h"

#include <fstream>
#include <sstream>
#include <string>
#include <vector>

namespace sst {

"""
    + chunk(840, 922)
    + "\n} // namespace sst\n",
)

write(
    "src/knot/fourier_eval.cpp",
    """#include "sst/knot.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

"""
    + chunk(924, 1115)
    + "\n} // namespace sst\n\n"
    + """namespace {
static inline double _sst_norm(const sst::Vec3& v) {
    return std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
}
static inline sst::Vec3 _sst_cross(const sst::Vec3& a, const sst::Vec3& b) {
    return sst::Vec3{a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]};
}
static inline sst::Vec3 _sst_sub(const sst::Vec3& a, const sst::Vec3& b) {
    return sst::Vec3{a[0]-b[0], a[1]-b[1], a[2]-b[2]};
}
}

"""
    + chunk(1875, 1974)
    + "\n",
)

write(
    "src/knot/ideal_parser.cpp",
    """#include "sst/knot/ideal_parser.h"

#include "sst/knot/resource_loader.h"

#include <fstream>
#include <map>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

"""
    + chunk(1569, 1777)
    + "\n"
    + chunk(1779, 1873)
    + "\n",
)

write(
    "src/filament/vortex_knot_system.cpp",
    """#include "sst/filament/vortex_knot_system.h"

#include "biot_savart.h"
#include "sst/knot/fourier_eval.h"
#include "sst/knot/resource_loader.h"

#include <cmath>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

"""
    + chunk(1117, 1165)
    + chunk(1504, 1565)
    + "\n} // namespace sst\n",
)

# Split into src/knot/, src/particle/, src/filament/ (P2 refactor).

print("done")
