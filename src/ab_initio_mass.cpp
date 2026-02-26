#include "ab_initio_mass.h"
#include "knot_files_embedded.h"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <knot_dynamics.h>
#include <regex>
#include <sstream>
#include <stdexcept>

namespace sst {

    static std::string load_ideal_database_from_file() {
        const char* paths[] = {
            "ideal_database.txt",
            "src/knot_fseries/ideal_database.txt",
            "../src/knot_fseries/ideal_database.txt",
            "../../src/knot_fseries/ideal_database.txt",
        };
        const char* env_path = std::getenv("SST_IDEAL_DATABASE");
        if (env_path && env_path[0] != '\0') {
            std::ifstream f(env_path);
            if (f) {
                std::ostringstream ss;
                ss << f.rdbuf();
                return ss.str();
            }
        }
        for (const char* p : paths) {
            std::ifstream f(p);
            if (f) {
                std::ostringstream ss;
                ss << f.rdbuf();
                return ss.str();
            }
        }
        return "";
    }

    ParticleEvaluator::ParticleEvaluator(const std::string& knot_ab_id, int resolution) {
        std::string db_content;
        auto embedded_files = get_embedded_knot_files();
        for (const auto& pair : embedded_files) {
            if (pair.first.find("ideal_database.txt") != std::string::npos) {
                db_content = pair.second;
                break;
            }
        }
        if (db_content.empty()) {
            db_content = load_ideal_database_from_file();
        }
        if (db_content.empty()) {
            throw std::runtime_error("[!] SSTcore: ideal_database.txt niet gevonden.");
        }

        if (!extract_and_build_filament(db_content, knot_ab_id, resolution)) {
            throw std::runtime_error("[!] SSTcore: Knoop ID " + knot_ab_id + " niet gevonden in database.");
        }
    }

    bool ParticleEvaluator::extract_and_build_filament(const std::string& db_content, const std::string& ab_id, int resolution) {
        std::string search_tag = "<AB Id=\"" + ab_id + "\"";
        size_t start_pos = db_content.find(search_tag);
        if (start_pos == std::string::npos) return false;

        size_t end_pos = db_content.find("</AB>", start_pos);
        if (end_pos == std::string::npos) return false;

        std::string block = db_content.substr(start_pos, end_pos - start_pos);
        std::vector<std::pair<Vec3, Vec3>> coeffs;
        coeffs.push_back({{0,0,0}, {0,0,0}});

        size_t coeff_pos = 0;
        while ((coeff_pos = block.find("<Coeff", coeff_pos)) != std::string::npos) {
            size_t end_coeff = block.find("/>", coeff_pos);
            if (end_coeff == std::string::npos) break;
            std::string line = block.substr(coeff_pos, end_coeff - coeff_pos);

            size_t a_start = line.find("A=\"");
            size_t b_start = line.find("B=\"");
            if (a_start != std::string::npos && b_start != std::string::npos) {
                a_start += 3; size_t a_end = line.find("\"", a_start);
                b_start += 3; size_t b_end = line.find("\"", b_start);
                if (a_end != std::string::npos && b_end != std::string::npos) {
                    std::string a_str = line.substr(a_start, a_end - a_start);
                    std::string b_str = line.substr(b_start, b_end - b_start);
                    Vec3 A_vec{0,0,0}, B_vec{0,0,0};
                    sscanf(a_str.c_str(), "%lf,%lf,%lf", &A_vec[0], &A_vec[1], &A_vec[2]);
                    sscanf(b_str.c_str(), "%lf,%lf,%lf", &B_vec[0], &B_vec[1], &B_vec[2]);
                    coeffs.push_back({A_vec, B_vec});
                }
            }
            coeff_pos = end_coeff + 2;
        }

        if (coeffs.size() <= 1) return false;

        filament_points.resize(resolution, {0.0, 0.0, 0.0});
        for (int i = 0; i < resolution; ++i) {
            double t = 2.0 * M_PI * i / resolution;
            Vec3 pt{0.0, 0.0, 0.0};
            for (size_t j = 1; j < coeffs.size(); ++j) {
                double c = std::cos(j * t);
                double s = std::sin(j * t);
                pt[0] += coeffs[j].first[0] * c + coeffs[j].second[0] * s;
                pt[1] += coeffs[j].first[1] * c + coeffs[j].second[1] * s;
                pt[2] += coeffs[j].first[2] * c + coeffs[j].second[2] * s;
            }
            filament_points[i] = pt;
        }
        return true;
    }

