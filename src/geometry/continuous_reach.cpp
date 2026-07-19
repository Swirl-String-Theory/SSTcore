#include "geometry/continuous_reach.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <limits>
#include <utility>
#include <vector>

namespace sst {
namespace geometry {
namespace {

double wrap01(double u, double L) {
    if (!(L > 0.0)) return 0.0;
    u = std::fmod(u, L);
    if (u < 0.0) u += L;
    return u;
}

double curvature(const SplineEval& ev) {
    const Vec3 c = cross(ev.d1, ev.d2);
    const double speed = norm(ev.d1);
    return speed > 1e-20 ? norm(c) / (speed * speed * speed) : 0.0;
}

struct GoldenResult {
    double x = 0.0;
    double value = 0.0;
};

GoldenResult golden_max(const PeriodicCubicSpline3D& sp, double a, double b, int it = 42) {
    const double gr = (std::sqrt(5.0) - 1.0) / 2.0;
    double c = b - gr * (b - a);
    double d = a + gr * (b - a);
    double fc = curvature(sp.eval(c));
    double fd = curvature(sp.eval(d));
    for (int k = 0; k < it; ++k) {
        if (fc > fd) {
            b = d;
            d = c;
            fd = fc;
            c = b - gr * (b - a);
            fc = curvature(sp.eval(c));
        } else {
            a = c;
            c = d;
            fc = fd;
            d = a + gr * (b - a);
            fd = curvature(sp.eval(d));
        }
    }
    GoldenResult g;
    if (fc > fd) {
        g.x = c;
        g.value = fc;
    } else {
        g.x = d;
        g.value = fd;
    }
    return g;
}

struct CurvLimit {
    double radius = std::numeric_limits<double>::infinity();
    double kappa = 0.0;
    double s = 0.0;
};

CurvLimit continuous_curvature_limit(const PeriodicCubicSpline3D& spline) {
    const std::size_t n = spline.n();
    constexpr int per = 6;
    GoldenResult best;
    best.value = -1.0;
    for (std::size_t i = 0; i < n; ++i) {
        const double a = spline.parameter_at(i);
        const double b = spline.parameter_at(i + 1);
        const double hh = (b - a) / static_cast<double>(per);
        double best_v = -1.0;
        int bk = 0;
        for (int k = 0; k <= per; ++k) {
            const double u = a + k * hh;
            const double v = curvature(spline.eval(u));
            if (v > best_v) {
                best_v = v;
                bk = k;
            }
        }
        const double la = std::max(a, a + (bk - 1) * hh);
        const double lb = std::min(b, a + (bk + 1) * hh);
        const GoldenResult g = golden_max(spline, la, lb);
        if (g.value > best.value) best = g;
    }
    CurvLimit out;
    out.kappa = best.value;
    out.s = best.x;
    out.radius = best.value > 1e-20 ? 1.0 / best.value : std::numeric_limits<double>::infinity();
    return out;
}

struct PairMetrics {
    SplineEval A, B;
    double dx = 0, dy = 0, dz = 0, d = 0, F1 = 0, F2 = 0;
};

PairMetrics pair_metrics(const PeriodicCubicSpline3D& sa, const PeriodicCubicSpline3D& sb,
                         double s, double t) {
    PairMetrics m;
    m.A = sa.eval(s);
    m.B = sb.eval(t);
    m.dx = m.A.p[0] - m.B.p[0];
    m.dy = m.A.p[1] - m.B.p[1];
    m.dz = m.A.p[2] - m.B.p[2];
    m.d = std::sqrt(m.dx * m.dx + m.dy * m.dy + m.dz * m.dz);
    m.F1 = m.dx * m.A.d1[0] + m.dy * m.A.d1[1] + m.dz * m.A.d1[2];
    m.F2 = m.dx * m.B.d1[0] + m.dy * m.B.d1[1] + m.dz * m.B.d1[2];
    return m;
}

struct RefineResult {
    double s = 0, t = 0, distance = 0, orth_residual = 0;
    bool local_min = false;
    double hss = 0, htt = 0, hst = 0, hessian_det = 0;
    Vec3 p{{0, 0, 0}}, q{{0, 0, 0}};
    bool used_damped_least_squares = false;
};

RefineResult refine_pair(const PeriodicCubicSpline3D& sa, const PeriodicCubicSpline3D& sb,
                         double s0, double t0, bool self_pair) {
    double s = wrap01(s0, sa.length());
    double t = wrap01(t0, sb.length());
    bool used_dls = false;
    const double min_arc = self_pair
        ? std::max(4.0 * sa.length() / static_cast<double>(sa.n()), 0.015 * sa.length())
        : 0.0;

    auto residual = [](const PairMetrics& m) {
        const double d = m.d > 0.0 ? m.d : 1e-30;
        const double scale = std::max({d * norm(m.A.d1), d * norm(m.B.d1), 1e-30});
        return std::max(std::abs(m.F1), std::abs(m.F2)) / scale;
    };
    auto arc_valid = [&](double ns, double nt) {
        if (!self_pair) return true;
        const double arc = std::min(std::abs(ns - nt), sa.length() - std::abs(ns - nt));
        return arc >= min_arc;
    };

    for (int it = 0; it < 64; ++it) {
        const PairMetrics m = pair_metrics(sa, sb, s, t);
        const double res = residual(m);
        if (res < 1e-13) break;

        const Vec3& ap = m.A.d1;
        const Vec3& bp = m.B.d1;
        const Vec3& app = m.A.d2;
        const Vec3& bpp = m.B.d2;
        const double j11 = ap[0] * ap[0] + ap[1] * ap[1] + ap[2] * ap[2]
                           + m.dx * app[0] + m.dy * app[1] + m.dz * app[2];
        const double j12 = -(ap[0] * bp[0] + ap[1] * bp[1] + ap[2] * bp[2]);
        const double j21 = -j12;
        const double j22 = -(bp[0] * bp[0] + bp[1] * bp[1] + bp[2] * bp[2])
                           + m.dx * bpp[0] + m.dy * bpp[1] + m.dz * bpp[2];
        const double det = j11 * j22 - j12 * j21;
        const double frob2 = j11 * j11 + j12 * j12 + j21 * j21 + j22 * j22;

        struct Cand { double ds, dt; const char* kind; };
        std::vector<Cand> candidates;
        if (std::abs(det) > 1e-12 * std::max(frob2, 1e-30)) {
            candidates.push_back({
                (-m.F1 * j22 + j12 * m.F2) / det,
                (-j11 * m.F2 + j21 * m.F1) / det,
                "newton"
            });
        }
        for (double factor : {1e-16, 1e-14, 1e-12, 1e-10, 1e-8}) {
            const double lam = std::max(1e-30, factor * std::max(frob2, 1e-30));
            const double a11 = j11 * j11 + j21 * j21 + lam;
            const double a12 = j11 * j12 + j21 * j22;
            const double a22 = j12 * j12 + j22 * j22 + lam;
            const double b1 = -(j11 * m.F1 + j21 * m.F2);
            const double b2 = -(j12 * m.F1 + j22 * m.F2);
            const double dd = a11 * a22 - a12 * a12;
            if (std::abs(dd) > 1e-40) {
                candidates.push_back({
                    (b1 * a22 - a12 * b2) / dd,
                    (a11 * b2 - a12 * b1) / dd,
                    "dls"
                });
            }
        }

        struct Best { double s, t, rr; const char* kind; };
        Best best{};
        bool have = false;
        for (Cand candidate : candidates) {
            double ds = candidate.ds, dt = candidate.dt;
            if (!std::isfinite(ds) || !std::isfinite(dt)) continue;
            const double cap = 0.08 * std::min(sa.length(), sb.length());
            const double mag = std::hypot(ds, dt);
            if (mag > cap) {
                ds *= cap / mag;
                dt *= cap / mag;
            }
            for (int q = 0; q < 14; ++q) {
                const double f = std::pow(2.0, -q);
                const double ns = wrap01(s + f * ds, sa.length());
                const double nt = wrap01(t + f * dt, sb.length());
                if (!arc_valid(ns, nt)) continue;
                const PairMetrics mm = pair_metrics(sa, sb, ns, nt);
                const double rr = residual(mm);
                if (!have || rr < best.rr) {
                    best = {ns, nt, rr, candidate.kind};
                    have = true;
                }
            }
        }
        if (!have || best.rr >= res * (1.0 - 1e-10)) break;
        s = best.s;
        t = best.t;
        if (best.kind && std::strcmp(best.kind, "dls") == 0) used_dls = true;
    }

    const PairMetrics m = pair_metrics(sa, sb, s, t);
    const double d = m.d > 0.0 ? m.d : 1e-30;
    const double sa1 = norm(m.A.d1);
    const double sb1 = norm(m.B.d1);
    const double orth = std::max(
        std::abs(m.F1) / (d * sa1 + 1e-30),
        std::abs(m.F2) / (d * sb1 + 1e-30));
    const double hss = m.A.d1[0] * m.A.d1[0] + m.A.d1[1] * m.A.d1[1] + m.A.d1[2] * m.A.d1[2]
                       + m.dx * m.A.d2[0] + m.dy * m.A.d2[1] + m.dz * m.A.d2[2];
    const double htt = m.B.d1[0] * m.B.d1[0] + m.B.d1[1] * m.B.d1[1] + m.B.d1[2] * m.B.d1[2]
                       - m.dx * m.B.d2[0] - m.dy * m.B.d2[1] - m.dz * m.B.d2[2];
    const double hst = -(m.A.d1[0] * m.B.d1[0] + m.A.d1[1] * m.B.d1[1] + m.A.d1[2] * m.B.d1[2]);
    const double hdet = hss * htt - hst * hst;
    const bool local_min = hss > -1e-10 && htt > -1e-10
                           && hdet > -1e-8 * std::max(1.0, std::abs(hss * htt));

    RefineResult r;
    r.s = s;
    r.t = t;
    r.distance = m.d;
    r.orth_residual = orth;
    r.local_min = local_min;
    r.hss = hss;
    r.htt = htt;
    r.hst = hst;
    r.hessian_det = hdet;
    r.p = m.A.p;
    r.q = m.B.p;
    r.used_damped_least_squares = used_dls;
    return r;
}

struct Seed {
    double s, t, score, orth, d;
};

bool continuous_pair_distance(const PeriodicCubicSpline3D& sa, const PeriodicCubicSpline3D& sb,
                              bool self_pair, RefineResult& out) {
    const int M = std::min(192, std::max(64, static_cast<int>(std::round(
        10.0 * std::sqrt(static_cast<double>(std::max(sa.n(), sb.n())))))));
    const double min_arc = self_pair
        ? std::max(4.0 * sa.length() / static_cast<double>(sa.n()), 0.015 * sa.length())
        : 0.0;
    std::vector<Seed> seeds;
    for (int i = 0; i < M; ++i) {
        const double s = sa.length() * i / static_cast<double>(M);
        const SplineEval A = sa.eval(s);
        for (int j = self_pair ? i + 1 : 0; j < M; ++j) {
            const double t = sb.length() * j / static_cast<double>(M);
            if (self_pair) {
                const double arc = std::min(std::abs(s - t), sa.length() - std::abs(s - t));
                if (arc < min_arc) continue;
            }
            const SplineEval B = sb.eval(t);
            const double dx = A.p[0] - B.p[0], dy = A.p[1] - B.p[1], dz = A.p[2] - B.p[2];
            const double d = std::sqrt(dx * dx + dy * dy + dz * dz);
            if (!(d > 1e-12)) continue;
            const double ci = std::abs((dx * A.d1[0] + dy * A.d1[1] + dz * A.d1[2])
                                       / (d * norm(A.d1) + 1e-30));
            const double cj = std::abs((dx * B.d1[0] + dy * B.d1[1] + dz * B.d1[2])
                                       / (d * norm(B.d1) + 1e-30));
            if (ci > 0.92 || cj > 0.92) continue;
            seeds.push_back({s, t, d * (0.02 + ci * ci + cj * cj), ci + cj, d});
        }
    }

    auto take_unique = [&](std::vector<Seed> arr, std::size_t count, auto cmp) {
        std::sort(arr.begin(), arr.end(), cmp);
        if (arr.size() > count) arr.resize(count);
        return arr;
    };
    std::vector<Seed> chosen;
    auto push_unique = [&](const std::vector<Seed>& arr) {
        for (const Seed& q : arr) {
            bool found = false;
            for (const Seed& c : chosen) {
                if (c.s == q.s && c.t == q.t) {
                    found = true;
                    break;
                }
            }
            if (!found) chosen.push_back(q);
        }
    };
    push_unique(take_unique(seeds, 64, [](const Seed& a, const Seed& b) { return a.score < b.score; }));
    push_unique(take_unique(seeds, 48, [](const Seed& a, const Seed& b) { return a.orth < b.orth; }));
    push_unique(take_unique(seeds, 32, [](const Seed& a, const Seed& b) { return a.d < b.d; }));

    std::vector<RefineResult> refined;
    for (const Seed& seed : chosen) {
        RefineResult r = refine_pair(sa, sb, seed.s, seed.t, self_pair);
        if (!std::isfinite(r.distance) || r.orth_residual >= 5e-9) continue;
        if (self_pair) {
            const double arc = std::min(std::abs(r.s - r.t), sa.length() - std::abs(r.s - r.t));
            if (arc < min_arc) continue;
        }
        bool dup = false;
        for (const RefineResult& x : refined) {
            if (std::abs(x.distance - r.distance) < 1e-8 * std::max(1.0, r.distance)
                && std::min(std::abs(x.s - r.s), sa.length() - std::abs(x.s - r.s)) < 1e-5 * sa.length()
                && std::min(std::abs(x.t - r.t), sb.length() - std::abs(x.t - r.t)) < 1e-5 * sb.length()) {
                dup = true;
                break;
            }
        }
        if (!dup) refined.push_back(r);
    }
    if (refined.empty()) return false;
    std::sort(refined.begin(), refined.end(),
              [](const RefineResult& a, const RefineResult& b) { return a.distance < b.distance; });
    out = refined[0];
    return true;
}

PairWitness to_witness(const RefineResult& r, std::size_t ca, std::size_t cb) {
    PairWitness w;
    w.component_a = ca;
    w.component_b = cb;
    w.s = r.s;
    w.t = r.t;
    w.p = r.p;
    w.q = r.q;
    w.distance = r.distance;
    w.orthogonality_residual = r.orth_residual;
    w.local_minimum = r.local_min;
    w.hss = r.hss;
    w.htt = r.htt;
    w.hst = r.hst;
    w.hessian_det = r.hessian_det;
    w.used_damped_least_squares = r.used_damped_least_squares;
    return w;
}

}  // namespace

ContinuousReachResult ContinuousReachSolver::compute(
    const std::vector<PeriodicCubicSpline3D>& splines) {
    ContinuousReachResult out;
    out.component_count = splines.size();
    if (splines.empty()) {
        out.limiter = ReachLimiter::Error;
        return out;
    }

    std::vector<CurvLimit> curv;
    curv.reserve(splines.size());
    for (const auto& sp : splines) curv.push_back(continuous_curvature_limit(sp));

    std::vector<RefineResult> self_res(splines.size());
    std::vector<bool> self_ok(splines.size(), false);
    for (std::size_t i = 0; i < splines.size(); ++i) {
        self_ok[i] = continuous_pair_distance(splines[i], splines[i], true, self_res[i]);
    }

    struct InterHit {
        RefineResult r;
        std::size_t i, j;
    };
    std::vector<InterHit> inter;
    for (std::size_t i = 0; i < splines.size(); ++i) {
        for (std::size_t j = i + 1; j < splines.size(); ++j) {
            RefineResult r;
            if (continuous_pair_distance(splines[i], splines[j], false, r)) {
                inter.push_back({r, i, j});
            }
        }
    }

    std::size_t c_best_i = 0;
    for (std::size_t i = 1; i < curv.size(); ++i) {
        if (curv[i].radius < curv[c_best_i].radius) c_best_i = i;
    }
    out.curvature_radius = curv[c_best_i].radius;

    int s_best = -1;
    for (std::size_t i = 0; i < self_res.size(); ++i) {
        if (!self_ok[i]) continue;
        if (s_best < 0 || self_res[i].distance < self_res[static_cast<std::size_t>(s_best)].distance) {
            s_best = static_cast<int>(i);
        }
    }
    if (s_best >= 0) {
        out.self_dcsd = self_res[static_cast<std::size_t>(s_best)].distance;
        out.self_radius = out.self_dcsd / 2.0;
        out.self_witness = to_witness(self_res[static_cast<std::size_t>(s_best)],
                                      static_cast<std::size_t>(s_best),
                                      static_cast<std::size_t>(s_best));
    } else {
        out.self_dcsd = std::numeric_limits<double>::infinity();
        out.self_radius = std::numeric_limits<double>::infinity();
    }

    int i_best = -1;
    for (std::size_t k = 0; k < inter.size(); ++k) {
        if (i_best < 0 || inter[k].r.distance < inter[static_cast<std::size_t>(i_best)].r.distance) {
            i_best = static_cast<int>(k);
        }
    }
    if (i_best >= 0) {
        out.inter_component_distance = inter[static_cast<std::size_t>(i_best)].r.distance;
        out.inter_component_radius = out.inter_component_distance / 2.0;
        out.inter_witness = to_witness(inter[static_cast<std::size_t>(i_best)].r,
                                       inter[static_cast<std::size_t>(i_best)].i,
                                       inter[static_cast<std::size_t>(i_best)].j);
    } else {
        out.inter_component_distance = std::numeric_limits<double>::infinity();
        out.inter_component_radius = std::numeric_limits<double>::infinity();
    }

    struct Cand {
        ReachLimiter type;
        double value;
    };
    std::vector<Cand> vals = {
        {ReachLimiter::Curvature, out.curvature_radius},
        {ReachLimiter::SelfDcsd, out.self_radius},
        {ReachLimiter::InterComponent, out.inter_component_radius},
    };
    std::sort(vals.begin(), vals.end(),
              [](const Cand& a, const Cand& b) { return a.value < b.value; });
    out.reach = vals[0].value;
    int near = 0;
    for (const Cand& v : vals) {
        if (std::isfinite(v.value)
            && std::abs(v.value - out.reach) <= 1e-5 * std::max(1.0, std::abs(out.reach))) {
            ++near;
        }
    }
    out.limiter = near > 1 ? ReachLimiter::Tie : vals[0].type;

    out.orth_residual = 0.0;
    for (std::size_t i = 0; i < self_res.size(); ++i) {
        if (self_ok[i]) out.orth_residual = std::max(out.orth_residual, self_res[i].orth_residual);
    }
    for (const InterHit& h : inter) {
        out.orth_residual = std::max(out.orth_residual, h.r.orth_residual);
    }
    return out;
}

ContinuousReachResult ContinuousReachSolver::compute(
    const std::vector<std::vector<Vec3>>& components) {
    std::vector<PeriodicCubicSpline3D> splines;
    splines.reserve(components.size());
    for (const auto& c : components) {
        splines.emplace_back(c);
    }
    return compute(splines);
}

}  // namespace geometry
}  // namespace sst
