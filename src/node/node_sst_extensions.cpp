// node_sst_extensions.cpp — f-series / helicity utilities (N-API)
#include <napi.h>
#include "../sst_extensions.h"

using namespace sst::sstext;

namespace {

Napi::Object canon_to_js(Napi::Env env, const CanonicalizeResult& r) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("path", Napi::String::New(env, r.path));
    o.Set("foundNumericRows", Napi::Number::New(env, r.found_numeric_rows));
    o.Set("changed", Napi::Boolean::New(env, r.changed));
    o.Set("reason", Napi::String::New(env, r.reason));
    return o;
}

Napi::Object helicity_to_js(Napi::Env env, const HelicityResult& r) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("path", Napi::String::New(env, r.path));
    o.Set("aMu", Napi::Number::New(env, r.a_mu));
    o.Set("Hc", Napi::Number::New(env, r.Hc));
    o.Set("Hm", Napi::Number::New(env, r.Hm));
    o.Set("L", Napi::Number::New(env, r.L));
    o.Set("kappaMax", Napi::Number::New(env, r.kappa_max));
    o.Set("kappaMean", Napi::Number::New(env, r.kappa_mean));
    o.Set("bendEnergy", Napi::Number::New(env, r.bend_energy));
    o.Set("minNonNeighborDist", Napi::Number::New(env, r.min_non_neighbor_dist));
    o.Set("reachProxy", Napi::Number::New(env, r.reach_proxy));
    o.Set("nsamples", Napi::Number::New(env, r.nsamples));
    return o;
}

FilamentEnergyParams params_from_js(Napi::Object p) {
    FilamentEnergyParams out;
    if (p.Has("rhoOuter")) out.rho_outer = p.Get("rhoOuter").As<Napi::Number>().DoubleValue();
    if (p.Has("rhoLocal")) out.rho_local = p.Get("rhoLocal").As<Napi::Number>().DoubleValue();
    if (p.Has("Gamma")) out.Gamma = p.Get("Gamma").As<Napi::Number>().DoubleValue();
    if (p.Has("aCore")) out.a_core = p.Get("aCore").As<Napi::Number>().DoubleValue();
    if (p.Has("delta")) out.delta = p.Get("delta").As<Napi::Number>().DoubleValue();
    if (p.Has("sCutLocal")) out.s_cut_local = p.Get("sCutLocal").As<Napi::Number>().DoubleValue();
    if (p.Has("includeNonlocal")) out.include_nonlocal = p.Get("includeNonlocal").As<Napi::Boolean>().Value();
    if (p.Has("includeLocalMatch")) out.include_local_match = p.Get("includeLocalMatch").As<Napi::Boolean>().Value();
    if (p.Has("includeCoreInt")) out.include_core_int = p.Get("includeCoreInt").As<Napi::Boolean>().Value();
    if (p.Has("cRankineOuter")) out.c_rankine_outer = p.Get("cRankineOuter").As<Napi::Number>().DoubleValue();
    if (p.Has("nsamples")) out.nsamples = p.Get("nsamples").As<Napi::Number>().Int32Value();
    if (p.Has("skipNeighborsBase")) out.skip_neighbors_base = p.Get("skipNeighborsBase").As<Napi::Number>().Int32Value();
    return out;
}

