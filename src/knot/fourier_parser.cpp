#include "sst/knot.h"

#include <fstream>
#include <sstream>
#include <string>
#include <vector>

namespace sst {

        std::vector<FourierBlock> FourierKnot::parse_fseries_multi(const std::string& path) {
                std::ifstream in(path);
                std::vector<FourierBlock> blocks;
                if (!in) return blocks;

                FourierBlock cur;
                auto flush_block = [&]() {
                        if (!cur.a_x.empty()) {
                                blocks.emplace_back(cur);
                                cur = FourierBlock{};
                        }
                };

                std::string line;
                while (std::getline(in, line)) {
                        // trim
                        while (!line.empty() && (line.back()=='\r' || line.back()=='\n' || line.back()==' ' || line.back()=='\t')) line.pop_back();
                        if (line.empty()) { flush_block(); continue; }
                        if (line.size() && line[0] == '%') {
                                flush_block();
                                cur.header = std::string(line.begin()+1, line.end());
                                // trim leading spaces
                                while (!cur.header.empty() && (cur.header.front()==' ' || cur.header.front()=='\t')) cur.header.erase(cur.header.begin());
                                continue;
                        }
                        std::istringstream iss(line);
                        double ax,bx,ay,by,az,bz;
                        if (iss >> ax >> bx >> ay >> by >> az >> bz) {
                                cur.a_x.push_back(ax); cur.b_x.push_back(bx);
                                cur.a_y.push_back(ay); cur.b_y.push_back(by);
                                cur.a_z.push_back(az); cur.b_z.push_back(bz);
                        }
                }
                flush_block();
                return blocks;
        }

        std::vector<FourierBlock> FourierKnot::parse_fseries_from_string(const std::string& content) {
                std::istringstream in(content);
                std::vector<FourierBlock> blocks;
                
                FourierBlock cur;
                auto flush_block = [&]() {
                        if (!cur.a_x.empty()) {
                                blocks.emplace_back(cur);
                                cur = FourierBlock{};
                        }
                };

                std::string line;
                while (std::getline(in, line)) {
                        // trim
                        while (!line.empty() && (line.back()=='\r' || line.back()=='\n' || line.back()==' ' || line.back()=='\t')) line.pop_back();
                        if (line.empty()) { flush_block(); continue; }
                        if (line.size() && line[0] == '%') {
                                flush_block();
                                cur.header = std::string(line.begin()+1, line.end());
                                // trim leading spaces
                                while (!cur.header.empty() && (cur.header.front()==' ' || cur.header.front()=='\t')) cur.header.erase(cur.header.begin());
                                continue;
                        }
                        std::istringstream iss(line);
                        double ax,bx,ay,by,az,bz;
                        if (iss >> ax >> bx >> ay >> by >> az >> bz) {
                                cur.a_x.push_back(ax); cur.b_x.push_back(bx);
                                cur.a_y.push_back(ay); cur.b_y.push_back(by);
                                cur.a_z.push_back(az); cur.b_z.push_back(bz);
                        }
                }
                flush_block();
                return blocks;
        }

        int FourierKnot::index_of_largest_block(const std::vector<FourierBlock>& blocks) {
                if (blocks.empty()) return -1;
                int idx = 0;
                size_t best = blocks[0].a_x.size();
                for (int i=1;i<(int)blocks.size();++i) {
                        size_t n = blocks[i].a_x.size();
                        if (n > best) { best = n; idx = i; }
                }
                return idx;
        }

} // namespace sst
