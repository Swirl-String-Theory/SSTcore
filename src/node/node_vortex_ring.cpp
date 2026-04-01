// node_vortex_ring.cpp
#include <napi.h>
#include "../vortex_ring.h"

namespace {

class GoldenNLSClosureWrap : public Napi::ObjectWrap<GoldenNLSClosureWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func =
            DefineClass(env, "GoldenNLSClosure",
                        {InstanceMethod("setRegime", &GoldenNLSClosureWrap::SetRegime),
                         InstanceMethod("getActiveDensity", &GoldenNLSClosureWrap::GetActiveDensity),
                         InstanceMethod("calculateLoopEnergy", &GoldenNLSClosureWrap::CalculateLoopEnergy),
                         InstanceMethod("calculateLoopMass", &GoldenNLSClosureWrap::CalculateLoopMass),
                         InstanceMethod("calculateScreenedMass", &GoldenNLSClosureWrap::CalculateScreenedMass),
                         InstanceMethod("inferGeometricRatio", &GoldenNLSClosureWrap::InferGeometricRatio),
                         InstanceMethod("inferGeometricRatioSafe", &GoldenNLSClosureWrap::InferGeometricRatioSafe),
                         InstanceMethod("geometricRatioResidual", &GoldenNLSClosureWrap::GeometricRatioResidual)});
        exports.Set("GoldenNLSClosure", func);
    }

    GoldenNLSClosureWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<GoldenNLSClosureWrap>(info),
          inner_(sst::GoldenNLSClosure::DensityRegime::CORE_DOMINATED) {
        if (info.Length() >= 1 && info[0].IsNumber()) {
            int v = info[0].As<Napi::Number>().Int32Value();
            inner_.set_regime(v == 0 ? sst::GoldenNLSClosure::DensityRegime::EFFECTIVE_FLUID
                                     : sst::GoldenNLSClosure::DensityRegime::CORE_DOMINATED);
        }
    }

private:
    sst::GoldenNLSClosure inner_;

    Napi::Value SetRegime(const Napi::CallbackInfo& info) {
        int v = info[0].As<Napi::Number>().Int32Value();
        inner_.set_regime(v == 0 ? sst::GoldenNLSClosure::DensityRegime::EFFECTIVE_FLUID
                                 : sst::GoldenNLSClosure::DensityRegime::CORE_DOMINATED);
        return info.Env().Undefined();
    }
    Napi::Value GetActiveDensity(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.get_active_density());
    }
    Napi::Value CalculateLoopEnergy(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.calculate_loop_energy(info[0].As<Napi::Number>().DoubleValue()));
    }
    Napi::Value CalculateLoopMass(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), inner_.calculate_loop_mass(info[0].As<Napi::Number>().DoubleValue()));
    }
    Napi::Value CalculateScreenedMass(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(), inner_.calculate_screened_mass(info[0].As<Napi::Number>().DoubleValue(),
                                                      info[1].As<Napi::Number>().Int32Value()));
    }
    Napi::Value InferGeometricRatio(const Napi::CallbackInfo& info) {
        double tm = (info.Length() > 0) ? info[0].As<Napi::Number>().DoubleValue() : 9.10938356e-31;
        double tol = (info.Length() > 1) ? info[1].As<Napi::Number>().DoubleValue() : 1e-12;
        int mi = (info.Length() > 2) ? info[2].As<Napi::Number>().Int32Value() : 100;
        return Napi::Number::New(info.Env(), inner_.infer_geometric_ratio(tm, tol, mi));
    }
    Napi::Value InferGeometricRatioSafe(const Napi::CallbackInfo& info) {
        double tm = (info.Length() > 0) ? info[0].As<Napi::Number>().DoubleValue() : 9.10938356e-31;
        double x0 = (info.Length() > 1) ? info[1].As<Napi::Number>().DoubleValue() : 1.0;
        double xmin = (info.Length() > 2) ? info[2].As<Napi::Number>().DoubleValue() : 1e-6;
        double xmax = (info.Length() > 3) ? info[3].As<Napi::Number>().DoubleValue() : 10.0;
        double xtol = (info.Length() > 4) ? info[4].As<Napi::Number>().DoubleValue() : 1e-12;
        double ftol = (info.Length() > 5) ? info[5].As<Napi::Number>().DoubleValue() : 1e-12;
        int mi = (info.Length() > 6) ? info[6].As<Napi::Number>().Int32Value() : 100;
        return Napi::Number::New(info.Env(),
                                 inner_.infer_geometric_ratio_safe(tm, x0, xmin, xmax, xtol, ftol, mi));
    }
    Napi::Value GeometricRatioResidual(const Napi::CallbackInfo& info) {
        double x = info[0].As<Napi::Number>().DoubleValue();
        double tm = (info.Length() > 1) ? info[1].As<Napi::Number>().DoubleValue() : 9.10938356e-31;
        return Napi::Number::New(info.Env(), inner_.geometric_ratio_residual(x, tm));
    }
};

} // namespace

