#include <napi.h>
#include "sst_swirl_tonic.h"
#include <vector>

static std::vector<double> as_vec(const Napi::Value& v) {
    std::vector<double> out;
    if (!v.IsArray()) return out;
    Napi::Array a = v.As<Napi::Array>();
    for (uint32_t i = 0; i < a.Length(); ++i) out.push_back(a.Get(i).As<Napi::Number>().DoubleValue());
    return out;
}

void bind_swirl_tonic(Napi::Env env, Napi::Object exports) {
    exports.Set("evaluateSwirlTonic", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 8) return e.Null();
        auto r = sst::SwirlTonicAPI::evaluate(
            as_vec(info[0]), as_vec(info[1]), as_vec(info[2]),
            as_vec(info[3]), as_vec(info[4]), as_vec(info[5]),
            info[6].As<Napi::Number>().DoubleValue(),
            info[7].As<Napi::Boolean>().Value());
        Napi::Object o = Napi::Object::New(e);
        o.Set("circulation", Napi::Number::New(e, r.circulation));
        o.Set("holonomy", Napi::Number::New(e, r.holonomy));
        o.Set("materialNotAEff", Napi::Boolean::New(e, r.material_not_a_eff));
        o.Set("passed", Napi::Boolean::New(e, r.passed));
        o.Set("message", Napi::String::New(e, r.message));
        return o;
    }));
}
