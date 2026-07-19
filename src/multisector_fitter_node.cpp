// multisector_fitter_node.cpp — N-API bindings for the multisector fitter suite
//
// Mirrors src/multisector_fitter_py.cpp. Real vectors are exposed as Float64Array
// (plain number[] accepted on input); complex vectors are exposed as
// { re: Float64Array, im: Float64Array } (an object with re/im arrays is accepted
// on input). Optional array arguments (sector_weights, node_weights) accept null
// or undefined for "not provided".
#include <napi.h>
#include <complex>
#include <cstddef>
#include <vector>
#include "multisector_fitter.h"

using namespace sst;

namespace {

// ---------------------------------------------------------------------------
// Argument helpers
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
std::size_t size_arg(const Napi::CallbackInfo& info, size_t i) {
    return static_cast<std::size_t>(info[i].As<Napi::Number>().Int64Value());
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
            Napi::Object obj = ta.As<Napi::Object>();
            out.reserve(n);
            for (size_t i = 0; i < n; ++i) {
                out.push_back(obj.Get(static_cast<uint32_t>(i)).As<Napi::Number>().DoubleValue());
            }
        }
    } else {
        throw Napi::TypeError::New(v.Env(), "Expected an array or Float64Array of numbers");
    }
    return out;
}

std::vector<int> read_ints(const Napi::Value& v) {
    std::vector<int> out;
    if (v.IsArray()) {
        Napi::Array a = v.As<Napi::Array>();
        out.reserve(a.Length());
        for (uint32_t i = 0; i < a.Length(); ++i) {
            out.push_back(a.Get(i).As<Napi::Number>().Int32Value());
        }
    } else if (v.IsTypedArray()) {
        Napi::TypedArray ta = v.As<Napi::TypedArray>();
        const size_t n = ta.ElementLength();
        Napi::Object obj = ta.As<Napi::Object>();
        out.reserve(n);
        for (size_t i = 0; i < n; ++i) {
            out.push_back(obj.Get(static_cast<uint32_t>(i)).As<Napi::Number>().Int32Value());
        }
    } else {
        throw Napi::TypeError::New(v.Env(), "Expected an array of integers");
    }
    return out;
}

// Returns true if the optional argument was provided (not null/undefined).
bool read_optional_doubles(const Napi::CallbackInfo& info, size_t i, std::vector<double>& out) {
    if (info.Length() <= i || info[i].IsNull() || info[i].IsUndefined()) {
        return false;
    }
    out = read_doubles(info[i]);
    return true;
}

