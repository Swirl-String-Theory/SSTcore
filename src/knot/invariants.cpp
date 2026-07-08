#include "sst/knot.h"

#include "biot_savart.h"
#include "sst/knot/invariants_bridge.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <optional>
#include <random>
#include <stdexcept>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

        KnotInvariants build_invariants_from_fourier_block(
                const FourierBlock& block,
                const std::string& knot_name,
                int crossing_number,
                int braid_index,
                int seifert_genus,
                int chirality,
                bool hyperbolic,
                double hyperbolic_volume,
                int nsamples,
                int exclude_window) {
                KnotInvariants K;
                K.name = knot_name;
                K.crossing_number = crossing_number;
                K.braid_index = braid_index;
                K.seifert_genus = seifert_genus;
                K.chirality = std::max(-1, std::min(1, chirality));
                K.hyperbolic = hyperbolic;
                K.hyperbolic_volume = hyperbolic ? std::max(0.0, hyperbolic_volume) : 0.0;
                K.hyperbolic_volume_opt = K.hyperbolic ? std::optional<double>(K.hyperbolic_volume) : std::nullopt;

                FourierKnot::GeometricDescriptors g = FourierKnot::describe_fourier_block(
                        block,
                        std::max(64, nsamples),
                        std::max(1, exclude_window));

                K.writhe = g.writhe;
                K.min_self_distance = g.min_self_distance;
                K.bending_energy = g.bending_energy;

                // Resolved-tube metrics: Rawdon/Cantarella thickness = min(MinRad, dcsd/2).
                std::vector<double> svals;
                svals.reserve(static_cast<size_t>(std::max(64, nsamples)));
                for (int i = 0; i < std::max(64, nsamples); ++i) {
                        svals.push_back(2.0 * M_PI * static_cast<double>(i) /
                                        static_cast<double>(std::max(64, nsamples)));
                }
                const auto pts = FourierKnot::evaluate(block, svals);
                knot::fill_resolved_tube_fields(K, pts, exclude_window);

                // Backward compatibility: historical SSTcore used the diameter convention.
                K.ropelength_like = (K.ropelength_diam > 0.0)
                        ? K.ropelength_diam
                        : ((g.min_self_distance > 1e-12) ? (g.L / g.min_self_distance) : g.L);
                K.ropelength = K.ropelength_like;
                return K;
        }

        KnotInvariants build_invariants_from_fseries(
                const std::string& path,
                const std::string& knot_name,
                int crossing_number,
                int braid_index,
                int seifert_genus,
                int chirality,
                bool hyperbolic,
                double hyperbolic_volume,
                int nsamples,
                int exclude_window) {
                const std::vector<FourierBlock> blocks = FourierKnot::parse_fseries_multi(path);
                const int idx = FourierKnot::index_of_largest_block(blocks);
                if (idx < 0) {
                        throw std::runtime_error("build_invariants_from_fseries: no Fourier block in file: " + path);
                }
                std::string resolved_name = knot_name;
                if (resolved_name.empty()) {
                        resolved_name = path;
                        const size_t slash = resolved_name.find_last_of("/\\");
                        if (slash != std::string::npos) resolved_name = resolved_name.substr(slash + 1);
                }
                return build_invariants_from_fourier_block(
                        blocks[static_cast<size_t>(idx)],
                        resolved_name,
                        crossing_number,
                        braid_index,
                        seifert_genus,
                        chirality,
                        hyperbolic,
                        hyperbolic_volume,
                        nsamples,
                        exclude_window);
        }
        double KnotDynamics::compute_writhe(const std::vector<Vec3>& X) {
                double W = 0.0;
                size_t N = X.size();
                for (size_t i = 0; i < N - 1; ++i) {
                        for (size_t j = i + 1; j < N - 1; ++j) {
                                Vec3 r = diff(X[i], X[j]);
                                double r_norm = norm(r);
                                if (r_norm < 1e-6) continue;
                                Vec3 t1 = diff(X[i+1], X[i]);
                                Vec3 t2 = diff(X[j+1], X[j]);
                                W += dot(cross(t1, t2), r) / (r_norm * r_norm * r_norm);
                        }
                }
                return W / (2.0 * SST::Constants::pi);
        }

        int KnotDynamics::compute_linking_number(const std::vector<Vec3>& X, const std::vector<Vec3>& Y) {
                double Lk = 0.0;
                size_t N = X.size(), M = Y.size();
                for (size_t i = 0; i < N - 1; ++i) {
                        Vec3 xi = X[i];
                        Vec3 dx = diff(X[i+1], xi);
                        for (size_t j = 0; j < M - 1; ++j) {
                                Vec3 yj = Y[j];
                                Vec3 dy = diff(Y[j+1], yj);
                                Vec3 r = diff(xi, yj);
                                double r_norm = norm(r);
                                if (r_norm < 1e-6) continue;
                                Lk += dot(cross(dx, dy), r) / (r_norm * r_norm * r_norm);
                        }
                }
                return static_cast<int>(std::round(Lk / (4.0 * SST::Constants::pi)));
        }

        double KnotDynamics::compute_twist(const std::vector<Vec3>& T, const std::vector<Vec3>& B) {
                double Tw = 0.0;
                size_t N = T.size();
                for (size_t i = 1; i < N - 1; ++i) {
                        Vec3 dB = diff(B[i+1], B[i-1]);
                        Vec3 dB_ds = {dB[0]/2.0, dB[1]/2.0, dB[2]/2.0};
                        Tw += dot(cross(T[i], dB_ds), B[i]);
                }
                return Tw / (2.0 * SST::Constants::pi);
        }

        double KnotDynamics::compute_centerline_helicity(const std::vector<Vec3>& curve,
                                                                           const std::vector<Vec3>& tangent) {
                return compute_writhe(curve); // Simplified: H_cl ~ Wr for single loop
        }

        std::vector<std::pair<int, int>> KnotDynamics::detect_reconnection_candidates(
                        const std::vector<Vec3>& curve, double threshold) {
                std::vector<std::pair<int, int>> candidates;
                size_t N = curve.size();
                for (size_t i = 0; i < N; ++i) {
                        for (size_t j = i + 5; j < N; ++j) { // Skip close neighbors
                                Vec3 d = diff(curve[i], curve[j]);
                                if (norm(d) < threshold) {
                                        candidates.emplace_back(static_cast<int>(i), static_cast<int>(j));
                                }
                        }
                }
                return candidates;
        }

        // Fourier series evaluation (from heavy_knot)
        KnotDynamics::FourierResult KnotDynamics::evaluate_fourier_series(
                const std::vector<std::array<double, 6>>& coeffs,
                const std::vector<double>& t_vals) {
                size_t N = coeffs.size();
                size_t T = t_vals.size();
                FourierResult result;
                result.positions.resize(T);
                result.tangents.resize(T);

                for (size_t ti = 0; ti < T; ++ti) {
                        double t = t_vals[ti];
                        Vec3 r = {0, 0, 0}, r_t = {0, 0, 0};

                        for (size_t n = 0; n < N; ++n) {
                                double nt = n * t;
                                double cos_nt = std::cos(nt), sin_nt = std::sin(nt);
                                auto& c = coeffs[n];

                                r[0] += c[0]*cos_nt + c[1]*sin_nt;
                                r[1] += c[2]*cos_nt + c[3]*sin_nt;
                                r[2] += c[4]*cos_nt + c[5]*sin_nt;

                                if (n > 0) {
                                        r_t[0] += -n * c[0]*sin_nt + n * c[1]*cos_nt;
                                        r_t[1] += -n * c[2]*sin_nt + n * c[3]*cos_nt;
                                        r_t[2] += -n * c[4]*sin_nt + n * c[5]*cos_nt;
                                }
                        }

                        result.positions[ti] = r;
                        result.tangents[ti] = r_t;
                }
                return result;
        }

        // Writhe computation using Gauss integral with tangents (from heavy_knot)
        double KnotDynamics::writhe_gauss_curve(
                const std::vector<Vec3>& r,
                const std::vector<Vec3>& r_t) {
                const double pi = 3.141592653589793;
                size_t M = r.size();
                double sum = 0.0;
                double dt = 2 * pi / M;

                for (size_t i = 0; i < M; ++i) {
                        for (size_t j = 0; j < M; ++j) {
                                if (i == j) continue;
                                Vec3 dR = {
                                        r[i][0] - r[j][0],
                                        r[i][1] - r[j][1],
                                        r[i][2] - r[j][2]
                                };
                                double dist = std::sqrt(dR[0]*dR[0] + dR[1]*dR[1] + dR[2]*dR[2]);
                                if (dist < 1e-6) continue;

                                Vec3 Ti = r_t[i];
                                Vec3 Tj = r_t[j];
                                Vec3 cross = {
                                        Ti[1]*Tj[2] - Ti[2]*Tj[1],
                                        Ti[2]*Tj[0] - Ti[0]*Tj[2],
                                        Ti[0]*Tj[1] - Ti[1]*Tj[0]
                                };
                                double dot = cross[0]*dR[0] + cross[1]*dR[1] + cross[2]*dR[2];
                                sum += dot / (dist*dist*dist);
                        }
                }
                return (dt*dt * sum) / (4 * pi);
        }

        // Estimate crossing number from projections (from heavy_knot)
        int KnotDynamics::estimate_crossing_number(
                const std::vector<Vec3>& r,
                int directions,
                int seed) {
                size_t M = r.size();
                std::mt19937 gen(seed);
                std::normal_distribution<> d(0.0, 1.0);

                int min_cross = M*M;

                for (int d_iter = 0; d_iter < directions; ++d_iter) {
                        Vec3 w = {d(gen), d(gen), d(gen)};
                        double norm_w = std::sqrt(w[0]*w[0] + w[1]*w[1] + w[2]*w[2]);
                        for (auto& x : w) x /= norm_w + 1e-12;

                        Vec3 tmp = {1,0,0};
                        if (std::abs(w[0]) > 0.9) tmp = {0,1,0};

                        Vec3 u = {
                                w[1]*tmp[2] - w[2]*tmp[1],
                                w[2]*tmp[0] - w[0]*tmp[2],
                                w[0]*tmp[1] - w[1]*tmp[0]
                        };
                        double norm_u = std::sqrt(u[0]*u[0] + u[1]*u[1] + u[2]*u[2]);
                        for (auto& x : u) x /= norm_u + 1e-12;

                        Vec3 v = {
                                w[1]*u[2] - w[2]*u[1],
                                w[2]*u[0] - w[0]*u[2],
                                w[0]*u[1] - w[1]*u[0]
                        };

                        using Vec2 = std::array<double, 2>;
                        std::vector<Vec2> proj(M);
                        for (size_t i = 0; i < M; ++i) {
                                proj[i] = {r[i][0]*u[0] + r[i][1]*u[1] + r[i][2]*u[2],
                                           r[i][0]*v[0] + r[i][1]*v[1] + r[i][2]*v[2]};
                        }

                        int count = 0;
                        for (size_t i = 0; i < M; ++i) {
                                auto p1 = proj[i], p2 = proj[(i+1)%M];
                                for (size_t j = i+2; j < M; ++j) {
                                        if (j == (i-1+M)%M) continue;
                                        auto q1 = proj[j], q2 = proj[(j+1)%M];

                                        auto orient = [](const auto& a, const auto& b, const auto& c) {
                                                return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]);
                                        };
                                        double o1 = orient(p1,p2,q1);
                                        double o2 = orient(p1,p2,q2);
                                        double o3 = orient(q1,q2,p1);
                                        double o4 = orient(q1,q2,p2);
                                        if ((o1*o2 < 0) && (o3*o4 < 0)) ++count;
                                }
                        }

                        if (count < min_cross) min_cross = count;
                }

                return min_cross;
        }

        // Planar diagram from curve (from knot_pd)
        // Helper functions
        static inline double dot3(const Vec3& a, const Vec3& b){
                return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
        }
        static inline Vec3 cross3(const Vec3& a, const Vec3& b){
                return { a[1]*b[2]-a[2]*b[1],
                         a[2]*b[0]-a[0]*b[2],
                         a[0]*b[1]-a[1]*b[0] };
        }
        static inline double norm3(const Vec3& a){ return std::sqrt(dot3(a,a)); }

        static inline Vec3 unit_random_dir(std::mt19937& rng){
                std::normal_distribution<double> N(0.0,1.0);
                Vec3 v{N(rng),N(rng),N(rng)};
                const double n = norm3(v) + 1e-18;
                return {v[0]/n, v[1]/n, v[2]/n};
        }

        static inline void orthonormal_basis(const Vec3& n, Vec3& u, Vec3& v){
                const Vec3 a = (std::abs(n[0]) < 0.9) ? Vec3{1.0,0.0,0.0} : Vec3{0.0,1.0,0.0};
                u = cross3(n, a);
                const double un = norm3(u) + 1e-18;
                u = {u[0]/un, u[1]/un, u[2]/un};
                v = cross3(n, u);
        }

        using Vec2 = std::array<double, 2>;
        static inline void project_curve(const std::vector<Vec3>& P3,
                                         const Vec3& n,
                                         std::vector<Vec2>& P2,
                                         std::vector<double>& D)
        {
                Vec3 u, v;
                orthonormal_basis(n, u, v);
                const size_t N = P3.size();
                P2.resize(N);
                D.resize(N);
                for(size_t i=0;i<N;++i){
                        const Vec3& p = P3[i];
                        P2[i] = { dot3(p,u), dot3(p,v) };
                        D[i]  =  dot3(p,n);
                }
        }

        static inline std::optional<std::pair<double,double>>
        seg_intersection(const Vec2& p1, const Vec2& p2,
                         const Vec2& q1, const Vec2& q2,
                         double eps = 1e-12)
        {
                const double x1=p1[0], y1=p1[1];
                const double x2=p2[0], y2=p2[1];
                const double x3=q1[0], y3=q1[1];
                const double x4=q2[0], y4=q2[1];
                const double den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4);
                if(std::abs(den) < eps) return std::nullopt;

                const double lam = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / den;
                const double mu  = ((x1-x3)*(y1-y2) - (y1-y3)*(x1-x2)) / den;

                if(lam <= eps || lam >= 1.0-eps) return std::nullopt;
                if(mu  <= eps || mu  >= 1.0-eps) return std::nullopt;
                return std::make_pair(lam, mu);
        }

        static std::vector<KnotDynamics::Crossing> build_pd_from_projection(
                const std::vector<Vec2>& P2,
                const std::vector<double>& D,
                double min_angle_deg,
                double depth_tol)
        {
                const int N = static_cast<int>(P2.size());
                struct CrossingGeom { int i,j; double lam,mu; bool over_i; };
                std::vector<CrossingGeom> crosses;

                for(int i=0;i<N;++i){
                        const Vec2& p1 = P2[i];
                        const Vec2& p2 = P2[(i+1)%N];
                        for(int j=i+2;j<N;++j){
                                if(j==i || j==(i-1+N)%N || (i==0 && j==N-1)) continue;
                                const Vec2& q1 = P2[j];
                                const Vec2& q2 = P2[(j+1)%N];
                                auto ans = seg_intersection(p1,p2,q1,q2);
                                if(!ans) continue;

                                const double lam = ans->first, mu = ans->second;
                                const double Di = D[i] + lam*(D[(i+1)%N]-D[i]);
                                const double Dj = D[j] + mu*(D[(j+1)%N]-D[j]);
                                if(std::abs(Di - Dj) < depth_tol) continue;

                                const double dxi = p2[0]-p1[0], dyi = p2[1]-p1[1];
                                const double dxj = q2[0]-q1[0], dyj = q2[1]-q1[1];
                                const double dotv = dxi*dxj + dyi*dyj;
                                const double ni = std::hypot(dxi, dyi) + 1e-18;
                                const double nj = std::hypot(dxj, dyj) + 1e-18;
                                double cosang = dotv/(ni*nj);
                                cosang = std::max(-1.0, std::min(1.0, cosang));
                                const double ang = std::acos(std::abs(cosang))*180.0/M_PI;
                                if(ang < min_angle_deg) continue;

                                crosses.push_back({i,j,lam,mu,(Di>Dj)});
                        }
                }
                if(crosses.empty()) throw std::runtime_error("No crossings detected (projection not generic).");

                struct Event { double s; int cross_id; bool over; int in_lab; int out_lab; };
                std::vector<Event> ev;
                ev.reserve(crosses.size()*2);
                for(int cid=0; cid<(int)crosses.size(); ++cid){
                        const auto& c = crosses[cid];
                        ev.push_back({ (c.i + c.lam)/double(N), cid,  c.over_i, 0,0 });
                        ev.push_back({ (c.j + c.mu )/double(N), cid, !c.over_i, 0,0 });
                }
                std::sort(ev.begin(), ev.end(), [](const Event& a, const Event& b){ return a.s < b.s; });
                for(size_t k=1;k<ev.size();++k){
                        if(std::abs(ev[k].s - ev[k-1].s) < 1e-12) ev[k].s += 1e-9;
                }

                const int L = static_cast<int>(ev.size());
                for(int idx=0; idx<L; ++idx){
                        ev[idx].in_lab  = (idx>0 ? idx : L);
                        ev[idx].out_lab = (idx+1<=L ? idx+1 : 1);
                }

                std::vector<KnotDynamics::Crossing> pd; pd.reserve(crosses.size());
                for(int cid=0; cid<(int)crosses.size(); ++cid){
                        int a=-1,b=-1,c=-1,d=-1;
                        for(const auto& e : ev){
                                if(e.cross_id != cid) continue;
                                if(e.over){ b = e.in_lab; d = e.out_lab; }
                                else      { a = e.in_lab; c = e.out_lab; }
                        }
                        if(a>0 && b>0 && c>0 && d>0) pd.push_back({a,b,c,d});
                }

                std::vector<int> counts(L+1,0);
                for(const auto& t : pd){ for(int lab : t) counts[lab]++; }
                for(int lab=1; lab<=L; ++lab){
                        if(counts[lab] != 2)
                                throw std::runtime_error("PD validation failed (labels must appear exactly twice).");
                }
                return pd;
        }

        KnotDynamics::PD KnotDynamics::pd_from_curve(
                const std::vector<Vec3>& P3,
                int tries,
                unsigned int seed,
                double min_angle_deg,
                double depth_tol)
        {
                if(P3.size() < 4) throw std::invalid_argument("pd_from_curve: need at least 4 points");
                std::mt19937 rng(seed);
                PD best; int best_score = -1;

                for(int t=0; t<tries; ++t){
                        const Vec3 n = unit_random_dir(rng);
                        std::vector<Vec2> P2; std::vector<double> D;
                        project_curve(P3, n, P2, D);
                        try{
                                PD pd = build_pd_from_projection(P2, D, min_angle_deg, depth_tol);
                                const int score = (int)pd.size();
                                if(score > best_score){ best_score = score; best = std::move(pd); }
                        }catch(...){ /* try next */ }
                }
                if(best_score < 0) throw std::runtime_error("Failed to extract PD from any projection.");
                return best;
        }

        // Biot-Savart and helicity calculation wrappers
        std::vector<Vec3> KnotDynamics::compute_biot_savart_velocity_grid(
                const std::vector<Vec3>& curve,
                const std::vector<Vec3>& grid_points) {
                return BiotSavart::computeVelocity(curve, grid_points);
        }

        std::vector<Vec3> KnotDynamics::compute_vorticity_grid(
                const std::vector<Vec3>& velocity,
                const std::array<int, 3>& shape,
                double spacing) {
                return BiotSavart::computeVorticity(velocity, shape, spacing);
        }

        std::vector<Vec3> KnotDynamics::extract_interior_field(
                const std::vector<Vec3>& field,
                const std::array<int, 3>& shape,
                int margin) {
                return BiotSavart::extractInterior(field, shape, margin);
        }

        std::tuple<double, double, double> KnotDynamics::compute_helicity_invariants(
                const std::vector<Vec3>& v_sub,
                const std::vector<Vec3>& w_sub,
                const std::vector<double>& r_sq) {
                return BiotSavart::computeInvariants(v_sub, w_sub, r_sq);
        }

        std::tuple<double, double, double> KnotDynamics::compute_helicity_from_fourier_block(
                const FourierBlock& block,
                int grid_size,
                double spacing,
                int interior_margin,
                int nsamples) {
                // Evaluate Fourier block to get knot points
                std::vector<double> s(nsamples);
                const double twoPi = 2.0 * M_PI;
                for (int i = 0; i < nsamples; ++i) {
                        s[i] = twoPi * double(i) / double(nsamples - 1);
                }
                std::vector<Vec3> curve = FourierKnot::evaluate(block, s);
                curve = FourierKnot::center_points(curve);

                // Create grid (matching Python: spacing * (np.arange(grid_size) - grid_size // 2))
                std::vector<Vec3> grid_points;
                grid_points.reserve(grid_size * grid_size * grid_size);
                const int half_grid = grid_size / 2;  // Integer division to match Python //
                for (int i = 0; i < grid_size; ++i) {
                        for (int j = 0; j < grid_size; ++j) {
                                for (int k = 0; k < grid_size; ++k) {
                                        double x = spacing * (i - half_grid);
                                        double y = spacing * (j - half_grid);
                                        double z = spacing * (k - half_grid);
                                        grid_points.push_back({x, y, z});
                                }
                        }
                }

                // Compute velocity on grid
                std::vector<Vec3> velocity = BiotSavart::computeVelocity(curve, grid_points);

                // Compute vorticity
                std::array<int, 3> shape = {grid_size, grid_size, grid_size};
                std::vector<Vec3> vorticity = BiotSavart::computeVorticity(velocity, shape, spacing);

                // Extract interior fields
                std::vector<Vec3> v_sub = BiotSavart::extractInterior(velocity, shape, interior_margin);
                std::vector<Vec3> w_sub = BiotSavart::extractInterior(vorticity, shape, interior_margin);

                // Compute r_sq for interior points (matching Python interior_vals)
                std::vector<double> r_sq;
                r_sq.reserve(v_sub.size());
                const int interior_size = grid_size - 2 * interior_margin;
                for (int i = 0; i < interior_size; ++i) {
                        for (int j = 0; j < interior_size; ++j) {
                                for (int k = 0; k < interior_size; ++k) {
                                        double x = spacing * (i + interior_margin - half_grid);
                                        double y = spacing * (j + interior_margin - half_grid);
                                        double z = spacing * (k + interior_margin - half_grid);
                                        r_sq.push_back(x*x + y*y + z*z);
                                }
                        }
                }

                // Compute invariants
                return BiotSavart::computeInvariants(v_sub, w_sub, r_sq);
        }

} // namespace sst
