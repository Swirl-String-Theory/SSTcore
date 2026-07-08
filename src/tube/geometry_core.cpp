#include "sst/tube/geometry_core.h"
#include "sst/tube/detail/common.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

using namespace sst::tube::detail;

namespace sst {

double ResolvedTubeGeometry::length(const std::vector<Vec3>& pts) {
    if (pts.size() < 2) return 0.0;
    double L = 0.0;
    for (std::size_t i = 0; i < pts.size(); ++i) {
        L += dist(pts[i], pts[(i + 1) % pts.size()]);
    }
    return L;
}

double ResolvedTubeGeometry::edge_length_mean(const std::vector<Vec3>& pts) {
    if (pts.size() < 2) return 0.0;
    return length(pts) / static_cast<double>(pts.size());
}

double ResolvedTubeGeometry::edge_length_relative_std(const std::vector<Vec3>& pts) {
    if (pts.size() < 2) return 0.0;
    const double mean = edge_length_mean(pts);
    if (mean <= 0.0) return 0.0;
    double acc = 0.0;
    for (std::size_t i = 0; i < pts.size(); ++i) {
        const double e = dist(pts[i], pts[(i + 1) % pts.size()]);
        const double d = e - mean;
        acc += d * d;
    }
    return std::sqrt(acc / static_cast<double>(pts.size())) / mean;
}

double ResolvedTubeGeometry::turning_angle(const Vec3& a, const Vec3& b, const Vec3& c) {
    const Vec3 u = sub(b, a);
    const Vec3 v = sub(c, b);
    const double nu = norm(u);
    const double nv = norm(v);
    if (nu <= eps_d || nv <= eps_d) return 0.0;
    return std::acos(clamp(dot(u, v) / (nu * nv), -1.0, 1.0));
}

double ResolvedTubeGeometry::minrad_at_vertex(const std::vector<Vec3>& pts, std::size_t i) {
    if (pts.size() < 3) return 0.0;
    const std::size_t n = pts.size();
    const Vec3& prev = pts[wrap_index(static_cast<long long>(i) - 1, n)];
    const Vec3& cur = pts[i % n];
    const Vec3& next = pts[(i + 1) % n];
    const double e_prev = dist(prev, cur);
    const double e_next = dist(cur, next);
    const double theta = turning_angle(prev, cur, next);
    if (e_prev <= eps_d || e_next <= eps_d) return 0.0;
    if (theta <= eps_d) return std::numeric_limits<double>::infinity();
    const double denom = 2.0 * std::tan(0.5 * theta);
    if (std::abs(denom) <= eps_d) return std::numeric_limits<double>::infinity();
    return std::min(e_prev, e_next) / denom;
}

KinkRecord ResolvedTubeGeometry::kink_at_vertex(const std::vector<Vec3>& pts, std::size_t i) {
    if (pts.size() < 3) throw std::invalid_argument("kink_at_vertex requires at least 3 points.");
    const std::size_t n = pts.size();
    const Vec3& prev = pts[wrap_index(static_cast<long long>(i) - 1, n)];
    const Vec3& cur = pts[i % n];
    const Vec3& next = pts[(i + 1) % n];
    const double e_prev = dist(prev, cur);
    const double e_next = dist(cur, next);
    const double theta = turning_angle(prev, cur, next);
    KinkRecord out;
    out.vertex = i % n;
    out.turning_angle = theta;
    if (theta <= eps_d) {
        out.minrad_minus = std::numeric_limits<double>::infinity();
        out.minrad_plus = std::numeric_limits<double>::infinity();
        out.minrad = std::numeric_limits<double>::infinity();
        return out;
    }
    const double denom = 2.0 * std::tan(0.5 * theta);
    out.minrad_minus = (e_prev <= eps_d || std::abs(denom) <= eps_d) ? 0.0 : e_prev / denom;
    out.minrad_plus = (e_next <= eps_d || std::abs(denom) <= eps_d) ? 0.0 : e_next / denom;
    out.minrad = std::min(out.minrad_minus, out.minrad_plus);
    return out;
}

double ResolvedTubeGeometry::global_minrad(const std::vector<Vec3>& pts) {
    if (pts.size() < 3) return 0.0;
    double mr = std::numeric_limits<double>::infinity();
    for (std::size_t i = 0; i < pts.size(); ++i) {
        mr = std::min(mr, minrad_at_vertex(pts, i));
    }
    return mr;
}

double ResolvedTubeGeometry::segment_segment_distance(
    const Vec3& p0, const Vec3& p1,
    const Vec3& q0, const Vec3& q1,
    double* s_out,
    double* t_out) {

    const Vec3 u = sub(p1, p0);
    const Vec3 v = sub(q1, q0);
    const Vec3 w = sub(p0, q0);
    const double a = dot(u, u);
    const double b = dot(u, v);
    const double c = dot(v, v);
    const double d = dot(u, w);
    const double e = dot(v, w);
    const double D = a * c - b * b;

    double sN, sD = D;
    double tN, tD = D;

    if (a <= eps_d && c <= eps_d) {
        if (s_out) *s_out = 0.0;
        if (t_out) *t_out = 0.0;
        return dist(p0, q0);
    }
    if (a <= eps_d) {
        const double t = clamp01(e / c);
        if (s_out) *s_out = 0.0;
        if (t_out) *t_out = t;
        return dist(p0, add(q0, mul(v, t)));
    }
    if (c <= eps_d) {
        const double s = clamp01(-d / a);
        if (s_out) *s_out = s;
        if (t_out) *t_out = 0.0;
        return dist(add(p0, mul(u, s)), q0);
    }

    if (D < eps_d) {
        sN = 0.0;
        sD = 1.0;
        tN = e;
        tD = c;
    } else {
        sN = (b * e - c * d);
        tN = (a * e - b * d);
        if (sN < 0.0) {
            sN = 0.0;
            tN = e;
            tD = c;
        } else if (sN > sD) {
            sN = sD;
            tN = e + b;
            tD = c;
        }
    }

    if (tN < 0.0) {
        tN = 0.0;
        if (-d < 0.0) sN = 0.0;
        else if (-d > a) sN = sD;
        else { sN = -d; sD = a; }
    } else if (tN > tD) {
        tN = tD;
        if ((-d + b) < 0.0) sN = 0.0;
        else if ((-d + b) > a) sN = sD;
        else { sN = (-d + b); sD = a; }
    }

    const double s = (std::abs(sN) < eps_d ? 0.0 : sN / sD);
    const double t = (std::abs(tN) < eps_d ? 0.0 : tN / tD);
    if (s_out) *s_out = clamp01(s);
    if (t_out) *t_out = clamp01(t);
    const Vec3 cp = add(p0, mul(u, clamp01(s)));
    const Vec3 cq = add(q0, mul(v, clamp01(t)));
    return dist(cp, cq);
}

std::vector<SegmentPair> ResolvedTubeGeometry::dcsd_candidates(
    const std::vector<Vec3>& pts,
    int skip_neighbors,
    double distance_tol) {
    std::vector<SegmentPair> out;
    const std::size_t n = pts.size();
    if (n < 4) return out;
    if (skip_neighbors < 0) skip_neighbors = 0;

    const auto cum = cumulative_lengths(pts);
    double best = std::numeric_limits<double>::infinity();
    std::vector<SegmentPair> all;

    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = i + 1; j < n; ++j) {
            if (cyclic_edge_distance(i, j, n) <= skip_neighbors) continue;
            double s = 0.0, t = 0.0;
            const double d = segment_segment_distance(pts[i], pts[(i + 1) % n],
                                                      pts[j], pts[(j + 1) % n],
                                                      &s, &t);
            SegmentPair pair;
            pair.i = i;
            pair.j = j;
            pair.s = s;
            pair.t = t;
            pair.distance = d;
            pair.arclength_i = cum[i] + s * dist(pts[i], pts[(i + 1) % n]);
            pair.arclength_j = cum[j] + t * dist(pts[j], pts[(j + 1) % n]);
            all.push_back(pair);
            best = std::min(best, d);
        }
    }

    if (all.empty()) return out;
    const double tol = std::max(0.0, distance_tol);
    for (const auto& pair : all) {
        if (tol <= 0.0) {
            if (pair.distance <= best + 1e-12) out.push_back(pair);
        } else if (pair.distance <= best * (1.0 + tol) + tol) {
            out.push_back(pair);
        }
    }
    return out;
}

