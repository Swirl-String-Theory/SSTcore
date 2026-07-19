// node_knot.cpp — KnotDynamics / FourierKnot (parity with knot_dynamics_py)
#include <array>
#include <map>
#include <memory>
#include <string>
#include <tuple>
#include <vector>
#include <napi.h>
#include "node_utils.h"
#include <sst/knot.h>
#include <sst/particle.h>
#include "knot_dynamics.h"

using namespace sst;

namespace {

Napi::Object pd_to_js(Napi::Env env, const KnotDynamics::PD& pd) {
    Napi::Array arr = Napi::Array::New(env, pd.size());
    for (size_t i = 0; i < pd.size(); ++i) {
        Napi::Array q = Napi::Array::New(env, 4);
        for (int k = 0; k < 4; ++k) {
            q.Set(static_cast<uint32_t>(k), Napi::Number::New(env, pd[i][static_cast<size_t>(k)]));
        }
        arr.Set(static_cast<uint32_t>(i), q);
    }
    return arr;
}

Napi::Object fourier_block_to_js(Napi::Env env, const FourierBlock& b) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("header", Napi::String::New(env, b.header));
    auto put_dv = [&](const char* name, const std::vector<double>& v) {
        Napi::Array a = Napi::Array::New(env, v.size());
        for (size_t i = 0; i < v.size(); ++i) {
            a.Set(static_cast<uint32_t>(i), Napi::Number::New(env, v[i]));
        }
        o.Set(name, a);
    };
    put_dv("aX", b.a_x);
    put_dv("bX", b.b_x);
    put_dv("aY", b.a_y);
    put_dv("bY", b.b_y);
    put_dv("aZ", b.a_z);
    put_dv("bZ", b.b_z);
    return o;
}

FourierBlock fourier_block_from_js(Napi::Object o) {
    FourierBlock b;
    if (o.Has("header")) b.header = o.Get("header").As<Napi::String>().Utf8Value();
    auto read = [&](const char* name, std::vector<double>& dst) {
        if (!o.Has(name)) return;
        Napi::Array a = o.Get(name).As<Napi::Array>();
        dst.resize(a.Length());
        for (uint32_t i = 0; i < a.Length(); ++i) {
            dst[i] = a.Get(i).As<Napi::Number>().DoubleValue();
        }
    };
    read("aX", b.a_x);
    read("bX", b.b_x);
    read("aY", b.a_y);
    read("bY", b.b_y);
    read("aZ", b.a_z);
    read("bZ", b.b_z);
    return b;
}

std::vector<double> read_double_array(Napi::Array a) {
    std::vector<double> s;
    s.reserve(a.Length());
    for (uint32_t i = 0; i < a.Length(); ++i) {
        s.push_back(a.Get(i).As<Napi::Number>().DoubleValue());
    }
    return s;
}

Napi::Object string_map_to_js(Napi::Env env, const std::map<std::string, std::string>& m) {
    Napi::Object o = Napi::Object::New(env);
    for (const auto& kv : m) {
        o.Set(kv.first, Napi::String::New(env, kv.second));
    }
    return o;
}

// ------------------------------------------------------------------
// Small scalar getters with defaults (missing/undefined -> default).
// ------------------------------------------------------------------
std::string get_str(Napi::Object o, const char* k, const std::string& d) {
    if (o.Has(k)) {
        Napi::Value v = o.Get(k);
        if (!v.IsUndefined() && !v.IsNull()) return v.As<Napi::String>().Utf8Value();
    }
    return d;
}
double get_num(Napi::Object o, const char* k, double d) {
    if (o.Has(k)) {
        Napi::Value v = o.Get(k);
        if (v.IsNumber()) return v.As<Napi::Number>().DoubleValue();
    }
    return d;
}
int get_int(Napi::Object o, const char* k, int d) {
    if (o.Has(k)) {
        Napi::Value v = o.Get(k);
        if (v.IsNumber()) return v.As<Napi::Number>().Int32Value();
    }
    return d;
}
bool get_bool(Napi::Object o, const char* k, bool d) {
    if (o.Has(k)) {
        Napi::Value v = o.Get(k);
        if (v.IsBoolean()) return v.As<Napi::Boolean>().Value();
    }
    return d;
}
bool is_plain_object(Napi::Value v) { return v.IsObject() && !v.IsArray(); }

// ------------------------------------------------------------------
// Vec3 <-> JS [x, y, z].
// ------------------------------------------------------------------
Napi::Array vec3_to_js(Napi::Env env, const Vec3& v) {
    Napi::Array a = Napi::Array::New(env, 3);
    a.Set(0u, Napi::Number::New(env, v[0]));
    a.Set(1u, Napi::Number::New(env, v[1]));
    a.Set(2u, Napi::Number::New(env, v[2]));
    return a;
}
Vec3 vec3_from_js(Napi::Value val) {
    Napi::Array a = val.As<Napi::Array>();
    Vec3 v{0.0, 0.0, 0.0};
    v[0] = a.Get(0u).As<Napi::Number>().DoubleValue();
    v[1] = a.Get(1u).As<Napi::Number>().DoubleValue();
    v[2] = a.Get(2u).As<Napi::Number>().DoubleValue();
    return v;
}

Napi::Array double_vec_to_js(Napi::Env env, const std::vector<double>& v) {
    Napi::Array a = Napi::Array::New(env, v.size());
    for (size_t i = 0; i < v.size(); ++i) a.Set(static_cast<uint32_t>(i), Napi::Number::New(env, v[i]));
    return a;
}

