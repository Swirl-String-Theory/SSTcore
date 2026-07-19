// clock_field_eft_node.cpp — N-API bindings for ClockFieldEFT
#include <napi.h>
#include <array>
#include "clock_field_eft.h"
#include "SST_Constants.h"

namespace {

static sst::Vec4 read_vec4(const Napi::Value& v) {
    Napi::Array a = v.As<Napi::Array>();
    if (a.Length() < 4) {
        throw Napi::TypeError::New(a.Env(), "Expected array of 4 numbers");
    }
    sst::Vec4 out{};
    for (uint32_t i = 0; i < 4; ++i) {
        out[i] = a.Get(i).As<Napi::Number>().DoubleValue();
    }
    return out;
}

static Napi::Array vec4_to_js(Napi::Env env, const sst::Vec4& v) {
    Napi::Array a = Napi::Array::New(env, 4);
    for (uint32_t i = 0; i < 4; ++i) {
        a.Set(i, Napi::Number::New(env, v[i]));
    }
    return a;
}

class ClockSectorConstraintsWrap : public Napi::ObjectWrap<ClockSectorConstraintsWrap> {
public:
    static Napi::FunctionReference constructor;

    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "ClockSectorConstraints",
            {InstanceAccessor("c13", &ClockSectorConstraintsWrap::GetC13, &ClockSectorConstraintsWrap::SetC13),
             InstanceAccessor("tensorSpeed", &ClockSectorConstraintsWrap::GetTensorSpeed,
                             &ClockSectorConstraintsWrap::SetTensorSpeed),
             InstanceAccessor("tensorSpeedFractionalOffset",
                             &ClockSectorConstraintsWrap::GetTensorSpeedFractionalOffset,
                             &ClockSectorConstraintsWrap::SetTensorSpeedFractionalOffset),
             InstanceAccessor("gw170817Ok", &ClockSectorConstraintsWrap::GetGw170817Ok,
                             &ClockSectorConstraintsWrap::SetGw170817Ok)});
        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("ClockSectorConstraints", func);
    }

    static Napi::Object NewInstance(Napi::Env env, const sst::ClockSectorConstraints& c) {
        Napi::Object obj = constructor.New({});
        Unwrap(obj)->inner_ = c;
        return obj;
    }

    ClockSectorConstraintsWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<ClockSectorConstraintsWrap>(info) {}

    sst::ClockSectorConstraints inner_;

private:
    Napi::Value GetC13(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.c13);
    }
    void SetC13(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.c13 = v.As<Napi::Number>().DoubleValue();
    }
    Napi::Value GetTensorSpeed(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.tensor_speed);
    }
    void SetTensorSpeed(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.tensor_speed = v.As<Napi::Number>().DoubleValue();
    }
    Napi::Value GetTensorSpeedFractionalOffset(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.tensor_speed_fractional_offset);
    }
    void SetTensorSpeedFractionalOffset(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.tensor_speed_fractional_offset = v.As<Napi::Number>().DoubleValue();
    }
    Napi::Value GetGw170817Ok(const Napi::CallbackInfo& info) {
        return Napi::Boolean::New(info.Env(), inner_.gw170817_ok);
    }
    void SetGw170817Ok(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.gw170817_ok = v.As<Napi::Boolean>().Value();
    }
};

Napi::FunctionReference ClockSectorConstraintsWrap::constructor;

class ClockFieldEFTWrap : public Napi::ObjectWrap<ClockFieldEFTWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "ClockFieldEFT",
            {StaticMethod("c13", &ClockFieldEFTWrap::C13),
             StaticMethod("tensorSpeed", &ClockFieldEFTWrap::TensorSpeed),
             StaticMethod("tensorSpeedFractionalOffset", &ClockFieldEFTWrap::TensorSpeedFractionalOffset),
             StaticMethod("satisfiesGw170817", &ClockFieldEFTWrap::SatisfiesGw170817),
             StaticMethod("constraints", &ClockFieldEFTWrap::Constraints),
             StaticMethod("poissonSource", &ClockFieldEFTWrap::PoissonSource),
             StaticMethod("effectiveGravityFromPotentialGradient",
                          &ClockFieldEFTWrap::EffectiveGravityFromPotentialGradient),
             StaticMethod("unitTimelikeFromGradientMinkowski",
                          &ClockFieldEFTWrap::UnitTimelikeFromGradientMinkowski)});
        exports.Set("ClockFieldEFT", func);
    }

    ClockFieldEFTWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<ClockFieldEFTWrap>(info) {}

private:
    static double opt(const Napi::CallbackInfo& info, size_t i, double def) {
        return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().DoubleValue() : def;
    }

    static Napi::Value C13(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::ClockFieldEFT::c13(info[0].As<Napi::Number>().DoubleValue(),
                                                                     info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value TensorSpeed(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(),
            sst::ClockFieldEFT::tensor_speed(info[0].As<Napi::Number>().DoubleValue(),
                                             opt(info, 1, static_cast<double>(SST::Constants::C_VACUUM))));
    }
    static Napi::Value TensorSpeedFractionalOffset(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(),
            sst::ClockFieldEFT::tensor_speed_fractional_offset(info[0].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value SatisfiesGw170817(const Napi::CallbackInfo& info) {
        return Napi::Boolean::New(
            info.Env(), sst::ClockFieldEFT::satisfies_gw170817(info[0].As<Napi::Number>().DoubleValue(),
                                                              opt(info, 1, 1e-15)));
    }
    static Napi::Value Constraints(const Napi::CallbackInfo& info) {
        sst::ClockSectorConstraints c = sst::ClockFieldEFT::constraints(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue(),
            opt(info, 2, 1e-15));
        return ClockSectorConstraintsWrap::NewInstance(info.Env(), c);
    }
    static Napi::Value PoissonSource(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(),
                                 sst::ClockFieldEFT::poisson_source(info[0].As<Napi::Number>().DoubleValue(),
                                                                    info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value EffectiveGravityFromPotentialGradient(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(), sst::ClockFieldEFT::effective_gravity_from_potential_gradient(
                            info[0].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value UnitTimelikeFromGradientMinkowski(const Napi::CallbackInfo& info) {
        sst::Vec4 g = read_vec4(info[0]);
        return vec4_to_js(info.Env(), sst::ClockFieldEFT::unit_timelike_from_gradient_minkowski(g));
    }
};

} // namespace

void bind_clock_field_eft(Napi::Env env, Napi::Object exports) {
    ClockSectorConstraintsWrap::Init(env, exports);
    ClockFieldEFTWrap::Init(env, exports);
    exports.Set("clockFieldEftAvailable", Napi::Boolean::New(env, true));
}
