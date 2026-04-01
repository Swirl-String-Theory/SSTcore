// node_vorticity_dynamics.cpp
#include <napi.h>
#include "node_utils.h"
#include "../vorticity_dynamics.h"

namespace {

sst::Vec3 read_v3(Napi::Env env, Napi::Array a) {
    if (a.Length() != 3u) {
        throw Napi::TypeError::New(env, "expected [x,y,z]");
    }
    return {a.Get(0u).As<Napi::Number>().DoubleValue(), a.Get(1u).As<Napi::Number>().DoubleValue(),
            a.Get(2u).As<Napi::Number>().DoubleValue()};
}

Napi::Array v3_to_arr(Napi::Env env, const sst::Vec3& v) {
    Napi::Array a = Napi::Array::New(env, 3);
    a.Set(0u, Napi::Number::New(env, v[0]));
    a.Set(1u, Napi::Number::New(env, v[1]));
    a.Set(2u, Napi::Number::New(env, v[2]));
    return a;
}

std::vector<double> read_doubles(Napi::Array a) {
    std::vector<double> out;
    out.reserve(a.Length());
    for (uint32_t i = 0; i < a.Length(); ++i) {
        out.push_back(a.Get(i).As<Napi::Number>().DoubleValue());
    }
    return out;
}

std::array<sst::Vec3, 3> read_grad_u(Napi::Env env, Napi::Array outer) {
    if (outer.Length() != 3u) {
        throw Napi::TypeError::New(env, "grad_u: array of 3 rows (each [du/dx,du/dy,du/dz] as vec3)");
    }
    std::array<sst::Vec3, 3> g;
    for (uint32_t i = 0; i < 3u; ++i) {
        g[i] = read_v3(env, outer.Get(i).As<Napi::Array>());
    }
    return g;
}

} // namespace

void bind_vorticity_dynamics(Napi::Env env, Napi::Object exports) {
    exports.Set("vorticityZ2D", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::VorticityDynamics::vorticity_z_2D(
                                                   info[0].As<Napi::Number>().DoubleValue(),
                                                   info[1].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("localCirculationDensity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::VorticityDynamics::local_circulation_density(
                                                   info[0].As<Napi::Number>().DoubleValue(),
                                                   info[1].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("solidBodyRotationVorticity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(
            info.Env(), sst::VorticityDynamics::solid_body_rotation_vorticity(info[0].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("couetteVorticity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(),
                                 sst::VorticityDynamics::couette_vorticity(info[0].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("croccoRelation", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env en = info.Env();
        auto w = read_v3(en, info[0].As<Napi::Array>());
        double rho = info[1].As<Napi::Number>().DoubleValue();
        auto gp = read_v3(en, info[2].As<Napi::Array>());
        auto r = sst::VorticityDynamics::crocco_relation(w, rho, gp);
        return v3_to_arr(en, r);
    }));
    exports.Set("computeVorticity2D", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env en = info.Env();
        if (info.Length() < 6) {
            throw Napi::TypeError::New(en, "Expected (u, v, nx, ny, dx, dy) as arrays + ints + floats");
        }
        std::vector<double> u = read_doubles(info[0].As<Napi::Array>());
        std::vector<double> v = read_doubles(info[1].As<Napi::Array>());
        int nx = info[2].As<Napi::Number>().Int32Value();
        int ny = info[3].As<Napi::Number>().Int32Value();
        double dx = info[4].As<Napi::Number>().DoubleValue();
        double dy = info[5].As<Napi::Number>().DoubleValue();
        std::vector<double> om = sst::VorticityDynamics::compute_vorticity2D(u, v, nx, ny, dx, dy);
        Napi::Array out = Napi::Array::New(en, om.size());
        for (size_t i = 0; i < om.size(); ++i) {
            out.Set(static_cast<uint32_t>(i), Napi::Number::New(en, om[i]));
        }
        return out;
    }));
    exports.Set("rotatingFrameRhs", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env en = info.Env();
        auto vel = read_v3(en, info[0].As<Napi::Array>());
        auto vor = read_v3(en, info[1].As<Napi::Array>());
        auto gp = read_v3(en, info[2].As<Napi::Array>());
        auto gpp = read_v3(en, info[3].As<Napi::Array>());
        auto om = read_v3(en, info[4].As<Napi::Array>());
        double rho = info[5].As<Napi::Number>().DoubleValue();
        auto r = sst::VorticityDynamics::rotating_frame_rhs(vel, vor, gp, gpp, om, rho);
        return v3_to_arr(en, r);
    }));
    exports.Set("croccoGradient", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env en = info.Env();
        auto vel = read_v3(en, info[0].As<Napi::Array>());
        auto vor = read_v3(en, info[1].As<Napi::Array>());
        auto gp = read_v3(en, info[2].As<Napi::Array>());
        auto gpp = read_v3(en, info[3].As<Napi::Array>());
        double rho = info[4].As<Napi::Number>().DoubleValue();
        auto r = sst::VorticityDynamics::crocco_gradient(vel, vor, gp, gpp, rho);
        return v3_to_arr(en, r);
    }));
    exports.Set("baroclinicTerm", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env en = info.Env();
        auto gr = read_v3(en, info[0].As<Napi::Array>());
        auto gp = read_v3(en, info[1].As<Napi::Array>());
        double rho = info[2].As<Napi::Number>().DoubleValue();
        auto r = sst::VorticityDynamics::baroclinic_term(gr, gp, rho);
        return v3_to_arr(en, r);
    }));
    exports.Set("computeVorticityRhs", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env en = info.Env();
        auto omega = read_v3(en, info[0].As<Napi::Array>());
        auto grad_u = read_grad_u(en, info[1].As<Napi::Array>());
        double div_u = info[2].As<Napi::Number>().DoubleValue();
        auto gr = read_v3(en, info[3].As<Napi::Array>());
        auto gp = read_v3(en, info[4].As<Napi::Array>());
        double rho = info[5].As<Napi::Number>().DoubleValue();
        auto r = sst::VorticityDynamics::compute_vorticity_rhs(omega, grad_u, div_u, gr, gp, rho);
        return v3_to_arr(en, r);
    }));

    exports.Set("vorticityDynamicsAvailable", Napi::Boolean::New(env, true));
}
