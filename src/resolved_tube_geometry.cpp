#include "resolved_tube_geometry.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
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

double sparse_column_dot_target(const SparseRigidityColumn& col, const std::vector<double>& target) {
    double acc = 0.0;
    for (const auto& e : col.entries) {
        if (e.row < target.size()) acc += e.value * target[e.row];
    }
    return acc;
}

double sparse_column_dot_column(const SparseRigidityColumn& a, const SparseRigidityColumn& b) {
    double acc = 0.0;
    std::size_t i = 0, j = 0;
    while (i < a.entries.size() && j < b.entries.size()) {
        if (a.entries[i].row == b.entries[j].row) {
            acc += a.entries[i].value * b.entries[j].value;
            ++i;
            ++j;
        } else if (a.entries[i].row < b.entries[j].row) {
            ++i;
        } else {
            ++j;
        }
    }
    return acc;
}

std::vector<double> matvec_sparse_columns(const SparseRigidityMatrix& matrix, const std::vector<double>& x) {
    std::vector<double> y(matrix.row_count, 0.0);
    const std::size_t cols = std::min(matrix.columns.size(), x.size());
    for (std::size_t j = 0; j < cols; ++j) {
        const double coeff = x[j];
        for (const auto& e : matrix.columns[j].entries) {
            if (e.row < y.size()) y[e.row] += coeff * e.value;
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

std::vector<double> residual_vector(const SparseRigidityMatrix& matrix, const std::vector<double>& x, const std::vector<double>& target) {
    std::vector<double> r = matvec_sparse_columns(matrix, x);
    const std::size_t n = std::min(r.size(), target.size());
    for (std::size_t i = 0; i < n; ++i) r[i] -= target[i];
    return r;
}

std::vector<SparseEntry> dense_to_sparse_entries(const std::vector<double>& values, double drop_tol = 1e-15) {
    std::vector<SparseEntry> out;
    out.reserve(12);
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (std::abs(values[i]) > drop_tol) out.push_back(SparseEntry{i, values[i]});
    }
    return out;
}

bool solve_dense_linear_system(
    std::vector<std::vector<double>> A,
    std::vector<double> b,
    std::vector<double>& x,
    double ridge) {
    const std::size_t n = b.size();
    x.assign(n, 0.0);
    if (n == 0) return true;
    if (A.size() != n) return false;
    for (std::size_t i = 0; i < n; ++i) {
        if (A[i].size() != n) return false;
        A[i][i] += std::max(0.0, ridge);
    }

    for (std::size_t k = 0; k < n; ++k) {
        std::size_t piv = k;
        double best = std::abs(A[k][k]);
        for (std::size_t r = k + 1; r < n; ++r) {
            const double cand = std::abs(A[r][k]);
            if (cand > best) { best = cand; piv = r; }
        }
        if (best <= 1e-18) return false;
        if (piv != k) {
            std::swap(A[piv], A[k]);
            std::swap(b[piv], b[k]);
        }
        const double diag = A[k][k];
        for (std::size_t j = k; j < n; ++j) A[k][j] /= diag;
        b[k] /= diag;
        for (std::size_t r = 0; r < n; ++r) {
            if (r == k) continue;
            const double f = A[r][k];
            if (std::abs(f) <= 0.0) continue;
            for (std::size_t j = k; j < n; ++j) A[r][j] -= f * A[k][j];
            b[r] -= f * b[k];
        }
    }
    x = std::move(b);
    return true;
}

NNLSResult active_set_nnls_from_gram(
    const std::vector<std::vector<double>>& AtA,
    const std::vector<double>& Atb,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance,
    double ridge,
    const RigidityMatrix* dense_matrix,
    const SparseRigidityMatrix* sparse_matrix) {
    NNLSResult out;
    out.algorithm = "active_set";
    const std::size_t n = Atb.size();
    out.multipliers.assign(n, 0.0);
    if (n == 0) {
        out.residual_norm = flat_norm(target);
        out.relative_residual = (out.residual_norm > 0.0) ? 1.0 : 0.0;
        out.objective = 0.5 * out.residual_norm * out.residual_norm;
        out.converged = out.residual_norm <= tolerance;
        return out;
    }
    if (max_iterations == 0) max_iterations = 1;
    if (tolerance <= 0.0) tolerance = 1e-10;
    if (ridge < 0.0) ridge = 0.0;

    std::vector<double> x(n, 0.0);
    std::vector<bool> passive(n, false);
    const double target_norm = std::max(flat_norm(target), eps_d);

    auto gradient = [&]() {
        std::vector<double> w = Atb;
        for (std::size_t i = 0; i < n; ++i) {
            if (x[i] == 0.0) continue;
            for (std::size_t j = 0; j < n; ++j) w[j] -= AtA[j][i] * x[i];
        }
        return w;
    };

    auto solve_passive = [&](std::vector<double>& z_full) -> bool {
        z_full.assign(n, 0.0);
        std::vector<std::size_t> ids;
        ids.reserve(n);
        for (std::size_t i = 0; i < n; ++i) if (passive[i]) ids.push_back(i);
        if (ids.empty()) return true;
        std::vector<std::vector<double>> G(ids.size(), std::vector<double>(ids.size(), 0.0));
        std::vector<double> c(ids.size(), 0.0);
        for (std::size_t r = 0; r < ids.size(); ++r) {
            c[r] = Atb[ids[r]];
            for (std::size_t q = 0; q < ids.size(); ++q) G[r][q] = AtA[ids[r]][ids[q]];
        }
        std::vector<double> sol;
        double local_ridge = ridge;
        bool ok = false;
        for (int attempt = 0; attempt < 6 && !ok; ++attempt) {
            ok = solve_dense_linear_system(G, c, sol, local_ridge);
            local_ridge = (local_ridge <= 0.0) ? 1e-14 : local_ridge * 10.0;
        }
        if (!ok) return false;
        for (std::size_t r = 0; r < ids.size(); ++r) z_full[ids[r]] = sol[r];
        return true;
    };

    bool singular = false;
    for (std::size_t iter = 0; iter < max_iterations; ++iter) {
        out.iterations = iter + 1;
        const auto w = gradient();
        std::size_t t = n;
        double wmax = tolerance;
        for (std::size_t j = 0; j < n; ++j) {
            if (!passive[j] && w[j] > wmax) { wmax = w[j]; t = j; }
        }
        if (t == n) {
            out.converged = true;
            break;
        }
        passive[t] = true;

        for (;;) {
            std::vector<double> z;
            if (!solve_passive(z)) {
                passive[t] = false;
                singular = true;
                break;
            }

            bool all_positive = true;
            for (std::size_t j = 0; j < n; ++j) {
                if (passive[j] && z[j] <= tolerance) { all_positive = false; break; }
            }
            if (all_positive) {
                x = std::move(z);
                break;
            }

            double alpha = 1.0;
            bool have_alpha = false;
            for (std::size_t j = 0; j < n; ++j) {
                if (!passive[j] || z[j] > tolerance) continue;
                const double denom = x[j] - z[j];
                if (denom <= eps_d) continue;
                const double a = x[j] / denom;
                if (!have_alpha || a < alpha) { alpha = a; have_alpha = true; }
            }
            if (!have_alpha) alpha = 1.0;
            alpha = clamp(alpha, 0.0, 1.0);
            for (std::size_t j = 0; j < n; ++j) x[j] += alpha * (z[j] - x[j]);
            for (std::size_t j = 0; j < n; ++j) {
                if (passive[j] && x[j] <= tolerance * (1.0 + flat_norm(x))) {
                    x[j] = 0.0;
                    passive[j] = false;
                }
            }
        }
        if (singular) continue;
    }

    out.multipliers = x;
    out.active_set_size = 0;
    for (double v : x) if (v > tolerance) ++out.active_set_size;
    std::vector<double> r;
    if (dense_matrix) r = residual_vector(*dense_matrix, x, target);
    else if (sparse_matrix) r = residual_vector(*sparse_matrix, x, target);
    else r = target;
    out.residual_norm = flat_norm(r);
    out.relative_residual = out.residual_norm / target_norm;
    out.objective = 0.5 * out.residual_norm * out.residual_norm;
    if (!out.converged) {
        const auto w = gradient();
        double max_dual = 0.0;
        for (std::size_t j = 0; j < n; ++j) if (x[j] <= tolerance) max_dual = std::max(max_dual, w[j]);
        out.converged = (max_dual <= std::sqrt(tolerance) || out.relative_residual <= tolerance);
    }
    return out;
}

std::vector<std::vector<double>> dense_gram(const RigidityMatrix& matrix, std::vector<double>& Atb, const std::vector<double>& target) {
    const std::size_t p = matrix.columns.size();
    Atb.assign(p, 0.0);
    std::vector<std::vector<double>> AtA(p, std::vector<double>(p, 0.0));
    for (std::size_t i = 0; i < p; ++i) {
        Atb[i] = flat_dot(matrix.columns[i].values, target);
        for (std::size_t j = 0; j <= i; ++j) {
            const double v = flat_dot(matrix.columns[i].values, matrix.columns[j].values);
            AtA[i][j] = v;
            AtA[j][i] = v;
        }
    }
    return AtA;
}

std::vector<std::vector<double>> sparse_gram(const SparseRigidityMatrix& matrix, std::vector<double>& Atb, const std::vector<double>& target) {
    const std::size_t p = matrix.columns.size();
    Atb.assign(p, 0.0);
    std::vector<std::vector<double>> AtA(p, std::vector<double>(p, 0.0));
    for (std::size_t i = 0; i < p; ++i) {
        Atb[i] = sparse_column_dot_target(matrix.columns[i], target);
        for (std::size_t j = 0; j <= i; ++j) {
            const double v = sparse_column_dot_column(matrix.columns[i], matrix.columns[j]);
            AtA[i][j] = v;
            AtA[j][i] = v;
        }
    }
    return AtA;
}

Vec3 centroid_of(const std::vector<Vec3>& pts) {
    Vec3 c{0.0, 0.0, 0.0};
    if (pts.empty()) return c;
    for (const auto& p : pts) c = add(c, p);
    return mul(c, 1.0 / static_cast<double>(pts.size()));
}

std::vector<Vec3> apply_flat_step(
    const std::vector<Vec3>& pts,
    const std::vector<double>& direction,
    double alpha) {
    std::vector<Vec3> out = pts;
    const std::size_t n = std::min(pts.size(), direction.size() / 3);
    for (std::size_t i = 0; i < n; ++i) {
        out[i][0] += alpha * direction[3 * i + 0];
        out[i][1] += alpha * direction[3 * i + 1];
        out[i][2] += alpha * direction[3 * i + 2];
    }
    return out;
}

double max_vertex_step_norm(const std::vector<double>& direction) {
    double mx = 0.0;
    for (std::size_t i = 0; i + 2 < direction.size(); i += 3) {
        const double n = std::sqrt(direction[i] * direction[i] +
                                   direction[i + 1] * direction[i + 1] +
                                   direction[i + 2] * direction[i + 2]);
        mx = std::max(mx, n);
    }
    return mx;
}

std::vector<double> normalized_direction_by_vertex_step(std::vector<double> direction) {
    const double mx = max_vertex_step_norm(direction);
    if (mx <= eps_d) return direction;
    for (double& v : direction) v /= mx;
    return direction;
}

double sparse_constraint_value(const ResolvedTubeMetrics& tube, const SparseRigidityColumn& col) {
    if (col.kind == "strut" && col.strut_index < tube.struts.size()) {
        return 0.5 * tube.struts[col.strut_index].distance;
    }
    if (col.kind == "kink" && col.kink_index < tube.kinks.size()) {
        return tube.kinks[col.kink_index].minrad;
    }
    return std::numeric_limits<double>::infinity();
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


RigidityMatrix ContactStressMap::build_rigidity_matrix(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool include_struts,
    bool include_kinks,
    double kink_finite_difference_step,
    bool use_analytic_kink_gradient) {
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
                pts, tube.kinks[k], use_analytic_kink_gradient, kink_finite_difference_step);
            col.norm = flat_norm(col.values);
            if (col.norm > eps_d) matrix.columns.push_back(std::move(col));
        }
    }

    matrix.column_count = matrix.columns.size();
    return matrix;
}

