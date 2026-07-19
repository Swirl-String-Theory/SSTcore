// atomic_bridge_model_node.cpp — N-API bindings for AtomicBridgeModel
#include <napi.h>
#include "atomic_bridge_model.h"
#include "SST_Constants.h"

namespace {

class AtomicBridgeModelWrap : public Napi::ObjectWrap<AtomicBridgeModelWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "AtomicBridgeModel",
            {StaticMethod("eta0", &AtomicBridgeModelWrap::Eta0),
             StaticMethod("bohrRadiusSst", &AtomicBridgeModelWrap::BohrRadiusSst),
             StaticMethod("rydbergEnergy", &AtomicBridgeModelWrap::RydbergEnergy),
             StaticMethod("lambdaSst", &AtomicBridgeModelWrap::LambdaSst),
             StaticMethod("softCorePotential", &AtomicBridgeModelWrap::SoftCorePotential),
             StaticMethod("softCoreForce", &AtomicBridgeModelWrap::SoftCoreForce),
             StaticMethod("clockBranchFactor", &AtomicBridgeModelWrap::ClockBranchFactor),
             StaticMethod("scalarClockPotentialLinear", &AtomicBridgeModelWrap::ScalarClockPotentialLinear),
             StaticMethod("orbitCouplingEnergy", &AtomicBridgeModelWrap::OrbitCouplingEnergy),
             StaticMethod("frozenLinearInteraction", &AtomicBridgeModelWrap::FrozenLinearInteraction),
             StaticMethod("pauliBarrierScale", &AtomicBridgeModelWrap::PauliBarrierScale),
             StaticMethod("omegaZFromDisplacementGradient",
                          &AtomicBridgeModelWrap::OmegaZFromDisplacementGradient),
             StaticMethod("uThetaUniformVorticity", &AtomicBridgeModelWrap::UThetaUniformVorticity),
             StaticMethod("gammaFromUniformVorticity", &AtomicBridgeModelWrap::GammaFromUniformVorticity),
             StaticMethod("helicalPacketGamma", &AtomicBridgeModelWrap::HelicalPacketGamma)});
        exports.Set("AtomicBridgeModel", func);
    }

    AtomicBridgeModelWrap(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<AtomicBridgeModelWrap>(info) {}

private:
    static double opt(const Napi::CallbackInfo& info, size_t i, double def) {
        return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().DoubleValue() : def;
    }

    static Napi::Value Eta0(const Napi::CallbackInfo& info) {
        double v = info[0].As<Napi::Number>().DoubleValue();
        double c = opt(info, 1, static_cast<double>(SST::Constants::C_VACUUM));
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::eta0(v, c));
    }
    static Napi::Value BohrRadiusSst(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::bohr_radius_sst(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value RydbergEnergy(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::rydberg_energy(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value LambdaSst(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::lambda_sst(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value SoftCorePotential(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::soft_core_potential(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value SoftCoreForce(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::soft_core_force(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value ClockBranchFactor(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::clock_branch_factor(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value ScalarClockPotentialLinear(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::scalar_clock_potential_linear(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value OrbitCouplingEnergy(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::orbit_coupling_energy(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value FrozenLinearInteraction(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::frozen_linear_interaction(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue(),
                                                 info[3].As<Napi::Number>().DoubleValue(),
                                                 info[4].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value PauliBarrierScale(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(),
                                 sst::AtomicBridgeModel::pauli_barrier_scale(
                                     info[0].As<Napi::Number>().DoubleValue(),
                                     info[1].As<Napi::Number>().DoubleValue(),
                                     info[2].As<Napi::Number>().DoubleValue(),
                                     info[3].As<Napi::Number>().DoubleValue(), opt(info, 4, 1.0)));
    }
    static Napi::Value OmegaZFromDisplacementGradient(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(),
                                 sst::AtomicBridgeModel::omega_z_from_displacement_gradient(
                                     info[0].As<Napi::Number>().DoubleValue(),
                                     info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value UThetaUniformVorticity(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::u_theta_uniform_vorticity(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value GammaFromUniformVorticity(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), sst::AtomicBridgeModel::gamma_from_uniform_vorticity(
                                                 info[0].As<Napi::Number>().DoubleValue(),
                                                 info[1].As<Napi::Number>().DoubleValue(),
                                                 info[2].As<Napi::Number>().DoubleValue()));
    }
    static Napi::Value HelicalPacketGamma(const Napi::CallbackInfo& info) {
        return Napi::Number::New(
            info.Env(), sst::AtomicBridgeModel::helical_packet_gamma(
                            info[0].As<Napi::Number>().DoubleValue(),
                            info[1].As<Napi::Number>().DoubleValue(),
                            info[2].As<Napi::Number>().DoubleValue(),
                            info[3].As<Napi::Number>().DoubleValue(),
                            info[4].As<Napi::Number>().DoubleValue(),
                            info[5].As<Napi::Number>().DoubleValue(),
                            info[6].As<Napi::Number>().DoubleValue(),
                            info[7].As<Napi::Number>().DoubleValue(),
                            info[8].As<Napi::Number>().Int32Value(),
                            info[9].As<Napi::Number>().DoubleValue(),
                            info[10].As<Napi::Number>().DoubleValue()));
    }
};

} // namespace

void bind_atomic_bridge_model(Napi::Env env, Napi::Object exports) {
    AtomicBridgeModelWrap::Init(env, exports);
    exports.Set("atomicBridgeModelAvailable", Napi::Boolean::New(env, true));
}
