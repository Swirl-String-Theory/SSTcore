// node_swirl_field.cpp
#include <napi.h>
#include "../swirl_field.h"

void bind_swirl_field(Napi::Env env, Napi::Object exports) {
    exports.Set("computeSwirlField", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        if (info.Length() < 2) {
            throw Napi::TypeError::New(info.Env(), "Expected (res: int, time: number)");
        }
        const int res = info[0].As<Napi::Number>().Int32Value();
        const float t = static_cast<float>(info[1].As<Napi::Number>().FloatValue());
        std::vector<sst::Vec2f> f = sst::compute_swirl_field(res, t);
        const size_t n = f.size() * 2u;
        Napi::ArrayBuffer buf = Napi::ArrayBuffer::New(info.Env(), n * sizeof(float));
        float* d = static_cast<float*>(buf.Data());
        for (size_t i = 0; i < f.size(); ++i) {
            d[2 * i] = f[i][0];
            d[2 * i + 1] = f[i][1];
        }
        return Napi::Float32Array::New(info.Env(), n, buf, 0);
    }));
    exports.Set("swirlFieldAvailable", Napi::Boolean::New(env, true));
}
