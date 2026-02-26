#include <iostream>
#include <vector>
#include <cmath>
#include <omp.h>

// --- SST Canon Constants ---
constexpr double C_LIGHT = 299792458.0;
constexpr double R_C = 1.40897017e-15;          // Core radius (m)
constexpr double V_SWIRL = 1.09384563e6;        // Swirl speed (m/s)
constexpr double RHO_CORE = 3.8934358266918687e18; // Core density (kg/m^3)
constexpr double RHO_F = 7.0e-7;                // Fluid density (kg/m^3)
constexpr double PI = 3.14159265358979323846;

struct Vec3 {
    double x, y, z;
};

// Vector math helpers
inline Vec3 subtract(const Vec3& a, const Vec3& b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
inline double dot_product(const Vec3& a, const Vec3& b) { return a.x*b.x + a.y*b.y + a.z*b.z; }
inline double norm_squared(const Vec3& a) { return a.x*a.x + a.y*a.y + a.z*a.z; }
inline double norm(const Vec3& a) { return std::sqrt(norm_squared(a)); }

void compute_sst_mass(const std::vector<Vec3>& points, double chi_spin, double& m_core, double& m_fluid) {
    size_t N = points.size();
    std::vector<Vec3> dp(N);
    double L_K = 0.0;

    // 1. Calculate tangent vectors (ds) and total length L_K
    for (size_t i = 0; i < N; ++i) {
        size_t next = (i + 1) % N;
        dp[i] = subtract(points[next], points[i]);
        L_K += norm(dp[i]);
    }

    // Static Core Mass
    m_core = PI * (R_C * R_C) * RHO_CORE * L_K;

    // 2. Compute the Neumann Mutual Inductance Integral (O(N^2) - Parallelized)
    double neumann_integral = 0.0;
    double r_c_sq = R_C * R_C;

    #pragma omp parallel for reduction(+:neumann_integral) schedule(dynamic)
    for (size_t i = 0; i < N; ++i) {
        double local_sum = 0.0;
        for (size_t j = 0; j < N; ++j) {
            Vec3 r_diff = subtract(points[i], points[j]);
            double dist_sq = norm_squared(r_diff);
            
            // Rosenhead-Moore Regularization avoids divergence at r -> 0
            double denom = std::sqrt(dist_sq + r_c_sq);
            double num = dot_product(dp[i], dp[j]);
            
            local_sum += num / denom;
        }
        neumann_integral += local_sum;
    }

    // 3. Fluid Mass (Hydrodynamic Dressing)
    double gamma = 2.0 * PI * R_C * V_SWIRL;
    double e_fluid = (RHO_F * gamma * gamma / (8.0 * PI)) * (chi_spin * chi_spin) * neumann_integral;
    
    m_fluid = e_fluid / (C_LIGHT * C_LIGHT);
}

int main() {
    // Example: Generate a simple 4000-point circle (unknot proxy) to test performance
    int N = 4000;
    std::vector<Vec3> ring(N);
    double R_ring = 1e-14; // 10 fm radius
    
    for(int i=0; i<N; ++i) {
        double theta = 2.0 * PI * i / N;
        ring[i] = { R_ring * std::cos(theta), R_ring * std::sin(theta), 0.0 };
    }

    double m_core = 0.0, m_fluid = 0.0;
    double chi_spin = 2.0; // Fermion

    std::cout << "[*] Running high-res SST integration on " << N << " points with OpenMP...\n";
    
    double start_time = omp_get_wtime();
    compute_sst_mass(ring, chi_spin, m_core, m_fluid);
    double end_time = omp_get_wtime();

    double m_tot_mev = (m_core + m_fluid) / 1.78266192e-30;

    std::cout << "[+] Integration complete in " << (end_time - start_time) << " seconds.\n";
    std::cout << "    M_core  : " << (m_core / 1.78266192e-30) << " MeV/c^2\n";
    std::cout << "    M_fluid : " << (m_fluid / 1.78266192e-30) << " MeV/c^2\n";
    std::cout << "    M_total : " << m_tot_mev << " MeV/c^2\n";

    return 0;
}