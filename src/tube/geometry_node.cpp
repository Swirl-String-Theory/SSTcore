// tube/geometry_node.cpp — N-API bindings for the resolved-tube geometry suite
//
// Mirrors src/tube/geometry_py.cpp. POD structs are exposed as plain JS objects
// (with converter helpers both directions); point lists are arrays of [x, y, z]
// (or a flat Float64Array). ResolvedTubeGeometry, ResolvedTubeTightener and
// ContactStressMap are exposed as thin ObjectWraps holding static methods, and
// the py convenience free functions are mirrored as camelCase exports.
#include <napi.h>
#include <cstddef>
#include <string>
#include <vector>
#include "node_utils.h"
#include "sst/tube/geometry.h"

using namespace sst;

namespace {

// ---------------------------------------------------------------------------
// Primitive helpers
// ---------------------------------------------------------------------------
double num(Napi::Object o, const char* k, double def) {
    return o.Has(k) ? o.Get(k).As<Napi::Number>().DoubleValue() : def;
}
int inum(Napi::Object o, const char* k, int def) {
    return o.Has(k) ? o.Get(k).As<Napi::Number>().Int32Value() : def;
}
std::size_t usize(Napi::Object o, const char* k, std::size_t def) {
    return o.Has(k) ? static_cast<std::size_t>(o.Get(k).As<Napi::Number>().Int64Value()) : def;
}
bool bval(Napi::Object o, const char* k, bool def) {
    return o.Has(k) ? o.Get(k).As<Napi::Boolean>().Value() : def;
}
std::string sval(Napi::Object o, const char* k, const std::string& def) {
    return o.Has(k) ? o.Get(k).As<Napi::String>().Utf8Value() : def;
}

double opt_double(const Napi::CallbackInfo& info, size_t i, double def) {
    return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().DoubleValue() : def;
}
int opt_int(const Napi::CallbackInfo& info, size_t i, int def) {
    return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().Int32Value() : def;
}
bool opt_bool(const Napi::CallbackInfo& info, size_t i, bool def) {
    return (info.Length() > i && info[i].IsBoolean()) ? info[i].As<Napi::Boolean>().Value() : def;
}
std::size_t opt_size(const Napi::CallbackInfo& info, size_t i, std::size_t def) {
    return (info.Length() > i && info[i].IsNumber())
               ? static_cast<std::size_t>(info[i].As<Napi::Number>().Int64Value())
               : def;
}

Napi::Float64Array to_f64(Napi::Env env, const std::vector<double>& v) {
    Napi::Float64Array a = Napi::Float64Array::New(env, v.size());
    for (size_t i = 0; i < v.size(); ++i) {
        a[i] = v[i];
    }
    return a;
}

std::vector<double> read_doubles(const Napi::Value& v) {
    std::vector<double> out;
    if (v.IsArray()) {
        Napi::Array a = v.As<Napi::Array>();
        out.reserve(a.Length());
        for (uint32_t i = 0; i < a.Length(); ++i) {
            out.push_back(a.Get(i).As<Napi::Number>().DoubleValue());
        }
    } else if (v.IsTypedArray()) {
        Napi::TypedArray ta = v.As<Napi::TypedArray>();
        if (ta.TypedArrayType() == napi_float64_array) {
            Napi::Float64Array fa = ta.As<Napi::Float64Array>();
            const double* d = fa.Data();
            out.assign(d, d + fa.ElementLength());
        } else {
            const size_t n = ta.ElementLength();
            Napi::Object obj = ta.As<Napi::Object>();
            out.reserve(n);
            for (size_t i = 0; i < n; ++i) {
                out.push_back(obj.Get(static_cast<uint32_t>(i)).As<Napi::Number>().DoubleValue());
            }
        }
    } else {
        throw Napi::TypeError::New(v.Env(), "Expected an array or Float64Array of numbers");
    }
    return out;
}

std::vector<Vec3> read_points(const Napi::Value& v) {
    if (v.IsArray()) return js_array_to_vec3_list(v.As<Napi::Array>());
    if (v.IsTypedArray()) return js_typedarray_to_vec3_list(v.As<Napi::TypedArray>());
    throw Napi::TypeError::New(v.Env(), "points must be an array of [x,y,z] or a Float64Array");
}

Vec3 read_vec3(const Napi::Value& v) {
    if (!v.IsArray()) throw Napi::TypeError::New(v.Env(), "Expected a [x,y,z] array");
    Napi::Array a = v.As<Napi::Array>();
    return {a.Get(0u).As<Napi::Number>().DoubleValue(),
            a.Get(1u).As<Napi::Number>().DoubleValue(),
            a.Get(2u).As<Napi::Number>().DoubleValue()};
}

// ---------------------------------------------------------------------------
// SegmentPair
// ---------------------------------------------------------------------------
Napi::Object segment_pair_to_js(Napi::Env env, const SegmentPair& p) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("i", Napi::Number::New(env, static_cast<double>(p.i)));
    o.Set("j", Napi::Number::New(env, static_cast<double>(p.j)));
    o.Set("s", Napi::Number::New(env, p.s));
    o.Set("t", Napi::Number::New(env, p.t));
    o.Set("distance", Napi::Number::New(env, p.distance));
    o.Set("arclength_i", Napi::Number::New(env, p.arclength_i));
    o.Set("arclength_j", Napi::Number::New(env, p.arclength_j));
    return o;
}
SegmentPair segment_pair_from_js(Napi::Object o) {
    SegmentPair p;
    p.i = usize(o, "i", 0);
    p.j = usize(o, "j", 0);
    p.s = num(o, "s", 0.0);
    p.t = num(o, "t", 0.0);
    p.distance = num(o, "distance", 0.0);
    p.arclength_i = num(o, "arclength_i", 0.0);
    p.arclength_j = num(o, "arclength_j", 0.0);
    return p;
}

