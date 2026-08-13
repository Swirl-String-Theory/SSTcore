#include <napi.h>
#include "sst_action_phase.h"

void bind_action_phase(Napi::Env env, Napi::Object exports) {
    exports.Set("massShellHamiltonian", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            Napi::TypeError::New(env, "massShellHamiltonian(P, E0, c)").ThrowAsJavaScriptException();
            return env.Null();
        }
        return Napi::Number::New(env, sst::ActionPhaseAPI::mass_shell_hamiltonian(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("velocityFromMassShell", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            Napi::TypeError::New(env, "velocityFromMassShell(P, E0, c)").ThrowAsJavaScriptException();
            return env.Null();
        }
        return Napi::Number::New(env, sst::ActionPhaseAPI::velocity_from_mass_shell(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("gammaFromMassShell", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            Napi::TypeError::New(env, "gammaFromMassShell(P, E0, c)").ThrowAsJavaScriptException();
            return env.Null();
        }
        return Napi::Number::New(env, sst::ActionPhaseAPI::gamma_from_mass_shell(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("properTimeRate", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            Napi::TypeError::New(env, "properTimeRate(P, E0, c)").ThrowAsJavaScriptException();
            return env.Null();
        }
        return Napi::Number::New(env, sst::ActionPhaseAPI::proper_time_rate(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("internalPhaseRateAtFixedMomentum", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 4) {
            Napi::TypeError::New(env, "internalPhaseRateAtFixedMomentum(P, E0, c, Omega0)").ThrowAsJavaScriptException();
            return env.Null();
        }
        return Napi::Number::New(env, sst::ActionPhaseAPI::internal_phase_rate_at_fixed_momentum(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(),
            info[3].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("actionPhaseResiduals", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 4) {
            Napi::TypeError::New(env, "actionPhaseResiduals(P, E0, c, Omega0)").ThrowAsJavaScriptException();
            return env.Null();
        }
        auto r = sst::ActionPhaseAPI::action_phase_residuals(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(),
            info[3].As<Napi::Number>().DoubleValue());
        Napi::Object o = Napi::Object::New(env);
        o.Set("hamiltonianConsistency", Napi::Number::New(env, r.hamiltonian_consistency));
        o.Set("velocityConsistency", Napi::Number::New(env, r.velocity_consistency));
        o.Set("gammaConsistency", Napi::Number::New(env, r.gamma_consistency));
        o.Set("properTimeConsistency", Napi::Number::New(env, r.proper_time_consistency));
        o.Set("phaseRateConsistency", Napi::Number::New(env, r.phase_rate_consistency));
        o.Set("deltaShapeSeparability", Napi::Number::New(env, r.delta_shape_separability));
        o.Set("finite", Napi::Boolean::New(env, r.finite));
        o.Set("withinTolerance", Napi::Boolean::New(env, r.within_tolerance));
        o.Set("ok", Napi::Boolean::New(env, r.ok));
        return o;
    }));
    exports.Set("deltaShapeSeparability", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 4) {
            Napi::TypeError::New(env, "deltaShapeSeparability(P, E0, dE0_dq, c)").ThrowAsJavaScriptException();
            return env.Null();
        }
        return Napi::Number::New(env, sst::ActionPhaseAPI::delta_shape_separability(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(),
            info[3].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("fixedVPhaseErrorFactor", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            Napi::TypeError::New(env, "fixedVPhaseErrorFactor(P, E0, c)").ThrowAsJavaScriptException();
            return env.Null();
        }
        return Napi::Number::New(env, sst::ActionPhaseAPI::fixed_v_phase_error_factor(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }));
}