std::vector<std::complex<double>> read_complex(const Napi::Value& v) {
    if (!v.IsObject()) {
        throw Napi::TypeError::New(v.Env(), "Expected a complex array as { re: [], im: [] }");
    }
    Napi::Object o = v.As<Napi::Object>();
    std::vector<double> re = read_doubles(o.Get("re"));
    std::vector<double> im = read_doubles(o.Get("im"));
    if (re.size() != im.size()) {
        throw Napi::TypeError::New(v.Env(), "complex array: re and im must have equal length");
    }
    std::vector<std::complex<double>> out(re.size());
    for (size_t i = 0; i < re.size(); ++i) {
        out[i] = std::complex<double>(re[i], im[i]);
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

Napi::Object cvec_to_js(Napi::Env env, const std::vector<std::complex<double>>& v) {
    Napi::Float64Array re = Napi::Float64Array::New(env, v.size());
    Napi::Float64Array im = Napi::Float64Array::New(env, v.size());
    for (size_t i = 0; i < v.size(); ++i) {
        re[i] = v[i].real();
        im[i] = v[i].imag();
    }
    Napi::Object o = Napi::Object::New(env);
    o.Set("re", re);
    o.Set("im", im);
    return o;
}

Napi::Array size_vec_to_js(Napi::Env env, const std::vector<std::size_t>& v) {
    Napi::Array a = Napi::Array::New(env, v.size());
    for (size_t i = 0; i < v.size(); ++i) {
        a.Set(static_cast<uint32_t>(i), Napi::Number::New(env, static_cast<double>(v[i])));
    }
    return a;
}

MultisectorEvalOptions make_eval_opts(double ell_trefoil, std::size_t truncation_M,
                                      int completion_mode, double alpha, double beta) {
    MultisectorEvalOptions opts;
    opts.ell_trefoil = ell_trefoil;
    opts.truncation_M = truncation_M;
    opts.completion_mode = completion_mode;
    opts.alpha = alpha;
    opts.beta = beta;
    return opts;
}

SuppressionOptions make_supp_opts(double lambda_extra, double sigma_extra, double lambda_reg,
                                  double target_halfwidth, bool penalize_all_extra_minima) {
    SuppressionOptions sopts;
    sopts.lambda_extra = lambda_extra;
    sopts.sigma_extra = sigma_extra;
    sopts.lambda_reg = lambda_reg;
    sopts.target_halfwidth = target_halfwidth;
    sopts.penalize_all_extra_minima = penalize_all_extra_minima;
    return sopts;
}

// ---------------------------------------------------------------------------
// MultisectorFitter (v1)
// ---------------------------------------------------------------------------
class MultisectorFitterWrap : public Napi::ObjectWrap<MultisectorFitterWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "MultisectorFitter",
            {StaticMethod("evaluateSector", &MultisectorFitterWrap::EvaluateSector),
             StaticMethod("evaluateMultisector", &MultisectorFitterWrap::EvaluateMultisector),
             StaticMethod("evaluateMultisectorAbs", &MultisectorFitterWrap::EvaluateMultisectorAbs),
             StaticMethod("objectiveNearNodes", &MultisectorFitterWrap::ObjectiveNearNodes)});
        exports.Set("MultisectorFitter", func);
    }
    MultisectorFitterWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<MultisectorFitterWrap>(info) {}

private:
    static Napi::Value EvaluateSector(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        int nu = info[1].As<Napi::Number>().Int32Value();
        double theta_nu = info[2].As<Napi::Number>().DoubleValue();
        double ell_trefoil = info[3].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 4);
        auto out = MultisectorFitter::evaluateSector(t.data(), t.size(), nu, theta_nu, ell_trefoil, truncation_M);
        return cvec_to_js(info.Env(), out);
    }
    static Napi::Value EvaluateMultisector(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        int completion_mode = opt_int(info, 6, 0);
        double alpha = opt_double(info, 7, 0.0);
        double beta = opt_double(info, 8, 0.0);
        auto out = MultisectorFitter::evaluateMultisector(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr,
            ell_trefoil, truncation_M, completion_mode, alpha, beta);
        return cvec_to_js(info.Env(), out);
    }
    static Napi::Value EvaluateMultisectorAbs(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        int completion_mode = opt_int(info, 6, 0);
        double alpha = opt_double(info, 7, 0.0);
        double beta = opt_double(info, 8, 0.0);
        auto out = MultisectorFitter::evaluateMultisectorAbs(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr,
            ell_trefoil, truncation_M, completion_mode, alpha, beta);
        return to_f64(info.Env(), out);
    }
    static Napi::Value ObjectiveNearNodes(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        int completion_mode = opt_int(info, 6, 0);
        double alpha = opt_double(info, 7, 0.0);
        double beta = opt_double(info, 8, 0.0);
        std::vector<double> target_nodes = read_doubles(info[9]);
        std::vector<double> node_weights;
        const double* nwptr = read_optional_doubles(info, 10, node_weights) ? node_weights.data() : nullptr;
        double val = MultisectorFitter::objectiveNearNodes(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr,
            ell_trefoil, truncation_M, completion_mode, alpha, beta,
            target_nodes.data(), target_nodes.size(), nwptr);
        return Napi::Number::New(info.Env(), val);
    }
};