ResolvedTubeMetrics ResolvedTubeGeometry::analyze(
    const std::vector<Vec3>& pts,
    int skip_neighbors,
    double contact_tol,
    double equilateral_tol) {
    if (pts.size() < 3) throw std::invalid_argument("analyze requires at least 3 points.");
    if (contact_tol < 0.0) throw std::invalid_argument("contact_tol must be non-negative.");
    if (equilateral_tol < 0.0) throw std::invalid_argument("equilateral_tol must be non-negative.");

    ResolvedTubeMetrics out;
    out.length = length(pts);
    out.edge_length_mean = edge_length_mean(pts);
    out.edge_length_rel_std = edge_length_relative_std(pts);
    out.equilateral_ok = out.edge_length_rel_std <= equilateral_tol;
    out.minrad = global_minrad(pts);

    const auto candidates = dcsd_candidates(pts, skip_neighbors, 0.0);
    if (!candidates.empty()) {
        out.min_dcsd = candidates.front().distance;
        for (const auto& c : candidates) out.min_dcsd = std::min(out.min_dcsd, c.distance);
    } else {
        out.min_dcsd = std::numeric_limits<double>::infinity();
    }
    out.half_min_dcsd = 0.5 * out.min_dcsd;
    out.thickness_rad = std::min(out.minrad, out.half_min_dcsd);
    out.reach_rad = out.thickness_rad;

    if (out.thickness_rad > 0.0 && std::isfinite(out.thickness_rad)) {
        out.ropelength_rad = out.length / out.thickness_rad;
        out.ropelength_diam = radius_to_diameter_ropelength(out.ropelength_rad);
    }
    out.lower_bound_ok = !(out.ropelength_rad > 0.0) ||
                         (out.ropelength_rad + 1e-9 >= nontrivial_knot_lower_bound_rad());

    const double contact_radius = std::isfinite(out.thickness_rad) ? out.thickness_rad : 0.0;
    if (contact_radius > 0.0) {
        const auto strut_candidates = dcsd_candidates(pts, skip_neighbors, contact_tol);
        for (const auto& c : strut_candidates) {
            if (0.5 * c.distance <= contact_radius * (1.0 + contact_tol) + contact_tol) {
                out.struts.push_back(c);
            }
        }
        for (std::size_t i = 0; i < pts.size(); ++i) {
            const auto k = kink_at_vertex(pts, i);
            if (k.minrad <= contact_radius * (1.0 + contact_tol) + contact_tol) {
                out.kinks.push_back(k);
            }
        }
    }
    return out;
}


