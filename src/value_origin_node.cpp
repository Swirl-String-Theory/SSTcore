#include <napi.h>
#include "sst_value_origin.h"

void bind_value_origin(Napi::Env env, Napi::Object exports) {
    exports.Set("fmaxSnapshot", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ValueOriginAPI::fmax_snapshot());
    }));
    exports.Set("bareMassRatioFromDimensionlessLength", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) {
            Napi::TypeError::New(env, "bareMassRatioFromDimensionlessLength(Ltot)").ThrowAsJavaScriptException();
            return env.Null();
        }
        return Napi::Number::New(env, sst::ValueOriginAPI::bare_mass_ratio_from_dimensionless_length(
            info[0].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("compareFmaxSnapshotToRecomputed", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
        auto r = sst::ValueOriginAPI::compare_fmax_snapshot_to_recomputed();
        Napi::Object o = Napi::Object::New(info.Env());
        o.Set("snapshot", Napi::Number::New(info.Env(), r.snapshot));
        o.Set("recomputed", Napi::Number::New(info.Env(), r.recomputed));
        o.Set("residual", Napi::Number::New(info.Env(), r.residual));
        o.Set("snapshotUnchanged", Napi::Boolean::New(info.Env(), r.snapshot_unchanged));
        return o;
    }));
}
