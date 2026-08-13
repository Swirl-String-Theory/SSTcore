#include <napi.h>
#include "sst_core_torsion.h"
#include "sst_link_field_gate.h"

void bind_core_torsion(Napi::Env env, Napi::Object exports) {
    exports.Set("torsionInertialMass", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            Napi::TypeError::New(env, "torsionInertialMass(E0, I, cT)").ThrowAsJavaScriptException();
            return env.Null();
        }
        auto r = sst::CoreTorsionAPI::torsion_inertial_mass(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue());
        Napi::Object o = Napi::Object::New(env);
        o.Set("mass", Napi::Number::New(env, r.mass));
        o.Set("dimensionalResidual", Napi::Number::New(env, r.dimensional_residual));
        o.Set("convention", Napi::String::New(env, r.convention));
        o.Set("ok", Napi::Boolean::New(env, r.ok));
        return o;
    }));

    exports.Set("torsionInertialMassLegacyFactor2", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            Napi::TypeError::New(env, "torsionInertialMassLegacyFactor2(E0, I, cT)").ThrowAsJavaScriptException();
            return env.Null();
        }
        auto r = sst::CoreTorsionAPI::torsion_inertial_mass_legacy_factor2(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue());
        Napi::Object o = Napi::Object::New(env);
        o.Set("mass", Napi::Number::New(env, r.mass));
        o.Set("convention", Napi::String::New(env, r.convention));
        o.Set("ok", Napi::Boolean::New(env, r.ok));
        return o;
    }));

    exports.Set("evaluateLinkFieldGate", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 4) {
            Napi::TypeError::New(env, "evaluateLinkFieldGate(rho, Gamma, r, phaseResidual, tol?)").ThrowAsJavaScriptException();
            return env.Null();
        }
        const double tol = info.Length() > 4 ? info[4].As<Napi::Number>().DoubleValue() : 1e-6;
        auto r = sst::LinkFieldGateAPI::evaluate(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(),
            info[3].As<Napi::Number>().DoubleValue(),
            tol);
        Napi::Object o = Napi::Object::New(env);
        o.Set("passed", Napi::Boolean::New(env, r.passed));
        o.Set("failure", Napi::String::New(env, sst::LinkFieldGateAPI::failure_name(r.failure)));
        o.Set("epistemicStatus", Napi::String::New(env, r.epistemic_status));
        o.Set("phaseResidual", Napi::Number::New(env, r.phase_residual));
        return o;
    }));
}
