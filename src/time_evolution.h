#ifndef SSTCORE_TIME_EVOLUTION_H
#define SSTCORE_TIME_EVOLUTION_H

#pragma once

#include "sst/filament/evolution.h"
#include "sst/types.h"
#include <vector>

namespace sst {

class [[deprecated("Use sst::FilamentEvolution")]] TimeEvolution {
public:
    TimeEvolution(std::vector<Vec3> initial_positions,
                  std::vector<Vec3> initial_tangents,
                  double gamma = 1.0);

    void evolve(double dt, int steps);
    const std::vector<Vec3>& get_positions() const;
    const std::vector<Vec3>& get_tangents() const;

private:
    FilamentEvolution core_;
};

} // namespace sst

#endif // SSTCORE_TIME_EVOLUTION_H