std::vector<double> ResolvedTubeGeometry::length_gradient_flat(const std::vector<Vec3>& pts) {
    const std::size_t n = pts.size();
    std::vector<double> grad(3 * n, 0.0);
    if (n < 2) return grad;
    for (std::size_t i = 0; i < n; ++i) {
        const Vec3& prev = pts[wrap_index(static_cast<long long>(i) - 1, n)];
        const Vec3& cur = pts[i];
        const Vec3& next = pts[(i + 1) % n];
        const Vec3 a = sub(cur, prev);
        const Vec3 b = sub(cur, next);
        const double na = norm(a);
        const double nb = norm(b);
        Vec3 g{0.0, 0.0, 0.0};
        if (na > eps_d) g = add(g, mul(a, 1.0 / na));
        if (nb > eps_d) g = add(g, mul(b, 1.0 / nb));
        add_to_flat(grad, i, g);
    }
    return grad;
}

std::vector<double> ResolvedTubeGeometry::strut_gradient_flat(
    const std::vector<Vec3>& pts,
    const SegmentPair& pair) {
    const std::size_t n = pts.size();
    std::vector<double> grad(3 * n, 0.0);
    if (n < 2) return grad;
    const std::size_t i0 = pair.i % n;
    const std::size_t i1 = (pair.i + 1) % n;
    const std::size_t j0 = pair.j % n;
    const std::size_t j1 = (pair.j + 1) % n;
    const double s = clamp01(pair.s);
    const double t = clamp01(pair.t);
    const Vec3 pnt = add(pts[i0], mul(sub(pts[i1], pts[i0]), s));
    const Vec3 qnt = add(pts[j0], mul(sub(pts[j1], pts[j0]), t));
    const Vec3 pq = sub(pnt, qnt);
    const double d = norm(pq);
    if (d <= eps_d) return grad;
    const Vec3 u = mul(pq, 1.0 / (2.0 * d)); // gradient of d(p,q)/2 with respect to p
    add_to_flat(grad, i0, mul(u, 1.0 - s));
    add_to_flat(grad, i1, mul(u, s));
    add_to_flat(grad, j0, mul(u, -(1.0 - t)));
    add_to_flat(grad, j1, mul(u, -t));
    return grad;
}

