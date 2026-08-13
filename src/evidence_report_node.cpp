#include <napi.h>
#include "sst_check_kind.h"
#include "sst_evidence_report.h"

void bind_evidence_report(Napi::Env env, Napi::Object exports) {
    exports.Set("checkKindExportString", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) {
            Napi::TypeError::New(env, "checkKindExportString(kindIndex0to6)").ThrowAsJavaScriptException();
            return env.Null();
        }
        const int k = info[0].As<Napi::Number>().Int32Value();
        auto kind = static_cast<sst::CheckKind>(k);
        return Napi::String::New(env, sst::check_kind_export_string(kind));
    }));

    exports.Set("buildEvidenceReportJson", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        sst::EvidenceReportMeta meta;
        meta.sstcore_version = info.Length() > 0 && info[0].IsString() ? info[0].As<Napi::String>().Utf8Value() : "";
        meta.canon_version = info.Length() > 1 && info[1].IsString() ? info[1].As<Napi::String>().Utf8Value() : "";
        std::vector<sst::CheckResult> checks;
        if (info.Length() > 2 && info[2].IsArray()) {
            Napi::Array arr = info[2].As<Napi::Array>();
            for (uint32_t i = 0; i < arr.Length(); ++i) {
                Napi::Object o = arr.Get(i).As<Napi::Object>();
                sst::CheckResult c;
                if (o.Has("name")) c.name = o.Get("name").As<Napi::String>().Utf8Value();
                if (o.Has("passed")) c.passed = o.Get("passed").As<Napi::Boolean>().Value();
                if (o.Has("kind")) c.kind = static_cast<sst::CheckKind>(o.Get("kind").As<Napi::Number>().Int32Value());
                if (o.Has("residual")) c.residual = o.Get("residual").As<Napi::Number>().DoubleValue();
                if (o.Has("tolerance")) c.tolerance = o.Get("tolerance").As<Napi::Number>().DoubleValue();
                if (o.Has("supportsEmpiricalClaim")) c.supports_empirical_claim = o.Get("supportsEmpiricalClaim").As<Napi::Boolean>().Value();
                if (o.Has("message")) c.message = o.Get("message").As<Napi::String>().Utf8Value();
                checks.push_back(c);
            }
        }
        return Napi::String::New(env, sst::EvidenceReportAPI::build_report_json(meta, checks));
    }));
}
