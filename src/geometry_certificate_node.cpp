// geometry_certificate_node.cpp
#include <napi.h>
#include "geometry_certificate.h"
#include "node_utils.h"

namespace {

Napi::String StatusName(Napi::Env env, sst::CertificateStatus s) {
    return Napi::String::New(env, sst::certificate_status_name(s));
}

Napi::Object GeometryCertToJs(Napi::Env env, const sst::GeometryCertificate& c) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("status", StatusName(env, c.status));
    o.Set("minimumSeparation", Napi::Number::New(env, c.minimum_separation));
    o.Set("minimumRadiusOfCurvature", Napi::Number::New(env, c.minimum_radius_of_curvature));
    o.Set("tubeRadius", Napi::Number::New(env, c.tube_radius));
    o.Set("thicknessMargin", Napi::Number::New(env, c.thickness_margin));
    o.Set("discretizationError", Napi::Number::New(env, c.discretization_error));
    o.Set("geometryHash", Napi::String::New(env, c.geometry_hash));
    return o;
}

Napi::Object ContactSatToJs(Napi::Env env, const sst::ContactSaturationResult& c) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("status", StatusName(env, c.status));
    o.Set("peakContactPressure", Napi::Number::New(env, c.peak_contact_pressure));
    o.Set("saturationPressure", Napi::Number::New(env, c.saturation_pressure));
    o.Set("saturationRatio", Napi::Number::New(env, c.saturation_ratio));
    o.Set("activeContactCount", Napi::Number::New(env, static_cast<double>(c.active_contact_count)));
    return o;
}

Napi::Object ChronosHitToJs(Napi::Env env, const sst::ChronosFirstHittingResult& c) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("status", StatusName(env, c.status));
    o.Set("firstHittingTime", Napi::Number::New(env, c.first_hitting_time));
    o.Set("eventIndex", Napi::Number::New(env, static_cast<double>(c.event_index)));
    o.Set("threshold", Napi::Number::New(env, c.threshold));
    return o;
}

Napi::Object Rank9ToJs(Napi::Env env, const sst::Rank9ChannelDiagnostics& c) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("status", StatusName(env, c.status));
    o.Set("numericalRank", Napi::Number::New(env, c.numerical_rank));
    o.Set("conditioning", Napi::Number::New(env, c.conditioning));
    Napi::Array sv = Napi::Array::New(env, 9);
    for (std::size_t i = 0; i < 9; ++i) sv.Set(i, Napi::Number::New(env, c.singular_values[i]));
    o.Set("singularValues", sv);
    return o;
}

} // namespace

void bind_geometry_certificate(Napi::Env env, Napi::Object exports) {
    exports.Set("evaluateTubeGeometry", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            Napi::TypeError::New(env, "evaluateTubeGeometry(pts, tubeRadius, ...)").ThrowAsJavaScriptException();
            return env.Null();
        }
        auto pts = js_array_to_vec3_list(info[0].As<Napi::Array>());
        const double a = info[1].As<Napi::Number>().DoubleValue();
        const double sep = info.Length() > 2 ? info[2].As<Napi::Number>().DoubleValue() : 1e-9;
        const double cur = info.Length() > 3 ? info[3].As<Napi::Number>().DoubleValue() : 1e-9;
        return GeometryCertToJs(env, sst::GeometryCertificateAPI::evaluate_tube_geometry(pts, a, sep, cur));
    }));

    exports.Set("evaluateContactSaturation", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            Napi::TypeError::New(env, "evaluateContactSaturation(pressures, saturationPressure)").ThrowAsJavaScriptException();
            return env.Null();
        }
        auto pressures = js_array_to_double_vector(info[0].As<Napi::Array>());
        const double psat = info[1].As<Napi::Number>().DoubleValue();
        const double eps = info.Length() > 2 ? info[2].As<Napi::Number>().DoubleValue() : 1e-9;
        return ContactSatToJs(env, sst::GeometryCertificateAPI::evaluate_contact_saturation(pressures, psat, eps));
    }));

    exports.Set("chronosFirstHitting", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            Napi::TypeError::New(env, "chronosFirstHitting(times, observable, threshold)").ThrowAsJavaScriptException();
            return env.Null();
        }
        auto times = js_array_to_double_vector(info[0].As<Napi::Array>());
        auto obs = js_array_to_double_vector(info[1].As<Napi::Array>());
        const double thr = info[2].As<Napi::Number>().DoubleValue();
        return ChronosHitToJs(env, sst::GeometryCertificateAPI::chronos_first_hitting(times, obs, thr));
    }));

    exports.Set("rank9FromSingularValues", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1 || !info[0].IsArray()) {
            Napi::TypeError::New(env, "rank9FromSingularValues(singularValues[9])").ThrowAsJavaScriptException();
            return env.Null();
        }
        Napi::Array arr = info[0].As<Napi::Array>();
        if (arr.Length() != 9) {
            Napi::TypeError::New(env, "singularValues must have length 9").ThrowAsJavaScriptException();
            return env.Null();
        }
        std::array<double, 9> sv{};
        for (uint32_t i = 0; i < 9; ++i) sv[i] = arr.Get(i).As<Napi::Number>().DoubleValue();
        const double tau = info.Length() > 1 ? info[1].As<Napi::Number>().DoubleValue() : 1e-12;
        return Rank9ToJs(env, sst::GeometryCertificateAPI::rank9_from_singular_values(sv, tau));
    }));
}
