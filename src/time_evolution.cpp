#include "time_evolution.h"

namespace sst {

TimeEvolution::TimeEvolution(std::vector<Vec3> initial_positions,
                             std::vector<Vec3> initial_tangents,
                             double gamma)
    : core_(gamma) {
    core_.set_positions(std::move(initial_positions));
    core_.set_tangents(std::move(initial_tangents));
}

void TimeEvolution::evolve(double dt, int steps) {
    core_.evolve(dt, static_cast<std::size_t>(steps));
}

const std::vector<Vec3>& TimeEvolution::get_positions() const {
    return core_.positions();
}

const std::vector<Vec3>& TimeEvolution::get_tangents() const {
    return core_.tangents();
}

} // namespace sst
