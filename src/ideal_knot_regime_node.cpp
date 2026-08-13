#include <napi.h>
#include "sst_ideal_knot_regime.h"

void bind_ideal_knot_regime(Napi::Env env, Napi::Object exports) {
    exports.Set("evaluateIdealKnotRegime", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 6) return e.Null();
        double kkt = info.Length() > 6 ? info[6].As<Napi::Number>().DoubleValue() : 0.0;
        auto r = sst::IdealKnotRegimeAPI::evaluate(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(),
            info[3].As<Napi::Number>().DoubleValue(),
            info[4].As<Napi::Number>().DoubleValue(),
            info[5].As<Napi::Number>().DoubleValue(),
            kkt);
        Napi::Object o = Napi::Object::New(e);
        o.Set("epsilonKappa", Napi::Number::New(e, r.epsilon_kappa));
        o.Set("epsilonSep", Napi::Number::New(e, r.epsilon_sep));
        o.Set("regime", Napi::String::New(e, sst::IdealKnotRegimeAPI::regime_name(r.regime)));
        o.Set("helicityMoffattRicca", Napi::Number::New(e, r.helicity_moffatt_ricca));
        o.Set("kktResidual", Napi::Number::New(e, r.kkt_residual));
        o.Set("liaKamExcluded", Napi::Boolean::New(e, r.lia_kam_excluded));
        o.Set("message", Napi::String::New(e, r.message));
        return o;
    }));
    exports.Set("moffattRiccaHelicity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 3) return e.Null();
        return Napi::Number::New(e, sst::IdealKnotRegimeAPI::moffatt_ricca_helicity(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }));
}
