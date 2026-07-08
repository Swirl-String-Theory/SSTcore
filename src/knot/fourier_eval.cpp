#include "sst/knot.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

        std::vector<Vec3> FourierKnot::evaluate(const FourierBlock& b, const std::vector<double>& s) {
                const int N = (int)b.a_x.size();
                std::vector<Vec3> out(s.size(), {0.0,0.0,0.0});
                for (size_t i=0;i<s.size();++i) {
                        double si = s[i];
                        double x=0, y=0, z=0;
                        for (int j=0;j<N;++j) {
                                int n = j+1;
                                double cn = std::cos(n*si), sn = std::sin(n*si);
                                x += b.a_x[j]*cn + b.b_x[j]*sn;
                                y += b.a_y[j]*cn + b.b_y[j]*sn;
                                z += b.a_z[j]*cn + b.b_z[j]*sn;
                        }
                        out[i] = {x,y,z};
                }
                return out;
        }

        std::vector<Vec3> FourierKnot::center_points(const std::vector<Vec3>& pts) {
                if (pts.empty()) return {};
                double cx=0, cy=0, cz=0;
                for (auto &p: pts) { cx+=p[0]; cy+=p[1]; cz+=p[2]; }
                cx/=pts.size(); cy/=pts.size(); cz/=pts.size();
                std::vector<Vec3> out; out.reserve(pts.size());
                for (auto &p: pts) out.push_back({p[0]-cx, p[1]-cy, p[2]-cz});
                return out;
        }

        std::vector<double> FourierKnot::curvature(const std::vector<Vec3>& pts, double eps) {
                const int n = (int)pts.size();
                std::vector<double> k(n, 0.0);
                if (n < 3) return k;

                auto minus = [](const Vec3& a, const Vec3& b)->Vec3 { return {a[0]-b[0], a[1]-b[1], a[2]-b[2]}; };
                auto cross = [](const Vec3& a, const Vec3& b)->Vec3 {
                        return {a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]};
                };
                auto norm = [](const Vec3& a)->double { return std::sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]); };

                // Uniform parameterization, periodic central differences
                for (int i=0;i<n;++i) {
                        const Vec3& pm = pts[(i-1+n)%n];
                        const Vec3& p0 = pts[i];
                        const Vec3& pp = pts[(i+1)%n];
                        // first derivative ~ (pp - pm)/2
                        Vec3 r1 = { (pp[0]-pm[0])*0.5, (pp[1]-pm[1])*0.5, (pp[2]-pm[2])*0.5 };
                        // second derivative ~ (pp - 2*p0 + pm)
                        Vec3 r2 = { pp[0]-2*p0[0]+pm[0], pp[1]-2*p0[1]+pm[1], pp[2]-2*p0[2]+pm[2] };
                        Vec3 cr = cross(r1, r2);
                        double num = norm(cr);
                        double den = std::pow(norm(r1), 3.0) + eps;
                        k[i] = num / den;
                }
                return k;
        }

        std::pair<std::vector<Vec3>, std::vector<double>>
        FourierKnot::load_knot(const std::string& path, int nsamples) {
                auto blocks = parse_fseries_multi(path);
                int idx = index_of_largest_block(blocks);
                if (idx < 0) return {{}, {}};
                std::vector<double> s(nsamples);
                const double twoPi = 6.2831853071795864769;
                for (int i=0;i<nsamples;++i) s[i] = twoPi * double(i) / double(nsamples-1);
                auto pts = center_points(evaluate(blocks[idx], s));
                auto kap = curvature(pts);
                return {pts, kap};
        }

        std::vector<FourierKnot::LoadedKnot>
        FourierKnot::load_all_knots(const std::vector<std::string>& paths, int nsamples) {
                std::vector<LoadedKnot> result;
                result.reserve(paths.size());

                for (const auto& path : paths) {
                        // Extract filename without extension
                        std::string name = path;
                        size_t last_slash = name.find_last_of("/\\");
                        if (last_slash != std::string::npos) {
                                name = name.substr(last_slash + 1);
                        }
                        size_t last_dot = name.find_last_of('.');
                        if (last_dot != std::string::npos) {
                                name = name.substr(0, last_dot);
                        }
                        // Remove 'knot' or 'Knot' from name (matching Python behavior)
                        std::string lower_name = name;
                        std::transform(lower_name.begin(), lower_name.end(), lower_name.begin(), ::tolower);
                        size_t pos = lower_name.find("knot");
                        if (pos != std::string::npos) {
                                name.erase(pos, 4);
                        }

                        // Load the knot
                        auto [pts, curv] = load_knot(path, nsamples);
                        if (!pts.empty()) {
                                LoadedKnot knot;
                                knot.name = name;
                                knot.points = std::move(pts);
                                knot.curvature = std::move(curv);
                                result.push_back(std::move(knot));
                        }
                }
                return result;
        }

        void FourierKnot::loadBlocks(const std::string& filename) {
                blocks.clear();
                std::ifstream file(filename);
                if (!file.is_open()) {
                        throw std::runtime_error("Cannot open file: " + filename);
                }

                FourierBlock current;
                std::string line;
                while (std::getline(file, line)) {
                        // trim
                        if (line.empty()) {
                                if (!current.a_x.empty()) {
                                        blocks.push_back(current);
                                        current = FourierBlock{};
                                }
                                continue;
                        }
                        if (line[0] == '%') {
                                if (!current.a_x.empty()) {
                                        blocks.push_back(current);
                                        current = FourierBlock{};
                                }
                                continue;
                        }

                        std::istringstream iss(line);
                        std::vector<double> parts;
                        double val;
                        while (iss >> val) parts.push_back(val);

                        if (parts.size() == 6) {
                                current.a_x.push_back(parts[0]);
                                current.b_x.push_back(parts[1]);
                                current.a_y.push_back(parts[2]);
                                current.b_y.push_back(parts[3]);
                                current.a_z.push_back(parts[4]);
                                current.b_z.push_back(parts[5]);
                        }
                }
                if (!current.a_x.empty()) {
                        blocks.push_back(current);
                }
        }

        void FourierKnot::selectMaxHarmonics() {
                if (blocks.empty()) {
                        throw std::runtime_error("No Fourier blocks loaded");
                }
                size_t maxSize = 0;
                size_t maxIdx = 0;
                for (size_t i = 0; i < blocks.size(); ++i) {
                        if (blocks[i].a_x.size() > maxSize) {
                                maxSize = blocks[i].a_x.size();
                                maxIdx = i;
                        }
                }
                activeBlock = blocks[maxIdx];
        }

        void FourierKnot::reconstruct(size_t N) {
                if (activeBlock.a_x.empty()) {
                        throw std::runtime_error("No active Fourier block selected");
                }
                points.clear();
                points.reserve(N);
                double step = 2.0 * M_PI / static_cast<double>(N);
                for (size_t i = 0; i < N; ++i) {
                        double s = step * static_cast<double>(i);
                        points.push_back(evalPoint(activeBlock, s));
                }
        }

        Vec3 FourierKnot::evalPoint(const FourierBlock& blk, double s) {
                double x = 0.0, y = 0.0, z = 0.0;
                size_t N = blk.a_x.size();
                for (size_t j = 0; j < N; ++j) {
                        auto n = static_cast<double>(j + 1);
                        double cs = std::cos(n * s);
                        double sn = std::sin(n * s);
                        x += blk.a_x[j] * cs + blk.b_x[j] * sn;
                        y += blk.a_y[j] * cs + blk.b_y[j] * sn;
                        z += blk.a_z[j] * cs + blk.b_z[j] * sn;
                }
                return Vec3{x, y, z};
        }

} // namespace sst