// ------------------------------------------------------------------
// KnotInvariants <-> JS.
// ------------------------------------------------------------------
Napi::Object invariants_to_js(Napi::Env e, const KnotInvariants& K) {
    Napi::Object o = Napi::Object::New(e);
    o.Set("name", Napi::String::New(e, K.name));
    o.Set("crossingNumber", Napi::Number::New(e, K.crossing_number));
    o.Set("braidIndex", Napi::Number::New(e, K.braid_index));
    o.Set("seifertGenus", Napi::Number::New(e, K.seifert_genus));
    o.Set("chirality", Napi::Number::New(e, K.chirality));
    o.Set("hyperbolic", Napi::Boolean::New(e, K.hyperbolic));
    o.Set("hyperbolicVolume", Napi::Number::New(e, K.hyperbolic_volume));
    o.Set("ropelengthLike", Napi::Number::New(e, K.ropelength_like));
    o.Set("hyperbolicVolumeOpt", K.hyperbolic_volume_opt.has_value()
                                     ? Napi::Value(Napi::Number::New(e, K.hyperbolic_volume_opt.value()))
                                     : Napi::Value(e.Null()));
    o.Set("ropelength", K.ropelength.has_value()
                            ? Napi::Value(Napi::Number::New(e, K.ropelength.value()))
                            : Napi::Value(e.Null()));
    o.Set("writhe", Napi::Number::New(e, K.writhe));
    o.Set("minSelfDistance", Napi::Number::New(e, K.min_self_distance));
    o.Set("bendingEnergy", Napi::Number::New(e, K.bending_energy));
    o.Set("thicknessRad", Napi::Number::New(e, K.thickness_rad));
    o.Set("ropelengthRad", Napi::Number::New(e, K.ropelength_rad));
    o.Set("ropelengthDiam", Napi::Number::New(e, K.ropelength_diam));
    o.Set("minradMin", Napi::Number::New(e, K.minrad_min));
    o.Set("dcsdMin", Napi::Number::New(e, K.dcsd_min));
    o.Set("strutCount", Napi::Number::New(e, K.strut_count));
    o.Set("kinkCount", Napi::Number::New(e, K.kink_count));
    o.Set("contactResidual", Napi::Number::New(e, K.contact_residual));
    o.Set("contactEntropy", Napi::Number::New(e, K.contact_entropy));
    o.Set("ropelengthLowerBoundOk", Napi::Boolean::New(e, K.ropelength_lower_bound_ok));
    return o;
}
KnotInvariants invariants_from_js(Napi::Value val) {
    KnotInvariants K;
    if (!is_plain_object(val)) return K;
    Napi::Object o = val.As<Napi::Object>();
    K.name = get_str(o, "name", K.name);
    K.crossing_number = get_int(o, "crossingNumber", K.crossing_number);
    K.braid_index = get_int(o, "braidIndex", K.braid_index);
    K.seifert_genus = get_int(o, "seifertGenus", K.seifert_genus);
    K.chirality = get_int(o, "chirality", K.chirality);
    K.hyperbolic = get_bool(o, "hyperbolic", K.hyperbolic);
    K.hyperbolic_volume = get_num(o, "hyperbolicVolume", K.hyperbolic_volume);
    K.ropelength_like = get_num(o, "ropelengthLike", K.ropelength_like);
    if (o.Has("hyperbolicVolumeOpt") && o.Get("hyperbolicVolumeOpt").IsNumber())
        K.hyperbolic_volume_opt = o.Get("hyperbolicVolumeOpt").As<Napi::Number>().DoubleValue();
    if (o.Has("ropelength") && o.Get("ropelength").IsNumber())
        K.ropelength = o.Get("ropelength").As<Napi::Number>().DoubleValue();
    K.writhe = get_num(o, "writhe", K.writhe);
    K.min_self_distance = get_num(o, "minSelfDistance", K.min_self_distance);
    K.bending_energy = get_num(o, "bendingEnergy", K.bending_energy);
    K.thickness_rad = get_num(o, "thicknessRad", K.thickness_rad);
    K.ropelength_rad = get_num(o, "ropelengthRad", K.ropelength_rad);
    K.ropelength_diam = get_num(o, "ropelengthDiam", K.ropelength_diam);
    K.minrad_min = get_num(o, "minradMin", K.minrad_min);
    K.dcsd_min = get_num(o, "dcsdMin", K.dcsd_min);
    K.strut_count = get_int(o, "strutCount", K.strut_count);
    K.kink_count = get_int(o, "kinkCount", K.kink_count);
    K.contact_residual = get_num(o, "contactResidual", K.contact_residual);
    K.contact_entropy = get_num(o, "contactEntropy", K.contact_entropy);
    K.ropelength_lower_bound_ok = get_bool(o, "ropelengthLowerBoundOk", K.ropelength_lower_bound_ok);
    return K;
}

Napi::Object derived_to_js(Napi::Env e, const KnotDerived& D) {
    Napi::Object o = Napi::Object::New(e);
    o.Set("gate", Napi::Number::New(e, static_cast<int>(D.gate)));
    o.Set("gateFactor", Napi::Number::New(e, D.gate_factor));
    o.Set("xi", Napi::Number::New(e, D.xi));
    o.Set("massRatio", Napi::Number::New(e, D.mass_ratio));
    o.Set("massKg", Napi::Number::New(e, D.mass_kg));
    o.Set("valid", Napi::Boolean::New(e, D.valid));
    o.Set("note", Napi::String::New(e, D.note));
    return o;
}
KnotDerived derived_from_js(Napi::Value val) {
    KnotDerived D;
    if (!is_plain_object(val)) return D;
    Napi::Object o = val.As<Napi::Object>();
    D.gate = static_cast<SectorGate>(get_int(o, "gate", static_cast<int>(D.gate)));
    D.gate_factor = get_num(o, "gateFactor", D.gate_factor);
    D.xi = get_num(o, "xi", D.xi);
    D.mass_ratio = get_num(o, "massRatio", D.mass_ratio);
    D.mass_kg = get_num(o, "massKg", D.mass_kg);
    D.valid = get_bool(o, "valid", D.valid);
    D.note = get_str(o, "note", D.note);
    return D;
}

Napi::Object prediction_to_js(Napi::Env e, const KnotPrediction& P) {
    Napi::Object o = Napi::Object::New(e);
    o.Set("gate", Napi::Number::New(e, static_cast<int>(P.gate)));
    o.Set("gateFactor", Napi::Number::New(e, P.gate_factor));
    o.Set("xi", Napi::Number::New(e, P.xi));
    o.Set("massRatio", Napi::Number::New(e, P.mass_ratio));
    o.Set("massKg", Napi::Number::New(e, P.mass_kg));
    o.Set("note", Napi::String::New(e, P.note));
    return o;
}

Napi::Object report_row_to_js(Napi::Env e, const KnotReportRow& R) {
    Napi::Object o = Napi::Object::New(e);
    o.Set("name", Napi::String::New(e, R.name));
    o.Set("k", Napi::Number::New(e, R.k));
    o.Set("b", Napi::Number::New(e, R.b));
    o.Set("g", Napi::Number::New(e, R.g));
    o.Set("volH", Napi::Number::New(e, R.vol_h));
    o.Set("lTot", Napi::Number::New(e, R.L_tot));
    o.Set("gate", Napi::Number::New(e, R.gate));
    o.Set("xi", Napi::Number::New(e, R.xi));
    o.Set("massRatio", Napi::Number::New(e, R.mass_ratio));
    o.Set("massKg", Napi::Number::New(e, R.mass_kg));
    return o;
}

Napi::Object descriptors_to_js(Napi::Env e, const FourierKnot::GeometricDescriptors& g) {
    Napi::Object o = Napi::Object::New(e);
    o.Set("L", Napi::Number::New(e, g.L));
    o.Set("bendingEnergy", Napi::Number::New(e, g.bending_energy));
    o.Set("minSelfDistance", Napi::Number::New(e, g.min_self_distance));
    o.Set("writhe", Napi::Number::New(e, g.writhe));
    o.Set("modeEnergy", double_vec_to_js(e, g.mode_energy));
    return o;
}

