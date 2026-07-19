// canonical_constants_node.cpp — N-API bindings for SSTCanonicalConstants
#include <napi.h>
#include "canonical_constants.h"
#include "SST_Constants.h"

namespace {

class SSTCanonicalValuesWrap : public Napi::ObjectWrap<SSTCanonicalValuesWrap> {
public:
    static Napi::FunctionReference constructor;

    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "SSTCanonicalValues",
            {InstanceAccessor("c", &SSTCanonicalValuesWrap::GetC, &SSTCanonicalValuesWrap::SetC),
             InstanceAccessor("hbar", &SSTCanonicalValuesWrap::GetHbar, &SSTCanonicalValuesWrap::SetHbar),
             InstanceAccessor("alpha", &SSTCanonicalValuesWrap::GetAlpha, &SSTCanonicalValuesWrap::SetAlpha),
             InstanceAccessor("mE", &SSTCanonicalValuesWrap::GetME, &SSTCanonicalValuesWrap::SetME),
             InstanceAccessor("eCharge", &SSTCanonicalValuesWrap::GetECharge, &SSTCanonicalValuesWrap::SetECharge),
             InstanceAccessor("rhoF", &SSTCanonicalValuesWrap::GetRhoF, &SSTCanonicalValuesWrap::SetRhoF),
             InstanceAccessor("vSwirl", &SSTCanonicalValuesWrap::GetVSwirl, &SSTCanonicalValuesWrap::SetVSwirl),
             InstanceAccessor("omegaC", &SSTCanonicalValuesWrap::GetOmegaC, &SSTCanonicalValuesWrap::SetOmegaC),
             InstanceAccessor("rC", &SSTCanonicalValuesWrap::GetRC, &SSTCanonicalValuesWrap::SetRC),
             InstanceAccessor("gamma0", &SSTCanonicalValuesWrap::GetGamma0, &SSTCanonicalValuesWrap::SetGamma0),
             InstanceAccessor("lambdaC", &SSTCanonicalValuesWrap::GetLambdaC, &SSTCanonicalValuesWrap::SetLambdaC),
             InstanceAccessor("lambdaBarC", &SSTCanonicalValuesWrap::GetLambdaBarC,
                             &SSTCanonicalValuesWrap::SetLambdaBarC),
             InstanceAccessor("rhoE", &SSTCanonicalValuesWrap::GetRhoE, &SSTCanonicalValuesWrap::SetRhoE),
             InstanceAccessor("rhoM", &SSTCanonicalValuesWrap::GetRhoM, &SSTCanonicalValuesWrap::SetRhoM),
             InstanceAccessor("rhoCore", &SSTCanonicalValuesWrap::GetRhoCore, &SSTCanonicalValuesWrap::SetRhoCore),
             InstanceAccessor("rhoHorn", &SSTCanonicalValuesWrap::GetRhoHorn, &SSTCanonicalValuesWrap::SetRhoHorn),
             InstanceAccessor("eta0", &SSTCanonicalValuesWrap::GetEta0, &SSTCanonicalValuesWrap::SetEta0),
             InstanceAccessor("geometricGate", &SSTCanonicalValuesWrap::GetGeometricGate,
                             &SSTCanonicalValuesWrap::SetGeometricGate),
             InstanceAccessor("swirlClock", &SSTCanonicalValuesWrap::GetSwirlClock,
                             &SSTCanonicalValuesWrap::SetSwirlClock),
             InstanceAccessor("fSwirlMax", &SSTCanonicalValuesWrap::GetFSwirlMax,
                             &SSTCanonicalValuesWrap::SetFSwirlMax),
             InstanceAccessor("rInftySst", &SSTCanonicalValuesWrap::GetRInftySst,
                             &SSTCanonicalValuesWrap::SetRInftySst)});
        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("SSTCanonicalValues", func);
    }

    static Napi::Object NewInstance(Napi::Env env, const sst::SSTCanonicalValues& v) {
        Napi::Object obj = constructor.New({});
        Unwrap(obj)->inner_ = v;
        return obj;
    }

    SSTCanonicalValuesWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<SSTCanonicalValuesWrap>(info) {}

    sst::SSTCanonicalValues inner_;

