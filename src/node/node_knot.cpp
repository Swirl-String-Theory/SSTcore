// node_knot.cpp — KnotDynamics / FourierKnot (subset of knot_dynamics_py)
#include <map>
#include <napi.h>
#include "node_utils.h"
#include "../knot_dynamics.h"

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

    exports.Set("knotAvailable", Napi::Boolean::New(env, true));
}
