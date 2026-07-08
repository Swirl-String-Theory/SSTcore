#ifndef SSTCORE_SST_FILAMENT_VORTEX_KNOT_SYSTEM_H
#define SSTCORE_SST_FILAMENT_VORTEX_KNOT_SYSTEM_H

#pragma once

#include "sst/filament/evolution.h"
#include "sst/types.h"

#include <cstddef>
#include <string>
#include <vector>

namespace sst {

class [[deprecated("Use sst::FilamentEvolution")]] VortexKnotSystem {
public:
    explicit VortexKnotSystem(double gamma = 1.0);

    void initialize_trefoil_knot(std::size_t resolution = 400);
    void initialize_figure8_knot(std::size_t resolution = 400);
    void initialize_knot_from_name(const std::string& knot_id, std::size_t resolution = 1000);

    void evolve(double dt, std::size_t steps);

    [[nodiscard]] const std::vector<Vec3>& get_positions() const;
    [[nodiscard]] const std::vector<Vec3>& get_tangents() const;

private:
    FilamentEvolution core_;
};

} // namespace sst

#endif // SSTCORE_SST_FILAMENT_VORTEX_KNOT_SYSTEM_H