SparseRigidityMatrix ContactStressMap::build_sparse_rigidity_matrix(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool include_struts,
    bool include_kinks,
    double kink_finite_difference_step,
    bool use_analytic_kink_gradient) {
    SparseRigidityMatrix sparse;
    sparse.row_count = 3 * pts.size();
    if (pts.empty()) return sparse;

    auto append_column = [&sparse](RigidityColumn&& dense) {
        SparseRigidityColumn col;
        col.kind = dense.kind;
        col.strut_index = dense.strut_index;
        col.kink_index = dense.kink_index;
        col.vertex = dense.vertex;
        col.norm = dense.norm;
        col.entries = dense_to_sparse_entries(dense.values);
        if (!col.entries.empty()) {
            sparse.nonzero_count += col.entries.size();
            sparse.columns.push_back(std::move(col));
        }
    };

    if (include_struts) {
        for (std::size_t k = 0; k < tube.struts.size(); ++k) {
            RigidityColumn dense;
            dense.kind = "strut";
            dense.strut_index = k;
            dense.values = ResolvedTubeGeometry::strut_gradient_flat(pts, tube.struts[k]);
            dense.norm = flat_norm(dense.values);
            if (dense.norm > eps_d) append_column(std::move(dense));
        }
    }

    if (include_kinks) {
        for (std::size_t k = 0; k < tube.kinks.size(); ++k) {
            RigidityColumn dense;
            dense.kind = "kink";
            dense.kink_index = k;
            dense.vertex = tube.kinks[k].vertex;
            dense.values = ResolvedTubeGeometry::kink_minrad_gradient_flat(
                pts, tube.kinks[k], use_analytic_kink_gradient, kink_finite_difference_step);
            dense.norm = flat_norm(dense.values);
            if (dense.norm > eps_d) append_column(std::move(dense));
        }
    }

    sparse.column_count = sparse.columns.size();
    return sparse;
}