// ------------------------------------------------------------------
// Ideal AB blocks/components <-> JS.
// ------------------------------------------------------------------
using IdealABBlock = FourierKnot::IdealABBlock;
using IdealABComponent = FourierKnot::IdealABComponent;

Napi::Object ideal_component_to_js(Napi::Env e, const IdealABComponent& c) {
    Napi::Object o = Napi::Object::New(e);
    o.Set("componentIndex", Napi::Number::New(e, c.component_index));
    o.Set("a0", vec3_to_js(e, c.A0));
    o.Set("b0", vec3_to_js(e, c.B0));
    o.Set("fourier", fourier_block_to_js(e, c.fourier));
    return o;
}
IdealABComponent ideal_component_from_js(Napi::Object o) {
    IdealABComponent c;
    c.component_index = get_int(o, "componentIndex", c.component_index);
    if (o.Has("a0")) c.A0 = vec3_from_js(o.Get("a0"));
    if (o.Has("b0")) c.B0 = vec3_from_js(o.Get("b0"));
    if (o.Has("fourier") && is_plain_object(o.Get("fourier")))
        c.fourier = fourier_block_from_js(o.Get("fourier").As<Napi::Object>());
    return c;
}

Napi::Object ideal_block_to_js(Napi::Env e, const IdealABBlock& b) {
    Napi::Object o = Napi::Object::New(e);
    o.Set("id", Napi::String::New(e, b.id));
    o.Set("conway", Napi::String::New(e, b.conway));
    o.Set("L", Napi::Number::New(e, b.L));
    o.Set("D", Napi::Number::New(e, b.D));
    o.Set("n", Napi::Number::New(e, b.n));
    o.Set("sourceTag", Napi::String::New(e, b.source_tag));
    Napi::Array comps = Napi::Array::New(e, b.components.size());
    for (size_t i = 0; i < b.components.size(); ++i)
        comps.Set(static_cast<uint32_t>(i), ideal_component_to_js(e, b.components[i]));
    o.Set("components", comps);
    o.Set("fourier", fourier_block_to_js(e, b.fourier));
    return o;
}
IdealABBlock ideal_block_from_js(Napi::Object o) {
    IdealABBlock b;
    b.id = get_str(o, "id", b.id);
    b.conway = get_str(o, "conway", b.conway);
    b.L = get_num(o, "L", b.L);
    b.D = get_num(o, "D", b.D);
    b.n = get_int(o, "n", b.n);
    b.source_tag = get_str(o, "sourceTag", b.source_tag);
    if (o.Has("components") && o.Get("components").IsArray()) {
        Napi::Array comps = o.Get("components").As<Napi::Array>();
        b.components.clear();
        b.components.reserve(comps.Length());
        for (uint32_t i = 0; i < comps.Length(); ++i)
            b.components.push_back(ideal_component_from_js(comps.Get(i).As<Napi::Object>()));
    }
    if (o.Has("fourier") && is_plain_object(o.Get("fourier")))
        b.fourier = fourier_block_from_js(o.Get("fourier").As<Napi::Object>());
    return b;
}

std::vector<IdealABBlock> ideal_blocks_from_js(Napi::Array arr) {
    std::vector<IdealABBlock> out;
    out.reserve(arr.Length());
    for (uint32_t i = 0; i < arr.Length(); ++i)
        out.push_back(ideal_block_from_js(arr.Get(i).As<Napi::Object>()));
    return out;
}
Napi::Array ideal_blocks_to_js(Napi::Env e, const std::vector<IdealABBlock>& blocks) {
    Napi::Array arr = Napi::Array::New(e, blocks.size());
    for (size_t i = 0; i < blocks.size(); ++i)
        arr.Set(static_cast<uint32_t>(i), ideal_block_to_js(e, blocks[i]));
    return arr;
}

// ------------------------------------------------------------------
// Model params / canonical constants from JS (defaults when absent).
// ------------------------------------------------------------------
SimpleInvariantXiModel::Params simple_params_from_js(Napi::Value val) {
    SimpleInvariantXiModel::Params p;
    if (!is_plain_object(val)) return p;
    Napi::Object o = val.As<Napi::Object>();
    p.a_k = get_num(o, "aK", p.a_k);
    p.a_b = get_num(o, "aB", p.a_b);
    p.a_g = get_num(o, "aG", p.a_g);
    p.a_vol = get_num(o, "aVol", p.a_vol);
    p.a_L = get_num(o, "aL", p.a_L);
    p.a_chi = get_num(o, "aChi", p.a_chi);
    return p;
}
SSTCanonicalXiModel::Params canonical_params_from_js(Napi::Value val) {
    SSTCanonicalXiModel::Params p;
    if (!is_plain_object(val)) return p;
    Napi::Object o = val.As<Napi::Object>();
    p.alpha_C = get_num(o, "alphaC", p.alpha_C);
    p.beta_L = get_num(o, "betaL", p.beta_L);
    p.gamma_H = get_num(o, "gammaH", p.gamma_H);
    p.delta_V = get_num(o, "deltaV", p.delta_V);
    p.golden_layer = get_int(o, "goldenLayer", p.golden_layer);
    p.use_crossing_number_as_C = get_bool(o, "useCrossingNumberAsC", p.use_crossing_number_as_C);
    p.use_writhe_as_H = get_bool(o, "useWritheAsH", p.use_writhe_as_H);
    return p;
}
KnotParticleModel::Params particle_params_from_js(Napi::Value val) {
    KnotParticleModel::Params p;
    if (!is_plain_object(val)) return p;
    Napi::Object o = val.As<Napi::Object>();
    p.a_k = get_num(o, "aK", p.a_k);
    p.a_b = get_num(o, "aB", p.a_b);
    p.a_g = get_num(o, "aG", p.a_g);
    p.a_vol = get_num(o, "aVol", p.a_vol);
    p.a_L = get_num(o, "aL", p.a_L);
    p.a_wr = get_num(o, "aWr", p.a_wr);
    p.a_sep = get_num(o, "aSep", p.a_sep);
    return p;
}
CanonicalConstants constants_from_js(Napi::Value val) {
    CanonicalConstants c;
    if (!is_plain_object(val)) return c;
    Napi::Object o = val.As<Napi::Object>();
    c.r_c = get_num(o, "rC", c.r_c);
    c.lambda_c = get_num(o, "lambdaC", c.lambda_c);
    c.m_e = get_num(o, "mE", c.m_e);
    c.rho_f = get_num(o, "rhoF", c.rho_f);
    c.v_swirl = get_num(o, "vSwirl", c.v_swirl);
    c.c = get_num(o, "c", c.c);
    c.rho_m = get_num(o, "rhoM", c.rho_m);
    c.rho_horn = get_num(o, "rhoHorn", c.rho_horn);
    return c;
}