Napi::Object filament_energy_to_js(Napi::Env env, const FilamentEnergyResult& r) {
    Napi::Object o = Napi::Object::New(env);
    o.Set("path", Napi::String::New(env, r.path));
    o.Set("L", Napi::Number::New(env, r.L));
    o.Set("dsAvg", Napi::Number::New(env, r.ds_avg));
    o.Set("mLoc", Napi::Number::New(env, r.m_loc));
    o.Set("E_nonlocal", Napi::Number::New(env, r.E_nonlocal));
    o.Set("E_local_match", Napi::Number::New(env, r.E_local_match));
    o.Set("E_core_int", Napi::Number::New(env, r.E_core_int));
    o.Set("E_total", Napi::Number::New(env, r.E_total));
    o.Set("kappaMax", Napi::Number::New(env, r.kappa_max));
    o.Set("kappaMean", Napi::Number::New(env, r.kappa_mean));
    o.Set("bendEnergy", Napi::Number::New(env, r.bend_energy));
    o.Set("minNonNeighborDist", Napi::Number::New(env, r.min_non_neighbor_dist));
    o.Set("reachProxy", Napi::Number::New(env, r.reach_proxy));
    o.Set("rhoOuter", Napi::Number::New(env, r.rho_outer));
    o.Set("rhoLocal", Napi::Number::New(env, r.rho_local));
    o.Set("Gamma", Napi::Number::New(env, r.Gamma));
    o.Set("aCore", Napi::Number::New(env, r.a_core));
    o.Set("delta", Napi::Number::New(env, r.delta));
    o.Set("sCutLocal", Napi::Number::New(env, r.s_cut_local));
    o.Set("cRankineOuter", Napi::Number::New(env, r.c_rankine_outer));
    o.Set("nsamples", Napi::Number::New(env, r.nsamples));
    return o;
}

Napi::TypedArray vec3s_to_flat(Napi::Env env, const std::vector<sst::Vec3>& pts) {
    const size_t n = pts.size() * 3u;
    Napi::ArrayBuffer buf = Napi::ArrayBuffer::New(env, n * sizeof(double));
    double* d = static_cast<double*>(buf.Data());
    for (size_t i = 0; i < pts.size(); ++i) {
        d[3 * i] = pts[i][0];
        d[3 * i + 1] = pts[i][1];
        d[3 * i + 2] = pts[i][2];
    }
    return Napi::Float64Array::New(env, n, buf, 0);
}

} // namespace

