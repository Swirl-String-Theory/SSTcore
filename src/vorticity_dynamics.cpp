#include "sst/continuum/vorticity.h"
#include <cassert>

namespace sst::continuum::vorticity {

std::vector<double> compute_vorticity2D(
    const std::vector<double>& u,
    const std::vector<double>& v,
    int nx, int ny,
    double dx, double dy)
{
    assert(u.size() == v.size());
    const int N = nx * ny;
    std::vector<double> omega(static_cast<std::size_t>(N), 0.0);

    for (int j = 1; j < ny - 1; ++j) {
        for (int i = 1; i < nx - 1; ++i) {
            const int idx = i + j * nx;
            const double dvdx = (v[static_cast<std::size_t>(idx + 1)] - v[static_cast<std::size_t>(idx - 1)]) / (2 * dx);
            const double dudy = (u[static_cast<std::size_t>(idx + nx)] - u[static_cast<std::size_t>(idx - nx)]) / (2 * dy);
            omega[static_cast<std::size_t>(idx)] = dvdx - dudy;
        }
    }
    return omega;
}

double vorticity_z_2D(double dv_dx, double du_dy) { return dv_dx - du_dy; }
double local_circulation_density(double dv_dx, double du_dy) { return vorticity_z_2D(dv_dx, du_dy); }
double solid_body_rotation_vorticity(double omega) { return 2.0 * omega; }
double couette_vorticity(double alpha) { return -alpha; }

std::array<double, 3> crocco_relation(
    const std::array<double, 3>& vorticity,
    double rho,
    const std::array<double, 3>& pressure_gradient)
{
    (void)vorticity;
    return {
        pressure_gradient[0] / rho,
        pressure_gradient[1] / rho,
        pressure_gradient[2] / rho,
    };
}

Vec3 rotating_frame_rhs(
    const Vec3& velocity,
    const Vec3& vorticity,
    const Vec3& grad_phi,
    const Vec3& grad_p,
    const Vec3& omega,
    double rho)
{
    (void)vorticity;
    const Vec3 omega_cross_u = {
        omega[1] * velocity[2] - omega[2] * velocity[1],
        omega[2] * velocity[0] - omega[0] * velocity[2],
        omega[0] * velocity[1] - omega[1] * velocity[0],
    };
    Vec3 rhs;
    for (int i = 0; i < 3; ++i) {
        rhs[i] = -2.0 * omega_cross_u[i] - grad_phi[i] - grad_p[i] / rho;
    }
    return rhs;
}

Vec3 crocco_gradient(
    const Vec3& velocity,
    const Vec3& vorticity,
    const Vec3& grad_phi,
    const Vec3& grad_p,
    double rho)
{
    const Vec3 omega_cross_u = {
        vorticity[1] * velocity[2] - vorticity[2] * velocity[1],
        vorticity[2] * velocity[0] - vorticity[0] * velocity[2],
        vorticity[0] * velocity[1] - vorticity[1] * velocity[0],
    };
    Vec3 grad_H;
    for (int i = 0; i < 3; ++i) {
        grad_H[i] = rho * omega_cross_u[i] + grad_phi[i] + grad_p[i] / rho;
    }
    return grad_H;
}

Vec3 baroclinic_term(const Vec3& grad_rho, const Vec3& grad_p, double rho) {
    return {
        (grad_rho[1] * grad_p[2] - grad_rho[2] * grad_p[1]) / (rho * rho),
        (grad_rho[2] * grad_p[0] - grad_rho[0] * grad_p[2]) / (rho * rho),
        (grad_rho[0] * grad_p[1] - grad_rho[1] * grad_p[0]) / (rho * rho),
    };
}

Vec3 compute_vorticity_rhs(
    const Vec3& omega,
    const std::array<Vec3, 3>& grad_u,
    double div_u,
    const Vec3& grad_rho,
    const Vec3& grad_p,
    double rho)
{
    const Vec3 stretch = {
        omega[0] * grad_u[0][0] + omega[1] * grad_u[0][1] + omega[2] * grad_u[0][2],
        omega[0] * grad_u[1][0] + omega[1] * grad_u[1][1] + omega[2] * grad_u[1][2],
        omega[0] * grad_u[2][0] + omega[1] * grad_u[2][1] + omega[2] * grad_u[2][2],
    };
    const Vec3 compress = {-div_u * omega[0], -div_u * omega[1], -div_u * omega[2]};
    const Vec3 baroclinic = baroclinic_term(grad_rho, grad_p, rho);
    return {
        stretch[0] + compress[0] + baroclinic[0],
        stretch[1] + compress[1] + baroclinic[1],
        stretch[2] + compress[2] + baroclinic[2],
    };
}

} // namespace sst::continuum::vorticity
