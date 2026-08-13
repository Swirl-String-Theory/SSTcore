#include <napi.h>
#include "sst_mechanical_falsifier.h"

void bind_mechanical_falsifier(Napi::Env env, Napi::Object exports) {
    exports.Set("evaluateMechanicalFalsifier", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 4) return e.Null();
        auto r = sst::MechanicalFalsifierAPI::evaluate(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(),
            info[3].As<Napi::Number>().DoubleValue());
        Napi::Object o = Napi::Object::New(e);
        o.Set("deltaPOmega", Napi::Number::New(e, r.delta_p_omega));
        o.Set("CBlind", Napi::Number::New(e, r.C_blind));
        o.Set("scalingOk", Napi::Boolean::New(e, r.scaling_ok));
        o.Set("message", Napi::String::New(e, r.message));
        return o;
    }));
}
