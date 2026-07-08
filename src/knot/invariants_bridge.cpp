#include "sst/knot/invariants_bridge.h"

#include <algorithm>

#include "sst/knot.h"
#include "sst/tube/geometry.h"

namespace sst::knot {

void fill_resolved_tube_fields(
    KnotInvariants& K,
    const std::vector<Vec3>& centerline,
    int exclude_window) {
    const int skip = std::max(1, exclude_window);
    const auto tube = ResolvedTubeGeometry::analyze(
        centerline,
        skip,
        1e-3,
        1e-2);
    const auto contact = ContactStressMap::diagnose_length_criticality(centerline, tube, false);

    K.tube = tube;
    K.sync_tube_from_optional();
    K.contact_residual = contact.contact_residual;
    K.contact_entropy = contact.contact_entropy;
}

} // namespace sst::knot
