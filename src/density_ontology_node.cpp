#include <napi.h>
#include "sst_density_ontology.h"

void bind_density_ontology(Napi::Env env, Napi::Object exports) {
    exports.Set("densitySymbolName", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1) return e.Null();
        int v = info[0].As<Napi::Number>().Int32Value();
        return Napi::String::New(e, sst::DensityOntologyAPI::symbol_name(static_cast<sst::DensitySymbol>(v)));
    }));
    exports.Set("validateEnergyDensityForm", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1) return e.Null();
        int v = info[0].As<Napi::Number>().Int32Value();
        auto r = sst::DensityOntologyAPI::validate_energy_density_form(static_cast<sst::EnergyDensityForm>(v));
        Napi::Object o = Napi::Object::New(e);
        o.Set("allowed", Napi::Boolean::New(e, r.allowed));
        o.Set("reason", Napi::String::New(e, r.reason));
        return o;
    }));
    exports.Set("rhoFAliasesRhoEff", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
        return Napi::Boolean::New(info.Env(), sst::DensityOntologyAPI::rho_f_aliases_rho_eff());
    }));
}