// ---------------------------------------------------------------------------
// KinkRecord
// ---------------------------------------------------------------------------
Napi::Object kink_record_to_js(Napi::Env env, const KinkRecord& k) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("vertex", Napi::Number::New(env, static_cast<double>(k.vertex)));
    o.Set("minrad_minus", Napi::Number::New(env, k.minrad_minus));
    o.Set("minrad_plus", Napi::Number::New(env, k.minrad_plus));
    o.Set("minrad", Napi::Number::New(env, k.minrad));
    o.Set("turning_angle", Napi::Number::New(env, k.turning_angle));
    return o;
}
KinkRecord kink_record_from_js(Napi::Object o) {
    KinkRecord k;
    k.vertex = usize(o, "vertex", 0);
    k.minrad_minus = num(o, "minrad_minus", 0.0);
    k.minrad_plus = num(o, "minrad_plus", 0.0);
    k.minrad = num(o, "minrad", 0.0);
    k.turning_angle = num(o, "turning_angle", 0.0);
    return k;
}

// ---------------------------------------------------------------------------
// ResolvedTubeMetrics
// ---------------------------------------------------------------------------
Napi::Object metrics_to_js(Napi::Env env, const ResolvedTubeMetrics& m) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("length", Napi::Number::New(env, m.length));
    o.Set("minrad", Napi::Number::New(env, m.minrad));
    o.Set("min_dcsd", Napi::Number::New(env, m.min_dcsd));
    o.Set("half_min_dcsd", Napi::Number::New(env, m.half_min_dcsd));
    o.Set("thickness_rad", Napi::Number::New(env, m.thickness_rad));
    o.Set("reach_rad", Napi::Number::New(env, m.reach_rad));
    o.Set("ropelength_rad", Napi::Number::New(env, m.ropelength_rad));
    o.Set("ropelength_diam", Napi::Number::New(env, m.ropelength_diam));
    o.Set("edge_length_mean", Napi::Number::New(env, m.edge_length_mean));
    o.Set("edge_length_rel_std", Napi::Number::New(env, m.edge_length_rel_std));
    o.Set("equilateral_ok", Napi::Boolean::New(env, m.equilateral_ok));
    o.Set("lower_bound_ok", Napi::Boolean::New(env, m.lower_bound_ok));
    Napi::Array struts = Napi::Array::New(env, m.struts.size());
    for (size_t i = 0; i < m.struts.size(); ++i) {
        struts.Set(static_cast<uint32_t>(i), segment_pair_to_js(env, m.struts[i]));
    }
    o.Set("struts", struts);
    Napi::Array kinks = Napi::Array::New(env, m.kinks.size());
    for (size_t i = 0; i < m.kinks.size(); ++i) {
        kinks.Set(static_cast<uint32_t>(i), kink_record_to_js(env, m.kinks[i]));
    }
    o.Set("kinks", kinks);
    return o;
}
ResolvedTubeMetrics metrics_from_js(Napi::Object o) {
    ResolvedTubeMetrics m;
    m.length = num(o, "length", 0.0);
    m.minrad = num(o, "minrad", 0.0);
    m.min_dcsd = num(o, "min_dcsd", 0.0);
    m.half_min_dcsd = num(o, "half_min_dcsd", 0.0);
    m.thickness_rad = num(o, "thickness_rad", 0.0);
    m.reach_rad = num(o, "reach_rad", 0.0);
    m.ropelength_rad = num(o, "ropelength_rad", 0.0);
    m.ropelength_diam = num(o, "ropelength_diam", 0.0);
    m.edge_length_mean = num(o, "edge_length_mean", 0.0);
    m.edge_length_rel_std = num(o, "edge_length_rel_std", 0.0);
    m.equilateral_ok = bval(o, "equilateral_ok", false);
    m.lower_bound_ok = bval(o, "lower_bound_ok", true);
    if (o.Has("struts") && o.Get("struts").IsArray()) {
        Napi::Array arr = o.Get("struts").As<Napi::Array>();
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            m.struts.push_back(segment_pair_from_js(arr.Get(i).As<Napi::Object>()));
        }
    }
    if (o.Has("kinks") && o.Get("kinks").IsArray()) {
        Napi::Array arr = o.Get("kinks").As<Napi::Array>();
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            m.kinks.push_back(kink_record_from_js(arr.Get(i).As<Napi::Object>()));
        }
    }
    return m;
}

// ---------------------------------------------------------------------------
// Sparse / rigidity matrices
// ---------------------------------------------------------------------------
Napi::Object sparse_entry_to_js(Napi::Env env, const SparseEntry& e) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("row", Napi::Number::New(env, static_cast<double>(e.row)));
    o.Set("value", Napi::Number::New(env, e.value));
    return o;
}
SparseEntry sparse_entry_from_js(Napi::Object o) {
    SparseEntry e;
    e.row = usize(o, "row", 0);
    e.value = num(o, "value", 0.0);
    return e;
}

Napi::Object rigidity_column_to_js(Napi::Env env, const RigidityColumn& c) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("kind", Napi::String::New(env, c.kind));
    o.Set("strut_index", Napi::Number::New(env, static_cast<double>(c.strut_index)));
    o.Set("kink_index", Napi::Number::New(env, static_cast<double>(c.kink_index)));
    o.Set("vertex", Napi::Number::New(env, static_cast<double>(c.vertex)));
    o.Set("norm", Napi::Number::New(env, c.norm));
    o.Set("values", to_f64(env, c.values));
    return o;
}
RigidityColumn rigidity_column_from_js(Napi::Object o) {
    RigidityColumn c;
    c.kind = sval(o, "kind", "");
    c.strut_index = usize(o, "strut_index", 0);
    c.kink_index = usize(o, "kink_index", 0);
    c.vertex = usize(o, "vertex", 0);
    c.norm = num(o, "norm", 0.0);
    if (o.Has("values")) c.values = read_doubles(o.Get("values"));
    return c;
}

