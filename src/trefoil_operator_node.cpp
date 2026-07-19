// trefoil_operator_node.cpp — N-API bindings for the trefoil spectral operator
//
// Mirrors src/trefoil_operator_py.cpp. Matrices are represented in JavaScript as
// flat, row-major Float64Array (or plain number[]) with length n*n; vectors are
// flat Float64Array (or plain number[]). Structs (Grid1D, BoundaryOptions,
// PotentialGaussianWell, PotentialOptions) are exposed as thin ObjectWraps with
// instance accessors so they can be read back either as wrap instances or plain
// objects.
#include <napi.h>
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <vector>
#include "trefoil_operator.h"

using namespace sst;

namespace {

// ---------------------------------------------------------------------------
// Small argument helpers
// ---------------------------------------------------------------------------
double opt_double(const Napi::CallbackInfo& info, size_t i, double def) {
    return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().DoubleValue() : def;
}
int opt_int(const Napi::CallbackInfo& info, size_t i, int def) {
    return (info.Length() > i && info[i].IsNumber()) ? info[i].As<Napi::Number>().Int32Value() : def;
}
bool opt_bool(const Napi::CallbackInfo& info, size_t i, bool def) {
    return (info.Length() > i && info[i].IsBoolean()) ? info[i].As<Napi::Boolean>().Value() : def;
}
std::size_t opt_size(const Napi::CallbackInfo& info, size_t i, std::size_t def) {
    return (info.Length() > i && info[i].IsNumber())
               ? static_cast<std::size_t>(info[i].As<Napi::Number>().Int64Value())
               : def;
}

std::vector<double> read_doubles(const Napi::Value& v) {
    std::vector<double> out;
    if (v.IsArray()) {
        Napi::Array a = v.As<Napi::Array>();
        out.reserve(a.Length());
        for (uint32_t i = 0; i < a.Length(); ++i) {
            out.push_back(a.Get(i).As<Napi::Number>().DoubleValue());
        }
    } else if (v.IsTypedArray()) {
        Napi::TypedArray ta = v.As<Napi::TypedArray>();
        if (ta.TypedArrayType() == napi_float64_array) {
            Napi::Float64Array fa = ta.As<Napi::Float64Array>();
            const double* d = fa.Data();
            out.assign(d, d + fa.ElementLength());
        } else {
            const size_t n = ta.ElementLength();
            out.reserve(n);
            Napi::Object obj = ta.As<Napi::Object>();
            for (size_t i = 0; i < n; ++i) {
                out.push_back(obj.Get(static_cast<uint32_t>(i)).As<Napi::Number>().DoubleValue());
            }
        }
    } else {
        throw Napi::TypeError::New(v.Env(), "Expected an array or Float64Array of numbers");
    }
    return out;
}

Napi::Float64Array to_f64(Napi::Env env, const std::vector<double>& v) {
    Napi::Float64Array a = Napi::Float64Array::New(env, v.size());
    for (size_t i = 0; i < v.size(); ++i) {
        a[i] = v[i];
    }
    return a;
}

// Read a flat square matrix and infer its dimension n from the length.
std::vector<double> read_square_matrix(const Napi::Value& v, std::size_t& n_out, const char* ctx) {
    std::vector<double> flat = read_doubles(v);
    const std::size_t total = flat.size();
    const std::size_t n = static_cast<std::size_t>(std::llround(std::sqrt(static_cast<double>(total))));
    if (n * n != total || n == 0) {
        throw Napi::TypeError::New(v.Env(), std::string(ctx) + ": matrix must be a flat square (n*n) array");
    }
    n_out = n;
    return flat;
}

Grid1D make_grid(double u_min, double u_max, std::size_t n) {
    Grid1D g;
    g.u_min = u_min;
    g.u_max = u_max;
    g.n = n;
    return g;
}

BoundaryOptions make_bc(int mode, bool force_center_dirichlet) {
    BoundaryOptions bc;
    bc.mode = mode;
    bc.force_center_dirichlet = force_center_dirichlet;
    return bc;
}

// Build PotentialOptions from any JS object exposing the expected fields. Works
// for both plain objects and PotentialOptions ObjectWrap instances (their
// instance accessors are readable through Get()).
PotentialOptions make_potential_options(const Napi::Value& v) {
    PotentialOptions opts;
    if (!v.IsObject()) {
        throw Napi::TypeError::New(v.Env(), "opts must be a PotentialOptions object");
    }
    Napi::Object o = v.As<Napi::Object>();
    if (o.Has("harmonic_coeff")) opts.harmonic_coeff = o.Get("harmonic_coeff").As<Napi::Number>().DoubleValue();
    if (o.Has("quartic_coeff")) opts.quartic_coeff = o.Get("quartic_coeff").As<Napi::Number>().DoubleValue();
    if (o.Has("constant_shift")) opts.constant_shift = o.Get("constant_shift").As<Napi::Number>().DoubleValue();
    if (o.Has("gaussians") && o.Get("gaussians").IsArray()) {
        Napi::Array arr = o.Get("gaussians").As<Napi::Array>();
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            Napi::Object g = arr.Get(i).As<Napi::Object>();
            PotentialGaussianWell well;
            if (g.Has("center")) well.center = g.Get("center").As<Napi::Number>().DoubleValue();
            if (g.Has("amplitude")) well.amplitude = g.Get("amplitude").As<Napi::Number>().DoubleValue();
            if (g.Has("sigma")) well.sigma = g.Get("sigma").As<Napi::Number>().DoubleValue();
            opts.gaussians.push_back(well);
        }
    }
    return opts;
}