RigidityMatrix ContactStressMap::sparse_to_dense(const SparseRigidityMatrix& sparse) {
    RigidityMatrix dense;
    dense.row_count = sparse.row_count;
    dense.column_count = sparse.column_count;
    dense.columns.reserve(sparse.columns.size());
    for (const auto& scol : sparse.columns) {
        RigidityColumn col;
        col.kind = scol.kind;
        col.strut_index = scol.strut_index;
        col.kink_index = scol.kink_index;
        col.vertex = scol.vertex;
        col.norm = scol.norm;
        col.values.assign(sparse.row_count, 0.0);
        for (const auto& e : scol.entries) {
            if (e.row < col.values.size()) col.values[e.row] = e.value;
        }
        dense.columns.push_back(std::move(col));
    }
    return dense;
}

#ifdef SSTCORE_USE_EIGEN
Eigen::SparseMatrix<double> ContactStressMap::to_eigen_sparse(const SparseRigidityMatrix& sparse) {
    std::vector<Eigen::Triplet<double>> triplets;
    triplets.reserve(sparse.nonzero_count);
    for (std::size_t j = 0; j < sparse.columns.size(); ++j) {
        for (const auto& e : sparse.columns[j].entries) {
            triplets.emplace_back(static_cast<int>(e.row), static_cast<int>(j), e.value);
        }
    }
    Eigen::SparseMatrix<double> A(static_cast<int>(sparse.row_count), static_cast<int>(sparse.column_count));
    A.setFromTriplets(triplets.begin(), triplets.end());
    return A;
}
#endif

