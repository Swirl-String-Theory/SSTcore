// node_hyperbolic_volume.cpp
#include <napi.h>
#include "../hyperbolic_volume.h"

void bind_hyperbolic_volume(Napi::Env env, Napi::Object exports) {
    exports.Set("hyperbolicVolumeFromPd", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        if (info.Length() < 1 || !info[0].IsArray()) {
            throw Napi::TypeError::New(info.Env(), "Expected PD: array of [a,b,c,d] crossings");
        }
        Napi::Array arr = info[0].As<Napi::Array>();
        sst::PD pd;
        pd.reserve(arr.Length());
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            Napi::Array q = arr.Get(i).As<Napi::Array>();
            if (q.Length() != 4u) {
                throw Napi::TypeError::New(info.Env(), "each crossing must have 4 integers");
            }
            sst::Crossing c = {q.Get(0u).As<Napi::Number>().Int32Value(), q.Get(1u).As<Napi::Number>().Int32Value(),
                               q.Get(2u).As<Napi::Number>().Int32Value(), q.Get(3u).As<Napi::Number>().Int32Value()};
            pd.push_back(c);
        }
        double v = sst::hyperbolic_volume_from_pd(pd);
        return Napi::Number::New(info.Env(), v);
    }));
    exports.Set("hyperbolicVolumeAvailable", Napi::Boolean::New(env, true));
}
