#ifndef SSTCORE_SST_FILAMENT_EVOLUTION_H
#define SSTCORE_SST_FILAMENT_EVOLUTION_H

#pragma once

#include "sst/types.h"
#include <cstddef>
#include <string>
#include <vector>

namespace sst {

class FilamentEvolution {
public:
    explicit FilamentEvolution(double gamma = 1.0);

    static FilamentEvolution make_trefoil(std::size_t resolution = 400, double gamma = 1.0);
    static FilamentEvolution make_figure8(std::size_t resolution = 400, double gamma = 1.0);
    static FilamentEvolution make_from_fseries(const std::string& knot_id, std::size_t resolution = 1000, double gamma = 1.0);

    void evolve(double dt, std::size_t steps);

    [[nodiscard]] const std::vector<Vec3>& positions() const { return positions_; }
    [[nodiscard]] const std::vector<Vec3>& tangents() const { return tangents_; }
    [[nodiscard]] double circulation() const { return circulation_; }

    void set_positions(std::vector<Vec3> pts);
    void set_tangents(std::vector<Vec3> t);

private:
    std::vector<Vec3> positions_;
    std::vector<Vec3> tangents_;
    double circulation_;

    void compute_tangents();
    static void init_trefoil(std::vector<Vec3>& out, std::size_t resolution);
    static void init_figure8(std::vector<Vec3>& out, std::size_t resolution);
    static void init_from_fseries(std::vector<Vec3>& out, const std::string& knot_id, std::size_t resolution);
};

} // namespace sst

#endif // SSTCORE_SST_FILAMENT_EVOLUTION_H
