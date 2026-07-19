// spectroscopic_gap_node.cpp — N-API bindings for SpectroscopicGap
#include <napi.h>
#include "spectroscopic_gap.h"

namespace {

class SpectroscopicGapWrap : public Napi::ObjectWrap<SpectroscopicGapWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "SpectroscopicGap",
            {StaticMethod("kelvinGapJoule", &SpectroscopicGapWrap::KelvinGapJoule),
             StaticMethod("jouleToEv", &SpectroscopicGapWrap::JouleToEv),
             StaticMethod("evToJoule", &SpectroscopicGapWrap::EvToJoule),
             StaticMethod("kelvinGapEv", &SpectroscopicGapWrap::KelvinGapEv),
             StaticMethod("boltzmannSuppression", &SpectroscopicGapWrap::BoltzmannSuppression),
             StaticMethod("isDecoupledFromAtomicTransition",
                          &SpectroscopicGapWrap::IsDecoupledFromAtomicTransition),
             StaticMethod("gapRatio", &SpectroscopicGapWrap::GapRatio)});
        exports.Set("SpectroscopicGap", func);
    }

    SpectroscopicGapWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<SpectroscopicGapWrap>(info) {}

private:
    static double opt(const Napi::CallbackInfo& info, size_t i, double def) {
        return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().DoubleValue() : def;
    }

    static Napi::Value KelvinGapJoule(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SpectroscopicGap::kelvin_gap_joule(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 opt(info, 3, 1.0)));
    }
    static Napi::Value JouleToEv(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(),
                                 sst::SpectroscopicGap::joule_to_ev(info[0].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value EvToJoule(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(),
                                 sst::SpectroscopicGap::ev_to_joule(info[0].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value KelvinGapEv(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SpectroscopicGap::kelvin_gap_ev(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 opt(info, 3, 1.0)));
    }
    static Napi::Value BoltzmannSuppression(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SpectroscopicGap::boltzmann_suppression(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 opt(info, 2, 1.380649e-23)));
    }
    static Napi::Value IsDecoupledFromAtomicTransition(const Napi::CallbackInfo& info) {
        return Napi::Boolean::New(info.Env(),
                                  sst::SpectroscopicGap::is_decoupled_from_atomic_transition(
                                      info[0].As<Napi::Number>().DoubleValue(),
                                      info[1].As<Napi::Number>().DoubleValue(), opt(info, 2, 10.0)));
    }
    static Napi::Value GapRatio(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SpectroscopicGap::gap_ratio(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
};

} // namespace

void bind_spectroscopic_gap(Napi::Env env, Napi::Object exports) {
    SpectroscopicGapWrap::Init(env, exports);
    exports.Set("spectroscopicGapAvailable", Napi::Boolean::New(env, true));
}
