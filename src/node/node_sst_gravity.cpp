// node_sst_gravity.cpp
#include <napi.h>
#include "node_utils.h"
#include "../sst_gravity.h"

namespace {

std::vector<double> read_scalar_array(Napi::Array a) {
    std::vector<double> out;
    out.reserve(a.Length());
    for (uint32_t i = 0; i < a.Length(); ++i) {
        out.push_back(a.Get(i).As<Napi::Number>().DoubleValue());
    }
    return out;
}

Napi::Array doubles_to_js(Napi::Env env, const std::vector<double>& v) {
    Napi::Array a = Napi::Array::New(env, v.size());
    for (size_t i = 0; i < v.size(); ++i) {
        a.Set(static_cast<uint32_t>(i), Napi::Number::New(env, v[i]));
    }
    return a;
}

} // namespace

void bind_sst_gravity(Napi::Env env, Napi::Object exports) {
    exports.Set("sstGravityBeltramiShear", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto B = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto C = js_array_to_vec3_list(info[1].As<Napi::Array>());
        return doubles_to_js(info.Env(), sst::SSTGravity::compute_beltrami_shear(B, C));
    }));
    exports.Set("sstGravityDilation", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto B = js_array_to_vec3_list(info[0].As<Napi::Array>());
        double od = info[1].As<Napi::Number>().DoubleValue();
        double vs = (info.Length() > 2) ? info[2].As<Napi::Number>().DoubleValue() : 1.09384563e6;
        double Bsat = (info.Length() > 3) ? info[3].As<Napi::Number>().DoubleValue() : 100.0;
        return doubles_to_js(info.Env(), sst::SSTGravity::compute_gravity_dilation(B, od, vs, Bsat));
    }));
    exports.Set("sstGravityHelicityDensity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto A = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto B = js_array_to_vec3_list(info[1].As<Napi::Array>());
        return doubles_to_js(info.Env(), sst::SSTGravity::compute_helicity_density(A, B));
    }));
    exports.Set("sstGravitySwirlClock", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto v = js_array_to_vec3_list(info[0].As<Napi::Array>());
        double c = (info.Length() > 1) ? info[1].As<Napi::Number>().DoubleValue() : 2.99792458e8;
        return doubles_to_js(info.Env(), sst::SSTGravity::compute_swirl_clock(v, c));
    }));
    exports.Set("sstGravitySwirlCoulombPotential", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto r = read_scalar_array(info[0].As<Napi::Array>());
        double L = info[1].As<Napi::Number>().DoubleValue();
        double rc = info[2].As<Napi::Number>().DoubleValue();
        return doubles_to_js(info.Env(), sst::SSTGravity::compute_swirl_coulomb_potential(r, L, rc));
    }));
    exports.Set("sstGravitySwirlCoulombForce", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto r = read_scalar_array(info[0].As<Napi::Array>());
        double L = info[1].As<Napi::Number>().DoubleValue();
        double rc = info[2].As<Napi::Number>().DoubleValue();
        return doubles_to_js(info.Env(), sst::SSTGravity::compute_swirl_coulomb_force(r, L, rc));
    }));
    exports.Set("sstGravitySwirlEnergyDensity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        auto v = js_array_to_vec3_list(info[0].As<Napi::Array>());
        double rf = info[1].As<Napi::Number>().DoubleValue();
        return doubles_to_js(info.Env(), sst::SSTGravity::compute_swirl_energy_density(v, rf));
    }));
    exports.Set("sstGravityGSwirl", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        double vsw = info[0].As<Napi::Number>().DoubleValue();
        double tp = info[1].As<Napi::Number>().DoubleValue();
        double Fm = info[2].As<Napi::Number>().DoubleValue();
        double rc = info[3].As<Napi::Number>().DoubleValue();
        double c = (info.Length() > 4) ? info[4].As<Napi::Number>().DoubleValue() : 2.99792458e8;
        return Napi::Number::New(info.Env(), sst::SSTGravity::compute_G_swirl(vsw, tp, Fm, rc, c));
    }));
    exports.Set("sstGravityAvailable", Napi::Boolean::New(env, true));
}
