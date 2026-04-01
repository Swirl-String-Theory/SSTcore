// node_thermo_dynamics.cpp
#include <napi.h>
#include "../thermo_dynamics.h"

void bind_thermo_dynamics(Napi::Env env, Napi::Object exports) {
    exports.Set("potentialTemperature", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(
            info.Env(), sst::ThermoDynamics::potential_temperature(info[0].As<Napi::Number>().DoubleValue(),
                                                                   info[1].As<Napi::Number>().DoubleValue(),
                                                                   info[2].As<Napi::Number>().DoubleValue(),
                                                                   info[3].As<Napi::Number>().DoubleValue(),
                                                                   info[4].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("entropyFromTheta", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(
            info.Env(), sst::ThermoDynamics::entropy_from_theta(info[0].As<Napi::Number>().DoubleValue(),
                                                                info[1].As<Napi::Number>().DoubleValue(),
                                                                info[2].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("entropyFromPv", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(
            info.Env(), sst::ThermoDynamics::entropy_from_pv(info[0].As<Napi::Number>().DoubleValue(),
                                                             info[1].As<Napi::Number>().DoubleValue(),
                                                             info[2].As<Napi::Number>().DoubleValue(),
                                                             info[3].As<Napi::Number>().DoubleValue(),
                                                             info[4].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("enthalpy", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(
            info.Env(), sst::ThermoDynamics::enthalpy(info[0].As<Napi::Number>().DoubleValue(),
                                                      info[1].As<Napi::Number>().DoubleValue(),
                                                      info[2].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("thermoDynamicsAvailable", Napi::Boolean::New(env, true));
}
