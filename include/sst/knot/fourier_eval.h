#ifndef SSTCORE_SST_KNOT_FOURIER_EVAL_H
#define SSTCORE_SST_KNOT_FOURIER_EVAL_H

#pragma once

// Fragment: include inside `class FourierKnot` (see sst/knot.h).

    struct Block {
        std::vector<double> a_x, b_x, a_y, b_y, a_z, b_z;
    };

    struct LoadedKnot {
        std::string name;
        std::vector<Vec3> points;
        std::vector<double> curvature;
    };

    struct GeometricDescriptors {
        double L = 0.0;
        double bending_energy = 0.0;
        double min_self_distance = 0.0;
        double writhe = 0.0;
        std::vector<double> mode_energy;
    };

    std::vector<FourierBlock> blocks;
    FourierBlock activeBlock;
    std::vector<Vec3> points;

    void loadBlocks(const std::string& filename);
    void selectMaxHarmonics();
    void reconstruct(size_t N = 1000);

    static std::vector<Vec3> evaluate(const FourierBlock& block, const std::vector<double>& s);
    static std::vector<Vec3> center_points(const std::vector<Vec3>& pts);
    static std::vector<double> curvature(const std::vector<Vec3>& pts, double eps = 1e-8);
    static std::pair<std::vector<Vec3>, std::vector<double>>
    load_knot(const std::string& path, int nsamples);
    static std::vector<LoadedKnot>
    load_all_knots(const std::vector<std::string>& paths, int nsamples = 1000);
    static std::tuple<Vec3, Vec3, Vec3, Vec3> evaluate_with_derivatives(const FourierBlock& block, double s);
    static std::vector<double> curvature_exact(const FourierBlock& block,
                                               const std::vector<double>& s,
                                               double eps = 1e-12);
    static double length_exact(const FourierBlock& block, int nsamples = 4096);
    static double bending_energy_exact(const FourierBlock& block, int nsamples = 4096, double eps = 1e-12);
    static std::vector<double> mode_energies(const FourierBlock& block);
    static double min_self_distance_sampled(const std::vector<Vec3>& pts, int exclude_window = 4);
    static double min_self_distance_exactish(const FourierBlock& block, int nsamples = 2048, int exclude_window = 4);
    static GeometricDescriptors describe_fourier_block(const FourierBlock& block,
                                                       int nsamples = 2048,
                                                       int exclude_window = 4);
    static Vec3 evalPoint(const FourierBlock& blk, double s);

#endif // SSTCORE_SST_KNOT_FOURIER_EVAL_H
