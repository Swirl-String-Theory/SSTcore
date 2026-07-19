#ifndef SSTCORE_FILAMENT_INTEGRATOR_H
#define SSTCORE_FILAMENT_INTEGRATOR_H

#pragma once

#include "vortexlab/types.h"

namespace sst {
namespace filament {

struct IntegratorStepResult {
    FilamentSystemState state;
    double maximum_stage_speed = 0.0;
};

class FilamentIntegrator {
public:
    static IntegratorStepResult rk4_step(
        const FilamentSystemState& state,
        double dt,
        const VelocityOptions& options);

    /** CFL estimate: cfl * min_segment_length / max_speed (default cfl = 0.5). */
    static double estimate_cfl_dt(
        const FilamentSystemState& state,
        const VelocityOptions& options,
        double cfl = 0.5);
};

}  // namespace filament
}  // namespace sst

#endif