Napi::Object spectral_result_to_js(Napi::Env env, const SpectralResult& r) {
    Napi::Object d = Napi::Object::New(env);
    d.Set("eigenvalues", to_f64(env, r.eigenvalues));
    if (!r.eigenvectors.empty()) {
        d.Set("eigenvectors", to_f64(env, r.eigenvectors));
    } else {
        d.Set("eigenvectors", env.Null());
    }
    d.Set("n", Napi::Number::New(env, static_cast<double>(r.n)));
    return d;
}

// ---------------------------------------------------------------------------
// Grid1D
// ---------------------------------------------------------------------------
class Grid1DWrap : public Napi::ObjectWrap<Grid1DWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "Grid1D",
            {InstanceAccessor("u_min", &Grid1DWrap::GetUMin, &Grid1DWrap::SetUMin),
             InstanceAccessor("u_max", &Grid1DWrap::GetUMax, &Grid1DWrap::SetUMax),
             InstanceAccessor("n", &Grid1DWrap::GetN, &Grid1DWrap::SetN),
             InstanceMethod("spacing", &Grid1DWrap::Spacing)});
        exports.Set("Grid1D", func);
    }
    Grid1DWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<Grid1DWrap>(info) {
        if (info.Length() > 0 && info[0].IsNumber()) inner_.u_min = info[0].As<Napi::Number>().DoubleValue();
        if (info.Length() > 1 && info[1].IsNumber()) inner_.u_max = info[1].As<Napi::Number>().DoubleValue();
        if (info.Length() > 2 && info[2].IsNumber())
            inner_.n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
    }

private:
    Grid1D inner_;
    Napi::Value GetUMin(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.u_min); }
    void SetUMin(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.u_min = v.As<Napi::Number>().DoubleValue(); }
    Napi::Value GetUMax(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.u_max); }
    void SetUMax(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.u_max = v.As<Napi::Number>().DoubleValue(); }
    Napi::Value GetN(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), static_cast<double>(inner_.n)); }
    void SetN(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.n = static_cast<std::size_t>(v.As<Napi::Number>().Int64Value());
    }
    Napi::Value Spacing(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.spacing()); }
};