void ContactStressMap::write_sparse_matrix_market(
    const SparseRigidityMatrix& sparse,
    const std::string& path,
    bool one_based_indices) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("could not open Matrix Market output path: " + path);
    out << "%%MatrixMarket matrix coordinate real general\n";
    out << "% SSTcore resolved-tube sparse rigidity matrix A, rows=3N, columns=struts+kinks\n";
    out << sparse.row_count << " " << sparse.column_count << " " << sparse.nonzero_count << "\n";
    out << std::setprecision(17);
    const std::size_t offset = one_based_indices ? 1u : 0u;
    for (std::size_t j = 0; j < sparse.columns.size(); ++j) {
        for (const auto& e : sparse.columns[j].entries) {
            out << (e.row + offset) << " " << (j + offset) << " " << e.value << "\n";
        }
    }
}

void ContactStressMap::write_vector_market(
    const std::vector<double>& vector,
    const std::string& path) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("could not open vector Matrix Market output path: " + path);
    out << "%%MatrixMarket matrix array real general\n";
    out << "% SSTcore resolved-tube dense vector\n";
    out << vector.size() << " 1\n";
    out << std::setprecision(17);
    for (double v : vector) out << v << "\n";
}

void ContactStressMap::write_vector_csv(
    const std::vector<double>& vector,
    const std::string& path) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("could not open vector CSV output path: " + path);
    out << "row,value\n";
    out << std::setprecision(17);
    for (std::size_t i = 0; i < vector.size(); ++i) out << i << "," << vector[i] << "\n";
}