Napi::Object rigidity_matrix_to_js(Napi::Env env, const RigidityMatrix& m) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("row_count", Napi::Number::New(env, static_cast<double>(m.row_count)));
    o.Set("column_count", Napi::Number::New(env, static_cast<double>(m.column_count)));
    Napi::Array cols = Napi::Array::New(env, m.columns.size());
    for (size_t i = 0; i < m.columns.size(); ++i) {
        cols.Set(static_cast<uint32_t>(i), rigidity_column_to_js(env, m.columns[i]));
    }
    o.Set("columns", cols);
    return o;
}
RigidityMatrix rigidity_matrix_from_js(Napi::Object o) {
    RigidityMatrix m;
    m.row_count = usize(o, "row_count", 0);
    m.column_count = usize(o, "column_count", 0);
    if (o.Has("columns") && o.Get("columns").IsArray()) {
        Napi::Array arr = o.Get("columns").As<Napi::Array>();
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            m.columns.push_back(rigidity_column_from_js(arr.Get(i).As<Napi::Object>()));
        }
    }
    return m;
}

Napi::Object sparse_rigidity_column_to_js(Napi::Env env, const SparseRigidityColumn& c) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("kind", Napi::String::New(env, c.kind));
    o.Set("strut_index", Napi::Number::New(env, static_cast<double>(c.strut_index)));
    o.Set("kink_index", Napi::Number::New(env, static_cast<double>(c.kink_index)));
    o.Set("vertex", Napi::Number::New(env, static_cast<double>(c.vertex)));
    o.Set("norm", Napi::Number::New(env, c.norm));
    Napi::Array entries = Napi::Array::New(env, c.entries.size());
    for (size_t i = 0; i < c.entries.size(); ++i) {
        entries.Set(static_cast<uint32_t>(i), sparse_entry_to_js(env, c.entries[i]));
    }
    o.Set("entries", entries);
    return o;
}
SparseRigidityColumn sparse_rigidity_column_from_js(Napi::Object o) {
    SparseRigidityColumn c;
    c.kind = sval(o, "kind", "");
    c.strut_index = usize(o, "strut_index", 0);
    c.kink_index = usize(o, "kink_index", 0);
    c.vertex = usize(o, "vertex", 0);
    c.norm = num(o, "norm", 0.0);
    if (o.Has("entries") && o.Get("entries").IsArray()) {
        Napi::Array arr = o.Get("entries").As<Napi::Array>();
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            c.entries.push_back(sparse_entry_from_js(arr.Get(i).As<Napi::Object>()));
        }
    }
    return c;
}

Napi::Object sparse_rigidity_matrix_to_js(Napi::Env env, const SparseRigidityMatrix& m) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("row_count", Napi::Number::New(env, static_cast<double>(m.row_count)));
    o.Set("column_count", Napi::Number::New(env, static_cast<double>(m.column_count)));
    o.Set("nonzero_count", Napi::Number::New(env, static_cast<double>(m.nonzero_count)));
    Napi::Array cols = Napi::Array::New(env, m.columns.size());
    for (size_t i = 0; i < m.columns.size(); ++i) {
        cols.Set(static_cast<uint32_t>(i), sparse_rigidity_column_to_js(env, m.columns[i]));
    }
    o.Set("columns", cols);
    return o;
}
SparseRigidityMatrix sparse_rigidity_matrix_from_js(Napi::Object o) {
    SparseRigidityMatrix m;
    m.row_count = usize(o, "row_count", 0);
    m.column_count = usize(o, "column_count", 0);
    m.nonzero_count = usize(o, "nonzero_count", 0);
    if (o.Has("columns") && o.Get("columns").IsArray()) {
        Napi::Array arr = o.Get("columns").As<Napi::Array>();
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            m.columns.push_back(sparse_rigidity_column_from_js(arr.Get(i).As<Napi::Object>()));
        }
    }
    return m;
}

// ---------------------------------------------------------------------------
// NNLSResult
// ---------------------------------------------------------------------------
Napi::Object nnls_result_to_js(Napi::Env env, const NNLSResult& r) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("multipliers", to_f64(env, r.multipliers));
    o.Set("residual_norm", Napi::Number::New(env, r.residual_norm));
    o.Set("relative_residual", Napi::Number::New(env, r.relative_residual));
    o.Set("objective", Napi::Number::New(env, r.objective));
    o.Set("iterations", Napi::Number::New(env, static_cast<double>(r.iterations)));
    o.Set("converged", Napi::Boolean::New(env, r.converged));
    o.Set("algorithm", Napi::String::New(env, r.algorithm));
    o.Set("active_set_size", Napi::Number::New(env, static_cast<double>(r.active_set_size)));
    return o;
}