KnotState knot_state_from_js(Napi::Value val) {
    KnotState s;
    if (!is_plain_object(val)) return s;
    Napi::Object o = val.As<Napi::Object>();
    if (o.Has("inv")) s.inv = invariants_from_js(o.Get("inv"));
    if (o.Has("contactScore") && o.Get("contactScore").IsNumber())
        s.contact_score = o.Get("contactScore").As<Napi::Number>().DoubleValue();
    if (o.Has("hopfLikeScore") && o.Get("hopfLikeScore").IsNumber())
        s.hopf_like_score = o.Get("hopfLikeScore").As<Napi::Number>().DoubleValue();
    if (o.Has("energyScore") && o.Get("energyScore").IsNumber())
        s.energy_score = o.Get("energyScore").As<Napi::Number>().DoubleValue();
    if (o.Has("derived") && is_plain_object(o.Get("derived")))
        s.derived = derived_from_js(o.Get("derived"));
    return s;
}

// Metadata bundle mirroring the optional args on build_/predict_ helpers.
struct KnotMeta {
    std::string knot_name;
    int crossing_number = 0;
    int braid_index = 0;
    int seifert_genus = 0;
    int chirality = 0;
    bool hyperbolic = false;
    double hyperbolic_volume = 0.0;
    int nsamples = 2048;
    int exclude_window = 4;
};
KnotMeta meta_from_js(Napi::Value val) {
    KnotMeta m;
    if (!is_plain_object(val)) return m;
    Napi::Object o = val.As<Napi::Object>();
    m.knot_name = get_str(o, "knotName", m.knot_name);
    m.crossing_number = get_int(o, "crossingNumber", m.crossing_number);
    m.braid_index = get_int(o, "braidIndex", m.braid_index);
    m.seifert_genus = get_int(o, "seifertGenus", m.seifert_genus);
    m.chirality = get_int(o, "chirality", m.chirality);
    m.hyperbolic = get_bool(o, "hyperbolic", m.hyperbolic);
    m.hyperbolic_volume = get_num(o, "hyperbolicVolume", m.hyperbolic_volume);
    m.nsamples = get_int(o, "nsamples", m.nsamples);
    m.exclude_window = get_int(o, "excludeWindow", m.exclude_window);
    return m;
}

std::vector<FourierBlock> fourier_blocks_from_js(Napi::Array arr) {
    std::vector<FourierBlock> blocks;
    blocks.reserve(arr.Length());
    for (uint32_t i = 0; i < arr.Length(); ++i)
        blocks.push_back(fourier_block_from_js(arr.Get(i).As<Napi::Object>()));
    return blocks;
}
Napi::Array fourier_blocks_to_js(Napi::Env e, const std::vector<FourierBlock>& blocks) {
    Napi::Array arr = Napi::Array::New(e, blocks.size());
    for (size_t i = 0; i < blocks.size(); ++i)
        arr.Set(static_cast<uint32_t>(i), fourier_block_to_js(e, blocks[i]));
    return arr;
}

// ------------------------------------------------------------------
// ObjectWrap: FourierKnot (parity with py `fourier_knot`).
// ------------------------------------------------------------------
class FourierKnotWrap : public Napi::ObjectWrap<FourierKnotWrap> {
public:
    static Napi::Function Init(Napi::Env env) {
        return DefineClass(env, "FourierKnot", {
            InstanceMethod("loadBlocks", &FourierKnotWrap::LoadBlocks),
            InstanceMethod("selectMaxHarmonics", &FourierKnotWrap::SelectMaxHarmonics),
            InstanceMethod("reconstruct", &FourierKnotWrap::Reconstruct),
            InstanceMethod("getPoints", &FourierKnotWrap::GetPoints),
            InstanceMethod("getBlocks", &FourierKnotWrap::GetBlocks),
            InstanceMethod("getActiveBlock", &FourierKnotWrap::GetActiveBlock),
            InstanceMethod("setActiveBlock", &FourierKnotWrap::SetActiveBlock),
        });
    }
    explicit FourierKnotWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<FourierKnotWrap>(info) {}

private:
    FourierKnot fk_;

    Napi::Value LoadBlocks(const Napi::CallbackInfo& info) {
        fk_.loadBlocks(info[0].As<Napi::String>().Utf8Value());
        return info.Env().Undefined();
    }
    Napi::Value SelectMaxHarmonics(const Napi::CallbackInfo& info) {
        fk_.selectMaxHarmonics();
        return info.Env().Undefined();
    }
    Napi::Value Reconstruct(const Napi::CallbackInfo& info) {
        size_t N = (info.Length() > 0 && info[0].IsNumber())
                       ? static_cast<size_t>(info[0].As<Napi::Number>().Int64Value())
                       : 1000;
        fk_.reconstruct(N);
        return info.Env().Undefined();
    }
    Napi::Value GetPoints(const Napi::CallbackInfo& info) {
        return vec3_list_to_js_typedarray(info.Env(), fk_.points);
    }
    Napi::Value GetBlocks(const Napi::CallbackInfo& info) {
        return fourier_blocks_to_js(info.Env(), fk_.blocks);
    }
    Napi::Value GetActiveBlock(const Napi::CallbackInfo& info) {
        return fourier_block_to_js(info.Env(), fk_.activeBlock);
    }
    Napi::Value SetActiveBlock(const Napi::CallbackInfo& info) {
        fk_.activeBlock = fourier_block_from_js(info[0].As<Napi::Object>());
        return info.Env().Undefined();
    }
};

// ------------------------------------------------------------------
// ObjectWrap: KnotParticleModel (parity with py `KnotParticleModel`).
// ------------------------------------------------------------------
class KnotParticleModelWrap : public Napi::ObjectWrap<KnotParticleModelWrap> {
public:
    static Napi::Function Init(Napi::Env env) {
        return DefineClass(env, "KnotParticleModel", {
            InstanceMethod("assignGate", &KnotParticleModelWrap::AssignGate),
            InstanceMethod("computeXi", &KnotParticleModelWrap::ComputeXi),
            InstanceMethod("predict", &KnotParticleModelWrap::Predict),
        });
    }
    explicit KnotParticleModelWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<KnotParticleModelWrap>(info),
          model_(std::make_unique<KnotParticleModel>(
              particle_params_from_js(info.Length() > 0 ? info[0] : info.Env().Undefined()))) {}

private:
    std::unique_ptr<KnotParticleModel> model_;

    Napi::Value AssignGate(const Napi::CallbackInfo& info) {
        KnotInvariants K = invariants_from_js(info[0]);
        return Napi::Number::New(info.Env(), static_cast<int>(model_->assign_gate(K)));
    }
    Napi::Value ComputeXi(const Napi::CallbackInfo& info) {
        KnotInvariants K = invariants_from_js(info[0]);
        return Napi::Number::New(info.Env(), model_->compute_xi(K));
    }
    Napi::Value Predict(const Napi::CallbackInfo& info) {
        KnotInvariants K = invariants_from_js(info[0]);
        return prediction_to_js(info.Env(), model_->predict(K));
    }
};

} // namespace