private:
#define DBL_GETSET(Name, field)                                                                    \
    Napi::Value Get##Name(const Napi::CallbackInfo& info) {                                         \
        return Napi::Number::New(info.Env(), inner_.field);                                        \
    }                                                                                              \
    void Set##Name(const Napi::CallbackInfo&, const Napi::Value& v) {                               \
        inner_.field = v.As<Napi::Number>().DoubleValue();                                         \
    }

    DBL_GETSET(C, c)
    DBL_GETSET(Hbar, hbar)
    DBL_GETSET(Alpha, alpha)
    DBL_GETSET(ME, m_e)
    DBL_GETSET(ECharge, e_charge)
    DBL_GETSET(RhoF, rho_f)
    DBL_GETSET(VSwirl, v_swirl)
    DBL_GETSET(OmegaC, omega_c)
    DBL_GETSET(RC, r_c)
    DBL_GETSET(Gamma0, gamma_0)
    DBL_GETSET(LambdaC, lambda_c)
    DBL_GETSET(LambdaBarC, lambda_bar_c)
    DBL_GETSET(RhoE, rho_E)
    DBL_GETSET(RhoM, rho_m)
    DBL_GETSET(RhoCore, rho_core)
    DBL_GETSET(RhoHorn, rho_horn)
    DBL_GETSET(Eta0, eta_0)
    DBL_GETSET(GeometricGate, geometric_gate)
    DBL_GETSET(SwirlClock, swirl_clock)
    DBL_GETSET(FSwirlMax, F_swirl_max)
    DBL_GETSET(RInftySst, R_infty_sst)
#undef DBL_GETSET
};

Napi::FunctionReference SSTCanonicalValuesWrap::constructor;

class SSTCanonicalConstantsWrap : public Napi::ObjectWrap<SSTCanonicalConstantsWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "SSTCanonicalConstants",
            {StaticMethod("speedOfLight", &SSTCanonicalConstantsWrap::SpeedOfLight),
             StaticMethod("hbar", &SSTCanonicalConstantsWrap::Hbar),
             StaticMethod("alpha", &SSTCanonicalConstantsWrap::Alpha),
             StaticMethod("electronMass", &SSTCanonicalConstantsWrap::ElectronMass),
             StaticMethod("elementaryCharge", &SSTCanonicalConstantsWrap::ElementaryCharge),
             StaticMethod("epsilon0", &SSTCanonicalConstantsWrap::Epsilon0),
             StaticMethod("phi", &SSTCanonicalConstantsWrap::Phi),
             StaticMethod("comptonAngularFrequency",
                          &SSTCanonicalConstantsWrap::ComptonAngularFrequency),
             StaticMethod("reducedComptonWavelength",
                          &SSTCanonicalConstantsWrap::ReducedComptonWavelength),
             StaticMethod("fullComptonWavelength", &SSTCanonicalConstantsWrap::FullComptonWavelength),
             StaticMethod("coreRadiusFromComptonAnchor",
                          &SSTCanonicalConstantsWrap::CoreRadiusFromComptonAnchor),
             StaticMethod("circulationQuantum", &SSTCanonicalConstantsWrap::CirculationQuantum),
             StaticMethod("circulationQuantumFromVOmega",
                          &SSTCanonicalConstantsWrap::CirculationQuantumFromVOmega),
             StaticMethod("eta0", &SSTCanonicalConstantsWrap::Eta0),
             StaticMethod("swirlClock", &SSTCanonicalConstantsWrap::SwirlClock),
             StaticMethod("swirlEnergyDensity", &SSTCanonicalConstantsWrap::SwirlEnergyDensity),
             StaticMethod("massEquivalentDensity", &SSTCanonicalConstantsWrap::MassEquivalentDensity),
             StaticMethod("hornEnvelopeDensity", &SSTCanonicalConstantsWrap::HornEnvelopeDensity),
             StaticMethod("coreDensityClosure", &SSTCanonicalConstantsWrap::CoreDensityClosure),
             StaticMethod("geometricGate", &SSTCanonicalConstantsWrap::GeometricGate),
             StaticMethod("fSwirlMax", &SSTCanonicalConstantsWrap::FSwirlMax),
             StaticMethod("rydbergSst", &SSTCanonicalConstantsWrap::RydbergSst),
             StaticMethod("bareMasterMassScale", &SSTCanonicalConstantsWrap::BareMasterMassScale),
             StaticMethod("values", &SSTCanonicalConstantsWrap::Values)});
        exports.Set("SSTCanonicalConstants", func);
    }

    SSTCanonicalConstantsWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<SSTCanonicalConstantsWrap>(info) {}