namespace {
static inline double _sst_norm(const sst::Vec3& v) {
    return std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
}
static inline sst::Vec3 _sst_cross(const sst::Vec3& a, const sst::Vec3& b) {
    return sst::Vec3{a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]};
}
static inline sst::Vec3 _sst_sub(const sst::Vec3& a, const sst::Vec3& b) {
    return sst::Vec3{a[0]-b[0], a[1]-b[1], a[2]-b[2]};
}
}

std::tuple<sst::Vec3, sst::Vec3, sst::Vec3, sst::Vec3>
sst::FourierKnot::evaluate_with_derivatives(const FourierBlock& b, double s) {
    const size_t n = std::max({b.a_x.size(), b.b_x.size(), b.a_y.size(), b.b_y.size(), b.a_z.size(), b.b_z.size()});
    Vec3 r{0,0,0}, r1{0,0,0}, r2{0,0,0}, r3{0,0,0};
    for (size_t k = 0; k < n; ++k) {
        double j = double(k + 1);
        double c = std::cos(j * s), q = std::sin(j * s);
        double ax = k < b.a_x.size() ? b.a_x[k] : 0.0; double bx = k < b.b_x.size() ? b.b_x[k] : 0.0;
        double ay = k < b.a_y.size() ? b.a_y[k] : 0.0; double by = k < b.b_y.size() ? b.b_y[k] : 0.0;
        double az = k < b.a_z.size() ? b.a_z[k] : 0.0; double bz = k < b.b_z.size() ? b.b_z[k] : 0.0;
        r[0]  += ax*c + bx*q; r[1]  += ay*c + by*q; r[2]  += az*c + bz*q;
        r1[0] += -j*ax*q + j*bx*c; r1[1] += -j*ay*q + j*by*c; r1[2] += -j*az*q + j*bz*c;
        r2[0] += -j*j*ax*c - j*j*bx*q; r2[1] += -j*j*ay*c - j*j*by*q; r2[2] += -j*j*az*c - j*j*bz*q;
        r3[0] +=  j*j*j*ax*q - j*j*j*bx*c; r3[1] +=  j*j*j*ay*q - j*j*j*by*c; r3[2] +=  j*j*j*az*q - j*j*j*bz*c;
    }
    return {r, r1, r2, r3};
}

