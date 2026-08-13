#include <napi.h>
#include "sst_spectro_response.h"
#include <vector>

void bind_spectro_response(Napi::Env env, Napi::Object exports) {
    exports.Set("spectroLinearResponseDeltaNu", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 3 || !info[1].IsArray() || !info[2].IsArray()) return e.Null();
        double h = info[0].As<Napi::Number>().DoubleValue();
        Napi::Array a = info[1].As<Napi::Array>();
        Napi::Array b = info[2].As<Napi::Array>();
        std::vector<double> dE, dq;
        for (uint32_t i = 0; i < a.Length(); ++i) dE.push_back(a.Get(i).As<Napi::Number>().DoubleValue());
        for (uint32_t i = 0; i < b.Length(); ++i) dq.push_back(b.Get(i).As<Napi::Number>().DoubleValue());
        return Napi::Number::New(e, sst::SpectroResponseAPI::linear_response_delta_nu(h, dE, dq));
    }));
}
