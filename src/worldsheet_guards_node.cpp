#include <napi.h>
#include "sst_worldsheet_guards.h"

void bind_worldsheet_guards(Napi::Env env, Napi::Object exports) {
    exports.Set("evaluateWorldsheetGuards", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 5) return e.Null();
        auto r = sst::WorldsheetGuardsAPI::evaluate(
            info[0].As<Napi::Number>().Int32Value(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(),
            info[3].As<Napi::Boolean>().Value(),
            info[4].As<Napi::Boolean>().Value());
        Napi::Object o = Napi::Object::New(e);
        o.Set("formDegreeOk", Napi::Boolean::New(e, r.form_degree_ok));
        o.Set("chargeNotGamma0", Napi::Boolean::New(e, r.charge_not_gamma0));
        o.Set("bNotAEm", Napi::Boolean::New(e, r.b_not_a_em));
        o.Set("materialVNotAEff", Napi::Boolean::New(e, r.material_v_not_a_eff));
        o.Set("passed", Napi::Boolean::New(e, r.passed));
        o.Set("message", Napi::String::New(e, r.message));
        return o;
    }));
}
