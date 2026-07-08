#ifndef SSTCORE_SST_TUBE_DETAIL_COMMON_H
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