std::vector<double> ResolvedTubeGeometry::kink_minrad_plus_gradient_flat(
    const std::vector<Vec3>& pts,
    const KinkRecord& kink) {
    const std::size_t npts = pts.size();
    std::vector<double> grad(3 * npts, 0.0);
    if (npts < 3) return grad;

    const std::size_t im = wrap_index(static_cast<long long>(kink.vertex) - 1, npts);
    const std::size_t i0 = kink.vertex % npts;
    const std::size_t ip = (kink.vertex + 1) % npts;
    const Vec3 A = sub(pts[im], pts[i0]);
    const Vec3 B = sub(pts[ip], pts[i0]);
    const double a = norm(A);
    const double b = norm(B);
    const double theta = kink.turning_angle;
    if (a <= eps_d || b <= eps_d || theta <= eps_d || !std::isfinite(theta)) return grad;

    Vec3 nvec = cross(B, A);
    const double nn = norm(nvec);
    if (nn <= eps_d) return grad;
    nvec = mul(nvec, 1.0 / nn);

    const double denom = 2.0 * std::cos(theta) - 2.0;
    const double tan_half = std::tan(0.5 * theta);
    if (std::abs(denom) <= eps_d || std::abs(tan_half) <= eps_d) return grad;

    const double K = b / denom;
    const Vec3 V = mul(B, 1.0 / (2.0 * tan_half * b));
    const Vec3 W = mul(cross(A, nvec), K / (a * a));
    const Vec3 X = mul(cross(nvec, B), K / (b * b));

    add_to_flat(grad, im, W);
    add_to_flat(grad, i0, sub(mul(add(W, X), -1.0), V));
    add_to_flat(grad, ip, add(X, V));
    return grad;
}

std::vector<double> ResolvedTubeGeometry::kink_minrad_minus_gradient_flat(
    const std::vector<Vec3>& pts,
    const KinkRecord& kink) {
    const std::size_t npts = pts.size();
    std::vector<double> grad(3 * npts, 0.0);
    if (npts < 3) return grad;

    const std::size_t im = wrap_index(static_cast<long long>(kink.vertex) - 1, npts);
    const std::size_t i0 = kink.vertex % npts;
    const std::size_t ip = (kink.vertex + 1) % npts;
    std::vector<Vec3> local = {pts[ip], pts[i0], pts[im]};
    KinkRecord local_kink;
    local_kink.vertex = 1;
    local_kink.turning_angle = kink.turning_angle;
    local_kink.minrad_plus = kink.minrad_minus;
    local_kink.minrad = kink.minrad_minus;
    const auto g = kink_minrad_plus_gradient_flat(local, local_kink);
    if (g.size() != 9) return grad;
    add_to_flat(grad, ip, Vec3{g[0], g[1], g[2]});
    add_to_flat(grad, i0, Vec3{g[3], g[4], g[5]});
    add_to_flat(grad, im, Vec3{g[6], g[7], g[8]});
    return grad;
}

std::vector<double> ResolvedTubeGeometry::kink_minrad_gradient_flat(
    const std::vector<Vec3>& pts,
    const KinkRecord& kink,
    bool use_analytic,
    double finite_difference_step) {
    const std::size_t n = pts.size();
    std::vector<double> grad(3 * n, 0.0);
    if (n < 3) return grad;

    if (use_analytic) {
        const double rel = 1e-12 * std::max(1.0, std::abs(kink.minrad));
        if (kink.minrad_minus <= kink.minrad_plus + rel) {
            grad = kink_minrad_minus_gradient_flat(pts, kink);
        } else {
            grad = kink_minrad_plus_gradient_flat(pts, kink);
        }
        if (flat_norm(grad) > eps_d) return grad;
    }

    if (finite_difference_step <= 0.0) finite_difference_step = 1e-6;

    // Fallback finite-difference only on the local three-vertex stencil.
    const std::size_t ids[3] = {
        wrap_index(static_cast<long long>(kink.vertex) - 1, n),
        kink.vertex % n,
        (kink.vertex + 1) % n
    };
    for (std::size_t id : ids) {
        for (std::size_t axis = 0; axis < 3; ++axis) {
            std::vector<Vec3> plus = pts;
            std::vector<Vec3> minus = pts;
            const double scale = std::max(1.0, std::abs(pts[id][axis]));
            const double h = finite_difference_step * scale;
            plus[id][axis] += h;
            minus[id][axis] -= h;
            const double fp = kink_at_vertex(plus, kink.vertex).minrad;
            const double fm = kink_at_vertex(minus, kink.vertex).minrad;
            double deriv = 0.0;
            if (std::isfinite(fp) && std::isfinite(fm)) {
                deriv = (fp - fm) / (2.0 * h);
            } else if (std::isfinite(fp)) {
                deriv = (fp - kink.minrad) / h;
            } else if (std::isfinite(fm)) {
                deriv = (kink.minrad - fm) / h;
            }
            grad[3 * id + axis] = deriv;
        }
    }
    return grad;
}

double ResolvedTubeGeometry::nontrivial_knot_lower_bound_rad() {
    return 4.0 * pi_d + 2.0 * pi_d * std::sqrt(2.0);
}

double ResolvedTubeGeometry::radius_to_diameter_ropelength(double ropelength_rad) {
    return 0.5 * ropelength_rad;
}

double ResolvedTubeGeometry::diameter_to_radius_ropelength(double ropelength_diam) {
    return 2.0 * ropelength_diam;
}



} // namespace sst