// ---------------------------------------------------------------------------
// BoundaryOptions
// ---------------------------------------------------------------------------
class BoundaryOptionsWrap : public Napi::ObjectWrap<BoundaryOptionsWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "BoundaryOptions",
            {InstanceAccessor("mode", &BoundaryOptionsWrap::GetMode, &BoundaryOptionsWrap::SetMode),
             InstanceAccessor("force_center_dirichlet", &BoundaryOptionsWrap::GetFcd, &BoundaryOptionsWrap::SetFcd)});
        exports.Set("BoundaryOptions", func);
    }
    BoundaryOptionsWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<BoundaryOptionsWrap>(info) {}

private:
    BoundaryOptions inner_;
    Napi::Value GetMode(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.mode); }
    void SetMode(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.mode = v.As<Napi::Number>().Int32Value(); }
    Napi::Value GetFcd(const Napi::CallbackInfo& info) { return Napi::Boolean::New(info.Env(), inner_.force_center_dirichlet); }
    void SetFcd(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.force_center_dirichlet = v.As<Napi::Boolean>().Value(); }
};

// ---------------------------------------------------------------------------
// PotentialGaussianWell
// ---------------------------------------------------------------------------
class PotentialGaussianWellWrap : public Napi::ObjectWrap<PotentialGaussianWellWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "PotentialGaussianWell",
            {InstanceAccessor("center", &PotentialGaussianWellWrap::GetCenter, &PotentialGaussianWellWrap::SetCenter),
             InstanceAccessor("amplitude", &PotentialGaussianWellWrap::GetAmp, &PotentialGaussianWellWrap::SetAmp),
             InstanceAccessor("sigma", &PotentialGaussianWellWrap::GetSigma, &PotentialGaussianWellWrap::SetSigma)});
        exports.Set("PotentialGaussianWell", func);
    }
    PotentialGaussianWellWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<PotentialGaussianWellWrap>(info) {}

private:
    PotentialGaussianWell inner_;
    Napi::Value GetCenter(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.center); }
    void SetCenter(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.center = v.As<Napi::Number>().DoubleValue(); }
    Napi::Value GetAmp(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.amplitude); }
    void SetAmp(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.amplitude = v.As<Napi::Number>().DoubleValue(); }
    Napi::Value GetSigma(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.sigma); }
    void SetSigma(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.sigma = v.As<Napi::Number>().DoubleValue(); }
};

// ---------------------------------------------------------------------------
// PotentialOptions
// ---------------------------------------------------------------------------
class PotentialOptionsWrap : public Napi::ObjectWrap<PotentialOptionsWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "PotentialOptions",
            {InstanceAccessor("harmonic_coeff", &PotentialOptionsWrap::GetHarmonic, &PotentialOptionsWrap::SetHarmonic),
             InstanceAccessor("quartic_coeff", &PotentialOptionsWrap::GetQuartic, &PotentialOptionsWrap::SetQuartic),
             InstanceAccessor("constant_shift", &PotentialOptionsWrap::GetShift, &PotentialOptionsWrap::SetShift),
             InstanceAccessor("gaussians", &PotentialOptionsWrap::GetGaussians, &PotentialOptionsWrap::SetGaussians)});
        exports.Set("PotentialOptions", func);
    }
    PotentialOptionsWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<PotentialOptionsWrap>(info) {}