// ---------------------------------------------------------------------------
// NodeAnalyzer
// ---------------------------------------------------------------------------
class NodeAnalyzerWrap : public Napi::ObjectWrap<NodeAnalyzerWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "NodeAnalyzer",
            {StaticMethod("localMinimaIndices", &NodeAnalyzerWrap::LocalMinimaIndices),
             StaticMethod("localMaximaIndices", &NodeAnalyzerWrap::LocalMaximaIndices),
             StaticMethod("strongestMinimaT", &NodeAnalyzerWrap::StrongestMinimaT),
             StaticMethod("strongestMinimaValues", &NodeAnalyzerWrap::StrongestMinimaValues),
             StaticMethod("strongestMinimaTWithNeighborhoodExclusion",
                          &NodeAnalyzerWrap::StrongestMinimaTWithNeighborhoodExclusion),
             StaticMethod("extraMinimaPenalty", &NodeAnalyzerWrap::ExtraMinimaPenalty)});
        exports.Set("NodeAnalyzer", func);
    }
    NodeAnalyzerWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<NodeAnalyzerWrap>(info) {}

private:
    static Napi::Value LocalMinimaIndices(const Napi::CallbackInfo& info) {
        std::vector<double> y = read_doubles(info[0]);
        return size_vec_to_js(info.Env(), NodeAnalyzer::localMinimaIndices(y.data(), y.size()));
    }
    static Napi::Value LocalMaximaIndices(const Napi::CallbackInfo& info) {
        std::vector<double> y = read_doubles(info[0]);
        return size_vec_to_js(info.Env(), NodeAnalyzer::localMaximaIndices(y.data(), y.size()));
    }
    static Napi::Value StrongestMinimaT(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<double> y = read_doubles(info[1]);
        if (t.size() != y.size()) {
            throw Napi::TypeError::New(info.Env(), "strongestMinimaT: t and y must have same length");
        }
        std::size_t keep_count = size_arg(info, 2);
        return to_f64(info.Env(), NodeAnalyzer::strongestMinimaT(t.data(), y.data(), t.size(), keep_count));
    }
    static Napi::Value StrongestMinimaValues(const Napi::CallbackInfo& info) {
        std::vector<double> y = read_doubles(info[0]);
        std::size_t keep_count = size_arg(info, 1);
        return to_f64(info.Env(), NodeAnalyzer::strongestMinimaValues(y.data(), y.size(), keep_count));
    }
    static Napi::Value StrongestMinimaTWithNeighborhoodExclusion(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<double> y = read_doubles(info[1]);
        if (t.size() != y.size()) {
            throw Napi::TypeError::New(
                info.Env(), "strongestMinimaTWithNeighborhoodExclusion: t and y must have same length");
        }
        std::vector<double> target_nodes = read_doubles(info[2]);
        double target_halfwidth = info[3].As<Napi::Number>().DoubleValue();
        bool keep_only_outside = info[4].As<Napi::Boolean>().Value();
        std::size_t keep_count = size_arg(info, 5);
        auto out = NodeAnalyzer::strongestMinimaTWithNeighborhoodExclusion(
            t.data(), y.data(), t.size(), target_nodes.data(), target_nodes.size(),
            target_halfwidth, keep_only_outside, keep_count);
        return to_f64(info.Env(), out);
    }
    static Napi::Value ExtraMinimaPenalty(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<double> y = read_doubles(info[1]);
        if (t.size() != y.size()) {
            throw Napi::TypeError::New(info.Env(), "extraMinimaPenalty: t and y must have same length");
        }
        std::vector<double> target_nodes = read_doubles(info[2]);
        double target_halfwidth = info[3].As<Napi::Number>().DoubleValue();
        double sigma_extra = info[4].As<Napi::Number>().DoubleValue();
        bool penalize_all_extra_minima = opt_bool(info, 5, true);
        double val = NodeAnalyzer::extraMinimaPenalty(
            t.data(), y.data(), t.size(), target_nodes.data(), target_nodes.size(),
            target_halfwidth, sigma_extra, penalize_all_extra_minima);
        return Napi::Number::New(info.Env(), val);
    }
};

