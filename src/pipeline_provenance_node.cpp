#include <napi.h>
#include "sst_pipeline_provenance.h"

namespace {

sst::ProvenanceRecord JsToRecord(const Napi::Object& o) {
    sst::ProvenanceRecord r;
    if (o.Has("stage")) r.stage = static_cast<sst::PipelineStage>(o.Get("stage").As<Napi::Number>().Int32Value());
    if (o.Has("certification")) r.certification = static_cast<sst::PipelineCertificationStatus>(o.Get("certification").As<Napi::Number>().Int32Value());
    auto getStr = [&](const char* k) -> std::string {
        if (!o.Has(k) || !o.Get(k).IsString()) return {};
        return o.Get(k).As<Napi::String>().Utf8Value();
    };
    r.tool_name = getStr("toolName");
    r.tool_version = getStr("toolVersion");
    r.input_sha256 = getStr("inputSha256");
    r.output_sha256 = getStr("outputSha256");
    r.parameter_sha256 = getStr("parameterSha256");
    r.parent_record_sha256 = getStr("parentRecordSha256");
    r.coordinate_convention = getStr("coordinateConvention");
    r.scale_convention = getStr("scaleConvention");
    r.timestamp_utc = getStr("timestampUtc");
    return r;
}

} // namespace

void bind_pipeline_provenance(Napi::Env env, Napi::Object exports) {
    exports.Set("evaluateProvenanceChain", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1 || !info[0].IsArray()) {
            Napi::TypeError::New(env, "evaluateProvenanceChain(records[])").ThrowAsJavaScriptException();
            return env.Null();
        }
        Napi::Array arr = info[0].As<Napi::Array>();
        std::vector<sst::ProvenanceRecord> recs;
        recs.reserve(arr.Length());
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            recs.push_back(JsToRecord(arr.Get(i).As<Napi::Object>()));
        }
        auto st = sst::PipelineProvenanceAPI::evaluate_chain(recs);
        return Napi::String::New(env, sst::PipelineProvenanceAPI::certification_name(st));
    }));

    exports.Set("provenanceRecordFingerprint", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1 || !info[0].IsObject()) {
            Napi::TypeError::New(env, "provenanceRecordFingerprint(record)").ThrowAsJavaScriptException();
            return env.Null();
        }
        auto r = JsToRecord(info[0].As<Napi::Object>());
        return Napi::String::New(env, sst::PipelineProvenanceAPI::record_fingerprint(r));
    }));
}