private:
    PotentialOptions inner_;
    Napi::Value GetHarmonic(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.harmonic_coeff); }
    void SetHarmonic(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.harmonic_coeff = v.As<Napi::Number>().DoubleValue(); }
    Napi::Value GetQuartic(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.quartic_coeff); }
    void SetQuartic(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.quartic_coeff = v.As<Napi::Number>().DoubleValue(); }
    Napi::Value GetShift(const Napi::CallbackInfo& info) { return Napi::Number::New(info.Env(), inner_.constant_shift); }
    void SetShift(const Napi::CallbackInfo&, const Napi::Value& v) { inner_.constant_shift = v.As<Napi::Number>().DoubleValue(); }
    Napi::Value GetGaussians(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        Napi::Array arr = Napi::Array::New(env, inner_.gaussians.size());
        for (size_t i = 0; i < inner_.gaussians.size(); ++i) {
            Napi::Object g = Napi::Object::New(env);
            g.Set("center", Napi::Number::New(env, inner_.gaussians[i].center));
            g.Set("amplitude", Napi::Number::New(env, inner_.gaussians[i].amplitude));
            g.Set("sigma", Napi::Number::New(env, inner_.gaussians[i].sigma));
            arr.Set(static_cast<uint32_t>(i), g);
        }
        return arr;
    }
    void SetGaussians(const Napi::CallbackInfo&, const Napi::Value& v) {
        inner_.gaussians.clear();
        if (!v.IsArray()) return;
        Napi::Array arr = v.As<Napi::Array>();
        for (uint32_t i = 0; i < arr.Length(); ++i) {
            Napi::Object g = arr.Get(i).As<Napi::Object>();
            PotentialGaussianWell well;
            if (g.Has("center")) well.center = g.Get("center").As<Napi::Number>().DoubleValue();
            if (g.Has("amplitude")) well.amplitude = g.Get("amplitude").As<Napi::Number>().DoubleValue();
            if (g.Has("sigma")) well.sigma = g.Get("sigma").As<Napi::Number>().DoubleValue();
            inner_.gaussians.push_back(well);
        }
    }
};

// ---------------------------------------------------------------------------
// TrefoilOperator (static methods)
// ---------------------------------------------------------------------------
class TrefoilOperatorWrap : public Napi::ObjectWrap<TrefoilOperatorWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "TrefoilOperator",
            {StaticMethod("buildIdentity", &TrefoilOperatorWrap::BuildIdentity),
             StaticMethod("buildUniformGrid", &TrefoilOperatorWrap::BuildUniformGrid),
             StaticMethod("buildSecondDifference", &TrefoilOperatorWrap::BuildSecondDifference),
             StaticMethod("buildLaplacianSchrodingerKinetic", &TrefoilOperatorWrap::BuildLaplacianSchrodingerKinetic),
             StaticMethod("buildPotentialFromOptions", &TrefoilOperatorWrap::BuildPotentialFromOptions),
             StaticMethod("buildPotentialFromNodes", &TrefoilOperatorWrap::BuildPotentialFromNodes),
             StaticMethod("buildPotentialFromTraceDensity", &TrefoilOperatorWrap::BuildPotentialFromTraceDensity),
             StaticMethod("buildPotentialFromPhiAbs", &TrefoilOperatorWrap::BuildPotentialFromPhiAbs),
             StaticMethod("assembleSchrodingerMatrix", &TrefoilOperatorWrap::AssembleSchrodingerMatrix),
             StaticMethod("applyDiagonalShift", &TrefoilOperatorWrap::ApplyDiagonalShift),
             StaticMethod("assembleTransferKernel", &TrefoilOperatorWrap::AssembleTransferKernel),
             StaticMethod("generatorFromTransferKernel", &TrefoilOperatorWrap::GeneratorFromTransferKernel),
             StaticMethod("matrixVectorMultiply", &TrefoilOperatorWrap::MatrixVectorMultiply),
             StaticMethod("rayleighQuotient", &TrefoilOperatorWrap::RayleighQuotient),
             StaticMethod("normalizeVector", &TrefoilOperatorWrap::NormalizeVector),
             StaticMethod("residualNorm", &TrefoilOperatorWrap::ResidualNorm),
             StaticMethod("eigenvalues", &TrefoilOperatorWrap::Eigenvalues),
             StaticMethod("traceFromDiagonal", &TrefoilOperatorWrap::TraceFromDiagonal),
             StaticMethod("logdetFromEigenvalues", &TrefoilOperatorWrap::LogdetFromEigenvalues),
             StaticMethod("spectralDensityHistogram", &TrefoilOperatorWrap::SpectralDensityHistogram),
             StaticMethod("jacobiEigensolveSymmetric", &TrefoilOperatorWrap::JacobiEigensolveSymmetric),
             StaticMethod("buildAndSolveNodeAnchoredOperator", &TrefoilOperatorWrap::BuildAndSolveNodeAnchoredOperator),
             StaticMethod("buildAndSolveTraceAnchoredOperator", &TrefoilOperatorWrap::BuildAndSolveTraceAnchoredOperator),
             StaticMethod("nearestEigenvaluesToTargets", &TrefoilOperatorWrap::NearestEigenvaluesToTargets)});
        exports.Set("TrefoilOperator", func);
    }
    TrefoilOperatorWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<TrefoilOperatorWrap>(info) {}

