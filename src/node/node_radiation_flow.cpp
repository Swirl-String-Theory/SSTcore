// node_radiation_flow.cpp
#include <napi.h>
#include "../radiation_flow.h"

void bind_radiation_flow(Napi::Env env, Napi::Object exports) {
    exports.Set("radiationForce", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        if (info.Length() < 5) {
            throw Napi::TypeError::New(info.Env(), "Expected (I0, Qm, lambda1, lambda2, lambda_g)");
        }
        double v = sst::RadiationFlow::radiation_force(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(), info[3].As<Napi::Number>().DoubleValue(),
            info[4].As<Napi::Number>().DoubleValue());
        return Napi::Number::New(info.Env(), v);
    }));
    exports.Set("vanDerPolDx", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(),
                                 sst::RadiationFlow::dxdt(info[0].As<Napi::Number>().DoubleValue(),
                                                          info[1].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("vanDerPolDy", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(),
                                 sst::RadiationFlow::dydt(info[0].As<Napi::Number>().DoubleValue(),
                                                          info[1].As<Napi::Number>().DoubleValue(),
                                                          info[2].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("radiationFlowAvailable", Napi::Boolean::New(env, true));
}
