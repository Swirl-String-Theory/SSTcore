#include <napi.h>
#include "sst_rotor_participation.h"

void bind_rotor_participation(Napi::Env env, Napi::Object exports) {
    exports.Set("evaluateRotorParticipation", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
        auto r = sst::RotorParticipationAPI::evaluate();
        Napi::Object o = Napi::Object::New(info.Env());
        o.Set("jOmegaRot", Napi::Number::New(info.Env(), r.j_omega_rot));
        o.Set("phiDynRef", Napi::Number::New(info.Env(), r.phi_dyn_ref));
        o.Set("ellRhoEqRef", Napi::Number::New(info.Env(), r.ell_rho_eq_ref));
        o.Set("cOmega", Napi::Number::New(info.Env(), r.c_omega));
        return o;
    }));
}
