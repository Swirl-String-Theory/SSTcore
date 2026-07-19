// chronos_kelvin_transport_node.cpp — N-API bindings for ChronosKelvinTransport
#include <napi.h>
#include "chronos_kelvin_transport.h"
#include "SST_Constants.h"

namespace {

class ChronosKelvinTransportWrap : public Napi::ObjectWrap<ChronosKelvinTransportWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "ChronosKelvinTransport",
            {StaticMethod("kelvinInvariant", &ChronosKelvinTransportWrap::KelvinInvariant),
             StaticMethod("omegaFromInvariant", &ChronosKelvinTransportWrap::OmegaFromInvariant),
             StaticMethod("omegaFromSwirlClock", &ChronosKelvinTransportWrap::OmegaFromSwirlClock),
             StaticMethod("vorticityFromSwirlClock",
                          &ChronosKelvinTransportWrap::VorticityFromSwirlClock),
             StaticMethod("swirlClockFromOmega", &ChronosKelvinTransportWrap::SwirlClockFromOmega),
             StaticMethod("chronosKelvinInvariant",
                          &ChronosKelvinTransportWrap::ChronosKelvinInvariant),
             StaticMethod("clockRadiusDerivative",
                          &ChronosKelvinTransportWrap::ClockRadiusDerivative),
             StaticMethod("radiusFromClockInvariant",
                          &ChronosKelvinTransportWrap::RadiusFromClockInvariant)});
        exports.Set("ChronosKelvinTransport", func);
    }

    ChronosKelvinTransportWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<ChronosKelvinTransportWrap>(info) {}

private:
    static double opt(const Napi::CallbackInfo& info, size_t i, double def) {
        return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().DoubleValue() : def;
    }
    static double c_default(const Napi::CallbackInfo& info, size_t i) {
        return opt(info, i, static_cast<double>(SST::Constants::C_VACUUM));
    }

    static Napi::Value KelvinInvariant(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ChronosKelvinTransport::kelvin_invariant(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value OmegaFromInvariant(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ChronosKelvinTransport::omega_from_invariant(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value OmegaFromSwirlClock(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ChronosKelvinTransport::omega_from_swirl_clock(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 c_default(info, 2)));
    }
    static Napi::Value VorticityFromSwirlClock(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ChronosKelvinTransport::vorticity_from_swirl_clock(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 c_default(info, 2)));
    }
    static Napi::Value SwirlClockFromOmega(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ChronosKelvinTransport::swirl_clock_from_omega(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 c_default(info, 2)));
    }
    static Napi::Value ChronosKelvinInvariant(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ChronosKelvinTransport::chronos_kelvin_invariant(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 c_default(info, 3)));
    }
    static Napi::Value ClockRadiusDerivative(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ChronosKelvinTransport::clock_radius_derivative(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value RadiusFromClockInvariant(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ChronosKelvinTransport::radius_from_clock_invariant(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 c_default(info, 3)));
    }
};

} // namespace

void bind_chronos_kelvin_transport(Napi::Env env, Napi::Object exports) {
    ChronosKelvinTransportWrap::Init(env, exports);
    exports.Set("chronosKelvinTransportAvailable", Napi::Boolean::New(env, true));
}
