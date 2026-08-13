#include <napi.h>
#include "sst_maxwell_kinetic.h"

void bind_maxwell_kinetic(Napi::Env env, Napi::Object exports) {
    exports.Set("maxwellThreeGate", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 5) return e.Null();
        return Napi::Boolean::New(e, sst::MaxwellKineticAPI::three_gate_condition(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(),
            info[3].As<Napi::Number>().DoubleValue(),
            info[4].As<Napi::Number>().DoubleValue()));
    }));
}
