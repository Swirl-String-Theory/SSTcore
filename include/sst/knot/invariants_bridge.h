#ifndef SSTCORE_SST_KNOT_INVARIANTS_BRIDGE_H
#define SSTCORE_SST_KNOT_INVARIANTS_BRIDGE_H

#pragma once

#include "sst/types.h"
#include <vector>

namespace sst {

struct KnotInvariants;

namespace knot {

/// Fill resolved-tube metric fields on KnotInvariants from a sampled centerline.
void fill_resolved_tube_fields(
    KnotInvariants& K,
    const std::vector<Vec3>& centerline,
    int exclude_window);

} // namespace knot
} // namespace sst

#endif // SSTCORE_SST_KNOT_INVARIANTS_BRIDGE_H
