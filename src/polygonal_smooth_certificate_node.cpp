#include <napi.h>
#include "polygonal_smooth_certificate.h"
#include "biot_savart_gate.h"
#include "node_utils.h"

namespace {

Napi::String StatusName(Napi::Env env, sst::CertificateStatus s) {
    return Napi::String::New(env, sst::certificate_status_name(s));
}

Napi::Object PolySmoothToJs(Napi::Env env, const sst::PolygonalSmoothCertificate& c) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("status", StatusName(env, c.status));
    o.Set("hausdorffBound", Napi::Number::New(env, c.hausdorff_bound));
    o.Set("tangentError", Napi::Number::New(env, c.tangent_error));
    o.Set("curvatureError", Napi::Number::New(env, c.curvature_error));
    o.Set("thicknessLowerBound", Napi::Number::New(env, c.thickness_lower_bound));
    o.Set("polygonHash", Napi::String::New(env, c.polygon_hash));
    o.Set("smoothHash", Napi::String::New(env, c.smooth_hash));
    return o;
}

Napi::Object BiotGateToJs(Napi::Env env, const sst::BiotSavartGateResult& c) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("status", StatusName(env, c.status));
    o.Set("observable", Napi::Number::New(env, c.observable));
    o.Set("estimatedLimit", Napi::Number::New(env, c.estimated_limit));
    o.Set("relativeResidual", Napi::Number::New(env, c.relative_residual));
    o.Set("boundaryMargin", Napi::Number::New(env, c.boundary_margin));
    o.Set("sampleCount", Napi::Number::New(env, static_cast<double>(c.sample_count)));
    o.Set("regularizationId", Napi::String::New(env, c.regularization_id));
    return o;
}

} // namespace

void bind_polygonal_smooth_certificate(Napi::Env env, Napi::Object exports) {
    exports.Set("evaluatePolygonalSmoothCertificate", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 6) {
            Napi::TypeError::New(env, "evaluatePolygonalSmoothCertificate(poly, smooth, a, hTol, tTol, kTol)").ThrowAsJavaScriptException();
            return env.Null();
        }
        auto poly = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto smooth = js_array_to_vec3_list(info[1].As<Napi::Array>());
        const double a = info[2].As<Napi::Number>().DoubleValue();
        const double ht = info[3].As<Napi::Number>().DoubleValue();
        const double tt = info[4].As<Napi::Number>().DoubleValue();
        const double kt = info[5].As<Napi::Number>().DoubleValue();
        return PolySmoothToJs(env, sst::PolygonalSmoothCertificateAPI::evaluate(poly, smooth, a, ht, tt, kt));
    }));

    exports.Set("evaluateBiotSavartGate", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 6) {
            Napi::TypeError::New(env, "evaluateBiotSavartGate(obs, limit, margin, minMargin, n, regId, ...)").ThrowAsJavaScriptException();
            return env.Null();
        }
        const double obs = info[0].As<Napi::Number>().DoubleValue();
        const double lim = info[1].As<Napi::Number>().DoubleValue();
        const double margin = info[2].As<Napi::Number>().DoubleValue();
        const double minMargin = info[3].As<Napi::Number>().DoubleValue();
        const std::size_t n = static_cast<std::size_t>(info[4].As<Napi::Number>().Uint32Value());
        const std::string reg = info[5].As<Napi::String>().Utf8Value();
        const double tol = info.Length() > 6 ? info[6].As<Napi::Number>().DoubleValue() : 1e-3;
        const bool fourPi = info.Length() > 7 ? info[7].As<Napi::Boolean>().Value() : true;
        return BiotGateToJs(env, sst::BiotSavartGateAPI::evaluate(obs, lim, margin, minMargin, n, reg, tol, fourPi));
    }));
}