    void ParticleEvaluator::relax_hamiltonian(int iterations, double timestep, std::function<void()> interrupt_callback) {
        size_t N = filament_points.size();
        if (N < 3) return;

        double k_spring = 25.0;
        double k_pressure = 15.0;
        double k_repulsion = 0.5;
        double repulsion_radius = 0.2;

        std::vector<Vec3> velocities(N, {0.0, 0.0, 0.0});
        double damping = 0.70;

        auto start_time = std::chrono::high_resolution_clock::now();

        for (int iter = 0; iter < iterations; ++iter) {
            if (iter % 10 == 0 || iter == iterations - 1) {
                if (interrupt_callback) interrupt_callback();
                auto current_time = std::chrono::high_resolution_clock::now();
                std::chrono::duration<double> elapsed = current_time - start_time;
                double seconds = elapsed.count();
                double progress = (double)(iter + 1) / iterations;
                double eta = (seconds / (iter + 1)) * (iterations - (iter + 1));
                int barWidth = 40;
                std::cout << "\r    [";
                int pos = barWidth * progress;
                for (int i = 0; i < barWidth; ++i) {
                    if (i < pos) std::cout << "=";
                    else if (i == pos) std::cout << ">";
                    else std::cout << " ";
                }
                std::cout << "] " << std::setw(3) << int(progress * 100.0) << "% "
                          << "| ETA: " << std::fixed << std::setprecision(1) << eta << "s   ";
                std::cout.flush();
            }

            Vec3 centroid = {0.0, 0.0, 0.0};
            for (size_t i = 0; i < N; ++i) {
                centroid[0] += filament_points[i][0];
                centroid[1] += filament_points[i][1];
                centroid[2] += filament_points[i][2];
            }
            centroid[0] /= (double)N;
            centroid[1] /= (double)N;
            centroid[2] /= (double)N;

            std::vector<Vec3> forces(N, {0.0, 0.0, 0.0});

            #pragma omp parallel
            {
                std::vector<Vec3> local_forces(N, {0.0, 0.0, 0.0});

                #pragma omp for schedule(dynamic)
                for (int i = 0; i < (int)N; ++i) {
                    int prev = (i - 1 + N) % N;
                    int next = (i + 1) % N;
                    Vec3 pt = filament_points[i];
                    Vec3 p_prev = filament_points[prev];
                    Vec3 p_next = filament_points[next];

                    local_forces[i][0] += k_spring * ((p_prev[0] - pt[0]) + (p_next[0] - pt[0]));
                    local_forces[i][1] += k_spring * ((p_prev[1] - pt[1]) + (p_next[1] - pt[1]));
                    local_forces[i][2] += k_spring * ((p_prev[2] - pt[2]) + (p_next[2] - pt[2]));

                    local_forces[i][0] += k_pressure * (centroid[0] - pt[0]);
                    local_forces[i][1] += k_pressure * (centroid[1] - pt[1]);
                    local_forces[i][2] += k_pressure * (centroid[2] - pt[2]);

                    for (int j = 0; j < (int)N; ++j) {
                        if (i == j || j == prev || j == next) continue;
                        double dx = pt[0] - filament_points[j][0];
                        double dy = pt[1] - filament_points[j][1];
                        double dz = pt[2] - filament_points[j][2];
                        double dist_sq = dx*dx + dy*dy + dz*dz;

                        if (dist_sq < repulsion_radius * repulsion_radius && dist_sq > 1e-8) {
                            double dist = std::sqrt(dist_sq);
                            double rep = k_repulsion * (1.0 / (dist_sq * dist_sq));
                            if (rep > 200.0) rep = 200.0;
                            local_forces[i][0] += rep * (dx / dist);
                            local_forces[i][1] += rep * (dy / dist);
                            local_forces[i][2] += rep * (dz / dist);
                        }
                    }
                }
                #pragma omp critical
                {
                    for (int i = 0; i < (int)N; ++i) {
                        forces[i][0] += local_forces[i][0];
                        forces[i][1] += local_forces[i][1];
                        forces[i][2] += local_forces[i][2];
                    }
                }
            }

            for (int i = 0; i < (int)N; ++i) {
                velocities[i][0] = (velocities[i][0] + forces[i][0] * timestep) * damping;
                velocities[i][1] = (velocities[i][1] + forces[i][1] * timestep) * damping;
                velocities[i][2] = (velocities[i][2] + forces[i][2] * timestep) * damping;

                double v_sq = velocities[i][0]*velocities[i][0] + velocities[i][1]*velocities[i][1] + velocities[i][2]*velocities[i][2];
                if (v_sq > 10.0) {
                    double v_mag = std::sqrt(v_sq);
                    velocities[i][0] = (velocities[i][0] / v_mag) * 3.16;
                    velocities[i][1] = (velocities[i][1] / v_mag) * 3.16;
                    velocities[i][2] = (velocities[i][2] / v_mag) * 3.16;
                }

                filament_points[i][0] += velocities[i][0] * timestep;
                filament_points[i][1] += velocities[i][1] * timestep;
                filament_points[i][2] += velocities[i][2] * timestep;
            }
        }
        std::cout << std::endl;

        // --- 4. HORN TORUS SCHALING ---
        // Bereken eerst het finale zwaartepunt
        Vec3 centroid = {0.0, 0.0, 0.0};
        for (size_t i = 0; i < N; ++i) {
            centroid[0] += filament_points[i][0];
            centroid[1] += filament_points[i][1];
            centroid[2] += filament_points[i][2];
        }
        centroid[0] /= (double)N;
        centroid[1] /= (double)N;
        centroid[2] /= (double)N;

        // Zoek de maximale radiële extensie vanuit het zwaartepunt
        double max_dist_sq = 0.0;
        for (size_t i = 0; i < N; ++i) {
            double dx = filament_points[i][0] - centroid[0];
            double dy = filament_points[i][1] - centroid[1];
            double dz = filament_points[i][2] - centroid[2];
            double d_sq = dx*dx + dy*dy + dz*dz;
            if (d_sq > max_dist_sq) max_dist_sq = d_sq;
        }

        double r_raw = std::sqrt(max_dist_sq);
        if (r_raw < 1e-12) r_raw = 1e-6;

        // Fysische schaling: forceer de radiële bounding box naar 2 * r_c
        // Dit garandeert dat de totale diameter gelijk is aan de klassieke elektronstraal (4 * r_c)
        double scale = (2.0 * r_c) / r_raw;

        for (int i = 0; i < (int)N; ++i) {
            // Schaalt vanuit het zwaartepunt om translatiefouten te voorkomen
            filament_points[i][0] = centroid[0] + (filament_points[i][0] - centroid[0]) * scale;
            filament_points[i][1] = centroid[1] + (filament_points[i][1] - centroid[1]) * scale;
            filament_points[i][2] = centroid[2] + (filament_points[i][2] - centroid[2]) * scale;
        }
    }

    double ParticleEvaluator::get_dimless_ropelength() const {
        size_t N = filament_points.size();
        if (N < 2) return 0.0;

        double L_K = 0.0;
        for (size_t i = 0; i < N; ++i) {
            size_t next = (i + 1) % N;
            double dx = filament_points[next][0] - filament_points[i][0];
            double dy = filament_points[next][1] - filament_points[i][1];
            double dz = filament_points[next][2] - filament_points[i][2];
            L_K += std::sqrt(dx*dx + dy*dy + dz*dz);
        }

        return L_K / (2.0 * r_c);
    }

    double ParticleEvaluator::compute_invariant_mass_kg(double) const { return 0.0; }
    double ParticleEvaluator::get_pdg_equivalent_mass_mev() const { return 0.0; }
}