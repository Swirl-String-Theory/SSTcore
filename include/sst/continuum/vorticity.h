#ifndef SSTCORE_SST_CONTINUUM_VORTICITY_H
#define SSTCORE_SST_CONTINUUM_VORTICITY_H

#pragma once

#include "sst/types.h"
#include <array>
#include <vector>

namespace sst::continuum::vorticity {

std::vector<double> compute_vorticity2D(
    const std::vector<double>& u,
    const std::vector<double>& v,
    int nx, int ny,
    double dx, double dy);
double vorticity_z_2D(double dv_dx, double du_dy);
double local_circulation_density(double dv_dx, double du_dy);
double solid_body_rotation_vorticity(double omega);
double couette_vorticity(double alpha);
std::array<double, 3> crocco_relation(
    const std::array<double, 3>& vorticity,
    double rho,
    const std::array<double, 3>& pressure_gradient);
Vec3 rotating_frame_rhs(
    const Vec3& velocity,
    const Vec3& vorticity,
    const Vec3& grad_phi,
    const Vec3& grad_p,
    const Vec3& omega,
    double rho);
Vec3 crocco_gradient(
    const Vec3& velocity,
    const Vec3& vorticity,
    const Vec3& grad_phi,
    const Vec3& grad_p,
    double rho);
Vec3 baroclinic_term(const Vec3& grad_rho, const Vec3& grad_p, double rho);
Vec3 compute_vorticity_rhs(
    const Vec3& omega,
    const std::array<Vec3, 3>& grad_u,
    double div_u,
    const Vec3& grad_rho,
    const Vec3& grad_p,
    double rho);

} // namespace sst::continuum::vorticity

#endif // SSTCORE_SST_CONTINUUM_VORTICITY_H
