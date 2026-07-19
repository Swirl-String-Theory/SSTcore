// sst_master_equation_node.cpp — N-API bindings for SSTMasterEquation
#include <napi.h>
#include "sst_master_equation.h"

namespace {

class TopologyKernelInputWrap : public Napi::ObjectWrap<TopologyKernelInputWrap> {
public:
    static Napi::FunctionReference constructor;

    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "SSTTopologyKernelInput",
            {InstanceAccessor("alphaC", &TopologyKernelInputWrap::GetAlphaC,
                              &TopologyKernelInputWrap::SetAlphaC),
             InstanceAccessor("betaL", &TopologyKernelInputWrap::GetBetaL,
                              &TopologyKernelInputWrap::SetBetaL),
             InstanceAccessor("gammaH", &TopologyKernelInputWrap::GetGammaH,
                              &TopologyKernelInputWrap::SetGammaH),
             InstanceAccessor("crossing", &TopologyKernelInputWrap::GetCrossing,
                              &TopologyKernelInputWrap::SetCrossing),
             InstanceAccessor("ropelength", &TopologyKernelInputWrap::GetRopelength,
                              &TopologyKernelInputWrap::SetRopelength),
             InstanceAccessor("helicity", &TopologyKernelInputWrap::GetHelicity,
                              &TopologyKernelInputWrap::SetHelicity),
             InstanceAccessor("goldenLayer", &TopologyKernelInputWrap::GetGoldenLayer,
                              &TopologyKernelInputWrap::SetGoldenLayer),
             InstanceAccessor("phi", &TopologyKernelInputWrap::GetPhi, &TopologyKernelInputWrap::SetPhi)});
        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("SSTTopologyKernelInput", func);
    }

    static Napi::Object NewInstance(Napi::Env env, const sst::SSTTopologyKernelInput& in) {
        Napi::Object obj = constructor.New({});
        Unwrap(obj)->inner_ = in;
        return obj;
    }

    static sst::SSTTopologyKernelInput FromJs(const Napi::Value& v) {
        Napi::Object o = v.As<Napi::Object>();
        if (o.InstanceOf(constructor.Value())) {
            return Unwrap(o)->inner_;
        }
        sst::SSTTopologyKernelInput in;
        if (o.Has("alphaC")) in.alpha_C = o.Get("alphaC").As<Napi::Number>().DoubleValue();
        if (o.Has("betaL")) in.beta_L = o.Get("betaL").As<Napi::Number>().DoubleValue();
        if (o.Has("gammaH")) in.gamma_H = o.Get("gammaH").As<Napi::Number>().DoubleValue();
        if (o.Has("crossing")) in.crossing = o.Get("crossing").As<Napi::Number>().DoubleValue();
        if (o.Has("ropelength")) in.ropelength = o.Get("ropelength").As<Napi::Number>().DoubleValue();
        if (o.Has("helicity")) in.helicity = o.Get("helicity").As<Napi::Number>().DoubleValue();
        if (o.Has("goldenLayer")) in.golden_layer = o.Get("goldenLayer").As<Napi::Number>().Int32Value();
        if (o.Has("phi")) in.phi = o.Get("phi").As<Napi::Number>().DoubleValue();
        return in;
    }

    TopologyKernelInputWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<TopologyKernelInputWrap>(info) {}

    sst::SSTTopologyKernelInput inner_;

private:
#define DBL_GS(Name, field)                                                                        \
    Napi::Value Get##Name(const Napi::CallbackInfo& info) {                                         \
        return Napi::Number::New(info.Env(), inner_.field);                                        \
    }                                                                                              \
    void Set##Name(const Napi::CallbackInfo&, const Napi::Value& v) {                               \
        inner_.field = v.As<Napi::Number>().DoubleValue();                                         \
    }

    DBL_GS(AlphaC, alpha_C)
    DBL_GS(BetaL, beta_L)
    DBL_GS(GammaH, gamma_H)
    DBL_GS(Crossing, crossing)
    DBL_GS(Ropelength, ropelength)
    DBL_GS(Helicity, helicity)
    DBL_GS(Phi, phi)
#undef DBL_GS

    Napi::Value GetGoldenLayer(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.golden_layer);
    }
    void SetGoldenLayer(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.golden_layer = v.As<Napi::Number>().Int32Value();
    }
};

Napi::FunctionReference TopologyKernelInputWrap::constructor;

