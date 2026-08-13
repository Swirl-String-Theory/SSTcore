#include <napi.h>
#include "sst_qss_spectroscopy.h"
#include "node_utils.h"

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
        o.Set("eigenvalueMagnitudeRatio", Napi::Number::New(env, r.eigenvalue_magnitude_ratio));
        o.Set("conditioning", Napi::Number::New(env, r.conditioning));
        o.Set("epistemicStatus", Napi::String::New(env, r.epistemic_status));
        return o;
    }));
}
