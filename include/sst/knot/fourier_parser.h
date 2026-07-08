#ifndef SSTCORE_SST_KNOT_FOURIER_PARSER_H
#define SSTCORE_SST_KNOT_FOURIER_PARSER_H

#pragma once

// Fragment: include inside `class FourierKnot` (see sst/knot.h).

    static std::vector<FourierBlock> parse_fseries_multi(const std::string& path);
    static std::vector<FourierBlock> parse_fseries_from_string(const std::string& content);
    static int index_of_largest_block(const std::vector<FourierBlock>& blocks);

#endif // SSTCORE_SST_KNOT_FOURIER_PARSER_H
