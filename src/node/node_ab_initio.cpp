// node_ab_initio.cpp — ParticleEvaluator & ZooEvaluator (N-API)
#include <napi.h>
#include "node_utils.h"
#include "../ab_initio_mass.h"

using namespace sst;

namespace {

Napi::Object tail_config_to_js(Napi::Env env, const ParticleEvaluator::TailApproxConfig& c) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("enabled", Napi::Boolean::New(env, c.enabled));
    o.Set("radialSamples", Napi::Number::New(env, c.radial_samples));
    o.Set("azimuthSamples", Napi::Number::New(env, c.azimuth_samples));
    o.Set("rMinFactor", Napi::Number::New(env, c.r_min_factor));
    o.Set("rMaxFactor", Napi::Number::New(env, c.r_max_factor));
    o.Set("exclusionDsFactor", Napi::Number::New(env, c.exclusion_ds_factor));
    o.Set("useLogShellWeight", Napi::Boolean::New(env, c.use_log_shell_weight));
    return o;
}

ParticleEvaluator::TailApproxConfig tail_config_from_js(Napi::Object o) {
    ParticleEvaluator::TailApproxConfig c;
    if (o.Has("enabled")) c.enabled = o.Get("enabled").As<Napi::Boolean>().Value();
    if (o.Has("radialSamples")) c.radial_samples = o.Get("radialSamples").As<Napi::Number>().Int32Value();
    if (o.Has("azimuthSamples")) c.azimuth_samples = o.Get("azimuthSamples").As<Napi::Number>().Int32Value();
    if (o.Has("rMinFactor")) c.r_min_factor = o.Get("rMinFactor").As<Napi::Number>().DoubleValue();
    if (o.Has("rMaxFactor")) c.r_max_factor = o.Get("rMaxFactor").As<Napi::Number>().DoubleValue();
    if (o.Has("exclusionDsFactor")) c.exclusion_ds_factor = o.Get("exclusionDsFactor").As<Napi::Number>().DoubleValue();
    if (o.Has("useLogShellWeight")) c.use_log_shell_weight = o.Get("useLogShellWeight").As<Napi::Boolean>().Value();
    return c;
}

Napi::Object relativistic_to_js(Napi::Env env, const ParticleEvaluator::RelativisticMetrics& m) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("helicity", Napi::Number::New(env, m.helicity));
    o.Set("coreTimeDilation", Napi::Number::New(env, m.core_time_dilation));
    Napi::Array td = Napi::Array::New(env, m.time_dilation_map.size());
    for (size_t i = 0; i < m.time_dilation_map.size(); ++i) {
        td.Set(static_cast<uint32_t>(i), Napi::Number::New(env, m.time_dilation_map[i]));
    }
    o.Set("timeDilationMap", td);
    return o;
}

class ParticleEvaluatorWrap : public Napi::ObjectWrap<ParticleEvaluatorWrap> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports);
    ParticleEvaluatorWrap(const Napi::CallbackInfo& info);

private:
    std::unique_ptr<ParticleEvaluator> pe_;

    Napi::Value Relax(const Napi::CallbackInfo& info);
    Napi::Value GetDimlessRopelength(const Napi::CallbackInfo& info);
    Napi::Value GetPhysicalLengthM(const Napi::CallbackInfo& info);
    Napi::Value ComputeCoreEnergyJ(const Napi::CallbackInfo& info);
    Napi::Value ComputeTailEnergyJ(const Napi::CallbackInfo& info);
    Napi::Value GetMassMevAbInitio(const Napi::CallbackInfo& info);
    Napi::Value GetCoreMassMevOnly(const Napi::CallbackInfo& info);
    Napi::Value SetTailApproxConfig(const Napi::CallbackInfo& info);
    Napi::Value GetTailApproxConfig(const Napi::CallbackInfo& info);
    Napi::Value ComputeTailEnergySurrogateJ(const Napi::CallbackInfo& info);
    Napi::Value ComputeRelativisticMetrics(const Napi::CallbackInfo& info);
    Napi::Value GetFilaments(const Napi::CallbackInfo& info);
};

