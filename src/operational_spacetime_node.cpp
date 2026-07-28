#include <napi.h>
#include "sst_operational_spacetime.h"
#include "sst_qss_spectroscopy.h"
#include "node_utils.h"

namespace {

Napi::Object RadarToJs(Napi::Env env, const sst::RadarInterval& r) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("emissionTime", Napi::Number::New(env, r.emission_time));
    o.Set("receptionTime", Napi::Number::New(env, r.reception_time));
    o.Set("radarTime", Napi::Number::New(env, r.radar_time));
    o.Set("radarDistance", Napi::Number::New(env, r.radar_distance));
    o.Set("causal", Napi::Boolean::New(env, r.causal));
    return o;
}

Napi::Object LorentzToJs(Napi::Env env, const sst::LorentzMapResult& r) {
    Napi::Object o = Napi::Object::New(env);
    Napi::Array ev = Napi::Array::New(env, 4);
    for (uint32_t i = 0; i < 4; ++i) ev.Set(i, Napi::Number::New(env, r.transformed_event[i]));
    o.Set("transformedEvent", ev);
    o.Set("gamma", Napi::Number::New(env, r.gamma));
    o.Set("invariantResidual", Napi::Number::New(env, r.invariant_residual));
    return o;
}

} // namespace

void bind_operational_spacetime(Napi::Env env, Napi::Object exports) {
    exports.Set("radarInterval", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            Napi::TypeError::New(env, "radarInterval(Tminus, Tplus, c=1)").ThrowAsJavaScriptException();
            return env.Null();
        }
        const double tm = info[0].As<Napi::Number>().DoubleValue();
        const double tp = info[1].As<Napi::Number>().DoubleValue();
        const double c = info.Length() > 2 ? info[2].As<Napi::Number>().DoubleValue() : 1.0;
        return RadarToJs(env, sst::OperationalSpacetimeAPI::radar_interval(tm, tp, c));
    }));

    exports.Set("lorentzBoostX", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2 || !info[0].IsArray()) {
            Napi::TypeError::New(env, "lorentzBoostX(event[4], v, c=1)").ThrowAsJavaScriptException();
            return env.Null();
        }
        Napi::Array arr = info[0].As<Napi::Array>();
        if (arr.Length() != 4) {
            Napi::TypeError::New(env, "event must have length 4").ThrowAsJavaScriptException();
            return env.Null();
        }
        std::array<double, 4> ev{};
        for (uint32_t i = 0; i < 4; ++i) ev[i] = arr.Get(i).As<Napi::Number>().DoubleValue();
        const double v = info[1].As<Napi::Number>().DoubleValue();
        const double c = info.Length() > 2 ? info[2].As<Napi::Number>().DoubleValue() : 1.0;
        return LorentzToJs(env, sst::OperationalSpacetimeAPI::lorentz_boost_x(ev, v, c));
    }));
}

void bind_qss_spectroscopy(Napi::Env env, Napi::Object exports) {
    exports.Set("qssEigen2x2", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1 || !info[0].IsArray()) {
            Napi::TypeError::New(env, "qssEigen2x2(matrixRowMajor[4])").ThrowAsJavaScriptException();
            return env.Null();
        }
        auto m = js_array_to_double_vector(info[0].As<Napi::Array>());
        auto r = sst::QSSSpectroscopyAPI::eigen_2x2(m);
        Napi::Object o = Napi::Object::New(env);
        Napi::Array eigs = Napi::Array::New(env, r.eigenvalues.size());
        for (size_t i = 0; i < r.eigenvalues.size(); ++i) {
            Napi::Object z = Napi::Object::New(env);
            z.Set("re", Napi::Number::New(env, r.eigenvalues[i].real()));
            z.Set("im", Napi::Number::New(env, r.eigenvalues[i].imag()));
            eigs.Set(i, z);
        }
        o.Set("eigenvalues", eigs);
        o.Set("eigenResidual", Napi::Number::New(env, r.eigen_residual));
        o.Set("conditioning", Napi::Number::New(env, r.conditioning));
        o.Set("epistemicStatus", Napi::String::New(env, r.epistemic_status));
        return o;
    }));
}
