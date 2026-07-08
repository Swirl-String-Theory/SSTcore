#include "sst/filament/evolution.h"

#include "biot_savart.h"
#include "frenet_helicity.h"
#include "sst/knot.h"

#include <cmath>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

FilamentEvolution::FilamentEvolution(double gamma) : circulation_(gamma) {}

FilamentEvolution FilamentEvolution::make_trefoil(std::size_t resolution, double gamma) {
    FilamentEvolution ev(gamma);
    init_trefoil(ev.positions_, resolution);
    ev.compute_tangents();
    return ev;
}

FilamentEvolution FilamentEvolution::make_figure8(std::size_t resolution, double gamma) {
    FilamentEvolution ev(gamma);
    init_figure8(ev.positions_, resolution);
    ev.compute_tangents();
    return ev;
}

FilamentEvolution FilamentEvolution::make_from_fseries(const std::string& knot_id, std::size_t resolution, double gamma) {
    FilamentEvolution ev(gamma);
    init_from_fseries(ev.positions_, knot_id, resolution);
    ev.compute_tangents();
    return ev;
}

void FilamentEvolution::set_positions(std::vector<Vec3> pts) {
    positions_ = std::move(pts);
}

void FilamentEvolution::set_tangents(std::vector<Vec3> t) {
    tangents_ = std::move(t);
}

void FilamentEvolution::init_trefoil(std::vector<Vec3>& out, std::size_t resolution) {
    out.clear();
    out.reserve(resolution);
    for (std::size_t i = 0; i < resolution; ++i) {
        const double s = 2.0 * M_PI * static_cast<double>(i) / static_cast<double>(resolution);
        const double x = (2.0 + std::cos(3.0 * s)) * std::cos(2.0 * s);
        const double y = (2.0 + std::cos(3.0 * s)) * std::sin(2.0 * s);
        const double z = std::sin(3.0 * s);
        out.push_back({x, y, z});
    }
}

void FilamentEvolution::init_figure8(std::vector<Vec3>& out, std::size_t resolution) {
    out.clear();
    out.reserve(resolution);
    for (std::size_t i = 0; i < resolution; ++i) {
        const double s = 2.0 * M_PI * static_cast<double>(i) / static_cast<double>(resolution);
        const double x = (2.0 + std::cos(2.0 * s)) * std::cos(3.0 * s);
        const double y = (2.0 + std::cos(2.0 * s)) * std::sin(3.0 * s);
        const double z = std::sin(4.0 * s);
        out.push_back({x, y, z});
    }
}

void FilamentEvolution::init_from_fseries(std::vector<Vec3>& out, const std::string& knot_id, std::size_t resolution) {
    static std::map<std::string, std::string> embedded_files = sst::get_embedded_knot_files();
    const auto it = embedded_files.find(knot_id);
    if (it != embedded_files.end() && !it->second.empty()) {
        const std::vector<FourierBlock> blocks = FourierKnot::parse_fseries_from_string(it->second);
        const int idx = FourierKnot::index_of_largest_block(blocks);
        if (idx >= 0) {
            std::vector<double> s(resolution);
            const double twoPi = 2.0 * M_PI;
            for (std::size_t i = 0; i < resolution; ++i) {
                s[i] = twoPi * double(i) / double(resolution - 1);
            }
            out = FourierKnot::center_points(FourierKnot::evaluate(blocks[static_cast<std::size_t>(idx)], s));
            return;
        }
    }

    const std::string path = find_knot_file_path(knot_id, "");
    if (path.empty()) {
        throw std::runtime_error("Could not find .fseries file for knot: " + knot_id);
    }
    auto [pts, curv] = FourierKnot::load_knot(path, static_cast<int>(resolution));
    if (pts.empty()) {
        throw std::runtime_error("Failed to load knot " + knot_id + " from " + path);
    }
    out = std::move(pts);
    (void)curv;
}

void FilamentEvolution::compute_tangents() {
    tangents_.resize(positions_.size());
    const std::size_t n = positions_.size();
    for (std::size_t i = 0; i < n; ++i) {
        const Vec3& prev = positions_[(i + n - 1) % n];
        const Vec3& next = positions_[(i + 1) % n];
        tangents_[i] = Vec3{
            (next[0] - prev[0]) * 0.5,
            (next[1] - prev[1]) * 0.5,
            (next[2] - prev[2]) * 0.5,
        };
    }
}

void FilamentEvolution::evolve(double dt, std::size_t steps) {
    for (std::size_t step = 0; step < steps; ++step) {
        std::vector<Vec3> velocity;
        velocity.reserve(positions_.size());
        for (const auto& p : positions_) {
            velocity.push_back(biot_savart_velocity(p, positions_, tangents_, circulation_));
        }
        for (std::size_t i = 0; i < positions_.size(); ++i) {
            positions_[i][0] += dt * velocity[i][0];
            positions_[i][1] += dt * velocity[i][1];
            positions_[i][2] += dt * velocity[i][2];
        }
        compute_tangents();
    }
}

} // namespace sst
