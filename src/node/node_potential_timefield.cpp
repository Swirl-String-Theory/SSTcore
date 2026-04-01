// node_potential_timefield.cpp
#include <napi.h>
#include "node_utils.h"
#include "../potential_timefield.h"

void bind_timefield(Napi::Env env, Napi::Object exports) {
    exports.Set("computeGravitationalPotentialGradient", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (positions, vorticity[, epsilon])");
        }
        auto pos = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto vor = js_array_to_vec3_list(info[1].As<Napi::Array>());
        double eps = (info.Length() > 2) ? info[2].As<Napi::Number>().DoubleValue() : 7e-7;
        std::vector<double> phi = sst::TimeField::compute_gravitational_potential_gradient(pos, vor, eps);
        Napi::Array out = Napi::Array::New(e, phi.size());
        for (size_t i = 0; i < phi.size(); ++i) {
            out.Set(static_cast<uint32_t>(i), Napi::Number::New(e, phi[i]));
        }
        return out;
    }));

    exports.Set("computeTimeDilationMapSqrt", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1) {
            throw Napi::TypeError::New(e, "Expected (tangents[, Ce])");
        }
        auto t = js_array_to_vec3_list(info[0].As<Napi::Array>());
        double Ce = (info.Length() > 1) ? info[1].As<Napi::Number>().DoubleValue() : 1093845.63;
        std::vector<double> m = sst::TimeField::compute_time_dilation_map_sqrt(t, Ce);
        Napi::Array out = Napi::Array::New(e, m.size());
        for (size_t i = 0; i < m.size(); ++i) {
            out.Set(static_cast<uint32_t>(i), Napi::Number::New(e, m[i]));
        }
        return out;
    }));

    exports.Set("computeGravitationalPotentialDirect", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (positions, vorticity[, epsilon])");
        }
        auto pos = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto vor = js_array_to_vec3_list(info[1].As<Napi::Array>());
        double eps = (info.Length() > 2) ? info[2].As<Napi::Number>().DoubleValue() : 0.1;
        std::vector<double> phi = sst::TimeField::compute_gravitational_potential_direct(pos, vor, eps);
        Napi::Array out = Napi::Array::New(e, phi.size());
        for (size_t i = 0; i < phi.size(); ++i) {
            out.Set(static_cast<uint32_t>(i), Napi::Number::New(e, phi[i]));
        }
        return out;
    }));

    exports.Set("computeTimeDilationMapLinear", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (tangents, Ce)");
        }
        auto t = js_array_to_vec3_list(info[0].As<Napi::Array>());
        double Ce = info[1].As<Napi::Number>().DoubleValue();
        std::vector<double> m = sst::TimeField::compute_time_dilation_map_linear(t, Ce);
        Napi::Array out = Napi::Array::New(e, m.size());
        for (size_t i = 0; i < m.size(); ++i) {
            out.Set(static_cast<uint32_t>(i), Napi::Number::New(e, m[i]));
        }
        return out;
    }));

    exports.Set("computeGravitationalPotential", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        auto pos = js_array_to_vec3_list(info[0].As<Napi::Array>());
        auto vor = js_array_to_vec3_list(info[1].As<Napi::Array>());
        double eps = (info.Length() > 2) ? info[2].As<Napi::Number>().DoubleValue() : 7e-7;
        std::vector<double> phi = sst::compute_gravitational_potential(pos, vor, eps);
        Napi::Array out = Napi::Array::New(e, phi.size());
        for (size_t i = 0; i < phi.size(); ++i) {
            out.Set(static_cast<uint32_t>(i), Napi::Number::New(e, phi[i]));
        }
        return out;
    }));

    exports.Set("computeTimeDilationMap", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        auto t = js_array_to_vec3_list(info[0].As<Napi::Array>());
        double Ce = (info.Length() > 1) ? info[1].As<Napi::Number>().DoubleValue() : 1093845.63;
        std::vector<double> m = sst::compute_time_dilation_map(t, Ce);
        Napi::Array out = Napi::Array::New(e, m.size());
        for (size_t i = 0; i < m.size(); ++i) {
            out.Set(static_cast<uint32_t>(i), Napi::Number::New(e, m[i]));
        }
        return out;
    }));

    exports.Set("timeFieldAvailable", Napi::Boolean::New(env, true));
}
