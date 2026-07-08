#ifndef SSTCORE_SST_KNOT_IDEAL_PARSER_H
#define SSTCORE_SST_KNOT_IDEAL_PARSER_H

#pragma once

// Fragment: include inside `class FourierKnot` (see sst/knot.h).

    struct IdealABComponent {
        int component_index = 0;
        Vec3 A0{0.0, 0.0, 0.0};
        Vec3 B0{0.0, 0.0, 0.0};
        FourierBlock fourier;
    };

    struct IdealABBlock {
        std::string id;
        std::string conway;
        double L = 0.0;
        double D = 0.0;
        int n = 1;
        std::string source_tag;
        std::vector<IdealABComponent> components;
        FourierBlock fourier;
    };

    static std::vector<IdealABBlock> parse_ideal_gilbert_from_string(const std::string& content);
    static std::vector<IdealABBlock> parse_ideal_txt_multi(const std::string& path);
    static std::vector<IdealABBlock> parse_ideal_txt_from_string(const std::string& content);
    static IdealABBlock parse_ideal_ab_by_id_from_string(const std::string& content, const std::string& ab_id);
    static IdealABBlock parse_ideal_ab_by_id_from_embedded(const std::string& ab_id,
                                                           const std::string& embedded_name = "ideal.txt");
    static int index_of_ideal_id(const std::vector<IdealABBlock>& blocks, const std::string& id);
    static std::string format_ideal_ab_header(const IdealABBlock& ab);
    static std::vector<Vec3> evaluate_ideal_component(const IdealABComponent& comp,
                                                      const std::vector<double>& s);
    static std::vector<std::vector<Vec3>> evaluate_ideal_ab_components(const IdealABBlock& ab,
                                                                       const std::vector<double>& s);

#endif // SSTCORE_SST_KNOT_IDEAL_PARSER_H