// ---------------------------------------------------------------------------
// TighteningOptions (input)
// ---------------------------------------------------------------------------
TighteningOptions tightening_options_from_js(const Napi::Value& v) {
    TighteningOptions t;
    if (!v.IsObject()) return t;
    Napi::Object o = v.As<Napi::Object>();
    t.max_steps = usize(o, "max_steps", t.max_steps);
    t.line_search_trials = usize(o, "line_search_trials", t.line_search_trials);
    t.nnls_max_iterations = usize(o, "nnls_max_iterations", t.nnls_max_iterations);
    t.skip_neighbors = inum(o, "skip_neighbors", t.skip_neighbors);
    t.contact_tol = num(o, "contact_tol", t.contact_tol);
    t.equilateral_tol = num(o, "equilateral_tol", t.equilateral_tol);
    t.target_kkt_residual = num(o, "target_kkt_residual", t.target_kkt_residual);
    t.nnls_tolerance = num(o, "nnls_tolerance", t.nnls_tolerance);
    t.max_step_size = num(o, "max_step_size", t.max_step_size);
    t.min_step_size = num(o, "min_step_size", t.min_step_size);
    t.line_search_shrink = num(o, "line_search_shrink", t.line_search_shrink);
    t.thickness_floor_fraction = num(o, "thickness_floor_fraction", t.thickness_floor_fraction);
    t.ropelength_increase_tolerance = num(o, "ropelength_increase_tolerance", t.ropelength_increase_tolerance);
    t.newton_correction_damping = num(o, "newton_correction_damping", t.newton_correction_damping);
    t.newton_ridge = num(o, "newton_ridge", t.newton_ridge);
    t.use_sparse_solver = bval(o, "use_sparse_solver", t.use_sparse_solver);
    t.use_active_set_solver = bval(o, "use_active_set_solver", t.use_active_set_solver);
    t.use_analytic_kink_gradient = bval(o, "use_analytic_kink_gradient", t.use_analytic_kink_gradient);
    t.normalize_direction = bval(o, "normalize_direction", t.normalize_direction);
    t.preserve_initial_thickness = bval(o, "preserve_initial_thickness", t.preserve_initial_thickness);
    t.correction_strategy = sval(o, "correction_strategy", t.correction_strategy);
    return t;
}

Napi::Object step_record_to_js(Napi::Env env, const TighteningStepRecord& s) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("step", Napi::Number::New(env, static_cast<double>(s.step)));
    o.Set("ropelength_before", Napi::Number::New(env, s.ropelength_before));
    o.Set("ropelength_after", Napi::Number::New(env, s.ropelength_after));
    o.Set("thickness_before", Napi::Number::New(env, s.thickness_before));
    o.Set("thickness_after", Napi::Number::New(env, s.thickness_after));
    o.Set("length_before", Napi::Number::New(env, s.length_before));
    o.Set("length_after", Napi::Number::New(env, s.length_after));
    o.Set("kkt_residual_before", Napi::Number::New(env, s.kkt_residual_before));
    o.Set("projected_gradient_norm", Napi::Number::New(env, s.projected_gradient_norm));
    o.Set("alpha", Napi::Number::New(env, s.alpha));
    o.Set("strut_count", Napi::Number::New(env, static_cast<double>(s.strut_count)));
    o.Set("kink_count", Napi::Number::New(env, static_cast<double>(s.kink_count)));
    o.Set("rigidity_columns", Napi::Number::New(env, static_cast<double>(s.rigidity_columns)));
    o.Set("accepted", Napi::Boolean::New(env, s.accepted));
    o.Set("thickness_corrected", Napi::Boolean::New(env, s.thickness_corrected));
    o.Set("correction_strategy", Napi::String::New(env, s.correction_strategy));
    o.Set("solver_algorithm", Napi::String::New(env, s.solver_algorithm));
    return o;
}

Napi::Object tightening_result_to_js(Napi::Env env, const TighteningResult& r) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("points", vec3_list_to_js_array(env, r.points));
    o.Set("metrics", metrics_to_js(env, r.metrics));
    Napi::Array steps = Napi::Array::New(env, r.steps.size());
    for (size_t i = 0; i < r.steps.size(); ++i) {
        steps.Set(static_cast<uint32_t>(i), step_record_to_js(env, r.steps[i]));
    }
    o.Set("steps", steps);
    o.Set("converged", Napi::Boolean::New(env, r.converged));
    o.Set("reason", Napi::String::New(env, r.reason));
    return o;
}

Napi::Object diagnostics_to_js(Napi::Env env, const ContactStressDiagnostics& d) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("contact_residual", Napi::Number::New(env, d.contact_residual));
    o.Set("strut_weight_sum", Napi::Number::New(env, d.strut_weight_sum));
    o.Set("kink_weight_sum", Napi::Number::New(env, d.kink_weight_sum));
    o.Set("contact_entropy", Napi::Number::New(env, d.contact_entropy));
    o.Set("gradient_norm", Napi::Number::New(env, d.gradient_norm));
    o.Set("residual_norm", Napi::Number::New(env, d.residual_norm));
    o.Set("nnls_objective", Napi::Number::New(env, d.nnls_objective));
    o.Set("strut_count", Napi::Number::New(env, static_cast<double>(d.strut_count)));
    o.Set("kink_count", Napi::Number::New(env, static_cast<double>(d.kink_count)));
    o.Set("rigidity_rows", Napi::Number::New(env, static_cast<double>(d.rigidity_rows)));
    o.Set("rigidity_columns", Napi::Number::New(env, static_cast<double>(d.rigidity_columns)));
    o.Set("nnls_iterations", Napi::Number::New(env, static_cast<double>(d.nnls_iterations)));
    o.Set("nnls_active_set_size", Napi::Number::New(env, static_cast<double>(d.nnls_active_set_size)));
    o.Set("nnls_algorithm", Napi::String::New(env, d.nnls_algorithm));
    o.Set("solved_nnls", Napi::Boolean::New(env, d.solved_nnls));
    o.Set("nnls_converged", Napi::Boolean::New(env, d.nnls_converged));
    o.Set("multipliers", to_f64(env, d.multipliers));
    return o;
}

