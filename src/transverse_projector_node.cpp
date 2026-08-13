#include <napi.h>
#include "sst_transverse_projector.h"

void bind_transverse_projector(Napi::Env env, Napi::Object exports) {
    exports.Set("projectorSphereIntegral", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::TransverseProjectorAPI::projector_sphere_integral());
    }));
    exports.Set("leadingResponseR0", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1) return e.Null();
        return Napi::Number::New(e, sst::TransverseProjectorAPI::leading_response_R0(
            info[0].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("evaluateTransverseProjector", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 9) return e.Null();
        auto r = sst::TransverseProjectorAPI::evaluate(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(),
            info[3].As<Napi::Number>().DoubleValue(),
            info[4].As<Napi::Number>().DoubleValue(),
            info[5].As<Napi::Number>().DoubleValue(),
            info[6].As<Napi::Number>().DoubleValue(),
            info[7].As<Napi::Number>().DoubleValue(),
            info[8].As<Napi::Number>().DoubleValue());
        Napi::Object o = Napi::Object::New(e);
        o.Set("projectorSphereIntegral", Napi::Number::New(e, r.projector_sphere_integral));
        o.Set("R0", Napi::Number::New(e, r.R0));
        o.Set("ropRad", Napi::Number::New(e, r.rop_rad));
        o.Set("deltaMicro", Napi::Number::New(e, r.delta_micro));
        o.Set("RSST", Napi::Number::New(e, r.R_SST));
        o.Set("twistBoundOk", Napi::Boolean::New(e, r.twist_bound_ok));
        o.Set("message", Napi::String::New(e, r.message));
        return o;
    }));
}
