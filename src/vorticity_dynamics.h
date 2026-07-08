#ifndef SSTCORE_VORTICITY_DYNAMICS_H
#define SSTCORE_VORTICITY_DYNAMICS_H

#pragma once

#include "sst/continuum/vorticity.h"
#include "sst/types.h"
#include <array>
#include <vector>

namespace sst {

class [[deprecated("Use sst::continuum::vorticity")]] VorticityDynamics {
public:
    static std::vector<double> compute_vorticity2D(
        const std::vector<double>& u, const std::vector<double>& v,
        int nx, int ny, double dx, double dy) {
        return continuum::vorticity::compute_vorticity2D(u, v, nx, ny, dx, dy);
    }
    static double vorticity_z_2D(double dv_dx, double du_dy) {
        return continuum::vorticity::vorticity_z_2D(dv_dx, du_dy);
    }
    static double local_circulation_density(double dv_dx, double du_dy) {
        return continuum::vorticity::local_circulation_density(dv_dx, du_dy);
    }
    static double solid_body_rotation_vorticity(double omega) {
        return continuum::vorticity::solid_body_rotation_vorticity(omega);
    }
    static double couette_vorticity(double alpha) {
        return continuum::vorticity::couette_vorticity(alpha);
    }
    static std::array<double, 3> crocco_relation(
        const std::array<double, 3>& vorticity, double rho,
        const std::array<double, 3>& pressure_gradient) {
        return continuum::vorticity::crocco_relation(vorticity, rho, pressure_gradient);
    }
    static Vec3 rotating_frame_rhs(
        const Vec3& velocity, const Vec3& vorticity, const Vec3& grad_phi,
        const Vec3& grad_p, const Vec3& omega, double rho) {
        return continuum::vorticity::rotating_frame_rhs(velocity, vorticity, grad_phi, grad_p, omega, rho);
    }
    static Vec3 crocco_gradient(
        const Vec3& velocity, const Vec3& vorticity, const Vec3& grad_phi,
        const Vec3& grad_p, double rho) {
        return continuum::vorticity::crocco_gradient(velocity, vorticity, grad_phi, grad_p, rho);
    }
    static Vec3 baroclinic_term(const Vec3& grad_rho, const Vec3& grad_p, double rho) {
        return continuum::vorticity::baroclinic_term(grad_rho, grad_p, rho);
    }
    static Vec3 compute_vorticity_rhs(
        const Vec3& omega, const std::array<Vec3, 3>& grad_u, double div_u,
        const Vec3& grad_rho, const Vec3& grad_p, double rho) {
        return continuum::vorticity::compute_vorticity_rhs(omega, grad_u, div_u, grad_rho, grad_p, rho);
    }
};

} // namespace sst

#endif // SSTCORE_VORTICITY_DYNAMICS_H