Napi::Object ParticleEvaluatorWrap::Init(Napi::Env env, Napi::Object exports) {
    Napi::Function func = DefineClass(env, "ParticleEvaluator", {
        InstanceMethod("relax", &ParticleEvaluatorWrap::Relax),
        InstanceMethod("getDimlessRopelength", &ParticleEvaluatorWrap::GetDimlessRopelength),
        InstanceMethod("getPhysicalLengthM", &ParticleEvaluatorWrap::GetPhysicalLengthM),
        InstanceMethod("computeCoreEnergyJ", &ParticleEvaluatorWrap::ComputeCoreEnergyJ),
        InstanceMethod("computeTailEnergyJ", &ParticleEvaluatorWrap::ComputeTailEnergyJ),
        InstanceMethod("getMassMevAbInitio", &ParticleEvaluatorWrap::GetMassMevAbInitio),
        InstanceMethod("getCoreMassMevOnly", &ParticleEvaluatorWrap::GetCoreMassMevOnly),
        InstanceMethod("setTailApproxConfig", &ParticleEvaluatorWrap::SetTailApproxConfig),
        InstanceMethod("getTailApproxConfig", &ParticleEvaluatorWrap::GetTailApproxConfig),
        InstanceMethod("computeTailEnergySurrogateJ", &ParticleEvaluatorWrap::ComputeTailEnergySurrogateJ),
        InstanceMethod("computeRelativisticMetrics", &ParticleEvaluatorWrap::ComputeRelativisticMetrics),
        InstanceMethod("getFilaments", &ParticleEvaluatorWrap::GetFilaments),
    });
    exports.Set("ParticleEvaluator", func);
    return exports;
}

ParticleEvaluatorWrap::ParticleEvaluatorWrap(const Napi::CallbackInfo& info)
    : Napi::ObjectWrap<ParticleEvaluatorWrap>(info) {
    Napi::Env env = info.Env();
    if (info.Length() < 1) {
        throw Napi::TypeError::New(env, "Expected knot_ab_id (string) or filaments (array of array of [x,y,z])");
    }
    if (info[0].IsString()) {
        const std::string id = info[0].As<Napi::String>().Utf8Value();
        int res = (info.Length() >= 2 && info[1].IsNumber()) ? info[1].As<Napi::Number>().Int32Value() : 4000;
        pe_ = std::make_unique<ParticleEvaluator>(id, res);
    } else if (info[0].IsArray()) {
        Napi::Array outer = info[0].As<Napi::Array>();
        std::vector<std::vector<Vec3>> fils;
        fils.reserve(outer.Length());
        for (uint32_t i = 0; i < outer.Length(); ++i) {
            Napi::Value v = outer.Get(i);
            if (!v.IsArray()) {
                throw Napi::TypeError::New(env, "each filament must be an array of [x,y,z]");
            }
            fils.push_back(js_array_to_vec3_list(v.As<Napi::Array>()));
        }
        pe_ = std::make_unique<ParticleEvaluator>(fils);
    } else {
        throw Napi::TypeError::New(env, "Expected string (knot_ab_id) or nested array of filaments");
    }
}

Napi::Value ParticleEvaluatorWrap::Relax(const Napi::CallbackInfo& info) {
    const int it = (info.Length() >= 1) ? info[0].As<Napi::Number>().Int32Value() : 1000;
    const double dt = (info.Length() >= 2) ? info[1].As<Napi::Number>().DoubleValue() : 0.01;
    pe_->relax_hamiltonian(it, dt, nullptr);
    return info.Env().Undefined();
}

Napi::Value ParticleEvaluatorWrap::GetDimlessRopelength(const Napi::CallbackInfo& info) {
    const double lam = (info.Length() >= 1) ? info[0].As<Napi::Number>().DoubleValue() : 1.0;
    return Napi::Number::New(info.Env(), pe_->get_dimless_ropelength(lam));
}

Napi::Value ParticleEvaluatorWrap::GetPhysicalLengthM(const Napi::CallbackInfo& info) {
    return Napi::Number::New(info.Env(), pe_->get_physical_length_m());
}

Napi::Value ParticleEvaluatorWrap::ComputeCoreEnergyJ(const Napi::CallbackInfo& info) {
    return Napi::Number::New(info.Env(), pe_->compute_core_energy_J());
}