void bind_knot(Napi::Env env, Napi::Object exports) {
    exports.Set("computeWrithe", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto c = js_array_to_vec3_list(info[0].As<Napi::Array>());
        return Napi::Number::New(info.Env(), KnotDynamics::compute_writhe(c));
    }));

    exports.Set("computeLinkingNumber", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto c1 = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto c2 = js_array_to_vec3_list(info[1].As<Napi::Array>());
        return Napi::Number::New(info.Env(), KnotDynamics::compute_linking_number(c1, c2));
    }));

    exports.Set("computeTwist", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto T = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto B = js_array_to_vec3_list(info[1].As<Napi::Array>());
        return Napi::Number::New(info.Env(), KnotDynamics::compute_twist(T, B));
    }));

    exports.Set("computeCenterlineHelicity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto curve = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto tan = js_array_to_vec3_list(info[1].As<Napi::Array>());
        return Napi::Number::New(info.Env(), KnotDynamics::compute_centerline_helicity(curve, tan));
    }));

    exports.Set("detectReconnectionCandidates", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        auto curve = js_array_to_vec3_list(info[0].As<Napi::Array>());
        double th = info[1].As<Napi::Number>().DoubleValue();
        auto pairs = KnotDynamics::detect_reconnection_candidates(curve, th);
        Napi::Array out = Napi::Array::New(e, pairs.size());
        for (size_t i = 0; i < pairs.size(); ++i) {
            Napi::Object p = Napi::Object::New(e);
            p.Set("i", Napi::Number::New(e, pairs[i].first));
            p.Set("j", Napi::Number::New(e, pairs[i].second));
            out.Set(static_cast<uint32_t>(i), p);
        }
        return out;
    }));

    exports.Set("knotComputeBiotSavartVelocityGrid", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto curve = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto grid = js_array_to_vec3_list(info[1].As<Napi::Array>());
        auto v = KnotDynamics::compute_biot_savart_velocity_grid(curve, grid);
        return vec3_list_to_js_typedarray(info.Env(), v);
    }));

    exports.Set("knotComputeVorticityGrid", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto vel = js_array_to_vec3_list(info[0].As<Napi::Array>());
        Napi::Array sh = info[1].As<Napi::Array>();
        std::array<int, 3> shape = {sh.Get(0u).As<Napi::Number>().Int32Value(), sh.Get(1u).As<Napi::Number>().Int32Value(),
                                    sh.Get(2u).As<Napi::Number>().Int32Value()};
        double sp = info[2].As<Napi::Number>().DoubleValue();
        auto w = KnotDynamics::compute_vorticity_grid(vel, shape, sp);
        return vec3_list_to_js_typedarray(info.Env(), w);
    }));

    exports.Set("knotExtractInteriorField", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto fld = js_array_to_vec3_list(info[0].As<Napi::Array>());
        Napi::Array sh = info[1].As<Napi::Array>();
        std::array<int, 3> shape = {sh.Get(0u).As<Napi::Number>().Int32Value(), sh.Get(1u).As<Napi::Number>().Int32Value(),
                                    sh.Get(2u).As<Napi::Number>().Int32Value()};
        int margin = info[2].As<Napi::Number>().Int32Value();
        auto out = KnotDynamics::extract_interior_field(fld, shape, margin);
        return vec3_list_to_js_typedarray(info.Env(), out);
    }));

    exports.Set("computeHelicityInvariants", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        auto vsub = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto wsub = js_array_to_vec3_list(info[1].As<Napi::Array>());
        auto rsq = read_double_array(info[2].As<Napi::Array>());
        auto t = KnotDynamics::compute_helicity_invariants(vsub, wsub, rsq);
        Napi::Object o = Napi::Object::New(e);
        o.Set("hCharge", Napi::Number::New(e, std::get<0>(t)));
        o.Set("hMass", Napi::Number::New(e, std::get<1>(t)));
        o.Set("aMu", Napi::Number::New(e, std::get<2>(t)));
        return o;
    }));

    exports.Set("parseFseriesMulti", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        const std::string path = info[0].As<Napi::String>().Utf8Value();
        std::vector<FourierBlock> blocks = FourierKnot::parse_fseries_multi(path);
        Napi::Array arr = Napi::Array::New(e, blocks.size());
        for (size_t i = 0; i < blocks.size(); ++i) {
            arr.Set(static_cast<uint32_t>(i), fourier_block_to_js(e, blocks[i]));
        }
        return arr;
    }));

    exports.Set("indexOfLargestFourierBlock", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Array arr = info[0].As<Napi::Array>();
        std::vector<FourierBlock> blocks;
        blocks.reserve(arr.Length());
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            blocks.push_back(fourier_block_from_js(arr.Get(i).As<Napi::Object>()));
        }
        return Napi::Number::New(info.Env(), FourierKnot::index_of_largest_block(blocks));
    }));

    exports.Set("evaluateFourierBlock", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        std::vector<double> s = read_double_array(info[1].As<Napi::Array>());
        auto pts = FourierKnot::evaluate(b, s);
        return vec3_list_to_js_typedarray(info.Env(), pts);
    }));

    exports.Set("pdFromCurve", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        auto P = js_array_to_vec3_list(info[0].As<Napi::Array>());
        int tries = (info.Length() > 1) ? info[1].As<Napi::Number>().Int32Value() : 40;
        unsigned seed = (info.Length() > 2) ? static_cast<unsigned>(info[2].As<Napi::Number>().Uint32Value()) : 12345u;
        double min_ang = (info.Length() > 3) ? info[3].As<Napi::Number>().DoubleValue() : 1.0;
        double depth = (info.Length() > 4) ? info[4].As<Napi::Number>().DoubleValue() : 1e-6;
        KnotDynamics::PD pd = KnotDynamics::pd_from_curve(P, tries, seed, min_ang, depth);
        return pd_to_js(e, pd);
    }));

    exports.Set("loadKnot", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        const std::string path = info[0].As<Napi::String>().Utf8Value();
        int ns = (info.Length() > 1) ? info[1].As<Napi::Number>().Int32Value() : 1000;
        auto pr = FourierKnot::load_knot(path, ns);
        Napi::Object o = Napi::Object::New(e);
        o.Set("points", vec3_list_to_js_typedarray(e, pr.first));
        Napi::Array curv = Napi::Array::New(e, pr.second.size());
        for (size_t i = 0; i < pr.second.size(); ++i) {
            curv.Set(static_cast<uint32_t>(i), Napi::Number::New(e, pr.second[i]));
        }
        o.Set("curvature", curv);
        return o;
    }));

    exports.Set("getEmbeddedKnotFiles", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return string_map_to_js(info.Env(), get_embedded_knot_files());
    }));

    exports.Set("getEmbeddedIdealFiles", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return string_map_to_js(info.Env(), get_embedded_ideal_files());
    }));

    // ==================================================================
    // Parity aliases for previously renamed exports (old names kept).
    // ==================================================================
    exports.Set("computeBiotSavartVelocityGrid", exports.Get("knotComputeBiotSavartVelocityGrid"));
    exports.Set("computeVorticityGrid", exports.Get("knotComputeVorticityGrid"));
    exports.Set("extractInteriorField", exports.Get("knotExtractInteriorField"));
    exports.Set("indexOfLargestBlock", exports.Get("indexOfLargestFourierBlock"));

    // ==================================================================
    // KnotDynamics free functions (py m.def parity).
    // ==================================================================
    exports.Set("evaluateFourierSeries", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        Napi::Array cs = info[0].As<Napi::Array>();
        std::vector<std::array<double, 6>> coeffs(cs.Length());
        for (uint32_t i = 0; i < cs.Length(); ++i) {
            Napi::Array row = cs.Get(i).As<Napi::Array>();
            for (uint32_t k = 0; k < 6; ++k)
                coeffs[i][k] = row.Get(k).As<Napi::Number>().DoubleValue();
        }
        std::vector<double> t = read_double_array(info[1].As<Napi::Array>());
        auto res = KnotDynamics::evaluate_fourier_series(coeffs, t);
        Napi::Object o = Napi::Object::New(e);
        o.Set("positions", vec3_list_to_js_typedarray(e, res.positions));
        o.Set("tangents", vec3_list_to_js_typedarray(e, res.tangents));
        return o;
    }));

    exports.Set("writheGaussCurve", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto r = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto r_t = js_array_to_vec3_list(info[1].As<Napi::Array>());
        return Napi::Number::New(info.Env(), KnotDynamics::writhe_gauss_curve(r, r_t));
    }));

    exports.Set("estimateCrossingNumber", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto r = js_array_to_vec3_list(info[0].As<Napi::Array>());
        int directions = (info.Length() > 1 && info[1].IsNumber()) ? info[1].As<Napi::Number>().Int32Value() : 24;
        int seed = (info.Length() > 2 && info[2].IsNumber()) ? info[2].As<Napi::Number>().Int32Value() : 12345;
        return Napi::Number::New(info.Env(), KnotDynamics::estimate_crossing_number(r, directions, seed));
    }));

    exports.Set("computeHelicityFromFourierBlock", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        int grid_size = (info.Length() > 1 && info[1].IsNumber()) ? info[1].As<Napi::Number>().Int32Value() : 32;
        double spacing = (info.Length() > 2 && info[2].IsNumber()) ? info[2].As<Napi::Number>().DoubleValue() : 0.1;
        int margin = (info.Length() > 3 && info[3].IsNumber()) ? info[3].As<Napi::Number>().Int32Value() : 8;
        int nsamples = (info.Length() > 4 && info[4].IsNumber()) ? info[4].As<Napi::Number>().Int32Value() : 1000;
        auto t = KnotDynamics::compute_helicity_from_fourier_block(b, grid_size, spacing, margin, nsamples);
        Napi::Object o = Napi::Object::New(e);
        o.Set("hCharge", Napi::Number::New(e, std::get<0>(t)));
        o.Set("hMass", Napi::Number::New(e, std::get<1>(t)));
        o.Set("aMu", Napi::Number::New(e, std::get<2>(t)));
        return o;
    }));

    exports.Set("computeCurvature", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto pts = js_array_to_vec3_list(info[0].As<Napi::Array>());
        double eps = (info.Length() > 1 && info[1].IsNumber()) ? info[1].As<Napi::Number>().DoubleValue() : 1e-8;
        return double_vec_to_js(info.Env(), FourierKnot::curvature(pts, eps));
    }));

    // ==================================================================
    // FourierKnot geometry / Fourier evaluation free functions.
    // ==================================================================
    exports.Set("evaluateWithDerivatives", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        double s = info[1].As<Napi::Number>().DoubleValue();
        auto t = FourierKnot::evaluate_with_derivatives(b, s);
        Napi::Object o = Napi::Object::New(e);
        o.Set("position", vec3_to_js(e, std::get<0>(t)));
        o.Set("d1", vec3_to_js(e, std::get<1>(t)));
        o.Set("d2", vec3_to_js(e, std::get<2>(t)));
        o.Set("d3", vec3_to_js(e, std::get<3>(t)));
        return o;
    }));

    exports.Set("curvatureExact", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        std::vector<double> s = read_double_array(info[1].As<Napi::Array>());
        double eps = (info.Length() > 2 && info[2].IsNumber()) ? info[2].As<Napi::Number>().DoubleValue() : 1e-12;
        return double_vec_to_js(info.Env(), FourierKnot::curvature_exact(b, s, eps));
    }));

    exports.Set("lengthExact", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        int nsamples = (info.Length() > 1 && info[1].IsNumber()) ? info[1].As<Napi::Number>().Int32Value() : 4096;
        return Napi::Number::New(info.Env(), FourierKnot::length_exact(b, nsamples));
    }));

    exports.Set("bendingEnergyExact", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        int nsamples = (info.Length() > 1 && info[1].IsNumber()) ? info[1].As<Napi::Number>().Int32Value() : 4096;
        double eps = (info.Length() > 2 && info[2].IsNumber()) ? info[2].As<Napi::Number>().DoubleValue() : 1e-12;
        return Napi::Number::New(info.Env(), FourierKnot::bending_energy_exact(b, nsamples, eps));
    }));

    exports.Set("modeEnergies", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        return double_vec_to_js(info.Env(), FourierKnot::mode_energies(b));
    }));

    exports.Set("minSelfDistanceSampled", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto pts = js_array_to_vec3_list(info[0].As<Napi::Array>());
        int win = (info.Length() > 1 && info[1].IsNumber()) ? info[1].As<Napi::Number>().Int32Value() : 4;
        return Napi::Number::New(info.Env(), FourierKnot::min_self_distance_sampled(pts, win));
    }));

    exports.Set("minSelfDistanceExactish", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        int nsamples = (info.Length() > 1 && info[1].IsNumber()) ? info[1].As<Napi::Number>().Int32Value() : 2048;
        int win = (info.Length() > 2 && info[2].IsNumber()) ? info[2].As<Napi::Number>().Int32Value() : 4;
        return Napi::Number::New(info.Env(), FourierKnot::min_self_distance_exactish(b, nsamples, win));
    }));

    exports.Set("describeFourierBlock", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        int nsamples = (info.Length() > 1 && info[1].IsNumber()) ? info[1].As<Napi::Number>().Int32Value() : 2048;
        int win = (info.Length() > 2 && info[2].IsNumber()) ? info[2].As<Napi::Number>().Int32Value() : 4;
        return descriptors_to_js(info.Env(), FourierKnot::describe_fourier_block(b, nsamples, win));
    }));

    exports.Set("fourierKnotEval", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        FourierBlock b;
        b.a_x = read_double_array(info[0].As<Napi::Array>());
        b.b_x = read_double_array(info[1].As<Napi::Array>());
        b.a_y = read_double_array(info[2].As<Napi::Array>());
        b.b_y = read_double_array(info[3].As<Napi::Array>());
        b.a_z = read_double_array(info[4].As<Napi::Array>());
        b.b_z = read_double_array(info[5].As<Napi::Array>());
        std::vector<double> s = read_double_array(info[6].As<Napi::Array>());
        auto pts = FourierKnot::evaluate(b, s);
        Napi::Array x = Napi::Array::New(e, pts.size());
        Napi::Array y = Napi::Array::New(e, pts.size());
        Napi::Array z = Napi::Array::New(e, pts.size());
        for (size_t i = 0; i < pts.size(); ++i) {
            x.Set(static_cast<uint32_t>(i), Napi::Number::New(e, pts[i][0]));
            y.Set(static_cast<uint32_t>(i), Napi::Number::New(e, pts[i][1]));
            z.Set(static_cast<uint32_t>(i), Napi::Number::New(e, pts[i][2]));
        }
        Napi::Object o = Napi::Object::New(e);
        o.Set("x", x);
        o.Set("y", y);
        o.Set("z", z);
        return o;
    }));

    // ==================================================================
    // Invariants / particle prediction / dataset evaluation.
    // ==================================================================
    exports.Set("buildInvariantsFromFourierBlock", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        KnotMeta m = meta_from_js(info.Length() > 1 ? info[1] : info.Env().Undefined());
        KnotInvariants K = build_invariants_from_fourier_block(
            b, m.knot_name, m.crossing_number, m.braid_index, m.seifert_genus,
            m.chirality, m.hyperbolic, m.hyperbolic_volume, m.nsamples, m.exclude_window);
        return invariants_to_js(info.Env(), K);
    }));

    exports.Set("buildInvariantsFromFseries", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string path = info[0].As<Napi::String>().Utf8Value();
        KnotMeta m = meta_from_js(info.Length() > 1 ? info[1] : info.Env().Undefined());
        KnotInvariants K = build_invariants_from_fseries(
            path, m.knot_name, m.crossing_number, m.braid_index, m.seifert_genus,
            m.chirality, m.hyperbolic, m.hyperbolic_volume, m.nsamples, m.exclude_window);
        return invariants_to_js(info.Env(), K);
    }));

    exports.Set("predictParticleFromFourierBlock", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        FourierBlock b = fourier_block_from_js(info[0].As<Napi::Object>());
        KnotParticleModel::Params p = particle_params_from_js(info.Length() > 1 ? info[1] : info.Env().Undefined());
        KnotMeta m = meta_from_js(info.Length() > 2 ? info[2] : info.Env().Undefined());
        KnotPrediction pr = predict_particle_from_fourier_block(
            b, p, m.knot_name, m.crossing_number, m.braid_index, m.seifert_genus,
            m.chirality, m.hyperbolic, m.hyperbolic_volume, m.nsamples, m.exclude_window);
        return prediction_to_js(info.Env(), pr);
    }));

    exports.Set("predictParticleFromFseries", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string path = info[0].As<Napi::String>().Utf8Value();
        KnotParticleModel::Params p = particle_params_from_js(info.Length() > 1 ? info[1] : info.Env().Undefined());
        KnotMeta m = meta_from_js(info.Length() > 2 ? info[2] : info.Env().Undefined());
        KnotPrediction pr = predict_particle_from_fseries(
            path, p, m.knot_name, m.crossing_number, m.braid_index, m.seifert_genus,
            m.chirality, m.hyperbolic, m.hyperbolic_volume, m.nsamples, m.exclude_window);
        return prediction_to_js(info.Env(), pr);
    }));

    exports.Set("makeKnotReportRow", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        KnotInvariants K = invariants_from_js(info[0]);
        KnotDerived D = derived_from_js(info[1]);
        return report_row_to_js(info.Env(), make_knot_report_row(K, D));
    }));

    exports.Set("evaluateSingleKnot", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        KnotInvariants K = invariants_from_js(info[0]);
        SimpleInvariantXiModel model(simple_params_from_js(info.Length() > 1 ? info[1] : info.Env().Undefined()));
        CanonicalConstants c = constants_from_js(info.Length() > 2 ? info[2] : info.Env().Undefined());
        return derived_to_js(info.Env(), evaluate_single_knot(K, model, c));
    }));

    exports.Set("evaluateSingleKnotSstCanonical", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        KnotInvariants K = invariants_from_js(info[0]);
        SSTCanonicalXiModel model(canonical_params_from_js(info.Length() > 1 ? info[1] : info.Env().Undefined()));
        CanonicalConstants c = constants_from_js(info.Length() > 2 ? info[2] : info.Env().Undefined());
        return derived_to_js(info.Env(), evaluate_single_knot(K, model, c));
    }));

    exports.Set("evaluateKnotDataset", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        Napi::Array ds = info[0].As<Napi::Array>();
        std::vector<KnotState> dataset;
        dataset.reserve(ds.Length());
        for (uint32_t i = 0; i < ds.Length(); ++i) dataset.push_back(knot_state_from_js(ds.Get(i)));
        SimpleInvariantXiModel model(simple_params_from_js(info.Length() > 1 ? info[1] : e.Undefined()));
        CanonicalConstants c = constants_from_js(info.Length() > 2 ? info[2] : e.Undefined());
        auto rows = evaluate_knot_dataset(dataset, model, c);
        Napi::Array out = Napi::Array::New(e, rows.size());
        for (size_t i = 0; i < rows.size(); ++i) out.Set(static_cast<uint32_t>(i), report_row_to_js(e, rows[i]));
        return out;
    }));

    exports.Set("evaluateKnotDatasetSstCanonical", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        Napi::Array ds = info[0].As<Napi::Array>();
        std::vector<KnotState> dataset;
        dataset.reserve(ds.Length());
        for (uint32_t i = 0; i < ds.Length(); ++i) dataset.push_back(knot_state_from_js(ds.Get(i)));
        SSTCanonicalXiModel model(canonical_params_from_js(info.Length() > 1 ? info[1] : e.Undefined()));
        CanonicalConstants c = constants_from_js(info.Length() > 2 ? info[2] : e.Undefined());
        auto rows = evaluate_knot_dataset(dataset, model, c);
        Napi::Array out = Napi::Array::New(e, rows.size());
        for (size_t i = 0; i < rows.size(); ++i) out.Set(static_cast<uint32_t>(i), report_row_to_js(e, rows[i]));
        return out;
    }));

    // ==================================================================
    // Ideal AB parsing / evaluation / lookup.
    // ==================================================================
    exports.Set("parseIdealTxtMulti", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string path = info[0].As<Napi::String>().Utf8Value();
        return ideal_blocks_to_js(info.Env(), FourierKnot::parse_ideal_txt_multi(path));
    }));

    exports.Set("parseIdealTxtFromString", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string content = info[0].As<Napi::String>().Utf8Value();
        return ideal_blocks_to_js(info.Env(), FourierKnot::parse_ideal_txt_from_string(content));
    }));

    exports.Set("parseIdealGilbertFromString", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string content = info[0].As<Napi::String>().Utf8Value();
        return ideal_blocks_to_js(info.Env(), FourierKnot::parse_ideal_gilbert_from_string(content));
    }));

    exports.Set("indexOfIdealId", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::vector<IdealABBlock> blocks = ideal_blocks_from_js(info[0].As<Napi::Array>());
        std::string id = info[1].As<Napi::String>().Utf8Value();
        return Napi::Number::New(info.Env(), FourierKnot::index_of_ideal_id(blocks, id));
    }));

    exports.Set("parseIdealAbByIdFromString", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string content = info[0].As<Napi::String>().Utf8Value();
        std::string ab_id = info[1].As<Napi::String>().Utf8Value();
        return ideal_block_to_js(info.Env(), FourierKnot::parse_ideal_ab_by_id_from_string(content, ab_id));
    }));

    exports.Set("formatIdealAbHeader", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        IdealABBlock ab = ideal_block_from_js(info[0].As<Napi::Object>());
        return Napi::String::New(info.Env(), FourierKnot::format_ideal_ab_header(ab));
    }));

    exports.Set("evaluateIdealComponent", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        IdealABComponent comp = ideal_component_from_js(info[0].As<Napi::Object>());
        std::vector<double> s = read_double_array(info[1].As<Napi::Array>());
        return vec3_list_to_js_typedarray(info.Env(), FourierKnot::evaluate_ideal_component(comp, s));
    }));

    exports.Set("evaluateIdealAbComponents", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        IdealABBlock ab = ideal_block_from_js(info[0].As<Napi::Object>());
        std::vector<double> s = read_double_array(info[1].As<Napi::Array>());
        auto all = FourierKnot::evaluate_ideal_ab_components(ab, s);
        Napi::Array out = Napi::Array::New(e, all.size());
        for (size_t i = 0; i < all.size(); ++i)
            out.Set(static_cast<uint32_t>(i), vec3_list_to_js_typedarray(e, all[i]));
        return out;
    }));

    exports.Set("findIdealAbBlockById", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string ab_id = info[0].As<Napi::String>().Utf8Value();
        return Napi::String::New(info.Env(), find_ideal_ab_block_by_id(ab_id));
    }));

    exports.Set("findIdealBlockById", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string block_id = info[0].As<Napi::String>().Utf8Value();
        std::string tag = (info.Length() > 1 && info[1].IsString()) ? info[1].As<Napi::String>().Utf8Value() : "";
        return Napi::String::New(info.Env(), find_ideal_block_by_id(block_id, tag));
    }));

    exports.Set("loadEmbeddedIdealText", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string name = (info.Length() > 0 && info[0].IsString()) ? info[0].As<Napi::String>().Utf8Value() : "ideal.txt";
        return Napi::String::New(info.Env(), load_embedded_ideal_text(name));
    }));

    exports.Set("parseEmbeddedIdealTxt", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string name = (info.Length() > 0 && info[0].IsString()) ? info[0].As<Napi::String>().Utf8Value() : "ideal.txt";
        return ideal_blocks_to_js(info.Env(), FourierKnot::parse_ideal_txt_from_string(load_embedded_ideal_text(name)));
    }));

    exports.Set("parseEmbeddedIdealAbById", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string ab_id = info[0].As<Napi::String>().Utf8Value();
        std::string name = (info.Length() > 1 && info[1].IsString()) ? info[1].As<Napi::String>().Utf8Value() : "ideal.txt";
        return ideal_block_to_js(info.Env(), FourierKnot::parse_ideal_ab_by_id_from_embedded(ab_id, name));
    }));

    // ==================================================================
    // .fseries parsing / embedded knot loading.
    // ==================================================================
    exports.Set("parseFseriesFromString", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string content = info[0].As<Napi::String>().Utf8Value();
        return fourier_blocks_to_js(info.Env(), FourierKnot::parse_fseries_from_string(content));
    }));

    exports.Set("loadEmbeddedKnotBlock", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        std::string knot_id = info[0].As<Napi::String>().Utf8Value();
        auto files = get_embedded_knot_files();
        auto it = files.find(knot_id);
        if (it == files.end()) {
            Napi::Error::New(info.Env(), "Embedded knot id not found: " + knot_id).ThrowAsJavaScriptException();
            return info.Env().Undefined();
        }
        auto blocks = FourierKnot::parse_fseries_from_string(it->second);
        int idx = FourierKnot::index_of_largest_block(blocks);
        if (idx < 0) {
            Napi::Error::New(info.Env(), "No Fourier block found in embedded knot: " + knot_id).ThrowAsJavaScriptException();
            return info.Env().Undefined();
        }
        return fourier_block_to_js(info.Env(), blocks[static_cast<size_t>(idx)]);
    }));

    exports.Set("loadAllKnots", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        Napi::Array paths_arr = info[0].As<Napi::Array>();
        std::vector<std::string> paths;
        paths.reserve(paths_arr.Length());
        for (uint32_t i = 0; i < paths_arr.Length(); ++i)
            paths.push_back(paths_arr.Get(i).As<Napi::String>().Utf8Value());
        int nsamples = (info.Length() > 1 && info[1].IsNumber()) ? info[1].As<Napi::Number>().Int32Value() : 1000;
        auto knots = FourierKnot::load_all_knots(paths, nsamples);
        Napi::Array out = Napi::Array::New(e, knots.size());
        for (size_t i = 0; i < knots.size(); ++i) {
            Napi::Object o = Napi::Object::New(e);
            o.Set("name", Napi::String::New(e, knots[i].name));
            o.Set("points", vec3_list_to_js_typedarray(e, knots[i].points));
            o.Set("curvature", double_vec_to_js(e, knots[i].curvature));
            out.Set(static_cast<uint32_t>(i), o);
        }
        return out;
    }));

    // ==================================================================
    // Wrapped classes (ObjectWrap).
    // ==================================================================
    exports.Set("FourierKnot", FourierKnotWrap::Init(env));
    exports.Set("KnotParticleModel", KnotParticleModelWrap::Init(env));

    exports.Set("knotAvailable", Napi::Boolean::New(env, true));
}
