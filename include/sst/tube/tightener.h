#ifndef SSTCORE_SST_TUBE_TIGHTENER_H
#define SSTCORE_SST_TUBE_TIGHTENER_H

#pragma once

#include "sst/tube/types.h"
#include <vector>

namespace sst {

class ResolvedTubeTightener {
public:
    [[nodiscard]] static std::vector<Vec3> rescale_to_thickness(
        const std::vector<Vec3>& pts,
        double target_thickness,
        int skip_neighbors = 2,
        double contact_tol = 1e-3,
        double equilateral_tol = 1e-3);

    [[nodiscard]] static std::vector<Vec3> correct_thickness(
        const std::vector<Vec3>& pts,
        double target_thickness,
        const TighteningOptions& options = TighteningOptions());

    [[nodiscard]] static std::vector<double> projected_gradient_flat(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        const TighteningOptions& options,
        ContactStressDiagnostics* diagnostics_out = nullptr);

    [[nodiscard]] static TighteningResult tighten(
        const std::vector<Vec3>& initial_points,
        const TighteningOptions& options = TighteningOptions());
};

} // namespace sst

#endif // SSTCORE_SST_TUBE_TIGHTENER_H