void bind_extensions(Napi::Env env, Napi::Object exports) {
    exports.Set("canonicalizeFseriesFileInplace", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(info.Env(), "Expected path string");
        }
        CanonicalizeResult r = canonicalize_fseries_file_inplace(info[0].As<Napi::String>().Utf8Value());
        return canon_to_js(info.Env(), r);
    }));

    exports.Set("computeHelicityFromFseries", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(e, "Expected path string");
        }
        const std::string path = info[0].As<Napi::String>().Utf8Value();
        int gs = (info.Length() > 1) ? info[1].As<Napi::Number>().Int32Value() : 32;
        double sp = (info.Length() > 2) ? info[2].As<Napi::Number>().DoubleValue() : 0.1;
        int im = (info.Length() > 3) ? info[3].As<Napi::Number>().Int32Value() : 8;
        int ns = (info.Length() > 4) ? info[4].As<Napi::Number>().Int32Value() : 1000;
        HelicityResult r = helicity_from_fseries(path, gs, sp, im, ns);
        return helicity_to_js(e, r);
    }));

    exports.Set("sampleCurveCentered", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(info.Env(), "Expected path string");
        }
        const std::string path = info[0].As<Napi::String>().Utf8Value();
        int ns = (info.Length() > 1) ? info[1].As<Napi::Number>().Int32Value() : 1024;
        std::vector<sst::Vec3> pts = sample_curve_centered(path, ns);
        return vec3s_to_flat(info.Env(), pts);
    }));

    exports.Set("computeCurveMetricsFromFseries", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(e, "Expected path string");
        }
        const std::string path = info[0].As<Napi::String>().Utf8Value();
        int ns = (info.Length() > 1) ? info[1].As<Napi::Number>().Int32Value() : 2048;
        int sk = (info.Length() > 2) ? info[2].As<Napi::Number>().Int32Value() : 3;
        FilamentEnergyResult r = curve_metrics_from_fseries(path, ns, sk);
        return filament_energy_to_js(e, r);
    }));

    exports.Set("curveLengthFromFseries", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(info.Env(), "Expected path string");
        }
        const std::string path = info[0].As<Napi::String>().Utf8Value();
        int ns = (info.Length() > 1) ? info[1].As<Napi::Number>().Int32Value() : 2048;
        auto pts = sample_curve_centered(path, ns);
        return Napi::Number::New(info.Env(), curve_length(pts));
    }));

    exports.Set("minNonNeighborDistanceFromFseries", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(info.Env(), "Expected path string");
        }
        const std::string path = info[0].As<Napi::String>().Utf8Value();
        int ns = (info.Length() > 1) ? info[1].As<Napi::Number>().Int32Value() : 2048;
        int sk = (info.Length() > 2) ? info[2].As<Napi::Number>().Int32Value() : 3;
        auto pts = sample_curve_centered(path, ns);
        return Napi::Number::New(info.Env(), min_non_neighbor_distance(pts, sk));
    }));

    exports.Set("reachProxyFromFseries", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(info.Env(), "Expected path string");
        }
        const std::string path = info[0].As<Napi::String>().Utf8Value();
        int ns = (info.Length() > 1) ? info[1].As<Napi::Number>().Int32Value() : 2048;
        int sk = (info.Length() > 2) ? info[2].As<Napi::Number>().Int32Value() : 3;
        auto pts = sample_curve_centered(path, ns);
        return Napi::Number::New(info.Env(), reach_proxy(pts, sk));
    }));

    exports.Set("computeFilamentEnergyFromFseries", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2 || !info[0].IsString() || !info[1].IsObject()) {
            throw Napi::TypeError::New(e, "Expected (path, paramsObject)");
        }
        const std::string path = info[0].As<Napi::String>().Utf8Value();
        FilamentEnergyParams p = params_from_js(info[1].As<Napi::Object>());
        FilamentEnergyResult r = filament_energy_from_fseries(path, p);
        return filament_energy_to_js(e, r);
    }));

    exports.Set("batchHelicityFromDir", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(e, "Expected rootDir string");
        }
        const std::string root = info[0].As<Napi::String>().Utf8Value();
        int gs = (info.Length() > 1) ? info[1].As<Napi::Number>().Int32Value() : 32;
        double sp = (info.Length() > 2) ? info[2].As<Napi::Number>().DoubleValue() : 0.1;
        int im = (info.Length() > 3) ? info[3].As<Napi::Number>().Int32Value() : 8;
        int ns = (info.Length() > 4) ? info[4].As<Napi::Number>().Int32Value() : 1000;
        bool rec = (info.Length() > 5) ? info[5].As<Napi::Boolean>().Value() : false;
        std::vector<HelicityResult> vec = batch_helicity_from_dir(root, gs, sp, im, ns, rec);
        Napi::Array arr = Napi::Array::New(e, vec.size());
        for (size_t i = 0; i < vec.size(); ++i) {
            arr.Set(static_cast<uint32_t>(i), helicity_to_js(e, vec[i]));
        }
        return arr;
    }));

    exports.Set("compareFseriesFiles", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2 || !info[0].IsString() || !info[1].IsString()) {
            throw Napi::TypeError::New(e, "Expected (pathA, pathB)");
        }
        const std::string a = info[0].As<Napi::String>().Utf8Value();
        const std::string b = info[1].As<Napi::String>().Utf8Value();
        int ns = (info.Length() > 2) ? info[2].As<Napi::Number>().Int32Value() : 2048;
        int sk = (info.Length() > 3) ? info[3].As<Napi::Number>().Int32Value() : 3;
        std::map<std::string, double> m = compare_fseries_files(a, b, ns, sk);
        Napi::Object o = Napi::Object::New(e);
        for (const auto& kv : m) {
            o.Set(kv.first, Napi::Number::New(e, kv.second));
        }
        return o;
    }));

    exports.Set("sstExtensionsAvailable", Napi::Boolean::New(env, true));
}
