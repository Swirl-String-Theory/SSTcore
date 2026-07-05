#include "resolved_tube_geometry.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>

namespace sst {
namespace {

constexpr double pi_d = 3.141592653589793238462643383279502884;
constexpr double eps_d = 1e-14;

Vec3 add(const Vec3& a, const Vec3& b) { return {a[0] + b[0], a[1] + b[1], a[2] + b[2]}; }
Vec3 sub(const Vec3& a, const Vec3& b) { return diff(a, b); }
Vec3 mul(const Vec3& a, double s) { return {s * a[0], s * a[1], s * a[2]}; }
double norm2(const Vec3& a) { return dot(a, a); }
double dist(const Vec3& a, const Vec3& b) { return norm(diff(a, b)); }
double clamp01(double x) { return std::max(0.0, std::min(1.0, x)); }
double clamp(double x, double lo, double hi) { return std::max(lo, std::min(hi, x)); }

std::size_t wrap_index(long long i, std::size_t n) {
    const long long nn = static_cast<long long>(n);
    long long r = i % nn;
    if (r < 0) r += nn;
    return static_cast<std::size_t>(r);
}

int cyclic_edge_distance(std::size_t i, std::size_t j, std::size_t n) {
    const std::size_t d = (i > j) ? (i - j) : (j - i);
    return static_cast<int>(std::min(d, n - d));
}

std::vector<double> cumulative_lengths(const std::vector<Vec3>& pts) {
    std::vector<double> cum(pts.size() + 1, 0.0);
    if (pts.size() < 2) return cum;
    for (std::size_t i = 0; i < pts.size(); ++i) {
        cum[i + 1] = cum[i] + dist(pts[i], pts[(i + 1) % pts.size()]);
    }
    return cum;
}

void add_to_flat(std::vector<double>& flat, std::size_t vertex, const Vec3& value) {
    const std::size_t k = 3 * vertex;
    if (k + 2 >= flat.size()) return;
    flat[k + 0] += value[0];
    flat[k + 1] += value[1];
    flat[k + 2] += value[2];
}

double flat_norm(const std::vector<double>& v) {
    double acc = 0.0;
    for (double x : v) acc += x * x;
    return std::sqrt(acc);
}

double flat_dot(const std::vector<double>& a, const std::vector<double>& b) {
    const std::size_t n = std::min(a.size(), b.size());
    double acc = 0.0;
    for (std::size_t i = 0; i < n; ++i) acc += a[i] * b[i];
    return acc;
}

std::vector<double> matvec_columns(const RigidityMatrix& matrix, const std::vector<double>& x) {
    std::vector<double> y(matrix.row_count, 0.0);
    const std::size_t cols = std::min(matrix.columns.size(), x.size());
    for (std::size_t j = 0; j < cols; ++j) {
        const auto& col = matrix.columns[j].values;
        const double coeff = x[j];
        for (std::size_t r = 0; r < std::min(y.size(), col.size()); ++r) {
            y[r] += coeff * col[r];
        }
    }
    return y;
}

std::vector<double> residual_vector(const RigidityMatrix& matrix, const std::vector<double>& x, const std::vector<double>& target) {
    std::vector<double> r = matvec_columns(matrix, x);
    const std::size_t n = std::min(r.size(), target.size());
    for (std::size_t i = 0; i < n; ++i) r[i] -= target[i];
    return r;
}

} // namespace

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

std::vector<double> ResolvedTubeGeometry::kink_minrad_gradient_flat(
    const std::vector<Vec3>& pts,
    const KinkRecord& kink,
    double finite_difference_step) {
    const std::size_t n = pts.size();
    std::vector<double> grad(3 * n, 0.0);
    if (n < 3) return grad;
    if (finite_difference_step <= 0.0) finite_difference_step = 1e-6;

    // Finite-difference only the local three-vertex stencil.  This keeps the column sparse
    // and mirrors Ridgerunner's kink-gradient role without pulling in external AD/sparse libs.
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


RigidityMatrix ContactStressMap::build_rigidity_matrix(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool include_struts,
    bool include_kinks,
    double kink_finite_difference_step) {
    RigidityMatrix matrix;
    matrix.row_count = 3 * pts.size();
    if (pts.empty()) return matrix;

    if (include_struts) {
        for (std::size_t k = 0; k < tube.struts.size(); ++k) {
            RigidityColumn col;
            col.kind = "strut";
            col.strut_index = k;
            col.values = ResolvedTubeGeometry::strut_gradient_flat(pts, tube.struts[k]);
            col.norm = flat_norm(col.values);
            if (col.norm > eps_d) matrix.columns.push_back(std::move(col));
        }
    }

    if (include_kinks) {
        for (std::size_t k = 0; k < tube.kinks.size(); ++k) {
            RigidityColumn col;
            col.kind = "kink";
            col.kink_index = k;
            col.vertex = tube.kinks[k].vertex;
            col.values = ResolvedTubeGeometry::kink_minrad_gradient_flat(
                pts, tube.kinks[k], kink_finite_difference_step);
            col.norm = flat_norm(col.values);
            if (col.norm > eps_d) matrix.columns.push_back(std::move(col));
        }
    }

    matrix.column_count = matrix.columns.size();
    return matrix;
}

NNLSResult ContactStressMap::solve_nonnegative_least_squares(
    const RigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance) {
    NNLSResult out;
    const std::size_t p = matrix.columns.size();
    const std::size_t m = matrix.row_count;
    out.multipliers.assign(p, 0.0);
    if (p == 0 || m == 0 || target.empty()) {
        out.residual_norm = flat_norm(target);
        out.relative_residual = (out.residual_norm > 0.0) ? 1.0 : 0.0;
        out.objective = 0.5 * out.residual_norm * out.residual_norm;
        out.converged = (out.residual_norm <= tolerance);
        return out;
    }
    if (tolerance <= 0.0) tolerance = 1e-10;
    if (max_iterations == 0) max_iterations = 1;

    std::vector<double> Atb(p, 0.0);
    std::vector<std::vector<double>> AtA(p, std::vector<double>(p, 0.0));
    for (std::size_t i = 0; i < p; ++i) {
        Atb[i] = flat_dot(matrix.columns[i].values, target);
        for (std::size_t j = 0; j <= i; ++j) {
            const double v = flat_dot(matrix.columns[i].values, matrix.columns[j].values);
            AtA[i][j] = v;
            AtA[j][i] = v;
        }
    }

    std::vector<double> x(p, 0.0);
    std::vector<double> AtAx(p, 0.0);
    const double target_norm = std::max(flat_norm(target), eps_d);
    double max_change = std::numeric_limits<double>::infinity();

    for (std::size_t iter = 0; iter < max_iterations; ++iter) {
        max_change = 0.0;
        std::fill(AtAx.begin(), AtAx.end(), 0.0);
        for (std::size_t i = 0; i < p; ++i) {
            if (x[i] == 0.0) continue;
            for (std::size_t j = 0; j < p; ++j) AtAx[j] += AtA[j][i] * x[i];
        }

        for (std::size_t j = 0; j < p; ++j) {
            const double diag = AtA[j][j];
            if (diag <= eps_d) continue;
            const double old = x[j];
            const double grad = AtAx[j] - Atb[j];
            const double updated = std::max(0.0, old - grad / diag);
            const double delta = updated - old;
            if (delta != 0.0) {
                x[j] = updated;
                max_change = std::max(max_change, std::abs(delta));
                for (std::size_t r = 0; r < p; ++r) AtAx[r] += AtA[r][j] * delta;
            }
        }

        out.iterations = iter + 1;
        const auto r = residual_vector(matrix, x, target);
        const double rel = flat_norm(r) / target_norm;
        if (max_change <= tolerance * (1.0 + flat_norm(x)) || rel <= tolerance) {
            out.converged = true;
            break;
        }
    }

    out.multipliers = x;
    const auto r = residual_vector(matrix, x, target);
    out.residual_norm = flat_norm(r);
    out.relative_residual = out.residual_norm / target_norm;
    out.objective = 0.5 * out.residual_norm * out.residual_norm;
    return out;
}

ContactStressDiagnostics ContactStressMap::diagnose_length_criticality(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool solve_nnls,
    std::size_t max_iterations,
    double tolerance) {
    ContactStressDiagnostics out;
    out.strut_count = tube.struts.size();
    out.kink_count = tube.kinks.size();
    out.rigidity_rows = 3 * pts.size();

    const auto grad_len = ResolvedTubeGeometry::length_gradient_flat(pts);
    out.gradient_norm = flat_norm(grad_len);
    if (out.gradient_norm <= eps_d) {
        out.contact_residual = 0.0;
        out.residual_norm = 0.0;
        out.nnls_converged = true;
        return out;
    }

    const RigidityMatrix matrix = build_rigidity_matrix(pts, tube, true, true, 1e-6);
    out.rigidity_columns = matrix.column_count;
    if (!solve_nnls || matrix.column_count == 0) {
        out.solved_nnls = false;
        out.residual_norm = out.gradient_norm;
        out.contact_residual = 1.0;
        return out;
    }

    const NNLSResult nnls = solve_nonnegative_least_squares(matrix, grad_len, max_iterations, tolerance);
    out.solved_nnls = true;
    out.nnls_converged = nnls.converged;
    out.nnls_iterations = nnls.iterations;
    out.nnls_objective = nnls.objective;
    out.residual_norm = nnls.residual_norm;
    out.contact_residual = nnls.relative_residual;
    out.multipliers = nnls.multipliers;

    double total_weight = 0.0;
    for (std::size_t j = 0; j < matrix.columns.size() && j < nnls.multipliers.size(); ++j) {
        const double w = std::max(0.0, nnls.multipliers[j]);
        total_weight += w;
        if (matrix.columns[j].kind == "strut") out.strut_weight_sum += w;
        if (matrix.columns[j].kind == "kink") out.kink_weight_sum += w;
    }
    if (total_weight > 0.0) {
        double H = 0.0;
        for (double w : nnls.multipliers) {
            if (w <= 0.0) continue;
            const double p = w / total_weight;
            H -= p * std::log(p);
        }
        out.contact_entropy = H;
    }
    return out;
}

} // namespace sst
