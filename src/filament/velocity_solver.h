#ifndef SSTCORE_FILAMENT_VELOCITY_SOLVER_H
#define SSTCORE_FILAMENT_VELOCITY_SOLVER_H

#pragma once

#include "vortexlab/types.h"

namespace sst {
namespace filament {

class FilamentVelocitySolver {
public:
    /**
     * VortexLab v7.6.25b velocityCore parity (LIA + midpoint Biot–Savart).
     * Ghost filaments: zero velocity as targets; never sources.
     * External / mutual-friction flags are ignored in this first version.
     */
    static VelocityFieldResult evaluate(
        const FilamentSystemState& filaments,
        const VelocityOptions& options);
};

}  // namespace filament
}  // namespace sst

#endif