class MasterEquationOutputWrap : public Napi::ObjectWrap<MasterEquationOutputWrap> {
public:
    static Napi::FunctionReference constructor;

    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "SSTMasterEquationOutput",
            {InstanceAccessor("rhoE", &MasterEquationOutputWrap::GetRhoE, &MasterEquationOutputWrap::SetRhoE),
             InstanceAccessor("rhoM", &MasterEquationOutputWrap::GetRhoM, &MasterEquationOutputWrap::SetRhoM),
             InstanceAccessor("swirlClock", &MasterEquationOutputWrap::GetSwirlClock,
                             &MasterEquationOutputWrap::SetSwirlClock),
             InstanceAccessor("clockImpedance", &MasterEquationOutputWrap::GetClockImpedance,
                             &MasterEquationOutputWrap::SetClockImpedance),
             InstanceAccessor("geometricGate", &MasterEquationOutputWrap::GetGeometricGate,
                             &MasterEquationOutputWrap::SetGeometricGate),
             InstanceAccessor("topologicalKernel", &MasterEquationOutputWrap::GetTopologicalKernel,
                             &MasterEquationOutputWrap::SetTopologicalKernel),
             InstanceAccessor("bareMassScaleKg", &MasterEquationOutputWrap::GetBareMassScaleKg,
                             &MasterEquationOutputWrap::SetBareMassScaleKg),
             InstanceAccessor("massKg", &MasterEquationOutputWrap::GetMassKg,
                             &MasterEquationOutputWrap::SetMassKg)});
        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("SSTMasterEquationOutput", func);
    }

    static Napi::Object NewInstance(Napi::Env env, const sst::SSTMasterEquationOutput& out) {
        Napi::Object obj = constructor.New({});
        Unwrap(obj)->inner_ = out;
        return obj;
    }

    MasterEquationOutputWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<MasterEquationOutputWrap>(info) {}

    sst::SSTMasterEquationOutput inner_;

private:
#define DBL_GS(Name, field)                                                                        \
    Napi::Value Get##Name(const Napi::CallbackInfo& info) {                                         \
        return Napi::Number::New(info.Env(), inner_.field);                                        \
    }                                                                                              \
    void Set##Name(const Napi::CallbackInfo&, const Napi::Value& v) {                               \
        inner_.field = v.As<Napi::Number>().DoubleValue();                                         \
    }

    DBL_GS(RhoE, rho_E)
    DBL_GS(RhoM, rho_m)
    DBL_GS(SwirlClock, swirl_clock)
    DBL_GS(ClockImpedance, clock_impedance)
    DBL_GS(GeometricGate, geometric_gate)
    DBL_GS(TopologicalKernel, topological_kernel)
    DBL_GS(BareMassScaleKg, bare_mass_scale_kg)
    DBL_GS(MassKg, mass_kg)
#undef DBL_GS
};

Napi::FunctionReference MasterEquationOutputWrap::constructor;

class MasterEquationInputWrap : public Napi::ObjectWrap<MasterEquationInputWrap> {
public:
    static Napi::FunctionReference constructor;

    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "SSTMasterEquationInput",
            {InstanceAccessor("rhoF", &MasterEquationInputWrap::GetRhoF, &MasterEquationInputWrap::SetRhoF),
             InstanceAccessor("vNorm", &MasterEquationInputWrap::GetVNorm, &MasterEquationInputWrap::SetVNorm),
             InstanceAccessor("rC", &MasterEquationInputWrap::GetRC, &MasterEquationInputWrap::SetRC),
             InstanceAccessor("lambdaC", &MasterEquationInputWrap::GetLambdaC,
                             &MasterEquationInputWrap::SetLambdaC),
             InstanceAccessor("gate", &MasterEquationInputWrap::GetGate, &MasterEquationInputWrap::SetGate),
             InstanceAccessor("topology", &MasterEquationInputWrap::GetTopology,
                             &MasterEquationInputWrap::SetTopology),
             InstanceAccessor("c", &MasterEquationInputWrap::GetC, &MasterEquationInputWrap::SetC),
             InstanceAccessor("explicitSwirlClock", &MasterEquationInputWrap::GetExplicitSwirlClock,
                             &MasterEquationInputWrap::SetExplicitSwirlClock)});
        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("SSTMasterEquationInput", func);
    }

    static sst::SSTMasterEquationInput FromJs(const Napi::Value& v) {
        Napi::Object o = v.As<Napi::Object>();
        if (o.InstanceOf(constructor.Value())) {
            return Unwrap(o)->inner_;
        }
        sst::SSTMasterEquationInput in;
        if (o.Has("rhoF")) in.rho_f = o.Get("rhoF").As<Napi::Number>().DoubleValue();
        if (o.Has("vNorm")) in.v_norm = o.Get("vNorm").As<Napi::Number>().DoubleValue();
        if (o.Has("rC")) in.r_c = o.Get("rC").As<Napi::Number>().DoubleValue();
        if (o.Has("lambdaC")) in.lambda_c = o.Get("lambdaC").As<Napi::Number>().DoubleValue();
        if (o.Has("gate")) in.gate = o.Get("gate").As<Napi::Number>().Int32Value();
        if (o.Has("topology")) in.topology = TopologyKernelInputWrap::FromJs(o.Get("topology"));
        if (o.Has("c")) in.c = o.Get("c").As<Napi::Number>().DoubleValue();
        if (o.Has("explicitSwirlClock"))
            in.explicit_swirl_clock = o.Get("explicitSwirlClock").As<Napi::Number>().DoubleValue();
        return in;
    }

    MasterEquationInputWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<MasterEquationInputWrap>(info) {}

    sst::SSTMasterEquationInput inner_;