// ---------------------------------------------------------------------------
// ResolvedTubeGeometry (static methods)
// ---------------------------------------------------------------------------
class ResolvedTubeGeometryWrap : public Napi::ObjectWrap<ResolvedTubeGeometryWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "ResolvedTubeGeometry",
            {StaticMethod("length", &ResolvedTubeGeometryWrap::Length),
             StaticMethod("edgeLengthMean", &ResolvedTubeGeometryWrap::EdgeLengthMean),
             StaticMethod("edgeLengthRelativeStd", &ResolvedTubeGeometryWrap::EdgeLengthRelativeStd),
             StaticMethod("turningAngle", &ResolvedTubeGeometryWrap::TurningAngle),
             StaticMethod("minradAtVertex", &ResolvedTubeGeometryWrap::MinradAtVertex),
             StaticMethod("kinkAtVertex", &ResolvedTubeGeometryWrap::KinkAtVertex),
             StaticMethod("globalMinrad", &ResolvedTubeGeometryWrap::GlobalMinrad),
             StaticMethod("segmentSegmentDistance", &ResolvedTubeGeometryWrap::SegmentSegmentDistance),
             StaticMethod("dcsdCandidates", &ResolvedTubeGeometryWrap::DcsdCandidates),
             StaticMethod("analyze", &ResolvedTubeGeometryWrap::Analyze),
             StaticMethod("lengthGradientFlat", &ResolvedTubeGeometryWrap::LengthGradientFlat),
             StaticMethod("strutGradientFlat", &ResolvedTubeGeometryWrap::StrutGradientFlat),
             StaticMethod("kinkMinradPlusGradientFlat", &ResolvedTubeGeometryWrap::KinkMinradPlusGradientFlat),
             StaticMethod("kinkMinradMinusGradientFlat", &ResolvedTubeGeometryWrap::KinkMinradMinusGradientFlat),
             StaticMethod("kinkMinradGradientFlat", &ResolvedTubeGeometryWrap::KinkMinradGradientFlat),
             StaticMethod("nontrivialKnotLowerBoundRad", &ResolvedTubeGeometryWrap::NontrivialKnotLowerBoundRad),
             StaticMethod("radiusToDiameterRopelength", &ResolvedTubeGeometryWrap::RadiusToDiameterRopelength),
             StaticMethod("diameterToRadiusRopelength", &ResolvedTubeGeometryWrap::DiameterToRadiusRopelength)});
        exports.Set("ResolvedTubeGeometry", func);
    }
    ResolvedTubeGeometryWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<ResolvedTubeGeometryWrap>(info) {}

private:
    static Napi::Value Length(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::length(read_points(info[0])));
    }
    static Napi::Value EdgeLengthMean(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::edge_length_mean(read_points(info[0])));
    }
    static Napi::Value EdgeLengthRelativeStd(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::edge_length_relative_std(read_points(info[0])));
    }
    static Napi::Value TurningAngle(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::turning_angle(
                                                 read_vec3(info[0]), read_vec3(info[1]), read_vec3(info[2])));
    }
    static Napi::Value MinradAtVertex(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::minrad_at_vertex(
                                                 read_points(info[0]), size_arg(info, 1)));
    }
    static Napi::Value KinkAtVertex(const Napi::CallbackInfo& info) {
        return kink_record_to_js(info.Env(), ResolvedTubeGeometry::kink_at_vertex(
                                                 read_points(info[0]), size_arg(info, 1)));
    }
    static Napi::Value GlobalMinrad(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::global_minrad(read_points(info[0])));
    }
    static Napi::Value SegmentSegmentDistance(const Napi::CallbackInfo& info) {
        double s = 0.0, t = 0.0;
        const double d = ResolvedTubeGeometry::segment_segment_distance(
            read_vec3(info[0]), read_vec3(info[1]), read_vec3(info[2]), read_vec3(info[3]), &s, &t);
        Napi::Object o = Napi::Object::New(info.Env());
        o.Set("distance", Napi::Number::New(info.Env(), d));
        o.Set("s", Napi::Number::New(info.Env(), s));
        o.Set("t", Napi::Number::New(info.Env(), t));
        return o;
    }
    static Napi::Value DcsdCandidates(const Napi::CallbackInfo& info) {
        auto pts = read_points(info[0]);
        int skip_neighbors = opt_int(info, 1, 2);
        double distance_tol = opt_double(info, 2, 0.0);
        auto out = ResolvedTubeGeometry::dcsd_candidates(pts, skip_neighbors, distance_tol);
        Napi::Array arr = Napi::Array::New(info.Env(), out.size());
        for (size_t i = 0; i < out.size(); ++i) {
            arr.Set(static_cast<uint32_t>(i), segment_pair_to_js(info.Env(), out[i]));
        }
        return arr;
    }
    static Napi::Value Analyze(const Napi::CallbackInfo& info) {
        auto pts = read_points(info[0]);
        int skip_neighbors = opt_int(info, 1, 2);
        double contact_tol = opt_double(info, 2, 1e-3);
        double equilateral_tol = opt_double(info, 3, 1e-3);
        return metrics_to_js(info.Env(),
                             ResolvedTubeGeometry::analyze(pts, skip_neighbors, contact_tol, equilateral_tol));
    }
    static Napi::Value LengthGradientFlat(const Napi::CallbackInfo& info) {
        return to_f64(info.Env(), ResolvedTubeGeometry::length_gradient_flat(read_points(info[0])));
    }
    static Napi::Value StrutGradientFlat(const Napi::CallbackInfo& info) {
        return to_f64(info.Env(), ResolvedTubeGeometry::strut_gradient_flat(
                                      read_points(info[0]), segment_pair_from_js(info[1].As<Napi::Object>())));
    }
    static Napi::Value KinkMinradPlusGradientFlat(const Napi::CallbackInfo& info) {
        return to_f64(info.Env(), ResolvedTubeGeometry::kink_minrad_plus_gradient_flat(
                                      read_points(info[0]), kink_record_from_js(info[1].As<Napi::Object>())));
    }
    static Napi::Value KinkMinradMinusGradientFlat(const Napi::CallbackInfo& info) {
        return to_f64(info.Env(), ResolvedTubeGeometry::kink_minrad_minus_gradient_flat(
                                      read_points(info[0]), kink_record_from_js(info[1].As<Napi::Object>())));
    }
    static Napi::Value KinkMinradGradientFlat(const Napi::CallbackInfo& info) {
        bool use_analytic = opt_bool(info, 2, true);
        double fd_step = opt_double(info, 3, 1e-6);
        return to_f64(info.Env(), ResolvedTubeGeometry::kink_minrad_gradient_flat(
                                      read_points(info[0]), kink_record_from_js(info[1].As<Napi::Object>()),
                                      use_analytic, fd_step));
    }
    static Napi::Value NontrivialKnotLowerBoundRad(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::nontrivial_knot_lower_bound_rad());
    }
    static Napi::Value RadiusToDiameterRopelength(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::radius_to_diameter_ropelength(
                                                 info[0].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value DiameterToRadiusRopelength(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::diameter_to_radius_ropelength(
                                                 info[0].As<Napi::Number>().DoubleValue()));
    }

    static std::size_t size_arg(const Napi::CallbackInfo& info, size_t i) {
        return static_cast<std::size_t>(info[i].As<Napi::Number>().Int64Value());
    }
};

