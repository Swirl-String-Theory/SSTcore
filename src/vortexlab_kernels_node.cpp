// VortexLab kernel Node bindings (thin N-API wrappers).
#include <napi.h>
#include <cmath>
#include <string>
#include <vector>

#include "node_utils.h"
#include "analysis/intrinsic_frame.h"
#include "analysis/rigid_motion.h"
#include "curve/sampling.h"
#include "filament/integrator.h"
#include "filament/velocity_solver.h"
#include "geometry/continuous_reach.h"
#include "geometry/polygonal_clearance.h"
#include "geometry/smooth_tube_metrics.h"
#include "knot/polygonal_gauss.h"
#include "topology/topology_guard.h"
#include "vortexlab/types.h"

using namespace sst;

static std::vector<Vec3> read_points(const Napi::Value& v) {
    if (v.IsTypedArray()) return js_typedarray_to_vec3_list(v.As<Napi::TypedArray>());
    if (v.IsArray()) return js_array_to_vec3_list(v.As<Napi::Array>());
    throw Napi::TypeError::New(v.Env(), "Expected points as Array or Float64Array");
}

static Napi::Object points_obj(Napi::Env env, const std::vector<Vec3>& pts) {
    return vec3_list_to_js_array(env, pts).As<Napi::Object>();
}

static FilamentSystemState read_filaments(const Napi::Array& arr) {
    FilamentSystemState state;
    for (uint32_t i = 0; i < arr.Length(); ++i) {
        Napi::Object o = arr.Get(i).As<Napi::Object>();
        FilamentComponent f;
        if (o.Has("id")) f.id = o.Get("id").As<Napi::String>().Utf8Value();
        if (o.Has("carrier")) f.carrier = o.Get("carrier").As<Napi::String>().Utf8Value();
        f.points = read_points(o.Get("points"));
        if (o.Has("circulation")) f.circulation = o.Get("circulation").As<Napi::Number>().DoubleValue();
        if (o.Has("ghost")) f.ghost = o.Get("ghost").As<Napi::Boolean>().Value();
        if (o.Has("source")) f.source = o.Get("source").As<Napi::Boolean>().Value();
        state.filaments.push_back(std::move(f));
    }
    return state;
}

static VelocityOptions read_options(const Napi::Value& v) {
    VelocityOptions o;
    if (!v.IsObject()) return o;
    Napi::Object d = v.As<Napi::Object>();
    if (d.Has("liaOnly")) o.lia_only = d.Get("liaOnly").As<Napi::Boolean>().Value();
    if (d.Has("lia_only")) o.lia_only = d.Get("lia_only").As<Napi::Boolean>().Value();
    if (d.Has("aSim")) o.a_sim = d.Get("aSim").As<Napi::Number>().DoubleValue();
    if (d.Has("a_sim")) o.a_sim = d.Get("a_sim").As<Napi::Number>().DoubleValue();
    if (d.Has("coreDelta")) o.core_delta = d.Get("coreDelta").As<Napi::Number>().DoubleValue();
    if (d.Has("core_delta")) o.core_delta = d.Get("core_delta").As<Napi::Number>().DoubleValue();
    if (d.Has("liaConstant")) o.lia_constant = d.Get("liaConstant").As<Napi::Number>().DoubleValue();
    if (d.Has("coreRadius")) o.core_radius = d.Get("coreRadius").As<Napi::Number>().DoubleValue();
    if (d.Has("core_radius")) o.core_radius = d.Get("core_radius").As<Napi::Number>().DoubleValue();
    return o;
}

static std::vector<std::vector<Vec3>> read_curve_list(const Napi::Array& arr) {
    std::vector<std::vector<Vec3>> out;
    for (uint32_t i = 0; i < arr.Length(); ++i) out.push_back(read_points(arr.Get(i)));
    return out;
}

static Napi::Value ResampleClosedCurve(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto pts = read_points(info[0]);
    std::size_t n = static_cast<std::size_t>(info[1].As<Napi::Number>().Uint32Value());
    return points_obj(env, curve::CurveSampling::resample_closed_arclength(pts, n));
}