// ---------------------------------------------------------------------------
// TraceFormula
// ---------------------------------------------------------------------------
class TraceFormulaWrap : public Napi::ObjectWrap<TraceFormulaWrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "TraceFormula",
            {StaticMethod("evaluateMultisectorLogz", &TraceFormulaWrap::EvaluateMultisectorLogz),
             StaticMethod("phaseDerivativeFromXi", &TraceFormulaWrap::PhaseDerivativeFromXi),
             StaticMethod("evaluateMultisectorDlogzDs", &TraceFormulaWrap::EvaluateMultisectorDlogzDs)});
        exports.Set("TraceFormula", func);
    }
    TraceFormulaWrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<TraceFormulaWrap>(info) {}

private:
    static Napi::Value EvaluateMultisectorLogz(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        auto out = TraceFormula::evaluateMultisectorLogZ(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr, ell_trefoil, truncation_M);
        return cvec_to_js(info.Env(), out);
    }
    static Napi::Value PhaseDerivativeFromXi(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<std::complex<double>> xi = read_complex(info[1]);
        if (xi.size() != t.size()) {
            throw Napi::TypeError::New(info.Env(), "phaseDerivativeFromXi: xi_values must match t_values");
        }
        auto out = TraceFormula::phaseDerivativeFromXi(t.data(), t.size(), xi.data());
        return to_f64(info.Env(), out);
    }
    static Napi::Value EvaluateMultisectorDlogzDs(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        auto out = TraceFormula::evaluateMultisectorDLogZDs(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr, ell_trefoil, truncation_M);
        return cvec_to_js(info.Env(), out);
    }
};

// ---------------------------------------------------------------------------
// MultisectorFitterV2
// ---------------------------------------------------------------------------
class MultisectorFitterV2Wrap : public Napi::ObjectWrap<MultisectorFitterV2Wrap> {
public:
    static void Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(
            env, "MultisectorFitterV2",
            {StaticMethod("completionFactor", &MultisectorFitterV2Wrap::CompletionFactor),
             StaticMethod("evaluateSector", &MultisectorFitterV2Wrap::EvaluateSector),
             StaticMethod("evaluateSectorAbs", &MultisectorFitterV2Wrap::EvaluateSectorAbs),
             StaticMethod("evaluateMultisector", &MultisectorFitterV2Wrap::EvaluateMultisector),
             StaticMethod("evaluateMultisectorAbs", &MultisectorFitterV2Wrap::EvaluateMultisectorAbs),
             StaticMethod("evaluateMultisectorAbsBatchM", &MultisectorFitterV2Wrap::EvaluateMultisectorAbsBatchM),
             StaticMethod("objectiveNearNodes", &MultisectorFitterV2Wrap::ObjectiveNearNodes),
             StaticMethod("objectiveSuppressed", &MultisectorFitterV2Wrap::ObjectiveSuppressed),
             StaticMethod("objectiveSuppressedBreakdown", &MultisectorFitterV2Wrap::ObjectiveSuppressedBreakdown),
             StaticMethod("phaseInvariants", &MultisectorFitterV2Wrap::PhaseInvariants)});
        exports.Set("MultisectorFitterV2", func);
    }
    MultisectorFitterV2Wrap(const Napi::CallbackInfo& info) : Napi::ObjectWrap<MultisectorFitterV2Wrap>(info) {}