std::vector<double> sst::FourierKnot::curvature_exact(const FourierBlock& block, const std::vector<double>& s, double eps) {
    std::vector<double> out; out.reserve(s.size());
    for (double si : s) {
        auto [r, r1, r2, r3] = evaluate_with_derivatives(block, si); (void)r; (void)r3;
        Vec3 c = _sst_cross(r1, r2);
        double den = std::pow(std::max(_sst_norm(r1), eps), 3.0);
        out.push_back(_sst_norm(c) / den);
    }
    return out;
}

double sst::FourierKnot::length_exact(const FourierBlock& block, int nsamples) {
    nsamples = std::max(nsamples, 16);
    double ds = 2.0 * M_PI / double(nsamples), acc = 0.0;
    for (int i = 0; i < nsamples; ++i) {
        auto [r, r1, r2, r3] = evaluate_with_derivatives(block, ds * i); (void)r; (void)r2; (void)r3;
        acc += _sst_norm(r1) * ds;
    }
    return acc;
}

double sst::FourierKnot::bending_energy_exact(const FourierBlock& block, int nsamples, double eps) {
    nsamples = std::max(nsamples, 32);
    double ds = 2.0 * M_PI / double(nsamples), acc = 0.0;
    for (int i = 0; i < nsamples; ++i) {
        auto [r, r1, r2, r3] = evaluate_with_derivatives(block, ds * i); (void)r; (void)r3;
        double v = std::max(_sst_norm(r1), eps);
        double kappa = _sst_norm(_sst_cross(r1, r2)) / (v*v*v);
        acc += (kappa*kappa) * v * ds;
    }
    return acc;
}

std::vector<double> sst::FourierKnot::mode_energies(const FourierBlock& block) {
    size_t n = std::max({block.a_x.size(), block.b_x.size(), block.a_y.size(), block.b_y.size(), block.a_z.size(), block.b_z.size()});
    std::vector<double> e(n, 0.0);
    for (size_t k = 0; k < n; ++k) {
        double ax = k < block.a_x.size() ? block.a_x[k] : 0.0; double bx = k < block.b_x.size() ? block.b_x[k] : 0.0;
        double ay = k < block.a_y.size() ? block.a_y[k] : 0.0; double by = k < block.b_y.size() ? block.b_y[k] : 0.0;
        double az = k < block.a_z.size() ? block.a_z[k] : 0.0; double bz = k < block.b_z.size() ? block.b_z[k] : 0.0;
        e[k] = ax*ax + bx*bx + ay*ay + by*by + az*az + bz*bz;
    }
    return e;
}

double sst::FourierKnot::min_self_distance_sampled(const std::vector<Vec3>& pts, int exclude_window) {
    if (pts.size() < 4) return 0.0;
    int N = int(pts.size());
    double dmin = std::numeric_limits<double>::infinity();
    for (int i = 0; i < N; ++i) {
        for (int j = i + 1; j < N; ++j) {
            int cyc = std::min(std::abs(j - i), N - std::abs(j - i));
            if (cyc <= exclude_window) continue;
            double d = _sst_norm(_sst_sub(pts[(size_t)i], pts[(size_t)j]));
            if (d < dmin) dmin = d;
        }
    }
    return std::isfinite(dmin) ? dmin : 0.0;
}

double sst::FourierKnot::min_self_distance_exactish(const FourierBlock& block, int nsamples, int exclude_window) {
    nsamples = std::max(nsamples, 64);
    std::vector<double> s; s.reserve((size_t)nsamples);
    for (int i = 0; i < nsamples; ++i) s.push_back(2.0 * M_PI * double(i) / double(nsamples));
    auto pts = evaluate(block, s);
    return min_self_distance_sampled(pts, exclude_window);
}

sst::FourierKnot::GeometricDescriptors
sst::FourierKnot::describe_fourier_block(const FourierBlock& block, int nsamples, int exclude_window) {
    GeometricDescriptors g;
    nsamples = std::max(nsamples, 64);
    std::vector<double> s; s.reserve((size_t)nsamples);
    for (int i = 0; i < nsamples; ++i) s.push_back(2.0 * M_PI * double(i) / double(nsamples));
    auto pts = evaluate(block, s);
    g.L = length_exact(block, std::max(512, 4 * nsamples));
    g.bending_energy = bending_energy_exact(block, std::max(512, 4 * nsamples));
    g.min_self_distance = min_self_distance_sampled(pts, exclude_window);
    g.writhe = KnotDynamics::compute_writhe(pts);
    g.mode_energy = mode_energies(block);
    return g;
}