static Napi::Value SampleCurve(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto pts = read_points(info[0]);
    std::size_t n = static_cast<std::size_t>(info[1].As<Napi::Number>().Uint32Value());
    bool arc = info.Length() > 2 ? info[2].As<Napi::Boolean>().Value() : true;
    if (!arc || pts.size() == n) return points_obj(env, pts);
    return points_obj(env, curve::CurveSampling::resample_closed_arclength(pts, n));
}

static Napi::Value ComputePolygonalGauss(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto a = read_points(info[0]);
    bool same = true;
    PolygonalGaussResult r;
    if (info.Length() > 1 && info[1].IsArray()) {
        same = false;
        r = knot::PolygonalGaussInvariants::linking(a, read_points(info[1]));
    } else {
        if (info.Length() > 2) same = info[2].As<Napi::Boolean>().Value();
        r = same ? knot::PolygonalGaussInvariants::writhe(a)
                 : knot::PolygonalGaussInvariants::linking(a, a);
    }
    Napi::Object o = Napi::Object::New(env);
    o.Set("signedIntegral", r.signed_integral);
    o.Set("absoluteIntegral", r.absolute_integral);
    o.Set("linkingIntegerAudit", r.linking_integer_audit);
    return o;
}

static Napi::Value AnalyzeResolvedTube(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto curves = read_curve_list(info[0].As<Napi::Array>());
    double core = info.Length() > 1 ? info[1].As<Napi::Number>().DoubleValue() : 0.0;
    auto r = geometry::multi_component_clearance(curves, core);
    Napi::Object o = Napi::Object::New(env);
    o.Set("clearance", r.clearance);
    o.Set("selfMin", r.self_min);
    o.Set("interMin", r.inter_min);
    return o;
}

static Napi::Value ComputeTopologyClearance(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto curves = read_curve_list(info[0].As<Napi::Array>());
    double core = info.Length() > 1 ? info[1].As<Napi::Number>().DoubleValue() : 0.0;
    auto r = topology::TopologyGuard::compute_clearance(curves, core);
    Napi::Object o = Napi::Object::New(env);
    o.Set("clearance", r.clearance);
    o.Set("selfMin", r.self_min);
    o.Set("interMin", r.inter_min);
    return o;
}

static Napi::Value ComputeContinuousReach(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto curves = read_curve_list(info[0].As<Napi::Array>());
    auto r = geometry::ContinuousReachSolver::compute(curves);
    Napi::Object o = Napi::Object::New(env);
    o.Set("curvatureRadius", r.curvature_radius);
    o.Set("selfDcsd", r.self_dcsd);
    o.Set("selfRadius", r.self_radius);
    o.Set("interComponentDistance", r.inter_component_distance);
    o.Set("interComponentRadius", r.inter_component_radius);
    o.Set("reach", r.reach);
    o.Set("limiter", reach_limiter_name(r.limiter));
    o.Set("orthResidual", r.orth_residual);
    o.Set("componentCount", static_cast<double>(r.component_count));
    o.Set("curvatureIntervalsExamined", static_cast<double>(r.curvature_intervals_examined));
    o.Set("dcsdSeedCount", static_cast<double>(r.dcsd_seed_count));
    o.Set("dcsdRefinedCount", static_cast<double>(r.dcsd_refined_count));
    o.Set("dcsdRejectedCount", static_cast<double>(r.dcsd_rejected_count));
    o.Set("searchResolution", r.search_resolution);
    o.Set("refinementTolerance", r.refinement_tolerance);
    o.Set("searchConverged", r.search_converged);
    return o;
}