// ---------------------------------------------------------------------------
// ResolvedTubeTightener (static methods)
// ---------------------------------------------------------------------------
class ResolvedTubeTightenerWrap : public Napi::ObjectWrap<ResolvedTubeTightenerWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "ResolvedTubeTightener",
            {StaticMethod("rescaleToThickness", &ResolvedTubeTightenerWrap::RescaleToThickness),
             StaticMethod("correctThickness", &ResolvedTubeTightenerWrap::CorrectThickness),
             StaticMethod("projectedGradientFlat", &ResolvedTubeTightenerWrap::ProjectedGradientFlat),
             StaticMethod("tighten", &ResolvedTubeTightenerWrap::Tighten)});
        exports.Set("ResolvedTubeTightener", func);
    }
    ResolvedTubeTightenerWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<ResolvedTubeTightenerWrap>(info) {}

private:
    static Napi::Value RescaleToThickness(const Napi::CallbackInfo& info) {
        auto pts = read_points(info[0]);
        double target_thickness = info[1].As<Napi::Number>().DoubleValue();
        int skip_neighbors = opt_int(info, 2, 2);
        double contact_tol = opt_double(info, 3, 1e-3);
        double equilateral_tol = opt_double(info, 4, 1e-3);
        auto out = ResolvedTubeTightener::rescale_to_thickness(
            pts, target_thickness, skip_neighbors, contact_tol, equilateral_tol);
        return vec3_list_to_js_array(info.Env(), out);
    }
    static Napi::Value CorrectThickness(const Napi::CallbackInfo& info) {
        auto pts = read_points(info[0]);
        double target_thickness = info[1].As<Napi::Number>().DoubleValue();
        TighteningOptions opts = (info.Length() > 2) ? tightening_options_from_js(info[2]) : TighteningOptions();
        auto out = ResolvedTubeTightener::correct_thickness(pts, target_thickness, opts);
        return vec3_list_to_js_array(info.Env(), out);
    }
    static Napi::Value ProjectedGradientFlat(const Napi::CallbackInfo& info) {
        auto pts = read_points(info[0]);
        ResolvedTubeMetrics tube = metrics_from_js(info[1].As<Napi::Object>());
        TighteningOptions opts = (info.Length() > 2) ? tightening_options_from_js(info[2]) : TighteningOptions();
        ContactStressDiagnostics diag;
        auto direction = ResolvedTubeTightener::projected_gradient_flat(pts, tube, opts, &diag);
        Napi::Object o = Napi::Object::New(info.Env());
        o.Set("direction", to_f64(info.Env(), direction));
        o.Set("diagnostics", diagnostics_to_js(info.Env(), diag));
        return o;
    }
    static Napi::Value Tighten(const Napi::CallbackInfo& info) {
        auto pts = read_points(info[0]);
        TighteningOptions opts = (info.Length() > 1) ? tightening_options_from_js(info[1]) : TighteningOptions();
        return tightening_result_to_js(info.Env(), ResolvedTubeTightener::tighten(pts, opts));
    }
};

// ---------------------------------------------------------------------------
// ContactStressMap (static methods)
// ---------------------------------------------------------------------------
class ContactStressMapWrap : public Napi::ObjectWrap<ContactStressMapWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "ContactStressMap",
            {StaticMethod("buildRigidityMatrix", &ContactStressMapWrap::BuildRigidityMatrix),
             StaticMethod("buildSparseRigidityMatrix", &ContactStressMapWrap::BuildSparseRigidityMatrix),
             StaticMethod("sparseToDense", &ContactStressMapWrap::SparseToDense),
             StaticMethod("writeSparseMatrixMarket", &ContactStressMapWrap::WriteSparseMatrixMarket),
             StaticMethod("writeVectorMarket", &ContactStressMapWrap::WriteVectorMarket),
             StaticMethod("writeVectorCsv", &ContactStressMapWrap::WriteVectorCsv),
             StaticMethod("solveNonnegativeLeastSquares", &ContactStressMapWrap::SolveNNLS),
             StaticMethod("solveNonnegativeLeastSquaresSparse", &ContactStressMapWrap::SolveNNLSSparse),
             StaticMethod("solveNonnegativeLeastSquaresActiveSet", &ContactStressMapWrap::SolveNNLSActiveSet),
             StaticMethod("solveNonnegativeLeastSquaresSparseActiveSet", &ContactStressMapWrap::SolveNNLSSparseActiveSet),
             StaticMethod("diagnoseLengthCriticality", &ContactStressMapWrap::DiagnoseLengthCriticality)});
        exports.Set("ContactStressMap", func);
    }
    ContactStressMapWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<ContactStressMapWrap>(info) {}

