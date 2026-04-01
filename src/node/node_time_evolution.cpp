// node_time_evolution.cpp
#include <napi.h>
#include "node_utils.h"
#include "../time_evolution.h"

namespace {

class TimeEvolutionWrap : public Napi::ObjectWrap<TimeEvolutionWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "TimeEvolution",
            {InstanceMethod("evolve", &TimeEvolutionWrap::Evolve),
             InstanceMethod("getPositions", &TimeEvolutionWrap::GetPositions),
             InstanceMethod("getTangents", &TimeEvolutionWrap::GetTangents)});
        exports.Set("TimeEvolution", func);
    }

    TimeEvolutionWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<TimeEvolutionWrap>(info) {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (initialPositions, initialTangents[, gamma])");
        }
        std::vector<sst::Vec3> pos = js_array_to_vec3_list(info[0].As<Napi::Array>());
        std::vector<sst::Vec3> tan = js_array_to_vec3_list(info[1].As<Napi::Array>());
        double gamma = (info.Length() > 2) ? info[2].As<Napi::Number>().DoubleValue() : 1.0;
        te_ = std::make_unique<sst::TimeEvolution>(pos, tan, gamma);
    }

private:
    std::unique_ptr<sst::TimeEvolution> te_;

    Napi::Value Evolve(const Napi::CallbackInfo& info) {
        if (info.Length() < 2) {
            throw Napi::TypeError::New(info.Env(), "Expected (dt, steps)");
        }
        te_->evolve(info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().Int32Value());
        return info.Env().Undefined();
    }

    Napi::Value GetPositions(const Napi::CallbackInfo& info) {
        return vec3_list_to_js_typedarray(info.Env(), te_->get_positions());
    }

    Napi::Value GetTangents(const Napi::CallbackInfo& info) {
        return vec3_list_to_js_typedarray(info.Env(), te_->get_tangents());
    }
};

} // namespace

void bind_time_evolution(Napi::Env env, Napi::Object exports) {
    TimeEvolutionWrap::Init(env, exports);
    exports.Set("timeEvolutionAvailable", Napi::Boolean::New(env, true));
}
