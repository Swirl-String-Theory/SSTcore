#include "topology/topology_guard.h"

#include "geometry/polygonal_clearance.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <string>
#include <vector>

namespace sst {
namespace topology {
namespace {

constexpr int kSweepSamples = 8;

std::vector<std::vector<Vec3>> curve_set_points(const CurveSet& cs) {
    std::vector<std::vector<Vec3>> out;
    out.reserve(cs.components.size());
    for (const auto& c : cs.components) out.push_back(c.points);
    return out;
}

std::vector<std::vector<Vec3>> lerp_states(
    const std::vector<std::vector<Vec3>>& a,
    const std::vector<std::vector<Vec3>>& b,
    double f) {
    std::vector<std::vector<Vec3>> out = a;
    const std::size_t nc = std::min(a.size(), b.size());
    out.resize(nc);
    for (std::size_t c = 0; c < nc; ++c) {
        const std::size_t n = std::min(a[c].size(), b[c].size());
        out[c].resize(n);
        for (std::size_t i = 0; i < n; ++i) {
            out[c][i][0] = a[c][i][0] + f * (b[c][i][0] - a[c][i][0]);
            out[c][i][1] = a[c][i][1] + f * (b[c][i][1] - a[c][i][1]);
            out[c][i][2] = a[c][i][2] + f * (b[c][i][2] - a[c][i][2]);
        }
    }
    return out;
}

bool hard_contact(const TopologyClearanceResult& cl, double threshold) {
    return std::isfinite(cl.clearance) && cl.clearance < threshold;
}

}  // namespace

TopologyClearanceResult TopologyGuard::compute_clearance(
    const std::vector<std::vector<Vec3>>& curves,
    double core_radius) {
    return geometry::multi_component_clearance(curves, core_radius, 2);
}

TopologyClearanceResult TopologyGuard::compute_clearance(
    const CurveSet& curves,
    double core_radius) {
    return compute_clearance(curve_set_points(curves), core_radius);
}

bool TopologyGuard::may_tunnel(
    double g0,
    double g1,
    double dmax,
    double threshold) {
    return std::isfinite(g0) && std::isfinite(g1)
           && std::min(g0, g1) <= threshold + 2.25 * dmax;
}

TopologyGuardResult TopologyGuard::guard_step(
    const std::vector<std::vector<Vec3>>& before,
    const std::vector<std::vector<Vec3>>& after,
    double contact_threshold,
    double max_displacement,
    double core_radius) {
    TopologyGuardResult out;
    const TopologyClearanceResult cl0 = compute_clearance(before, core_radius);
    const TopologyClearanceResult cl1 = compute_clearance(after, core_radius);
    out.clearance_before = cl0.clearance;
    out.clearance_after = cl1.clearance;
    out.safe_dt_fraction = 1.0;
    out.contact = false;
    out.warn_only = false;

    if (!may_tunnel(cl0.clearance, cl1.clearance, max_displacement, contact_threshold)) {
        if (hard_contact(cl1, contact_threshold)) {
            out.contact = true;
            out.safe_dt_fraction = 0.0;
            out.message = "contact at end of step";
        }
        return out;
    }

    // Already in contact before the step.
    if (hard_contact(cl0, contact_threshold)) {
        out.contact = true;
        out.safe_dt_fraction = 0.0;
        out.message = "contact at start of step";
        return out;
    }

    double lo = 0.0;
    double hi = std::numeric_limits<double>::quiet_NaN();
    bool found = false;
    for (int k = 1; k <= kSweepSamples; ++k) {
        const double f = static_cast<double>(k) / static_cast<double>(kSweepSamples);
        const auto mid = lerp_states(before, after, f);
        const TopologyClearanceResult cl = compute_clearance(mid, core_radius);
        if (hard_contact(cl, contact_threshold)) {
            hi = f;
            lo = static_cast<double>(k - 1) / static_cast<double>(kSweepSamples);
            found = true;
            break;
        }
    }

    if (!found) {
        if (hard_contact(cl1, contact_threshold)) {
            out.contact = true;
            out.safe_dt_fraction = 0.0;
            out.message = "contact at end of step";
        }
        return out;
    }

    // Bisect to first-hit; land on safe side (lo).
    for (int it = 0; it < 18 && (hi - lo) > 1e-6; ++it) {
        const double mid_f = 0.5 * (lo + hi);
        const auto mid = lerp_states(before, after, mid_f);
        const TopologyClearanceResult cl = compute_clearance(mid, core_radius);
        if (hard_contact(cl, contact_threshold)) hi = mid_f;
        else lo = mid_f;
    }

    out.contact = true;
    out.safe_dt_fraction = lo;
    out.message =
        "topology guard: transient contact within step; stopped on safe side";
    return out;
}

TopologyGuardResult TopologyGuard::guard_step(
    const CurveSet& before,
    const CurveSet& after,
    double contact_threshold,
    double max_displacement,
    double core_radius) {
    return guard_step(
        curve_set_points(before),
        curve_set_points(after),
        contact_threshold,
        max_displacement,
        core_radius);
}

}  // namespace topology
}  // namespace sst