private:
    static Napi::Value BuildRigidityMatrix(const Napi::CallbackInfo& info) {
        auto pts = read_points(info[0]);
        ResolvedTubeMetrics tube = metrics_from_js(info[1].As<Napi::Object>());
        bool include_struts = opt_bool(info, 2, true);
        bool include_kinks = opt_bool(info, 3, true);
        double fd_step = opt_double(info, 4, 1e-6);
        bool use_analytic = opt_bool(info, 5, true);
        return rigidity_matrix_to_js(info.Env(), ContactStressMap::build_rigidity_matrix(
                                                     pts, tube, include_struts, include_kinks, fd_step, use_analytic));
    }
    static Napi::Value BuildSparseRigidityMatrix(const Napi::CallbackInfo& info) {
        auto pts = read_points(info[0]);
        ResolvedTubeMetrics tube = metrics_from_js(info[1].As<Napi::Object>());
        bool include_struts = opt_bool(info, 2, true);
        bool include_kinks = opt_bool(info, 3, true);
        double fd_step = opt_double(info, 4, 1e-6);
        bool use_analytic = opt_bool(info, 5, true);
        return sparse_rigidity_matrix_to_js(
            info.Env(), ContactStressMap::build_sparse_rigidity_matrix(
                            pts, tube, include_struts, include_kinks, fd_step, use_analytic));
    }
    static Napi::Value SparseToDense(const Napi::CallbackInfo& info) {
        return rigidity_matrix_to_js(info.Env(), ContactStressMap::sparse_to_dense(
                                                     sparse_rigidity_matrix_from_js(info[0].As<Napi::Object>())));
    }
    static Napi::Value WriteSparseMatrixMarket(const Napi::CallbackInfo& info) {
        auto sparse = sparse_rigidity_matrix_from_js(info[0].As<Napi::Object>());
        std::string path = info[1].As<Napi::String>().Utf8Value();
        bool one_based = opt_bool(info, 2, true);
        ContactStressMap::write_sparse_matrix_market(sparse, path, one_based);
        return info.Env().Undefined();
    }
    static Napi::Value WriteVectorMarket(const Napi::CallbackInfo& info) {
        std::vector<double> vec = read_doubles(info[0]);
        std::string path = info[1].As<Napi::String>().Utf8Value();
        ContactStressMap::write_vector_market(vec, path);
        return info.Env().Undefined();
    }
    static Napi::Value WriteVectorCsv(const Napi::CallbackInfo& info) {
        std::vector<double> vec = read_doubles(info[0]);
        std::string path = info[1].As<Napi::String>().Utf8Value();
        ContactStressMap::write_vector_csv(vec, path);
        return info.Env().Undefined();
    }
    static Napi::Value SolveNNLS(const Napi::CallbackInfo& info) {
        auto matrix = rigidity_matrix_from_js(info[0].As<Napi::Object>());
        std::vector<double> target = read_doubles(info[1]);
        std::size_t max_it = opt_size(info, 2, 5000);
        double tol = opt_double(info, 3, 1e-10);
        return nnls_result_to_js(info.Env(),
                                 ContactStressMap::solve_nonnegative_least_squares(matrix, target, max_it, tol));
    }
    static Napi::Value SolveNNLSSparse(const Napi::CallbackInfo& info) {
        auto matrix = sparse_rigidity_matrix_from_js(info[0].As<Napi::Object>());
        std::vector<double> target = read_doubles(info[1]);
        std::size_t max_it = opt_size(info, 2, 5000);
        double tol = opt_double(info, 3, 1e-10);
        return nnls_result_to_js(
            info.Env(), ContactStressMap::solve_nonnegative_least_squares_sparse(matrix, target, max_it, tol));
    }
    static Napi::Value SolveNNLSActiveSet(const Napi::CallbackInfo& info) {
        auto matrix = rigidity_matrix_from_js(info[0].As<Napi::Object>());
        std::vector<double> target = read_doubles(info[1]);
        std::size_t max_it = opt_size(info, 2, 2000);
        double tol = opt_double(info, 3, 1e-10);
        double ridge = opt_double(info, 4, 1e-12);
        return nnls_result_to_js(
            info.Env(),
            ContactStressMap::solve_nonnegative_least_squares_active_set(matrix, target, max_it, tol, ridge));
    }
    static Napi::Value SolveNNLSSparseActiveSet(const Napi::CallbackInfo& info) {
        auto matrix = sparse_rigidity_matrix_from_js(info[0].As<Napi::Object>());
        std::vector<double> target = read_doubles(info[1]);
        std::size_t max_it = opt_size(info, 2, 2000);
        double tol = opt_double(info, 3, 1e-10);
        double ridge = opt_double(info, 4, 1e-12);
        return nnls_result_to_js(
            info.Env(),
            ContactStressMap::solve_nonnegative_least_squares_sparse_active_set(matrix, target, max_it, tol, ridge));
    }
    static Napi::Value DiagnoseLengthCriticality(const Napi::CallbackInfo& info) {
        auto pts = read_points(info[0]);
        ResolvedTubeMetrics tube = metrics_from_js(info[1].As<Napi::Object>());
        bool solve_nnls = opt_bool(info, 2, true);
        std::size_t max_it = opt_size(info, 3, 5000);
        double tol = opt_double(info, 4, 1e-10);
        bool use_sparse = opt_bool(info, 5, true);
        bool use_analytic_kink = opt_bool(info, 6, true);
        bool use_active_set = opt_bool(info, 7, true);
        return diagnostics_to_js(
            info.Env(), ContactStressMap::diagnose_length_criticality(
                            pts, tube, solve_nnls, max_it, tol, use_sparse, use_analytic_kink, use_active_set));
    }
};

} // namespace

