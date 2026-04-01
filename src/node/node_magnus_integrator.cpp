// node_magnus_integrator.cpp — N-API bindings for MagnusBernoulliIntegrator
#include <napi.h>
#include "node_utils.h"
#include "../magnus_integrator.h"

namespace {

sst::Vec3 read_vec3(Napi::Env env, const Napi::Value& v) {
    if (v.IsArray()) {
        Napi::Array a = v.As<Napi::Array>();
        if (a.Length() == 3u && a.Get(0u).IsNumber()) {
            return {a.Get(0u).As<Napi::Number>().DoubleValue(),
                    a.Get(1u).As<Napi::Number>().DoubleValue(),
                    a.Get(2u).As<Napi::Number>().DoubleValue()};
        }
        std::vector<sst::Vec3> vecs = js_array_to_vec3_list(a);
        if (vecs.empty()) {
            throw Napi::TypeError::New(env, "expected at least one [x,y,z] vector");
        }
        return vecs[0];
    }
    if (v.IsTypedArray()) {
        std::vector<sst::Vec3> vecs = js_typedarray_to_vec3_list(v.As<Napi::TypedArray>());
        if (vecs.empty()) {
            throw Napi::TypeError::New(env, "expected non-empty Float64Array (multiple of 3)");
        }
        return vecs[0];
    }
    throw Napi::TypeError::New(env, "expected array or Float64Array for vec3");
}

Vec3D to_v3d(const sst::Vec3& v) { return {v[0], v[1], v[2]}; }

Napi::Array v3d_to_js(Napi::Env env, const Vec3D& a) {
    Napi::Array o = Napi::Array::New(env, 3);
    o.Set(0u, Napi::Number::New(env, a[0]));
    o.Set(1u, Napi::Number::New(env, a[1]));
    o.Set(2u, Napi::Number::New(env, a[2]));
    return o;
}

} // namespace

void bind_magnus_integrator(Napi::Env env, Napi::Object exports) {
    exports.Set("createMagnusBernoulliIntegrator", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 4) {
            throw Napi::TypeError::New(e, "Expected (rho_f, v_swirl, r_c, Gamma)");
        }
        const double rho_f = info[0].As<Napi::Number>().DoubleValue();
        const double v_swirl = info[1].As<Napi::Number>().DoubleValue();
        const double r_c = info[2].As<Napi::Number>().DoubleValue();
        const double Gamma = info[3].As<Napi::Number>().DoubleValue();
        auto* p = new MagnusBernoulliIntegrator(rho_f, v_swirl, r_c, Gamma);
        return Napi::External<MagnusBernoulliIntegrator>::New(e, p, [](Napi::Env, MagnusBernoulliIntegrator* data) {
            delete data;
        });
    }));

    exports.Set("magnusComputeForce", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 6 || !info[0].IsExternal()) {
            throw Napi::TypeError::New(e, "Expected (integrator, tangent, normal, R, v_knot, v_bg)");
        }
        auto* integ = info[0].As<Napi::External<MagnusBernoulliIntegrator>>().Data();
        Vec3D T = to_v3d(read_vec3(e, info[1]));
        Vec3D N = to_v3d(read_vec3(e, info[2]));
        const double R = info[3].As<Napi::Number>().DoubleValue();
        Vec3D vk = to_v3d(read_vec3(e, info[4]));
        Vec3D vb = to_v3d(read_vec3(e, info[5]));
        Vec3D F = integ->compute_magnus_force(T, N, R, vk, vb);
        return v3d_to_js(e, F);
    }));

    exports.Set("magnusComputeSwirlCoulombAccel", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 3 || !info[0].IsExternal()) {
            throw Napi::TypeError::New(e, "Expected (integrator, eval_pos, source_pos)");
        }
        auto* integ = info[0].As<Napi::External<MagnusBernoulliIntegrator>>().Data();
        Vec3D pe = to_v3d(read_vec3(e, info[1]));
        Vec3D ps = to_v3d(read_vec3(e, info[2]));
        Vec3D a = integ->compute_swirl_coulomb_accel(pe, ps);
        return v3d_to_js(e, a);
    }));

    exports.Set("magnusIntegratorAvailable", Napi::Boolean::New(env, true));
}
