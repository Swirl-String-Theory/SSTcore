// sst_tension_scales_node.cpp — N-API bindings for SSTTensionScales
#include <napi.h>
#include "sst_tension_scales.h"

namespace {

class SSTTensionScalesWrap : public Napi::ObjectWrap<SSTTensionScalesWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "SSTTensionScales",
            {StaticMethod("fSwirlMax", &SSTTensionScalesWrap::FSwirlMax),
             StaticMethod("fGrMax", &SSTTensionScalesWrap::FGrMax),
             StaticMethod("gravitationalFineStructure",
                          &SSTTensionScalesWrap::GravitationalFineStructure),
             StaticMethod("tensionRatioFromCouplings",
                          &SSTTensionScalesWrap::TensionRatioFromCouplings),
             StaticMethod("coulombForceAtCore", &SSTTensionScalesWrap::CoulombForceAtCore),
             StaticMethod("electronSpringConstant", &SSTTensionScalesWrap::ElectronSpringConstant),
             StaticMethod("electronSpringFrequency", &SSTTensionScalesWrap::ElectronSpringFrequency),
             StaticMethod("electronSpringEnergy", &SSTTensionScalesWrap::ElectronSpringEnergy),
             StaticMethod("rydbergFromSst", &SSTTensionScalesWrap::RydbergFromSst),
             StaticMethod("swirlImpedance", &SSTTensionScalesWrap::SwirlImpedance),
             StaticMethod("dimensionlessStiffnessRatio",
                          &SSTTensionScalesWrap::DimensionlessStiffnessRatio)});
        exports.Set("SSTTensionScales", func);
    }

    SSTTensionScalesWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<SSTTensionScalesWrap>(info) {}

private:
    static double opt(const Napi::CallbackInfo& info, size_t i, double def) {
        return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().DoubleValue() : def;
    }

    static Napi::Value FSwirlMax(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::F_swirl_max(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value FGrMax(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::F_gr_max(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value GravitationalFineStructure(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::gravitational_fine_structure(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value TensionRatioFromCouplings(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::tension_ratio_from_couplings(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value CoulombForceAtCore(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::coulomb_force_at_core(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value ElectronSpringConstant(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::electron_spring_constant(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 opt(info, 2, 2.0)));
    }
    static Napi::Value ElectronSpringFrequency(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::electron_spring_frequency(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 opt(info, 3, 2.0)));
    }
    static Napi::Value ElectronSpringEnergy(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::electron_spring_energy(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 opt(info, 2, 2.0)));
    }
    static Napi::Value RydbergFromSst(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::rydberg_from_sst(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value SwirlImpedance(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::swirl_impedance(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value DimensionlessStiffnessRatio(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTTensionScales::dimensionless_stiffness_ratio(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue()));
    }
};

} // namespace

void bind_sst_tension_scales(Napi::Env env, Napi::Object exports) {
    SSTTensionScalesWrap::Init(env, exports);
    exports.Set("sstTensionScalesAvailable", Napi::Boolean::New(env, true));
}