Napi::Value ParticleEvaluatorWrap::ComputeTailEnergyJ(const Napi::CallbackInfo& info) {
    const bool inc = (info.Length() >= 1) ? info[0].As<Napi::Boolean>().Value() : false;
    return Napi::Number::New(info.Env(), pe_->compute_tail_energy_J(inc));
}

Napi::Value ParticleEvaluatorWrap::GetMassMevAbInitio(const Napi::CallbackInfo& info) {
    const bool inc = (info.Length() >= 1) ? info[0].As<Napi::Boolean>().Value() : false;
    return Napi::Number::New(info.Env(), pe_->get_mass_mev_ab_initio(inc));
}

Napi::Value ParticleEvaluatorWrap::GetCoreMassMevOnly(const Napi::CallbackInfo& info) {
    return Napi::Number::New(info.Env(), pe_->get_core_mass_mev_only());
}

Napi::Value ParticleEvaluatorWrap::SetTailApproxConfig(const Napi::CallbackInfo& info) {
    if (info.Length() < 1 || !info[0].IsObject()) {
        throw Napi::TypeError::New(info.Env(), "Expected config object");
    }
    pe_->set_tail_approx_config(tail_config_from_js(info[0].As<Napi::Object>()));
    return info.Env().Undefined();
}

Napi::Value ParticleEvaluatorWrap::GetTailApproxConfig(const Napi::CallbackInfo& info) {
    return tail_config_to_js(info.Env(), pe_->get_tail_approx_config());
}

Napi::Value ParticleEvaluatorWrap::ComputeTailEnergySurrogateJ(const Napi::CallbackInfo& info) {
    return Napi::Number::New(info.Env(), pe_->compute_tail_energy_surrogate_J());
}

Napi::Value ParticleEvaluatorWrap::ComputeRelativisticMetrics(const Napi::CallbackInfo& info) {
    const double circ = (info.Length() >= 1) ? info[0].As<Napi::Number>().DoubleValue() : 9.683619203e-9;
    return relativistic_to_js(info.Env(), pe_->compute_relativistic_metrics(circ));
}

Napi::Value ParticleEvaluatorWrap::GetFilaments(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array out = Napi::Array::New(env);
    uint32_t fi = 0;
    for (const auto& fil : pe_->filaments) {
        Napi::Array ring = Napi::Array::New(env, fil.size());
        for (size_t j = 0; j < fil.size(); ++j) {
            Napi::Array p = Napi::Array::New(env, 3);
            p.Set(0u, Napi::Number::New(env, fil[j][0]));
            p.Set(1u, Napi::Number::New(env, fil[j][1]));
            p.Set(2u, Napi::Number::New(env, fil[j][2]));
            ring.Set(static_cast<uint32_t>(j), p);
        }
        out.Set(fi++, ring);
    }
    return out;
}

} // namespace

void bind_ab_initio(Napi::Env env, Napi::Object exports) {
    ParticleEvaluatorWrap::Init(env, exports);

    exports.Set("particlePrintCanonicalDerivation", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        ParticleEvaluator::print_canonical_derivation();
        return info.Env().Undefined();
    }));

    exports.Set("zooEvaluateAllGoldenNls", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        std::vector<ZooEvaluator::Result> r = ZooEvaluator::evaluate_all_golden_nls();
        Napi::Array arr = Napi::Array::New(e, r.size());
        for (size_t i = 0; i < r.size(); ++i) {
            Napi::Object o = Napi::Object::New(e);
            o.Set("identifier", Napi::String::New(e, r[i].identifier));
            o.Set("massMev", Napi::Number::New(e, r[i].mass_mev));
            o.Set("bridgeB", Napi::Number::New(e, r[i].bridge_b));
            o.Set("genusG", Napi::Number::New(e, r[i].genus_g));
            arr.Set(static_cast<uint32_t>(i), o);
        }
        return arr;
    }));

    exports.Set("zooGetEntryMass", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(info.Env(), "Expected identifier string");
        }
        const std::string id = info[0].As<Napi::String>().Utf8Value();
        return Napi::Number::New(info.Env(), ZooEvaluator::get_entry_mass(id));
    }));

    exports.Set("abInitioAvailable", Napi::Boolean::New(env, true));
}