static Napi::Value AnalyzeSmoothResolvedTube(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto curves = read_curve_list(info[0].As<Napi::Array>());
    const double abs_tol = info.Length() > 1 ? info[1].As<Napi::Number>().DoubleValue() : 1e-10;
    const double rel_tol = info.Length() > 2 ? info[2].As<Napi::Number>().DoubleValue() : 1e-10;
    auto mtr = geometry::SmoothTubeAnalyzer::analyze(curves, abs_tol, rel_tol);
    const auto& r = mtr.reach_detail;
    Napi::Object o = Napi::Object::New(env);
    o.Set("splineLength", mtr.spline_length);
    o.Set("splineLengthError", mtr.spline_length_error);
    o.Set("curvatureRadius", mtr.curvature_radius);
    o.Set("selfDcsd", mtr.self_dcsd);
    o.Set("selfRadius", mtr.self_radius);
    o.Set("interComponentRadius", mtr.inter_component_radius);
    o.Set("reach", mtr.reach);
    o.Set("ropelengthRad", mtr.ropelength_rad);
    o.Set("ropelengthDiam", mtr.ropelength_diam);
    o.Set("orthogonalityResidual", mtr.orthogonality_residual);
    o.Set("converged", mtr.converged);
    o.Set("limiter", reach_limiter_name(r.limiter));
    o.Set("curvatureIntervalsExamined", static_cast<double>(r.curvature_intervals_examined));
    o.Set("dcsdSeedCount", static_cast<double>(r.dcsd_seed_count));
    o.Set("dcsdRefinedCount", static_cast<double>(r.dcsd_refined_count));
    o.Set("dcsdRejectedCount", static_cast<double>(r.dcsd_rejected_count));
    o.Set("searchResolution", r.search_resolution);
    o.Set("refinementTolerance", r.refinement_tolerance);
    o.Set("searchConverged", r.search_converged);
    o.Set("lengthIntervalCount", static_cast<double>(mtr.length_detail.interval_count));
    o.Set("lengthConverged", mtr.length_detail.converged);
    return o;
}

static Napi::Value ComputeFilamentVelocity(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto state = read_filaments(info[0].As<Napi::Array>());
    auto opt = info.Length() > 1 ? read_options(info[1]) : VelocityOptions{};
    auto r = filament::FilamentVelocitySolver::evaluate(state, opt);
    Napi::Array vel = Napi::Array::New(env, r.velocity.size());
    for (std::size_t i = 0; i < r.velocity.size(); ++i)
        vel.Set(static_cast<uint32_t>(i), points_obj(env, r.velocity[i]));
    Napi::Object o = Napi::Object::New(env);
    o.Set("velocity", vel);
    o.Set("maximumSpeed", r.maximum_speed);
    return o;
}

static Napi::Value ComputeRegularizedMutualVelocity(const Napi::CallbackInfo& info) {
    return ComputeFilamentVelocity(info);
}

static Napi::Value Rk4Step(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto state = read_filaments(info[0].As<Napi::Array>());
    double dt = info[1].As<Napi::Number>().DoubleValue();
    auto opt = info.Length() > 2 ? read_options(info[2]) : VelocityOptions{};
    auto r = filament::FilamentIntegrator::rk4_step(state, dt, opt);
    Napi::Array fils = Napi::Array::New(env, r.state.filaments.size());
    for (std::size_t i = 0; i < r.state.filaments.size(); ++i) {
        const auto& f = r.state.filaments[i];
        Napi::Object o = Napi::Object::New(env);
        o.Set("id", f.id);
        o.Set("carrier", f.carrier);
        o.Set("points", points_obj(env, f.points));
        o.Set("circulation", f.circulation);
        o.Set("ghost", f.ghost);
        fils.Set(static_cast<uint32_t>(i), o);
    }
    Napi::Object out = Napi::Object::New(env);
    out.Set("filaments", fils);
    out.Set("maximumStageSpeed", r.maximum_stage_speed);
    return out;
}

static Napi::Value EstimateCflDt(const Napi::CallbackInfo& info) {
    auto state = read_filaments(info[0].As<Napi::Array>());
    auto opt = info.Length() > 1 ? read_options(info[1]) : VelocityOptions{};
    double cfl = info.Length() > 2 ? info[2].As<Napi::Number>().DoubleValue() : 0.5;
    return Napi::Number::New(info.Env(),
        filament::FilamentIntegrator::estimate_cfl_dt(state, opt, cfl));
}

