#include <napi.h>
#include "sst_scaling_audit.h"

void bind_scaling_audit(Napi::Env env, Napi::Object exports) {
    exports.Set("rhoRefLegacy", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ScalingAuditAPI::rho_ref_legacy());
    }));
    exports.Set("classifyObservableScaling", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1) return e.Null();
        std::string tag = info[0].As<Napi::String>().Utf8Value();
        auto c = sst::ScalingAuditAPI::classify_observable(tag);
        return Napi::String::New(e, sst::ScalingAuditAPI::scaling_class_name(c));
    }));
    exports.Set("classifyPrimitiveSymbol", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1) return e.Null();
        auto m = sst::ScalingAuditAPI::classify_symbol(info[0].As<Napi::String>().Utf8Value());
        Napi::Object o = Napi::Object::New(e);
        o.Set("inPCal", Napi::Boolean::New(e, m.in_p_cal));
        o.Set("inPOpen", Napi::Boolean::New(e, m.in_p_open));
        o.Set("inPRef", Napi::Boolean::New(e, m.in_p_ref));
        o.Set("legacyReference", Napi::Boolean::New(e, m.legacy_reference));
        return o;
    }));
}