void bind_resolved_tube_geometry(Napi::Env env, Napi::Object exports) {
    ResolvedTubeGeometryWrap::Init(env, exports);
    ResolvedTubeTightenerWrap::Init(env, exports);
    ContactStressMapWrap::Init(env, exports);

    // Convenience free functions mirroring the py module-level helpers.
    exports.Set("resolvedTubeAnalyze", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto pts = read_points(info[0]);
        int skip_neighbors = opt_int(info, 1, 2);
        double contact_tol = opt_double(info, 2, 1e-3);
        double equilateral_tol = opt_double(info, 3, 1e-3);
        return metrics_to_js(info.Env(),
                             ResolvedTubeGeometry::analyze(pts, skip_neighbors, contact_tol, equilateral_tol));
    }));
    exports.Set("resolvedTubeLength", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::length(read_points(info[0])));
    }));
    exports.Set("resolvedTubeMinrad", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::global_minrad(read_points(info[0])));
    }));
    exports.Set("resolvedTubeLowerBoundRad", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), ResolvedTubeGeometry::nontrivial_knot_lower_bound_rad());
    }));
    exports.Set("resolvedTubeLengthGradientFlat", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return to_f64(info.Env(), ResolvedTubeGeometry::length_gradient_flat(read_points(info[0])));
    }));
    exports.Set("resolvedTubeBuildRigidityMatrix", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto pts = read_points(info[0]);
        ResolvedTubeMetrics tube = metrics_from_js(info[1].As<Napi::Object>());
        bool include_struts = opt_bool(info, 2, true);
        bool include_kinks = opt_bool(info, 3, true);
        double fd_step = opt_double(info, 4, 1e-6);
        bool use_analytic = opt_bool(info, 5, true);
        return rigidity_matrix_to_js(info.Env(), ContactStressMap::build_rigidity_matrix(
                                                     pts, tube, include_struts, include_kinks, fd_step, use_analytic));
    }));
    exports.Set("resolvedTubeBuildSparseRigidityMatrix", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto pts = read_points(info[0]);
        ResolvedTubeMetrics tube = metrics_from_js(info[1].As<Napi::Object>());
        bool include_struts = opt_bool(info, 2, true);
        bool include_kinks = opt_bool(info, 3, true);
        double fd_step = opt_double(info, 4, 1e-6);
        bool use_analytic = opt_bool(info, 5, true);
        return sparse_rigidity_matrix_to_js(
            info.Env(), ContactStressMap::build_sparse_rigidity_matrix(
                            pts, tube, include_struts, include_kinks, fd_step, use_analytic));
    }));
    exports.Set("resolvedTubeWriteMatrixMarket", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto sparse = sparse_rigidity_matrix_from_js(info[0].As<Napi::Object>());
        std::string path = info[1].As<Napi::String>().Utf8Value();
        bool one_based = opt_bool(info, 2, true);
        ContactStressMap::write_sparse_matrix_market(sparse, path, one_based);
        return info.Env().Undefined();
    }));
    exports.Set("resolvedTubeWriteVectorMarket", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::vector<double> vec = read_doubles(info[0]);
        std::string path = info[1].As<Napi::String>().Utf8Value();
        ContactStressMap::write_vector_market(vec, path);
        return info.Env().Undefined();
    }));
    exports.Set("resolvedTubeSolveActiveSet", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto matrix = sparse_rigidity_matrix_from_js(info[0].As<Napi::Object>());
        std::vector<double> target = read_doubles(info[1]);
        std::size_t max_it = opt_size(info, 2, 2000);
        double tol = opt_double(info, 3, 1e-10);
        double ridge = opt_double(info, 4, 1e-12);
        return nnls_result_to_js(
            info.Env(),
            ContactStressMap::solve_nonnegative_least_squares_sparse_active_set(matrix, target, max_it, tol, ridge));
    }));
    exports.Set("resolvedTubeKktDiagnostics", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto pts = read_points(info[0]);
        ResolvedTubeMetrics tube = metrics_from_js(info[1].As<Napi::Object>());
        bool solve_nnls = opt_bool(info, 2, true);
        std::size_t max_it = opt_size(info, 3, 5000);
        double tol = opt_double(info, 4, 1e-10);
        bool use_sparse = opt_bool(info, 5, true);
        bool use_analytic_kink = opt_bool(info, 6, true);
        bool use_active_set = opt_bool(info, 7, true);
        return diagnostics_to_js(
            info.Env(), ContactStressMap::diagnose_length_criticality(
                            pts, tube, solve_nnls, max_it, tol, use_sparse, use_analytic_kink, use_active_set));
    }));
    exports.Set("resolvedTubeTighten", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto pts = read_points(info[0]);
        TighteningOptions opts = (info.Length() > 1) ? tightening_options_from_js(info[1]) : TighteningOptions();
        return tightening_result_to_js(info.Env(), ResolvedTubeTightener::tighten(pts, opts));
    }));
    exports.Set("resolvedTubeProjectedGradient", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto pts = read_points(info[0]);
        ResolvedTubeMetrics tube = metrics_from_js(info[1].As<Napi::Object>());
        TighteningOptions opts = (info.Length() > 2) ? tightening_options_from_js(info[2]) : TighteningOptions();
        ContactStressDiagnostics diag;
        auto direction = ResolvedTubeTightener::projected_gradient_flat(pts, tube, opts, &diag);
        Napi::Object o = Napi::Object::New(info.Env());
        o.Set("direction", to_f64(info.Env(), direction));
        o.Set("diagnostics", diagnostics_to_js(info.Env(), diag));
        return o;
    }));

    exports.Set("resolvedTubeGeometryAvailable", Napi::Boolean::New(env, true));
}