private:
    static Napi::Value BuildIdentity(const Napi::CallbackInfo& info) {
        std::size_t n = static_cast<std::size_t>(info[0].As<Napi::Number>().Int64Value());
        return to_f64(info.Env(), TrefoilOperator::buildIdentity(n));
    }
    static Napi::Value BuildUniformGrid(const Napi::CallbackInfo& info) {
        double u_min = info[0].As<Napi::Number>().DoubleValue();
        double u_max = info[1].As<Napi::Number>().DoubleValue();
        std::size_t n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
        return to_f64(info.Env(), TrefoilOperator::buildUniformGrid(make_grid(u_min, u_max, n)));
    }
    static Napi::Value BuildSecondDifference(const Napi::CallbackInfo& info) {
        double u_min = info[0].As<Napi::Number>().DoubleValue();
        double u_max = info[1].As<Napi::Number>().DoubleValue();
        std::size_t n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
        auto g = make_grid(u_min, u_max, n);
        auto bc = make_bc(opt_int(info, 3, 0), opt_bool(info, 4, true));
        return to_f64(info.Env(), TrefoilOperator::buildSecondDifference(g, bc));
    }
    static Napi::Value BuildLaplacianSchrodingerKinetic(const Napi::CallbackInfo& info) {
        double u_min = info[0].As<Napi::Number>().DoubleValue();
        double u_max = info[1].As<Napi::Number>().DoubleValue();
        std::size_t n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
        auto g = make_grid(u_min, u_max, n);
        auto bc = make_bc(opt_int(info, 3, 0), opt_bool(info, 4, true));
        double kinetic_prefactor = opt_double(info, 5, 1.0);
        return to_f64(info.Env(), TrefoilOperator::buildLaplacianSchrodingerKinetic(g, bc, kinetic_prefactor));
    }
    static Napi::Value BuildPotentialFromOptions(const Napi::CallbackInfo& info) {
        double u_min = info[0].As<Napi::Number>().DoubleValue();
        double u_max = info[1].As<Napi::Number>().DoubleValue();
        std::size_t n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
        auto opts = make_potential_options(info[3]);
        return to_f64(info.Env(), TrefoilOperator::buildPotentialFromOptions(make_grid(u_min, u_max, n), opts));
    }
    static Napi::Value BuildPotentialFromNodes(const Napi::CallbackInfo& info) {
        double u_min = info[0].As<Napi::Number>().DoubleValue();
        double u_max = info[1].As<Napi::Number>().DoubleValue();
        std::size_t n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
        std::vector<double> target_nodes = read_doubles(info[3]);
        double well_amplitude = info[4].As<Napi::Number>().DoubleValue();
        double well_sigma = info[5].As<Napi::Number>().DoubleValue();
        double harmonic_coeff = opt_double(info, 6, 0.0);
        double quartic_coeff = opt_double(info, 7, 0.0);
        double constant_shift = opt_double(info, 8, 0.0);
        auto V = TrefoilOperator::buildPotentialFromNodes(
            make_grid(u_min, u_max, n), target_nodes.data(), target_nodes.size(),
            well_amplitude, well_sigma, harmonic_coeff, quartic_coeff, constant_shift);
        return to_f64(info.Env(), V);
    }
    static Napi::Value BuildPotentialFromTraceDensity(const Napi::CallbackInfo& info) {
        std::vector<double> trace_density = read_doubles(info[0]);
        double scale = info[1].As<Napi::Number>().DoubleValue();
        double constant_shift = opt_double(info, 2, 0.0);
        double smooth_strength = opt_double(info, 3, 0.0);
        auto V = TrefoilOperator::buildPotentialFromTraceDensity(
            trace_density.data(), trace_density.size(), scale, constant_shift);
        if (smooth_strength > 0.0) {
            const int radius = std::max(1, static_cast<int>(std::round(smooth_strength)));
            V = TrefoilOperator::smoothPotentialBox(V.data(), V.size(), radius);
        }
        return to_f64(info.Env(), V);
    }
    static Napi::Value BuildPotentialFromPhiAbs(const Napi::CallbackInfo& info) {
        std::vector<double> phi_abs = read_doubles(info[0]);
        double scale = info[1].As<Napi::Number>().DoubleValue();
        double smooth_strength = opt_double(info, 2, 0.0);
        double constant_shift = opt_double(info, 3, 0.0);
        auto V = TrefoilOperator::buildPotentialFromPhiAbs(
            phi_abs.data(), phi_abs.size(), scale, smooth_strength, constant_shift);
        return to_f64(info.Env(), V);
    }
    static Napi::Value AssembleSchrodingerMatrix(const Napi::CallbackInfo& info) {
        double u_min = info[0].As<Napi::Number>().DoubleValue();
        double u_max = info[1].As<Napi::Number>().DoubleValue();
        std::size_t n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
        int boundary_mode = info[3].As<Napi::Number>().Int32Value();
        bool fcd = info[4].As<Napi::Boolean>().Value();
        std::vector<double> V = read_doubles(info[5]);
        if (V.size() != n) {
            throw Napi::TypeError::New(info.Env(), "assembleSchrodingerMatrix: potential length must equal n");
        }
        double kinetic_prefactor = opt_double(info, 6, 1.0);
        auto H = TrefoilOperator::assembleSchrodingerMatrix(
            make_grid(u_min, u_max, n), make_bc(boundary_mode, fcd), V.data(), kinetic_prefactor);
        return to_f64(info.Env(), H);
    }
    static Napi::Value ApplyDiagonalShift(const Napi::CallbackInfo& info) {
        std::size_t n = 0;
        std::vector<double> flat = read_square_matrix(info[0], n, "applyDiagonalShift");
        double shift = info[1].As<Napi::Number>().DoubleValue();
        return to_f64(info.Env(), TrefoilOperator::applyDiagonalShift(flat.data(), n, shift));
    }
    static Napi::Value AssembleTransferKernel(const Napi::CallbackInfo& info) {
        double u_min = info[0].As<Napi::Number>().DoubleValue();
        double u_max = info[1].As<Napi::Number>().DoubleValue();
        std::size_t n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
        std::vector<double> V = read_doubles(info[3]);
        if (V.size() != n) {
            throw Napi::TypeError::New(info.Env(), "assembleTransferKernel: potential length must equal n");
        }
        double diffusion_scale = info[4].As<Napi::Number>().DoubleValue();
        double potential_scale = info[5].As<Napi::Number>().DoubleValue();
        bool normalize_rows = opt_bool(info, 6, true);
        auto K = TrefoilOperator::assembleTransferKernel(
            make_grid(u_min, u_max, n), V.data(), diffusion_scale, potential_scale, normalize_rows);
        return to_f64(info.Env(), K);
    }
    static Napi::Value GeneratorFromTransferKernel(const Napi::CallbackInfo& info) {
        std::size_t n = 0;
        std::vector<double> flat = read_square_matrix(info[0], n, "generatorFromTransferKernel");
        double dt = info[1].As<Napi::Number>().DoubleValue();
        bool subtract_identity_first = opt_bool(info, 2, true);
        return to_f64(info.Env(),
                      TrefoilOperator::generatorFromTransferKernel(flat.data(), n, dt, subtract_identity_first));
    }
    static Napi::Value MatrixVectorMultiply(const Napi::CallbackInfo& info) {
        std::size_t n = 0;
        std::vector<double> flat = read_square_matrix(info[0], n, "matrixVectorMultiply");
        std::vector<double> x = read_doubles(info[1]);
        if (x.size() != n) {
            throw Napi::TypeError::New(info.Env(), "matrixVectorMultiply: x length must equal matrix dimension");
        }
        return to_f64(info.Env(), TrefoilOperator::matrixVectorMultiply(flat.data(), n, x.data()));
    }
    static Napi::Value RayleighQuotient(const Napi::CallbackInfo& info) {
        std::size_t n = 0;
        std::vector<double> flat = read_square_matrix(info[0], n, "rayleighQuotient");
        std::vector<double> x = read_doubles(info[1]);
        if (x.size() != n) {
            throw Napi::TypeError::New(info.Env(), "rayleighQuotient: x length must equal matrix dimension");
        }
        return Napi::Number::New(info.Env(), TrefoilOperator::rayleighQuotient(flat.data(), n, x.data()));
    }
    static Napi::Value NormalizeVector(const Napi::CallbackInfo& info) {
        std::vector<double> x = read_doubles(info[0]);
        TrefoilOperator::normalizeVector(x.data(), x.size());
        return to_f64(info.Env(), x);
    }
    static Napi::Value ResidualNorm(const Napi::CallbackInfo& info) {
        std::size_t n = 0;
        std::vector<double> flat = read_square_matrix(info[0], n, "residualNorm");
        std::vector<double> x = read_doubles(info[1]);
        if (x.size() != n) {
            throw Napi::TypeError::New(info.Env(), "residualNorm: x length must equal matrix dimension");
        }
        double lambda = info[2].As<Napi::Number>().DoubleValue();
        return Napi::Number::New(info.Env(), TrefoilOperator::residualNorm(flat.data(), n, x.data(), lambda));
    }
    static Napi::Value Eigenvalues(const Napi::CallbackInfo& info) {
        std::size_t n = 0;
        std::vector<double> flat = read_square_matrix(info[0], n, "eigenvalues");
        std::size_t max_sweeps = opt_size(info, 1, 100);
        double tol = opt_double(info, 2, 1e-12);
        bool sort_ascending = opt_bool(info, 3, true);
        return to_f64(info.Env(), TrefoilOperator::eigenvalues(flat.data(), n, max_sweeps, tol, sort_ascending));
    }
    static Napi::Value TraceFromDiagonal(const Napi::CallbackInfo& info) {
        std::size_t n = 0;
        std::vector<double> flat = read_square_matrix(info[0], n, "traceFromDiagonal");
        return Napi::Number::New(info.Env(), TrefoilOperator::traceFromDiagonal(flat.data(), n));
    }
    static Napi::Value LogdetFromEigenvalues(const Napi::CallbackInfo& info) {
        std::vector<double> ev = read_doubles(info[0]);
        double regularization = opt_double(info, 1, 1e-15);
        return Napi::Number::New(info.Env(),
                                 TrefoilOperator::logDetFromEigenvalues(ev.data(), ev.size(), regularization));
    }
    static Napi::Value SpectralDensityHistogram(const Napi::CallbackInfo& info) {
        std::vector<double> ev = read_doubles(info[0]);
        double x_min = info[1].As<Napi::Number>().DoubleValue();
        double x_max = info[2].As<Napi::Number>().DoubleValue();
        std::size_t n_bins = static_cast<std::size_t>(info[3].As<Napi::Number>().Int64Value());
        return to_f64(info.Env(),
                      TrefoilOperator::spectralDensityHistogram(ev.data(), ev.size(), x_min, x_max, n_bins));
    }
    static Napi::Value JacobiEigensolveSymmetric(const Napi::CallbackInfo& info) {
        std::size_t n = 0;
        std::vector<double> flat = read_square_matrix(info[0], n, "jacobiEigensolveSymmetric");
        bool compute_eigenvectors = opt_bool(info, 1, true);
        std::size_t max_sweeps = opt_size(info, 2, 100);
        double tol = opt_double(info, 3, 1e-12);
        bool sort_ascending = opt_bool(info, 4, true);
        auto res = TrefoilOperator::jacobiEigenSolveSymmetric(
            flat.data(), n, compute_eigenvectors, max_sweeps, tol, sort_ascending);
        return spectral_result_to_js(info.Env(), res);
    }
    static Napi::Value BuildAndSolveNodeAnchoredOperator(const Napi::CallbackInfo& info) {
        double u_min = info[0].As<Napi::Number>().DoubleValue();
        double u_max = info[1].As<Napi::Number>().DoubleValue();
        std::size_t n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
        int boundary_mode = info[3].As<Napi::Number>().Int32Value();
        bool fcd = info[4].As<Napi::Boolean>().Value();
        std::vector<double> target_nodes = read_doubles(info[5]);
        double well_amplitude = info[6].As<Napi::Number>().DoubleValue();
        double well_sigma = info[7].As<Napi::Number>().DoubleValue();
        double harmonic_coeff = opt_double(info, 8, 0.0);
        double quartic_coeff = opt_double(info, 9, 0.0);
        double constant_shift = opt_double(info, 10, 0.0);
        double kinetic_prefactor = opt_double(info, 11, 1.0);
        std::size_t max_sweeps = opt_size(info, 12, 100);
        double tol = opt_double(info, 13, 1e-12);
        bool sort_ascending = opt_bool(info, 14, true);
        auto res = TrefoilOperator::buildAndSolveNodeAnchoredOperator(
            make_grid(u_min, u_max, n), make_bc(boundary_mode, fcd),
            target_nodes.data(), target_nodes.size(), well_amplitude, well_sigma,
            harmonic_coeff, quartic_coeff, constant_shift, kinetic_prefactor,
            max_sweeps, tol, sort_ascending);
        return spectral_result_to_js(info.Env(), res);
    }
    static Napi::Value BuildAndSolveTraceAnchoredOperator(const Napi::CallbackInfo& info) {
        double u_min = info[0].As<Napi::Number>().DoubleValue();
        double u_max = info[1].As<Napi::Number>().DoubleValue();
        std::size_t n = static_cast<std::size_t>(info[2].As<Napi::Number>().Int64Value());
        int boundary_mode = info[3].As<Napi::Number>().Int32Value();
        bool fcd = info[4].As<Napi::Boolean>().Value();
        std::vector<double> trace_density = read_doubles(info[5]);
        double trace_scale = info[6].As<Napi::Number>().DoubleValue();
        double smooth_strength = opt_double(info, 7, 0.0);
        double constant_shift = opt_double(info, 8, 0.0);
        double kinetic_prefactor = opt_double(info, 9, 1.0);
        std::size_t max_sweeps = opt_size(info, 10, 100);
        double tol = opt_double(info, 11, 1e-12);
        bool sort_ascending = opt_bool(info, 12, true);
        auto res = TrefoilOperator::buildAndSolveTraceAnchoredOperator(
            make_grid(u_min, u_max, n), make_bc(boundary_mode, fcd),
            trace_density.data(), trace_density.size(), trace_scale, smooth_strength,
            constant_shift, kinetic_prefactor, max_sweeps, tol, sort_ascending);
        return spectral_result_to_js(info.Env(), res);
    }
    static Napi::Value NearestEigenvaluesToTargets(const Napi::CallbackInfo& info) {
        std::vector<double> ev = read_doubles(info[0]);
        std::vector<double> targets = read_doubles(info[1]);
        auto out = TrefoilOperator::nearestEigenvaluesToTargets(
            ev.data(), ev.size(), targets.data(), targets.size());
        return to_f64(info.Env(), out);
    }
};

} // namespace

void bind_trefoil_operator(Napi::Env env, Napi::Object exports) {
    Grid1DWrap::Init(env, exports);
    BoundaryOptionsWrap::Init(env, exports);
    PotentialGaussianWellWrap::Init(env, exports);
    PotentialOptionsWrap::Init(env, exports);
    TrefoilOperatorWrap::Init(env, exports);
    exports.Set("trefoilOperatorAvailable", Napi::Boolean::New(env, true));
}
