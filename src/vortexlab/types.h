#ifndef SSTCORE_VORTEXLAB_TYPES_H
#define SSTCORE_VORTEXLAB_TYPES_H

#pragma once

#include "sst/types.h"

#include <cstddef>
#include <string>
#include <vector>

namespace sst {

struct CurveComponent {
    std::string id;
    std::vector<Vec3> points;
    double circulation = 1.0;
};

struct CurveSet {
    std::vector<CurveComponent> components;
};

struct FilamentComponent {
    std::string id;
    std::string carrier = "A";
    std::vector<Vec3> points;
    double circulation = 1.0;
    bool dynamic = true;
    bool source = true;
    bool ghost = false;
};

struct FilamentSystemState {
    std::vector<FilamentComponent> filaments;
};

struct VelocityOptions {
    bool lia_only = false;
    bool include_external = false;  // parity default: pure self/mutual first
    bool include_mutual_friction = false;
    double a_sim = 0.0;
    double core_delta = 0.0;       // DELTA index proxy: use exp(core_delta)
    double lia_constant = 0.25;    // VortexLab C0 default ≈ 0.25
    double core_radius = 0.01;     // a
};

struct VelocityFieldResult {
    std::vector<std::vector<Vec3>> velocity;
    double maximum_speed = 0.0;
};

enum class ReachLimiter {
    Curvature,
    SelfDcsd,
    InterComponent,
    Tie,
    Error
};

struct PairWitness {
    std::size_t component_a = 0;
    std::size_t component_b = 0;
    double s = 0.0;
    double t = 0.0;
    Vec3 p{{0, 0, 0}};
    Vec3 q{{0, 0, 0}};
    double distance = 0.0;
    double orthogonality_residual = 0.0;
    bool local_minimum = false;
    double hss = 0.0;
    double htt = 0.0;
    double hst = 0.0;
    double hessian_det = 0.0;
    bool used_damped_least_squares = false;
};

struct ContinuousReachResult {
    double curvature_radius = 0.0;
    double self_dcsd = 0.0;
    double self_radius = 0.0;
    double inter_component_distance = 0.0;
    double inter_component_radius = 0.0;
    double reach = 0.0;
    ReachLimiter limiter = ReachLimiter::Error;
    PairWitness self_witness;
    PairWitness inter_witness;
    double orth_residual = 0.0;
    std::size_t component_count = 0;
};

struct TopologyClearanceResult {
    double clearance = 0.0;
    double self_min = 0.0;
    double inter_min = 0.0;
};

struct TopologyGuardResult {
    bool contact = false;
    bool warn_only = false;
    double safe_dt_fraction = 1.0;
    double clearance_before = 0.0;
    double clearance_after = 0.0;
    std::string message;
};

struct IntrinsicFrameResult {
    Vec3 centroid{{0, 0, 0}};
    Vec3 axis_x{{1, 0, 0}};
    Vec3 axis_y{{0, 1, 0}};
    Vec3 axis_z{{0, 0, 1}};
    Vec3 eigenvalues{{0, 0, 0}};
};

struct RigidMotionResult {
    Vec3 centroid{{0, 0, 0}};
    Vec3 translation{{0, 0, 0}};
    Vec3 omega{{0, 0, 0}};
    std::vector<Vec3> translation_field;
    std::vector<Vec3> rotation_field;
    std::vector<Vec3> deformation_field;
    double reconstruction_relative_error = 0.0;
    double deformation_relative_norm = 0.0;
};

struct PolygonalGaussResult {
    double signed_integral = 0.0;
    double absolute_integral = 0.0;
    int linking_integer_audit = 0;
};

inline const char* reach_limiter_name(ReachLimiter lim) {
    switch (lim) {
        case ReachLimiter::Curvature: return "CURVATURE";
        case ReachLimiter::SelfDcsd: return "SELF_DCSD";
        case ReachLimiter::InterComponent: return "INTER_COMPONENT";
        case ReachLimiter::Tie: return "TIE";
        default: return "ERROR";
    }
}

}  // namespace sst

#endif
