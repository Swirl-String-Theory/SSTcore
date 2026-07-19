// delay_mode_selector_node.cpp — N-API bindings for DelayModeSelector
#include <napi.h>
#include "delay_mode_selector.h"

namespace {

class DelayModeResultWrap : public Napi::ObjectWrap<DelayModeResultWrap> {
public:
    static Napi::FunctionReference constructor;

    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "DelayModeResult",
            {InstanceAccessor("omega", &DelayModeResultWrap::GetOmega, &DelayModeResultWrap::SetOmega),
             InstanceAccessor("residual", &DelayModeResultWrap::GetResidual, &DelayModeResultWrap::SetResidual),
             InstanceAccessor("tau", &DelayModeResultWrap::GetTau, &DelayModeResultWrap::SetTau),
             InstanceAccessor("converged", &DelayModeResultWrap::GetConverged, &DelayModeResultWrap::SetConverged),
             InstanceAccessor("iterations", &DelayModeResultWrap::GetIterations,
                             &DelayModeResultWrap::SetIterations)});
        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("DelayModeResult", func);
    }

    static Napi::Object NewInstance(Napi::Env env, const sst::DelayModeResult& r) {
        Napi::Object obj = constructor.New({});
        Unwrap(obj)->inner_ = r;
        return obj;
    }

    DelayModeResultWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<DelayModeResultWrap>(info) {}

    sst::DelayModeResult inner_;

private:
    Napi::Value GetOmega(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.omega);
    }
    void SetOmega(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.omega = v.As<Napi::Number>().DoubleValue();
    }
    Napi::Value GetResidual(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.residual);
    }
    void SetResidual(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.residual = v.As<Napi::Number>().DoubleValue();
    }
    Napi::Value GetTau(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.tau);
    }
    void SetTau(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.tau = v.As<Napi::Number>().DoubleValue();
    }
    Napi::Value GetConverged(const Napi::CallbackInfo& info) {
        return Napi::Boolean::New(info.Env(), inner_.converged);
    }
    void SetConverged(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.converged = v.As<Napi::Boolean>().Value();
    }
    Napi::Value GetIterations(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.iterations);
    }
    void SetIterations(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.iterations = v.As<Napi::Number>().Int32Value();
    }
};

Napi::FunctionReference DelayModeResultWrap::constructor;

class DelayModeSelectorWrap : public Napi::ObjectWrap<DelayModeSelectorWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "DelayModeSelector",
            {StaticMethod("circulationDelay", &DelayModeSelectorWrap::CirculationDelay),
             StaticMethod("coreTurnoverDelay", &DelayModeSelectorWrap::CoreTurnoverDelay),
             StaticMethod("discreteModeFrequency", &DelayModeSelectorWrap::DiscreteModeFrequency),
             StaticMethod("phaseLockResidual", &DelayModeSelectorWrap::PhaseLockResidual),
             StaticMethod("phaseLockStabilitySlope", &DelayModeSelectorWrap::PhaseLockStabilitySlope),
             StaticMethod("solvePhaseLockedFrequency",
                          &DelayModeSelectorWrap::SolvePhaseLockedFrequency)});
        exports.Set("DelayModeSelector", func);
    }

    DelayModeSelectorWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<DelayModeSelectorWrap>(info) {}

private:
    static double opt(const Napi::CallbackInfo& info, size_t i, double def) {
        return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().DoubleValue() : def;
    }
    static int opt_i(const Napi::CallbackInfo& info, size_t i, int def) {
        return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().Int32Value() : def;
    }

    static Napi::Value CirculationDelay(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::DelayModeSelector::circulation_delay(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value CoreTurnoverDelay(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::DelayModeSelector::core_turnover_delay(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value DiscreteModeFrequency(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::DelayModeSelector::discrete_mode_frequency(
                                                 info[0].As<Napi::Number>().Int32Value(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value PhaseLockResidual(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::DelayModeSelector::phase_lock_residual(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value PhaseLockStabilitySlope(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::DelayModeSelector::phase_lock_stability_slope(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value SolvePhaseLockedFrequency(const Napi::CallbackInfo& info) {
        sst::DelayModeResult r = sst::DelayModeSelector::solve_phase_locked_frequency(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue(), opt(info, 3, 0.0), opt_i(info, 4, 64),
            opt(info, 5, 1e-12));
        return DelayModeResultWrap::NewInstance(info.Env(), r);
    }
};

} // namespace

void bind_delay_mode_selector(Napi::Env env, Napi::Object exports) {
    DelayModeResultWrap::Init(env, exports);
    DelayModeSelectorWrap::Init(env, exports);
    exports.Set("delayModeSelectorAvailable", Napi::Boolean::New(env, true));
}