static Napi::Value GuardTopologyStep(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto before = read_curve_list(info[0].As<Napi::Array>());
    auto after = read_curve_list(info[1].As<Napi::Array>());
    double thr = info[2].As<Napi::Number>().DoubleValue();
    double dmax = info[3].As<Napi::Number>().DoubleValue();
    double core = info.Length() > 4 ? info[4].As<Napi::Number>().DoubleValue() : 0.0;
    auto r = topology::TopologyGuard::guard_step(before, after, thr, dmax, core);
    Napi::Object o = Napi::Object::New(env);
    o.Set("contact", r.contact);
    o.Set("warnOnly", r.warn_only);
    o.Set("safeDtFraction", r.safe_dt_fraction);
    o.Set("clearanceBefore", r.clearance_before);
    o.Set("clearanceAfter", r.clearance_after);
    o.Set("message", r.message);
    return o;
}

static Napi::Value ComputeIntrinsicFrame(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto pts = read_points(info[0]);
    auto r = analysis::IntrinsicFrame::compute(pts, nullptr);
    Napi::Object o = Napi::Object::New(env);
    o.Set("centroid", points_obj(env, {r.centroid}).Get(uint32_t(0)));
    o.Set("axisX", points_obj(env, {r.axis_x}).Get(uint32_t(0)));
    o.Set("axisY", points_obj(env, {r.axis_y}).Get(uint32_t(0)));
    o.Set("axisZ", points_obj(env, {r.axis_z}).Get(uint32_t(0)));
    o.Set("eigenvalues", points_obj(env, {r.eigenvalues}).Get(uint32_t(0)));
    return o;
}

static Napi::Value ComputeRigidMotion(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto pts = read_points(info[0]);
    auto vel = read_points(info[1]);
    auto r = analysis::RigidMotion::fit(pts, vel, nullptr);
    Napi::Object o = Napi::Object::New(env);
    o.Set("centroid", points_obj(env, {r.centroid}).Get(uint32_t(0)));
    o.Set("translation", points_obj(env, {r.translation}).Get(uint32_t(0)));
    o.Set("omega", points_obj(env, {r.omega}).Get(uint32_t(0)));
    o.Set("translationField", points_obj(env, r.translation_field));
    o.Set("rotationField", points_obj(env, r.rotation_field));
    o.Set("deformationField", points_obj(env, r.deformation_field));
    o.Set("reconstructionRelativeError", r.reconstruction_relative_error);
    o.Set("deformationRelativeNorm", r.deformation_relative_norm);
    return o;
}

void bind_vortexlab_kernels(Napi::Env env, Napi::Object exports) {
    exports.Set("resampleClosedCurve", Napi::Function::New(env, ResampleClosedCurve));
    exports.Set("sampleCurve", Napi::Function::New(env, SampleCurve));
    exports.Set("computePolygonalGauss", Napi::Function::New(env, ComputePolygonalGauss));
    exports.Set("analyzeResolvedTube", Napi::Function::New(env, AnalyzeResolvedTube));
    exports.Set("computeTopologyClearance", Napi::Function::New(env, ComputeTopologyClearance));
    exports.Set("computeContinuousReach", Napi::Function::New(env, ComputeContinuousReach));
    exports.Set("analyzeSmoothResolvedTube", Napi::Function::New(env, AnalyzeSmoothResolvedTube));
    exports.Set("computeFilamentVelocity", Napi::Function::New(env, ComputeFilamentVelocity));
    exports.Set("computeRegularizedMutualVelocity", Napi::Function::New(env, ComputeRegularizedMutualVelocity));
    exports.Set("rk4Step", Napi::Function::New(env, Rk4Step));
    exports.Set("estimateCflDt", Napi::Function::New(env, EstimateCflDt));
    exports.Set("guardTopologyStep", Napi::Function::New(env, GuardTopologyStep));
    exports.Set("computeIntrinsicFrame", Napi::Function::New(env, ComputeIntrinsicFrame));
    exports.Set("computeRigidMotion", Napi::Function::New(env, ComputeRigidMotion));
}
