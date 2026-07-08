#ifndef SSTCORE_SST_KNOT_INVARIANTS_H
#define SSTCORE_SST_KNOT_INVARIANTS_H

#pragma once

#include "sst/knot/fourier_types.h"
#include "sst/particle/types.h"
#include "sst/types.h"

#include <array>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace sst {

class KnotDynamics {
public:
    static double compute_writhe(const std::vector<Vec3>& centerline);
    static int compute_linking_number(const std::vector<Vec3>& curve1, const std::vector<Vec3>& curve2);
    static double compute_twist(const std::vector<Vec3>& T, const std::vector<Vec3>& B);
    static double compute_centerline_helicity(const std::vector<Vec3>& curve,
                                              const std::vector<Vec3>& tangent);
    static std::vector<std::pair<int, int>> detect_reconnection_candidates(
        const std::vector<Vec3>& curve, double threshold);

    struct FourierResult {
        std::vector<Vec3> positions;
        std::vector<Vec3> tangents;
    };
    static FourierResult evaluate_fourier_series(
        const std::vector<std::array<double, 6>>& coeffs,
        const std::vector<double>& t_vals);

    static double writhe_gauss_curve(
        const std::vector<Vec3>& r,
        const std::vector<Vec3>& r_t);

    static int estimate_crossing_number(
        const std::vector<Vec3>& r,
        int directions = 24,
        int seed = 12345);

    using Crossing = std::array<int, 4>;
    using PD = std::vector<Crossing>;
    static PD pd_from_curve(
        const std::vector<Vec3>& P3,
        int tries = 40,
        unsigned int seed = 12345,
        double min_angle_deg = 1.0,
        double depth_tol = 1e-6);

    static std::vector<Vec3> compute_biot_savart_velocity_grid(
        const std::vector<Vec3>& curve,
        const std::vector<Vec3>& grid_points);

    static std::vector<Vec3> compute_vorticity_grid(
        const std::vector<Vec3>& velocity,
        const std::array<int, 3>& shape,
        double spacing);

    static std::vector<Vec3> extract_interior_field(
        const std::vector<Vec3>& field,
        const std::array<int, 3>& shape,
        int margin);

    static std::tuple<double, double, double> compute_helicity_invariants(
        const std::vector<Vec3>& v_sub,
        const std::vector<Vec3>& w_sub,
        const std::vector<double>& r_sq);

    static std::tuple<double, double, double> compute_helicity_from_fourier_block(
        const FourierBlock& block,
        int grid_size = 32,
        double spacing = 0.1,
        int interior_margin = 8,
        int nsamples = 1000);
};

KnotInvariants build_invariants_from_fourier_block(
    const FourierBlock& block,
    const std::string& knot_name = "",
    int crossing_number = 0,
    int braid_index = 0,
    int seifert_genus = 0,
    int chirality = 0,
    bool hyperbolic = false,
    double hyperbolic_volume = 0.0,
    int nsamples = 2048,
    int exclude_window = 4);

KnotInvariants build_invariants_from_fseries(
    const std::string& path,
    const std::string& knot_name = "",
    int crossing_number = 0,
    int braid_index = 0,
    int seifert_genus = 0,
    int chirality = 0,
    bool hyperbolic = false,
    double hyperbolic_volume = 0.0,
    int nsamples = 2048,
    int exclude_window = 4);

inline double compute_writhe(const std::vector<Vec3>& centerline) {
    return KnotDynamics::compute_writhe(centerline);
}

inline int compute_linking_number(const std::vector<Vec3>& curve1, const std::vector<Vec3>& curve2) {
    return KnotDynamics::compute_linking_number(curve1, curve2);
}

inline double compute_twist(const std::vector<Vec3>& T, const std::vector<Vec3>& B) {
    return KnotDynamics::compute_twist(T, B);
}

inline double compute_centerline_helicity(const std::vector<Vec3>& curve,
                                          const std::vector<Vec3>& tangent) {
    return KnotDynamics::compute_centerline_helicity(curve, tangent);
}

inline std::vector<std::pair<int, int>> detect_reconnection_candidates(
    const std::vector<Vec3>& curve, double threshold) {
    return KnotDynamics::detect_reconnection_candidates(curve, threshold);
}

} // namespace sst

#endif // SSTCORE_SST_KNOT_INVARIANTS_H
