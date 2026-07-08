#include "sst/filament/vortex_knot_system.h"

namespace sst {

VortexKnotSystem::VortexKnotSystem(double gamma) : core_(gamma) {}

void VortexKnotSystem::initialize_trefoil_knot(std::size_t resolution) {
    core_ = FilamentEvolution::make_trefoil(resolution, core_.circulation());
}

void VortexKnotSystem::initialize_figure8_knot(std::size_t resolution) {
    core_ = FilamentEvolution::make_figure8(resolution, core_.circulation());
}

void VortexKnotSystem::initialize_knot_from_name(const std::string& knot_id, std::size_t resolution) {
    core_ = FilamentEvolution::make_from_fseries(knot_id, resolution, core_.circulation());
}

void VortexKnotSystem::evolve(double dt, std::size_t steps) {
    core_.evolve(dt, steps);
}

const std::vector<Vec3>& VortexKnotSystem::get_positions() const {
    return core_.positions();
}

const std::vector<Vec3>& VortexKnotSystem::get_tangents() const {
    return core_.tangents();
}

} // namespace sst
