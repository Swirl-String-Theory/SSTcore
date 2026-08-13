#include <napi.h>
#include "sst_kam_diagnostics.h"
#include "node_utils.h"

void bind_kam_diagnostics(Napi::Env env, Napi::Object exports) {
    exports.Set("kamStage1", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            Napi::TypeError::New(env, "kamStage1(sectorSBool, frequencies, hessian)").ThrowAsJavaScriptException();
            return env.Null();
        }
        const bool isS = info[0].As<Napi::Boolean>().Value();
        auto freqs = js_array_to_double_vector(info[1].As<Napi::Array>());
        auto hess = js_array_to_double_vector(info[2].As<Napi::Array>());
        const double tau = info.Length() > 3 ? info[3].As<Napi::Number>().DoubleValue() : 1e-6;
        auto r = sst::KAMDiagnosticsAPI::stage1(isS ? sst::KAMSector::S : sst::KAMSector::T, freqs, hess, tau);
        Napi::Object o = Napi::Object::New(env);
        o.Set("sector", Napi::String::New(env, sst::KAMDiagnosticsAPI::sector_name(r.sector)));
        o.Set("achievedStage", Napi::String::New(env, sst::KAMDiagnosticsAPI::stage_name(r.achieved_stage)));
        o.Set("hessianDeterminant", Napi::Number::New(env, r.hessian_determinant));
        o.Set("minimumDetuning", Napi::Number::New(env, r.minimum_detuning));
        o.Set("diophantineMargin", Napi::Number::New(env, r.diophantine_margin));
        o.Set("status", Napi::String::New(env, sst::certificate_status_name(r.status)));
        return o;
    }));

    exports.Set("goldenRatioNullTest", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) {
            Napi::TypeError::New(env, "goldenRatioNullTest(value, tol?)").ThrowAsJavaScriptException();
            return env.Null();
        }
        const double v = info[0].As<Napi::Number>().DoubleValue();
        const double tol = info.Length() > 1 ? info[1].As<Napi::Number>().DoubleValue() : 1e-9;
        return Napi::Boolean::New(env, sst::KAMDiagnosticsAPI::golden_ratio_null_test(v, tol));
    }));
}
