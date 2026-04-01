// node_sst_integrator.cpp
#include <napi.h>
#include "node_utils.h"
#include "../sst_integrator.h"

void bind_sst_integrator(Napi::Env env, Napi::Object exports) {
    exports.Set("computeSstMass", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (points, chi_spin)");
        }
        std::vector<sst::Vec3> pts;
        if (info[0].IsArray()) {
            pts = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            pts = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(e, "points must be array or Float64Array");
        }
        const double chi = info[1].As<Napi::Number>().DoubleValue();
        double m_core = 0.0, m_fluid = 0.0;
        sst::compute_sst_mass(pts, chi, m_core, m_fluid);
        Napi::Array out = Napi::Array::New(e, 2);
        out.Set(0u, Napi::Number::New(e, m_core));
        out.Set(1u, Napi::Number::New(e, m_fluid));
        return out;
    }));
    exports.Set("sstIntegratorAvailable", Napi::Boolean::New(env, true));
}
