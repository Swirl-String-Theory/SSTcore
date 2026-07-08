#!/usr/bin/env python3
"""Split src/tube/geometry.cpp into P2 tube modules (one-shot helper)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "tube"
INC = ROOT / "include" / "sst" / "tube"

COMMON_CPP = r'''#include "sst/tube/detail/common.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>

namespace sst::tube::detail {

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

std::vector<SparseEntry> dense_to_sparse_entries(const std::vector<double>& values, double drop_tol) {
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

} // namespace sst::tube::detail
'''

COMMON_H = r'''#ifndef SSTCORE_SST_TUBE_DETAIL_COMMON_H
#define SSTCORE_SST_TUBE_DETAIL_COMMON_H

#pragma once

#include "sst/tube/types.h"
#include <cmath>
#include <cstddef>
#include <vector>

namespace sst::tube::detail {

extern const double pi_d;
extern const double eps_d;

Vec3 add(const Vec3& a, const Vec3& b);
Vec3 sub(const Vec3& a, const Vec3& b);
Vec3 mul(const Vec3& a, double s);
double norm2(const Vec3& a);
double dist(const Vec3& a, const Vec3& b);
double clamp01(double x);
double clamp(double x, double lo, double hi);
std::size_t wrap_index(long long i, std::size_t n);
int cyclic_edge_distance(std::size_t i, std::size_t j, std::size_t n);
std::vector<double> cumulative_lengths(const std::vector<Vec3>& pts);
void add_to_flat(std::vector<double>& flat, std::size_t vertex, const Vec3& value);
double flat_norm(const std::vector<double>& v);
double flat_dot(const std::vector<double>& a, const std::vector<double>& b);
std::vector<double> matvec_columns(const RigidityMatrix& matrix, const std::vector<double>& x);
double sparse_column_dot_target(const SparseRigidityColumn& col, const std::vector<double>& target);
double sparse_column_dot_column(const SparseRigidityColumn& a, const SparseRigidityColumn& b);
std::vector<double> matvec_sparse_columns(const SparseRigidityMatrix& matrix, const std::vector<double>& x);
std::vector<double> residual_vector(const RigidityMatrix& matrix, const std::vector<double>& x, const std::vector<double>& target);
std::vector<double> residual_vector(const SparseRigidityMatrix& matrix, const std::vector<double>& x, const std::vector<double>& target);
std::vector<SparseEntry> dense_to_sparse_entries(const std::vector<double>& values, double drop_tol = 1e-15);
bool solve_dense_linear_system(std::vector<std::vector<double>> A, std::vector<double> b, std::vector<double>& x, double ridge);
Vec3 centroid_of(const std::vector<Vec3>& pts);
std::vector<Vec3> apply_flat_step(const std::vector<Vec3>& pts, const std::vector<double>& direction, double alpha);
double max_vertex_step_norm(const std::vector<double>& direction);
std::vector<double> normalized_direction_by_vertex_step(std::vector<double> direction);
double sparse_constraint_value(const ResolvedTubeMetrics& tube, const SparseRigidityColumn& col);
std::vector<std::vector<double>> dense_gram(const RigidityMatrix& matrix, std::vector<double>& Atb, const std::vector<double>& target);
std::vector<std::vector<double>> sparse_gram(const SparseRigidityMatrix& matrix, std::vector<double>& Atb, const std::vector<double>& target);

} // namespace sst::tube::detail

#endif
'''

def main():
    geo = (SRC / "geometry.cpp").read_text(encoding="utf-8")
    lines = geo.splitlines(keepends=True)

    # Extract body between namespace sst { and closing }
    start = next(i for i, l in enumerate(lines) if l.strip() == "namespace sst {")
    end = next(i for i in range(len(lines) - 1, -1, -1) if lines[i].strip() == "} // namespace sst")

    body = "".join(lines[start + 1 : end])
    # Remove anonymous namespace block (helpers now in detail/common)
    anon_start = body.find("namespace {")
    anon_end = body.find("} // namespace\n\ndouble ResolvedTubeGeometry")
    if anon_start >= 0 and anon_end > anon_start:
        body = body[anon_end + len("} // namespace\n\n") :]

    sections = {
        "geometry_core": ("double ResolvedTubeGeometry::", "RigidityMatrix ContactStressMap::build_rigidity_matrix"),
        "rigidity_matrix": ("RigidityMatrix ContactStressMap::build_rigidity_matrix", "void ContactStressMap::write_sparse_matrix_market"),
        "io": ("void ContactStressMap::write_sparse_matrix_market", "std::vector<Vec3> ResolvedTubeTightener::rescale_to_thickness"),
        "tightener": ("std::vector<Vec3> ResolvedTubeTightener::rescale_to_thickness", "NNLSResult ContactStressMap::solve_nonnegative_least_squares"),
        "nnls": ("NNLSResult ContactStressMap::solve_nonnegative_least_squares", "ContactStressDiagnostics ContactStressMap::diagnose_length_criticality"),
        "contact_stress": ("ContactStressDiagnostics ContactStressMap::diagnose_length_criticality", None),
    }

    def slice_between(text, start_marker, end_marker):
        s = text.index(start_marker)
        e = text.index(end_marker, s) if end_marker else len(text)
        return text[s:e]

    (INC / "detail").mkdir(parents=True, exist_ok=True)
    (INC / "detail" / "common.h").write_text(COMMON_H, encoding="utf-8")
    (SRC / "detail").mkdir(parents=True, exist_ok=True)
    (SRC / "detail" / "common.cpp").write_text(COMMON_CPP, encoding="utf-8")

    includes = {
        "geometry_core": '#include "sst/tube/geometry_core.h"\n#include "sst/tube/detail/common.h"\n\n#include <algorithm>\n#include <cmath>\n#include <limits>\n#include <stdexcept>\n\nusing namespace sst::tube::detail;\n\nnamespace sst {\n\n',
        "rigidity_matrix": '#include "sst/tube/rigidity_matrix.h"\n#include "sst/tube/geometry_core.h"\n#include "sst/tube/detail/common.h"\n\n#ifdef SSTCORE_USE_EIGEN\n#include <Eigen/Sparse>\n#endif\n\nusing namespace sst::tube::detail;\n\nnamespace sst {\n\n',
        "io": '#include "sst/tube/io.h"\n\n#include <fstream>\n#include <iomanip>\n#include <stdexcept>\n\nnamespace sst {\n\n',
        "tightener": '#include "sst/tube/tightener.h"\n#include "sst/tube/geometry_core.h"\n#include "sst/tube/rigidity_matrix.h"\n#include "sst/tube/nnls.h"\n#include "sst/tube/detail/common.h"\n\nusing namespace sst::tube::detail;\n\nnamespace sst {\n\n',
        "nnls": '#include "sst/tube/nnls.h"\n#include "sst/tube/detail/common.h"\n\n#include <algorithm>\n#include <cmath>\n#include <limits>\n\nusing namespace sst::tube::detail;\n\nnamespace sst {\n\n',
        "contact_stress": '#include "sst/tube/contact_stress.h"\n#include "sst/tube/geometry_core.h"\n#include "sst/tube/rigidity_matrix.h"\n#include "sst/tube/nnls.h"\n#include "sst/tube/detail/common.h"\n\n#include <cmath>\n\nusing namespace sst::tube::detail;\n\nnamespace sst {\n\n',
    }

    markers = list(sections.items())
    for i, (name, (start_m, end_m)) in enumerate(markers):
        chunk = slice_between(body, start_m, end_m)
        # Rename ContactStressMap::build_* to free functions in rigidity/io/nnls
        if name == "rigidity_matrix":
            chunk = chunk.replace("ContactStressMap::build_rigidity_matrix", "build_rigidity_matrix")
            chunk = chunk.replace("ContactStressMap::build_sparse_rigidity_matrix", "build_sparse_rigidity_matrix")
            chunk = chunk.replace("ContactStressMap::sparse_to_dense", "sparse_to_dense")
            chunk = chunk.replace("ContactStressMap::to_eigen_sparse", "to_eigen_sparse")
        elif name == "io":
            chunk = chunk.replace("ContactStressMap::", "")
        elif name == "nnls":
            chunk = chunk.replace("ContactStressMap::solve_nonnegative_least_squares_sparse_active_set", "solve_nonnegative_least_squares_sparse_active_set")
            chunk = chunk.replace("ContactStressMap::solve_nonnegative_least_squares_active_set", "solve_nonnegative_least_squares_active_set")
            chunk = chunk.replace("ContactStressMap::solve_nonnegative_least_squares_sparse", "solve_nonnegative_least_squares_sparse")
            chunk = chunk.replace("ContactStressMap::solve_nonnegative_least_squares", "solve_nonnegative_least_squares")
            # active_set_nnls_from_gram was in anon namespace - need to add from original
            active_set = geo[geo.find("NNLSResult active_set_nnls_from_gram"): geo.find("std::vector<std::vector<double>> dense_gram")]
            chunk = active_set + "\n" + chunk
        elif name == "contact_stress":
            chunk = chunk.replace("build_sparse_rigidity_matrix(", "build_sparse_rigidity_matrix(")
            chunk = chunk.replace("solve_nonnegative_least_squares_sparse_active_set(", "solve_nonnegative_least_squares_sparse_active_set(")
            chunk = chunk.replace("solve_nonnegative_least_squares_sparse(", "solve_nonnegative_least_squares_sparse(")
            chunk = chunk.replace("solve_nonnegative_least_squares_active_set(", "solve_nonnegative_least_squares_active_set(")
            chunk = chunk.replace("solve_nonnegative_least_squares(", "solve_nonnegative_least_squares(")

        out = includes[name] + chunk + "\n} // namespace sst\n"
        (SRC / f"{name}.cpp").write_text(out, encoding="utf-8")
        print(f"wrote {name}.cpp ({len(out)} bytes)")

    print("done")


if __name__ == "__main__":
    main()