private:
    static double opt(const Napi::CallbackInfo& info, size_t i, double def) {
        return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().DoubleValue() : def;
    }

    static Napi::Value SpeedOfLight(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::speed_of_light());
    }
    static Napi::Value Hbar(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::hbar());
    }
    static Napi::Value Alpha(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::alpha());
    }
    static Napi::Value ElectronMass(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::electron_mass());
    }
    static Napi::Value ElementaryCharge(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::elementary_charge());
    }
    static Napi::Value Epsilon0(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::epsilon_0());
    }
    static Napi::Value Phi(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::phi());
    }
    static Napi::Value ComptonAngularFrequency(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(),
            sst::SSTCanonicalConstants::compton_angular_frequency(
                opt(info, 0, static_cast<double>(SST::Constants::M_ELECTRON)),
                opt(info, 1, static_cast<double>(SST::Constants::C_VACUUM)),
                opt(info, 2, static_cast<double>(SST::Constants::H_BAR))));
    }
    static Napi::Value ReducedComptonWavelength(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(),
            sst::SSTCanonicalConstants::reduced_compton_wavelength(
                opt(info, 0, static_cast<double>(SST::Constants::H_BAR)),
                opt(info, 1, static_cast<double>(SST::Constants::M_ELECTRON)),
                opt(info, 2, static_cast<double>(SST::Constants::C_VACUUM))));
    }
    static Napi::Value FullComptonWavelength(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(),
            sst::SSTCanonicalConstants::full_compton_wavelength(
                opt(info, 0, static_cast<double>(SST::Constants::H_BAR)),
                opt(info, 1, static_cast<double>(SST::Constants::M_ELECTRON)),
                opt(info, 2, static_cast<double>(SST::Constants::C_VACUUM))));
    }
    static Napi::Value CoreRadiusFromComptonAnchor(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(),
                                 sst::SSTCanonicalConstants::core_radius_from_compton_anchor(
                                     info[0].As<Napi::Number>().DoubleValue(),
                                     info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value CirculationQuantum(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::circulation_quantum(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value CirculationQuantumFromVOmega(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(),
                                 sst::SSTCanonicalConstants::circulation_quantum_from_v_omega(
                                     info[0].As<Napi::Number>().DoubleValue(),
                                     info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value Eta0(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(),
            sst::SSTCanonicalConstants::eta0(info[0].As<Napi::Number>().DoubleValue(),
                                             opt(info, 1, static_cast<double>(SST::Constants::C_VACUUM))));
    }
    static Napi::Value SwirlClock(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(), sst::SSTCanonicalConstants::swirl_clock(
                            info[0].As<Napi::Number>().DoubleValue(),
                            opt(info, 1, static_cast<double>(SST::Constants::C_VACUUM))));
    }
    static Napi::Value SwirlEnergyDensity(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::swirl_energy_density(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value MassEquivalentDensity(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(), sst::SSTCanonicalConstants::mass_equivalent_density(
                            info[0].As<Napi::Number>().DoubleValue(),
                            opt(info, 1, static_cast<double>(SST::Constants::C_VACUUM))));
    }
    static Napi::Value HornEnvelopeDensity(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::horn_envelope_density(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value CoreDensityClosure(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::core_density_closure(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value GeometricGate(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::geometric_gate(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value FSwirlMax(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::f_swirl_max(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value RydbergSst(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(),
            sst::SSTCanonicalConstants::rydberg_sst(info[0].As<Napi::Number>().DoubleValue(),
                                                    info[1].As<Napi::Number>().DoubleValue(),
                                                    opt(info, 2, static_cast<double>(SST::Constants::C_VACUUM))));
    }
    static Napi::Value BareMasterMassScale(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTCanonicalConstants::bare_master_mass_scale(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value Values(const Napi::CallbackInfo& info) {
        sst::SSTCanonicalValues v = sst::SSTCanonicalConstants::values(
            opt(info, 0, static_cast<double>(SST::Constants::RHO_FLUID_CANON)),
            opt(info, 1, static_cast<double>(SST::Constants::V_SWIRL)));
        return SSTCanonicalValuesWrap::NewInstance(info.Env(), v);
    }
};

} // namespace

void bind_canonical_constants(Napi::Env env, Napi::Object exports) {
    SSTCanonicalValuesWrap::Init(env, exports);
    SSTCanonicalConstantsWrap::Init(env, exports);
    exports.Set("canonicalConstantsAvailable", Napi::Boolean::New(env, true));
}