private:
#define DBL_GS(Name, field)                                                                        \
    Napi::Value Get##Name(const Napi::CallbackInfo& info) {                                         \
        return Napi::Number::New(info.Env(), inner_.field);                                        \
    }                                                                                              \
    void Set##Name(const Napi::CallbackInfo&, const Napi::Value& v) {                               \
        inner_.field = v.As<Napi::Number>().DoubleValue();                                         \
    }

    DBL_GS(RhoF, rho_f)
    DBL_GS(VNorm, v_norm)
    DBL_GS(RC, r_c)
    DBL_GS(LambdaC, lambda_c)
    DBL_GS(C, c)
    DBL_GS(ExplicitSwirlClock, explicit_swirl_clock)
#undef DBL_GS

    Napi::Value GetGate(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.gate);
    }
    void SetGate(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.gate = v.As<Napi::Number>().Int32Value();
    }
    Napi::Value GetTopology(const Napi::CallbackInfo& info) {
        return TopologyKernelInputWrap::NewInstance(info.Env(), inner_.topology);
    }
    void SetTopology(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.topology = TopologyKernelInputWrap::FromJs(v);
    }
};

Napi::FunctionReference MasterEquationInputWrap::constructor;

class SSTMasterEquationWrap : public Napi::ObjectWrap<SSTMasterEquationWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "SSTMasterEquation",
            {StaticMethod("topologicalKernel", &SSTMasterEquationWrap::TopologicalKernel),
             StaticMethod("geometricGateFactor", &SSTMasterEquationWrap::GeometricGateFactor),
             StaticMethod("clockImpedance", &SSTMasterEquationWrap::ClockImpedance),
             StaticMethod("weakSwirlClockImpedance", &SSTMasterEquationWrap::WeakSwirlClockImpedance),
             StaticMethod("geometricBaselineMass", &SSTMasterEquationWrap::GeometricBaselineMass),
             StaticMethod("geometricBaselineMassFromRhoM",
                          &SSTMasterEquationWrap::GeometricBaselineMassFromRhoM),
             StaticMethod("geometricHornBaselineMass",
                          &SSTMasterEquationWrap::GeometricHornBaselineMass),
             StaticMethod("evaluate", &SSTMasterEquationWrap::Evaluate)});
        exports.Set("SSTMasterEquation", func);
    }

    SSTMasterEquationWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<SSTMasterEquationWrap>(info) {}

private:
    static Napi::Value TopologicalKernel(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(),
            sst::SSTMasterEquation::topological_kernel(TopologyKernelInputWrap::FromJs(info[0])));
    }
    static Napi::Value GeometricGateFactor(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTMasterEquation::geometric_gate_factor(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().Int32Value()));
    }
    static Napi::Value ClockImpedance(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(),
            sst::SSTMasterEquation::clock_impedance(info[0].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value WeakSwirlClockImpedance(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTMasterEquation::weak_swirl_clock_impedance(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value GeometricBaselineMass(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTMasterEquation::geometric_baseline_mass(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value GeometricBaselineMassFromRhoM(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(),
                                 sst::SSTMasterEquation::geometric_baseline_mass_from_rho_m(
                                     info[0].As<Napi::Number>().DoubleValue(),
                                     info[1].As<Napi::Number>().DoubleValue(),
                                     info[2].As<Napi::Number>().DoubleValue(),
                                     info[3].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value GeometricHornBaselineMass(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::SSTMasterEquation::geometric_horn_baseline_mass(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value Evaluate(const Napi::CallbackInfo& info) {
        sst::SSTMasterEquationOutput out =
            sst::SSTMasterEquation::evaluate(MasterEquationInputWrap::FromJs(info[0]));
        return MasterEquationOutputWrap::NewInstance(info.Env(), out);
    }
};

} // namespace

void bind_sst_master_equation(Napi::Env env, Napi::Object exports) {
    TopologyKernelInputWrap::Init(env, exports);
    MasterEquationInputWrap::Init(env, exports);
    MasterEquationOutputWrap::Init(env, exports);
    SSTMasterEquationWrap::Init(env, exports);
    exports.Set("sstMasterEquationAvailable", Napi::Boolean::New(env, true));
}