void bind_vortex_ring(Napi::Env env, Napi::Object exports) {
    GoldenNLSClosureWrap::Init(env, exports);

    exports.Set("lambOseenVelocity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::VortexRing::lamb_oseen_velocity(
                                                   info[0].As<Napi::Number>().DoubleValue(),
                                                   info[1].As<Napi::Number>().DoubleValue(),
                                                   info[2].As<Napi::Number>().DoubleValue(),
                                                   info[3].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("lambOseenVorticity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::VortexRing::lamb_oseen_vorticity(
                                                   info[0].As<Napi::Number>().DoubleValue(),
                                                   info[1].As<Napi::Number>().DoubleValue(),
                                                   info[2].As<Napi::Number>().DoubleValue(),
                                                   info[3].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("hillStreamfunction", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::VortexRing::hill_streamfunction(
                                                   info[0].As<Napi::Number>().DoubleValue(),
                                                   info[1].As<Napi::Number>().DoubleValue(),
                                                   info[2].As<Napi::Number>().DoubleValue(),
                                                   info[3].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("hillVorticity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::VortexRing::hill_vorticity(
                                                   info[0].As<Napi::Number>().DoubleValue(),
                                                   info[1].As<Napi::Number>().DoubleValue(),
                                                   info[2].As<Napi::Number>().DoubleValue(),
                                                   info[3].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("hillCirculation", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::VortexRing::hill_circulation(info[0].As<Napi::Number>().DoubleValue(),
                                                                              info[1].As<Napi::Number>().DoubleValue()));
    }));
    exports.Set("hillVelocity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::VortexRing::hill_velocity(info[0].As<Napi::Number>().DoubleValue(),
                                                                            info[1].As<Napi::Number>().DoubleValue()));
    }));

    exports.Set("goldenNlsInferEffectiveBase", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::GoldenNLSClosure::infer_effective_base(
                                                   info[0].As<Napi::Number>().DoubleValue(),
                                                   info[1].As<Napi::Number>().Int32Value()));
    }));
    exports.Set("goldenNlsPredictedRatioFromBase", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::GoldenNLSClosure::predicted_ratio_from_base(
                                                   info[0].As<Napi::Number>().DoubleValue(),
                                                   info[1].As<Napi::Number>().Int32Value()));
    }));
    exports.Set("goldenNlsRelativeError", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        return Napi::Number::New(info.Env(), sst::GoldenNLSClosure::relative_error(
                                                   info[0].As<Napi::Number>().DoubleValue(),
                                                   info[1].As<Napi::Number>().DoubleValue()));
    }));

    exports.Set("densityRegimeEffectiveFluid", Napi::Number::New(env, 0));
    exports.Set("densityRegimeCoreDominated", Napi::Number::New(env, 1));

    exports.Set("vortexRingAvailable", Napi::Boolean::New(env, true));
}