std::vector<Vec3> ResolvedTubeTightener::rescale_to_thickness(
    const std::vector<Vec3>& pts,
    double target_thickness,
    int skip_neighbors,
    double contact_tol,
    double equilateral_tol) {
    if (pts.empty()) return pts;
    if (!(target_thickness > 0.0) || !std::isfinite(target_thickness)) return pts;
    const auto metrics = ResolvedTubeGeometry::analyze(pts, skip_neighbors, contact_tol, equilateral_tol);
    if (!(metrics.thickness_rad > 0.0) || !std::isfinite(metrics.thickness_rad)) return pts;
    if (metrics.thickness_rad >= target_thickness) return pts;
    const double scale = (target_thickness / metrics.thickness_rad) * (1.0 + 1e-12);
    const Vec3 c = centroid_of(pts);
    std::vector<Vec3> out = pts;
    for (auto& p : out) p = add(c, mul(sub(p, c), scale));
    return out;
}

std::vector<Vec3> ResolvedTubeTightener::correct_thickness(
    const std::vector<Vec3>& pts,
    double target_thickness,
    const TighteningOptions& options) {
    if (pts.empty()) return pts;
    if (!(target_thickness > 0.0) || !std::isfinite(target_thickness)) return pts;
    if (options.correction_strategy == "none") return pts;

    auto current = ResolvedTubeGeometry::analyze(
        pts, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
    if (current.thickness_rad >= target_thickness) return pts;

    if (options.correction_strategy == "scale") {
        return rescale_to_thickness(pts, target_thickness, options.skip_neighbors,
                                    options.contact_tol, options.equilateral_tol);
    }

    std::vector<Vec3> out = pts;
    for (int attempt = 0; attempt < 3; ++attempt) {
        current = ResolvedTubeGeometry::analyze(
            out, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
        if (current.thickness_rad >= target_thickness) return out;

        const auto A = ContactStressMap::build_sparse_rigidity_matrix(
            out, current, true, true, 1e-6, options.use_analytic_kink_gradient);
        if (A.column_count == 0) break;

        std::vector<double> margin(A.column_count, 0.0);
        bool any = false;
        for (std::size_t j = 0; j < A.columns.size(); ++j) {
            const double g = sparse_constraint_value(current, A.columns[j]);
            if (std::isfinite(g) && g < target_thickness) {
                margin[j] = target_thickness - g;
                any = true;
            }
        }
        if (!any) break;

        std::vector<double> dummy;
        auto AtA = sparse_gram(A, dummy, std::vector<double>(A.row_count, 0.0));
        std::vector<double> y;
        if (!solve_dense_linear_system(AtA, margin, y, std::max(0.0, options.newton_ridge))) break;
        auto W = matvec_sparse_columns(A, y);
        const double max_step = max_vertex_step_norm(W);
        if (!(max_step > 0.0) || !std::isfinite(max_step)) break;
        const double damping = clamp(options.newton_correction_damping, 0.0, 1.0);
        out = apply_flat_step(out, W, damping);
    }

    current = ResolvedTubeGeometry::analyze(
        out, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
    if (current.thickness_rad < target_thickness) {
        out = rescale_to_thickness(out, target_thickness, options.skip_neighbors,
                                   options.contact_tol, options.equilateral_tol);
    }
    return out;
}

std::vector<double> ResolvedTubeTightener::projected_gradient_flat(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    const TighteningOptions& options,
    ContactStressDiagnostics* diagnostics_out) {
    const auto grad = ResolvedTubeGeometry::length_gradient_flat(pts);
    if (grad.empty()) return grad;

    std::vector<double> projected(grad.size(), 0.0);
    if (options.use_sparse_solver) {
        const auto A = ContactStressMap::build_sparse_rigidity_matrix(
            pts, tube, true, true, 1e-6, options.use_analytic_kink_gradient);
        NNLSResult nnls;
        if (A.column_count > 0) {
            nnls = options.use_active_set_solver
                ? ContactStressMap::solve_nonnegative_least_squares_sparse_active_set(
                      A, grad, options.nnls_max_iterations, options.nnls_tolerance)
                : ContactStressMap::solve_nonnegative_least_squares_sparse(
                      A, grad, options.nnls_max_iterations, options.nnls_tolerance);
            projected = matvec_sparse_columns(A, nnls.multipliers);
        }
        for (std::size_t i = 0; i < projected.size() && i < grad.size(); ++i) projected[i] -= grad[i];
        if (diagnostics_out) {
            *diagnostics_out = ContactStressDiagnostics{};
            diagnostics_out->gradient_norm = flat_norm(grad);
            diagnostics_out->residual_norm = flat_norm(projected);
            diagnostics_out->contact_residual = diagnostics_out->residual_norm / std::max(diagnostics_out->gradient_norm, eps_d);
            diagnostics_out->rigidity_rows = A.row_count;
            diagnostics_out->rigidity_columns = A.column_count;
            diagnostics_out->strut_count = tube.struts.size();
            diagnostics_out->kink_count = tube.kinks.size();
            diagnostics_out->solved_nnls = A.column_count > 0;
            diagnostics_out->nnls_converged = nnls.converged;
            diagnostics_out->nnls_iterations = nnls.iterations;
            diagnostics_out->nnls_active_set_size = nnls.active_set_size;
            diagnostics_out->nnls_algorithm = nnls.algorithm;
            diagnostics_out->nnls_objective = nnls.objective;
            diagnostics_out->multipliers = nnls.multipliers;
        }
    } else {
        const auto A = ContactStressMap::build_rigidity_matrix(
            pts, tube, true, true, 1e-6, options.use_analytic_kink_gradient);
        NNLSResult nnls;
        if (A.column_count > 0) {
            nnls = options.use_active_set_solver
                ? ContactStressMap::solve_nonnegative_least_squares_active_set(
                      A, grad, options.nnls_max_iterations, options.nnls_tolerance)
                : ContactStressMap::solve_nonnegative_least_squares(
                      A, grad, options.nnls_max_iterations, options.nnls_tolerance);
            projected = matvec_columns(A, nnls.multipliers);
        }
        for (std::size_t i = 0; i < projected.size() && i < grad.size(); ++i) projected[i] -= grad[i];
        if (diagnostics_out) {
            *diagnostics_out = ContactStressDiagnostics{};
            diagnostics_out->gradient_norm = flat_norm(grad);
            diagnostics_out->residual_norm = flat_norm(projected);
            diagnostics_out->contact_residual = diagnostics_out->residual_norm / std::max(diagnostics_out->gradient_norm, eps_d);
            diagnostics_out->rigidity_rows = A.row_count;
            diagnostics_out->rigidity_columns = A.column_count;
            diagnostics_out->strut_count = tube.struts.size();
            diagnostics_out->kink_count = tube.kinks.size();
            diagnostics_out->solved_nnls = A.column_count > 0;
            diagnostics_out->nnls_converged = nnls.converged;
            diagnostics_out->nnls_iterations = nnls.iterations;
            diagnostics_out->nnls_active_set_size = nnls.active_set_size;
            diagnostics_out->nnls_algorithm = nnls.algorithm;
            diagnostics_out->nnls_objective = nnls.objective;
            diagnostics_out->multipliers = nnls.multipliers;
        }
    }
    return projected;
}

TighteningResult ResolvedTubeTightener::tighten(
    const std::vector<Vec3>& initial_points,
    const TighteningOptions& options) {
    if (initial_points.size() < 3) throw std::invalid_argument("tighten requires at least 3 points.");
    TighteningResult result;
    result.points = initial_points;
    result.metrics = ResolvedTubeGeometry::analyze(
        result.points, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
    if (options.max_steps == 0) {
        result.reason = "max_steps_zero";
        return result;
    }

    const double initial_thickness = result.metrics.thickness_rad;
    if (!(initial_thickness > 0.0) || !std::isfinite(initial_thickness)) {
        result.reason = "nonpositive_initial_thickness";
        return result;
    }

    for (std::size_t step = 0; step < options.max_steps; ++step) {
        ContactStressDiagnostics diag;
        auto direction = projected_gradient_flat(result.points, result.metrics, options, &diag);
        const double projected_norm = flat_norm(direction);
        const double rel = projected_norm / std::max(diag.gradient_norm, eps_d);
        if (rel <= options.target_kkt_residual) {
            result.converged = true;
            result.reason = "target_kkt_residual";
            break;
        }
        if (!(projected_norm > eps_d) || !std::isfinite(projected_norm)) {
            result.reason = "zero_projected_gradient";
            break;
        }
        if (options.normalize_direction) direction = normalized_direction_by_vertex_step(std::move(direction));

        TighteningStepRecord rec;
        rec.step = step;
        rec.ropelength_before = result.metrics.ropelength_rad;
        rec.thickness_before = result.metrics.thickness_rad;
        rec.length_before = result.metrics.length;
        rec.kkt_residual_before = rel;
        rec.projected_gradient_norm = projected_norm;
        rec.strut_count = result.metrics.struts.size();
        rec.kink_count = result.metrics.kinks.size();
        rec.rigidity_columns = diag.rigidity_columns;
        rec.solver_algorithm = diag.nnls_algorithm;
        rec.correction_strategy = options.correction_strategy;

        const double target_thickness = options.preserve_initial_thickness
            ? initial_thickness
            : result.metrics.thickness_rad * std::max(0.0, options.thickness_floor_fraction);
        const double min_allowed_thickness = result.metrics.thickness_rad * std::max(0.0, options.thickness_floor_fraction);
        double alpha = std::max(options.min_step_size, options.max_step_size);
        bool accepted = false;
        std::vector<Vec3> best_points = result.points;
        ResolvedTubeMetrics best_metrics = result.metrics;
        bool corrected = false;

        for (std::size_t trial = 0; trial < options.line_search_trials && alpha >= options.min_step_size; ++trial) {
            auto candidate = apply_flat_step(result.points, direction, alpha);
            bool did_correct = false;
            auto cand_metrics = ResolvedTubeGeometry::analyze(
                candidate, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
            if (cand_metrics.thickness_rad < min_allowed_thickness ||
                (options.preserve_initial_thickness && cand_metrics.thickness_rad < target_thickness)) {
                candidate = correct_thickness(candidate, target_thickness, options);
                did_correct = true;
                cand_metrics = ResolvedTubeGeometry::analyze(
                    candidate, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
            }
            const bool thickness_ok = cand_metrics.thickness_rad + 1e-12 >= min_allowed_thickness &&
                (!options.preserve_initial_thickness || cand_metrics.thickness_rad + 1e-12 >= target_thickness * options.thickness_floor_fraction);
            const double allowed_rop = result.metrics.ropelength_rad +
                std::max(0.0, options.ropelength_increase_tolerance) *
                std::max(1.0, result.metrics.ropelength_rad);
            const bool rop_ok = cand_metrics.ropelength_rad <= allowed_rop ||
                                cand_metrics.length < result.metrics.length;
            if (thickness_ok && rop_ok && cand_metrics.thickness_rad > 0.0) {
                accepted = true;
                best_points = std::move(candidate);
                best_metrics = cand_metrics;
                corrected = did_correct;
                break;
            }
            alpha *= clamp(options.line_search_shrink, 0.05, 0.95);
        }

        rec.alpha = alpha;
        rec.accepted = accepted;
        rec.thickness_corrected = corrected;
        rec.ropelength_after = best_metrics.ropelength_rad;
        rec.thickness_after = best_metrics.thickness_rad;
        rec.length_after = best_metrics.length;
        result.steps.push_back(rec);

        if (!accepted) {
            result.reason = "line_search_failed";
            break;
        }
        result.points = std::move(best_points);
        result.metrics = best_metrics;
    }

    if (result.reason.empty()) {
        result.reason = result.converged ? "target_kkt_residual" : "max_steps";
    }
    return result;
}

NNLSResult ContactStressMap::solve_nonnegative_least_squares(
    const RigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance) {
    NNLSResult out;
    out.algorithm = "coordinate_descent";
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
    for (double v : out.multipliers) if (v > tolerance) ++out.active_set_size;
    return out;
}

NNLSResult ContactStressMap::solve_nonnegative_least_squares_sparse(
    const SparseRigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance) {
    NNLSResult out;
    out.algorithm = "coordinate_descent_sparse";
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
        Atb[i] = sparse_column_dot_target(matrix.columns[i], target);
        for (std::size_t j = 0; j <= i; ++j) {
            const double v = sparse_column_dot_column(matrix.columns[i], matrix.columns[j]);
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
    for (double v : out.multipliers) if (v > tolerance) ++out.active_set_size;
    return out;
}

NNLSResult ContactStressMap::solve_nonnegative_least_squares_active_set(
    const RigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance,
    double ridge) {
    std::vector<double> Atb;
    const auto AtA = dense_gram(matrix, Atb, target);
    return active_set_nnls_from_gram(AtA, Atb, target, max_iterations, tolerance, ridge, &matrix, nullptr);
}

NNLSResult ContactStressMap::solve_nonnegative_least_squares_sparse_active_set(
    const SparseRigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance,
    double ridge) {
    std::vector<double> Atb;
    const auto AtA = sparse_gram(matrix, Atb, target);
    return active_set_nnls_from_gram(AtA, Atb, target, max_iterations, tolerance, ridge, nullptr, &matrix);
}

ContactStressDiagnostics ContactStressMap::diagnose_length_criticality(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool solve_nnls,
    std::size_t max_iterations,
    double tolerance,
    bool use_sparse_solver,
    bool use_analytic_kink_gradient,
    bool use_active_set_solver) {
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

    NNLSResult nnls;
    std::vector<std::string> column_kinds;
    if (use_sparse_solver) {
        const SparseRigidityMatrix matrix = build_sparse_rigidity_matrix(
            pts, tube, true, true, 1e-6, use_analytic_kink_gradient);
        out.rigidity_columns = matrix.column_count;
        if (!solve_nnls || matrix.column_count == 0) {
            out.solved_nnls = false;
            out.residual_norm = out.gradient_norm;
            out.contact_residual = 1.0;
            return out;
        }
        for (const auto& col : matrix.columns) column_kinds.push_back(col.kind);
        nnls = use_active_set_solver
            ? solve_nonnegative_least_squares_sparse_active_set(matrix, grad_len, max_iterations, tolerance)
            : solve_nonnegative_least_squares_sparse(matrix, grad_len, max_iterations, tolerance);
    } else {
        const RigidityMatrix matrix = build_rigidity_matrix(
            pts, tube, true, true, 1e-6, use_analytic_kink_gradient);
        out.rigidity_columns = matrix.column_count;
        if (!solve_nnls || matrix.column_count == 0) {
            out.solved_nnls = false;
            out.residual_norm = out.gradient_norm;
            out.contact_residual = 1.0;
            return out;
        }
        for (const auto& col : matrix.columns) column_kinds.push_back(col.kind);
        nnls = use_active_set_solver
            ? solve_nonnegative_least_squares_active_set(matrix, grad_len, max_iterations, tolerance)
            : solve_nonnegative_least_squares(matrix, grad_len, max_iterations, tolerance);
    }
    out.solved_nnls = true;
    out.nnls_converged = nnls.converged;
    out.nnls_iterations = nnls.iterations;
    out.nnls_active_set_size = nnls.active_set_size;
    out.nnls_algorithm = nnls.algorithm;
    out.nnls_objective = nnls.objective;
    out.residual_norm = nnls.residual_norm;
    out.contact_residual = nnls.relative_residual;
    out.multipliers = nnls.multipliers;

    double total_weight = 0.0;
    for (std::size_t j = 0; j < column_kinds.size() && j < nnls.multipliers.size(); ++j) {
        const double w = std::max(0.0, nnls.multipliers[j]);
        total_weight += w;
        if (column_kinds[j] == "strut") out.strut_weight_sum += w;
        if (column_kinds[j] == "kink") out.kink_weight_sum += w;
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