private:
    static Napi::Value CompletionFactor(const Napi::CallbackInfo& info) {
        std::complex<double> s;
        if (info[0].IsObject()) {
            Napi::Object o = info[0].As<Napi::Object>();
            double re = o.Has("re") ? o.Get("re").As<Napi::Number>().DoubleValue() : 0.0;
            double im = o.Has("im") ? o.Get("im").As<Napi::Number>().DoubleValue() : 0.0;
            s = std::complex<double>(re, im);
        } else {
            s = std::complex<double>(info[0].As<Napi::Number>().DoubleValue(), 0.0);
        }
        int completion_mode = opt_int(info, 1, 0);
        double alpha = opt_double(info, 2, 0.0);
        double beta = opt_double(info, 3, 0.0);
        auto r = MultisectorFitterV2::completionFactor(s, completion_mode, alpha, beta);
        Napi::Object o = Napi::Object::New(info.Env());
        o.Set("re", Napi::Number::New(info.Env(), r.real()));
        o.Set("im", Napi::Number::New(info.Env(), r.imag()));
        return o;
    }
    static Napi::Value EvaluateSector(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        int nu = info[1].As<Napi::Number>().Int32Value();
        double theta_nu = info[2].As<Napi::Number>().DoubleValue();
        double ell_trefoil = info[3].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 4);
        auto opts = make_eval_opts(ell_trefoil, truncation_M, opt_int(info, 5, 0),
                                   opt_double(info, 6, 0.0), opt_double(info, 7, 0.0));
        auto out = MultisectorFitterV2::evaluateSector(t.data(), t.size(), nu, theta_nu, opts);
        return cvec_to_js(info.Env(), out);
    }
    static Napi::Value EvaluateSectorAbs(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        int nu = info[1].As<Napi::Number>().Int32Value();
        double theta_nu = info[2].As<Napi::Number>().DoubleValue();
        double ell_trefoil = info[3].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 4);
        auto opts = make_eval_opts(ell_trefoil, truncation_M, opt_int(info, 5, 0),
                                   opt_double(info, 6, 0.0), opt_double(info, 7, 0.0));
        auto out = MultisectorFitterV2::evaluateSectorAbs(t.data(), t.size(), nu, theta_nu, opts);
        return to_f64(info.Env(), out);
    }
    static Napi::Value EvaluateMultisector(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        auto opts = make_eval_opts(ell_trefoil, truncation_M, opt_int(info, 6, 0),
                                   opt_double(info, 7, 0.0), opt_double(info, 8, 0.0));
        auto out = MultisectorFitterV2::evaluateMultisector(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr, opts);
        return cvec_to_js(info.Env(), out);
    }
    static Napi::Value EvaluateMultisectorAbs(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        auto opts = make_eval_opts(ell_trefoil, truncation_M, opt_int(info, 6, 0),
                                   opt_double(info, 7, 0.0), opt_double(info, 8, 0.0));
        auto out = MultisectorFitterV2::evaluateMultisectorAbs(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr, opts);
        return to_f64(info.Env(), out);
    }
    static Napi::Value EvaluateMultisectorAbsBatchM(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::vector<double> Mraw = read_doubles(info[5]);
        std::vector<std::size_t> Mvals(Mraw.size());
        for (size_t i = 0; i < Mraw.size(); ++i) {
            Mvals[i] = static_cast<std::size_t>(Mraw[i]);
        }
        int completion_mode = opt_int(info, 6, 0);
        double alpha = opt_double(info, 7, 0.0);
        double beta = opt_double(info, 8, 0.0);
        const std::size_t nt = t.size();
        const std::size_t nM = Mvals.size();
        auto out = MultisectorFitterV2::evaluateMultisectorAbsBatchM(
            t.data(), nt, s.data(), s.size(), th.data(), wptr,
            ell_trefoil, Mvals.data(), nM, completion_mode, alpha, beta);
        Napi::Array rows = Napi::Array::New(info.Env(), nM);
        for (std::size_t iM = 0; iM < nM; ++iM) {
            Napi::Float64Array row = Napi::Float64Array::New(info.Env(), nt);
            for (std::size_t j = 0; j < nt; ++j) {
                row[j] = out[iM * nt + j];
            }
            rows.Set(static_cast<uint32_t>(iM), row);
        }
        return rows;
    }
    static Napi::Value ObjectiveNearNodes(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        auto opts = make_eval_opts(ell_trefoil, truncation_M, opt_int(info, 6, 0),
                                   opt_double(info, 7, 0.0), opt_double(info, 8, 0.0));
        std::vector<double> target_nodes = read_doubles(info[9]);
        std::vector<double> node_weights;
        const double* nwptr = read_optional_doubles(info, 10, node_weights) ? node_weights.data() : nullptr;
        double val = MultisectorFitterV2::objectiveNearNodes(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr, opts,
            target_nodes.data(), target_nodes.size(), nwptr);
        return Napi::Number::New(info.Env(), val);
    }
    static Napi::Value ObjectiveSuppressed(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        auto opts = make_eval_opts(ell_trefoil, truncation_M, opt_int(info, 6, 0),
                                   opt_double(info, 7, 0.0), opt_double(info, 8, 0.0));
        std::vector<double> target_nodes = read_doubles(info[9]);
        std::vector<double> node_weights;
        const double* nwptr = read_optional_doubles(info, 10, node_weights) ? node_weights.data() : nullptr;
        auto sopts = make_supp_opts(opt_double(info, 11, 0.5), opt_double(info, 12, 0.05),
                                    opt_double(info, 13, 0.01), opt_double(info, 14, 0.35),
                                    opt_bool(info, 15, true));
        double val = MultisectorFitterV2::objectiveSuppressed(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr, opts,
            target_nodes.data(), target_nodes.size(), nwptr, sopts);
        return Napi::Number::New(info.Env(), val);
    }
    static Napi::Value ObjectiveSuppressedBreakdown(const Napi::CallbackInfo& info) {
        std::vector<double> t = read_doubles(info[0]);
        std::vector<int> s = read_ints(info[1]);
        std::vector<double> th = read_doubles(info[2]);
        std::vector<double> weights;
        const double* wptr = read_optional_doubles(info, 3, weights) ? weights.data() : nullptr;
        double ell_trefoil = info[4].As<Napi::Number>().DoubleValue();
        std::size_t truncation_M = size_arg(info, 5);
        auto opts = make_eval_opts(ell_trefoil, truncation_M, opt_int(info, 6, 0),
                                   opt_double(info, 7, 0.0), opt_double(info, 8, 0.0));
        std::vector<double> target_nodes = read_doubles(info[9]);
        std::vector<double> node_weights;
        const double* nwptr = read_optional_doubles(info, 10, node_weights) ? node_weights.data() : nullptr;
        auto sopts = make_supp_opts(opt_double(info, 11, 0.5), opt_double(info, 12, 0.05),
                                    opt_double(info, 13, 0.01), opt_double(info, 14, 0.35),
                                    opt_bool(info, 15, true));
        auto br = MultisectorFitterV2::objectiveSuppressedBreakdown(
            t.data(), t.size(), s.data(), s.size(), th.data(), wptr, opts,
            target_nodes.data(), target_nodes.size(), nwptr, sopts);
        Napi::Object o = Napi::Object::New(info.Env());
        o.Set("total", Napi::Number::New(info.Env(), br.total));
        o.Set("mismatch", Napi::Number::New(info.Env(), br.mismatch));
        o.Set("extra_penalty", Napi::Number::New(info.Env(), br.extra_penalty));
        o.Set("reg_penalty", Napi::Number::New(info.Env(), br.reg_penalty));
        return o;
    }
    static Napi::Value PhaseInvariants(const Napi::CallbackInfo& info) {
        std::vector<double> th = read_doubles(info[0]);
        auto inv = MultisectorFitterV2::phaseInvariants(th.data(), th.size());
        Napi::Object o = Napi::Object::New(info.Env());
        o.Set("delta23", Napi::Number::New(info.Env(), std::get<0>(inv)));
        o.Set("delta35", Napi::Number::New(info.Env(), std::get<1>(inv)));
        o.Set("theta_sum_mod", Napi::Number::New(info.Env(), std::get<2>(inv)));
        return o;
    }
};

} // namespace

void bind_multisector_fitter(Napi::Env env, Napi::Object exports) {
    MultisectorFitterWrap::Init(env, exports);
    NodeAnalyzerWrap::Init(env, exports);
    TraceFormulaWrap::Init(env, exports);
    MultisectorFitterV2Wrap::Init(env, exports);
    exports.Set("multisectorFitterAvailable", Napi::Boolean::New(env, true));
}
