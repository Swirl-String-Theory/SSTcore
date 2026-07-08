#include "sst/knot/resource_loader.h"

#include <cctype>
#include <cstdlib>
#include <fstream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <vector>

#include "knot_files_embedded.h"

namespace sst {

        std::string load_embedded_ideal_text(const std::string& name) {
                static std::map<std::string, std::string> ideal_files = get_embedded_ideal_files();

                auto it = ideal_files.find(name);
                if (it != ideal_files.end()) return it->second;

                // Friendly fallback: allow basename lookup if caller passes "ideal.txt"
                for (const auto& kv : ideal_files) {
                        const std::string& key = kv.first;
                        auto slash = key.find_last_of("/\\");
                        std::string base = (slash == std::string::npos) ? key : key.substr(slash + 1);
                        if (base == name) return kv.second;
                }

                throw std::runtime_error("Embedded ideal text not found: " + name);
        }
        namespace {
        static inline bool path_exists(const std::string& path) {
                std::ifstream f(path);
                return f.good();
        }
        }

        std::string find_knot_file_path(const std::string& knot_id, const std::string& explicit_base) {
                const std::string filename = "knot." + knot_id + ".fseries";

                // 1) Explicit path parameter
                if (!explicit_base.empty()) {
                        std::string p = explicit_base + "/" + filename;
                        if (path_exists(p)) return p;
                        p = explicit_base + "/knot_fseries/" + filename;
                        if (path_exists(p)) return p;
                }

                // 2) Env SST_KNOT_DATA_DIR (direct dir containing knot.XX.fseries)
                if (const char* env = std::getenv("SST_KNOT_DATA_DIR")) {
                        std::string p = std::string(env) + "/" + filename;
                        if (path_exists(p)) return p;
                }
                // Env SST_RESOURCE_DIR (resource root: .../share/sstcore or .../resources)
                if (const char* env = std::getenv("SST_RESOURCE_DIR")) {
                        std::string base(env);
                        std::string p = base + "/resources/knot_fseries/" + filename;
                        if (path_exists(p)) return p;
                        p = base + "/knot_fseries/" + filename;
                        if (path_exists(p)) return p;
                }

                // 3) Build tree / 4) Installed share (relative to cwd)
#ifdef SST_DEFAULT_KNOT_FSERIES_SUBDIR
                {
                        std::string p = std::string(SST_DEFAULT_KNOT_FSERIES_SUBDIR) + "/" + filename;
                        if (path_exists(p)) return p;
                }
#endif
                // 5) Legacy development paths
                std::vector<std::string> legacy = {
                        "src/knot_fseries",
                        "src/Knots_FourierSeries",
                        "../src/knot_fseries",
                        "../src/Knots_FourierSeries",
                        "../../src/knot_fseries",
                        "../../src/Knots_FourierSeries",
                        "knot_fseries",
                        "../knot_fseries",
                        "share/sstcore/knot_fseries",
                        "../../share/sstcore/knot_fseries",
                        "share/swirl_string_core/knot_fseries",
                };
#if defined(_WIN32)
                legacy.push_back("../../share/swirl_string_core/knot_fseries");
#else
                legacy.push_back("/usr/local/share/sstcore/knot_fseries");
                legacy.push_back("/usr/share/sstcore/knot_fseries");
                legacy.push_back("../../share/swirl_string_core/knot_fseries");
                legacy.push_back("/usr/local/share/swirl_string_core/knot_fseries");
                legacy.push_back("/usr/share/swirl_string_core/knot_fseries");
#endif
                for (const auto& base : legacy) {
                        std::string p = base + "/" + filename;
                        if (path_exists(p)) return p;
                }
                return {};
        }

        std::string find_ideal_file_path(const std::string& filename, const std::string& explicit_base) {
                // 1) Explicit path parameter
                if (!explicit_base.empty()) {
                        std::string p = explicit_base + "/" + filename;
                        if (path_exists(p)) return p;
                        p = explicit_base + "/resources/" + filename;
                        if (path_exists(p)) return p;
                }

                // 2) Env SST_RESOURCE_DIR
                if (const char* env = std::getenv("SST_RESOURCE_DIR")) {
                        std::string base(env);
                        std::string p = base + "/" + filename;
                        if (path_exists(p)) return p;
                        p = base + "/resources/" + filename;
                        if (path_exists(p)) return p;
                }
                if (const char* env = std::getenv("SST_KNOT_DATA_DIR")) {
                        std::string p = std::string(env) + "/../" + filename;
                        if (path_exists(p)) return p;
                }

                // 3) Build tree / 4) Installed share
#ifdef SST_DEFAULT_RESOURCE_SUBDIR
                {
                        std::string p = std::string(SST_DEFAULT_RESOURCE_SUBDIR) + "/" + filename;
                        if (path_exists(p)) return p;
                }
#endif
                // 5) Legacy
                std::vector<std::string> legacy = {
                        "resources",
                        "../resources",
                        "share/sstcore/resources",
                        "share/swirl_string_core/resources",
                };
                for (const auto& base : legacy) {
                        std::string p = base + "/" + filename;
                        if (path_exists(p)) return p;
                }
                return {};
        }

        namespace {

        std::string embed_basename(const std::string& key) {
                const auto slash = key.find_last_of("/\\");
                return (slash == std::string::npos) ? key : key.substr(slash + 1);
        }

        bool is_allowed_ideal_ab_source_key(const std::string& key) {
                std::string lower = key;
                for (char& c : lower) {
                        c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
                }
                if (lower.find("knotplot") != std::string::npos) return false;
                const std::string base = embed_basename(lower);
                if (base.find("_ideal.txt") != std::string::npos) return false;
                if (base == "ideal.txt") return true;
                if (base.rfind("ideal", 0) == 0 && base.size() > 4 &&
                    base.compare(base.size() - 4, 4, ".txt") == 0) {
                        return true;
                }
                return false;
        }

        std::string extract_gilbert_block_xml(const std::string& content,
                                              const std::string& block_id,
                                              const std::string& tag) {
                if (tag.empty()) return {};
                const std::string open_needle = "<" + tag;
                const std::string close_tag = "</" + tag + ">";
                const std::string id_needle = "Id=\"" + block_id + "\"";
                size_t pos = 0;
                while (true) {
                        const size_t a0 = content.find(open_needle, pos);
                        if (a0 == std::string::npos) break;
                        const size_t a1 = content.find('>', a0);
                        if (a1 == std::string::npos) break;
                        const std::string open_tag = content.substr(a0, a1 - a0 + 1);
                        if (open_tag.find(id_needle) == std::string::npos) {
                                pos = a1 + 1;
                                continue;
                        }
                        const size_t z0 = content.find(close_tag, a1);
                        if (z0 == std::string::npos) break;
                        return content.substr(a0, (z0 + close_tag.size()) - a0);
                }
                return {};
        }

        std::string extract_ab_block_xml(const std::string& content, const std::string& ab_id) {
                return extract_gilbert_block_xml(content, ab_id, "AB");
        }

        std::string try_ideal_content_for_tag(const std::string& content,
                                              const std::string& block_id,
                                              const std::string& tag) {
                return extract_gilbert_block_xml(content, block_id, tag);
        }

        std::string read_file_or_empty(const std::string& path) {
                std::ifstream in(path);
                if (!in) return {};
                std::ostringstream ss;
                ss << in.rdbuf();
                return ss.str();
        }

        std::vector<std::string> ideal_ab_search_filenames() {
                return {
                        "ideal.txt",
                        "ideal_short.txt",
                        "ideal_11a.txt",
                        "ideal_11n.txt",
                        "idealLinks.txt",
                        "idealLinks_10a.txt",
                        "idealLinks_10n.txt",
                };
        }

        std::string try_ideal_content_for_ab(const std::string& content, const std::string& ab_id) {
                return extract_ab_block_xml(content, ab_id);
        }

        } // namespace

        std::string find_ideal_ab_block_by_id(const std::string& ab_id) {
                if (ab_id.empty()) return {};

                const auto search_in_map = [&](const std::map<std::string, std::string>& files,
                                               const std::string& target_basename) -> std::string {
                        for (const auto& kv : files) {
                                if (!is_allowed_ideal_ab_source_key(kv.first)) continue;
                                if (embed_basename(kv.first) != target_basename) continue;
                                const std::string block = try_ideal_content_for_ab(kv.second, ab_id);
                                if (!block.empty()) return block;
                        }
                        return {};
                };

                static std::map<std::string, std::string> embedded_ideal = get_embedded_ideal_files();

                // 1) Embedded ideal.txt first
                {
                        const std::string block = search_in_map(embedded_ideal, "ideal.txt");
                        if (!block.empty()) return block;
                }

                // 2) Other embedded ideal*.txt in deterministic order
                for (const std::string& fname : ideal_ab_search_filenames()) {
                        if (fname == "ideal.txt") continue;
                        const std::string block = search_in_map(embedded_ideal, fname);
                        if (!block.empty()) return block;
                }

                // 3) Disk: same filename order
                for (const std::string& fname : ideal_ab_search_filenames()) {
                        const std::string path = find_ideal_file_path(fname);
                        if (path.empty()) continue;
                        const std::string content = read_file_or_empty(path);
                        if (content.empty()) continue;
                        const std::string block = try_ideal_content_for_ab(content, ab_id);
                        if (!block.empty()) return block;
                }

                // 4) Legacy ideal_database.txt (embedded knot files + disk + env)
                {
                        static std::map<std::string, std::string> embedded_knot = get_embedded_knot_files();
                        for (const auto& kv : embedded_knot) {
                                if (kv.first.find("ideal_database.txt") == std::string::npos) continue;
                                const std::string block = try_ideal_content_for_ab(kv.second, ab_id);
                                if (!block.empty()) return block;
                        }
                }
                if (const char* env_path = std::getenv("SST_IDEAL_DATABASE")) {
                        if (env_path[0] != '\0') {
                                const std::string block =
                                    try_ideal_content_for_ab(read_file_or_empty(env_path), ab_id);
                                if (!block.empty()) return block;
                        }
                }
                const char* legacy_paths[] = {
                        "ideal_database.txt",
                        "Front-End/knot_fseries/ideal_database.txt",
                        "../Front-End/knot_fseries/ideal_database.txt",
                        "../../Front-End/knot_fseries/ideal_database.txt",
                };
                for (const char* p : legacy_paths) {
                        const std::string block = try_ideal_content_for_ab(read_file_or_empty(p), ab_id);
                        if (!block.empty()) return block;
                }

                // 5) Env SST_IDEAL_TXT explicit file
                if (const char* env_txt = std::getenv("SST_IDEAL_TXT")) {
                        if (env_txt[0] != '\0') {
                                const std::string block =
                                    try_ideal_content_for_ab(read_file_or_empty(env_txt), ab_id);
                                if (!block.empty()) return block;
                        }
                }

                return {};
        }

        std::string find_ideal_block_by_id(const std::string& block_id, const std::string& tag) {
                if (block_id.empty()) return {};

                std::vector<std::string> tags;
                if (tag.empty()) {
                        tags = {"AB", "HT", "TL"};
                } else {
                        tags = {tag};
                }

                const auto search_in_map = [&](const std::map<std::string, std::string>& files,
                                               const std::string& target_basename) -> std::string {
                        for (const auto& kv : files) {
                                if (!is_allowed_ideal_ab_source_key(kv.first)) continue;
                                if (embed_basename(kv.first) != target_basename) continue;
                                for (const std::string& t : tags) {
                                        const std::string block =
                                            try_ideal_content_for_tag(kv.second, block_id, t);
                                        if (!block.empty()) return block;
                                }
                        }
                        return {};
                };

                static std::map<std::string, std::string> embedded_ideal = get_embedded_ideal_files();

                {
                        const std::string block = search_in_map(embedded_ideal, "ideal.txt");
                        if (!block.empty()) return block;
                }

                for (const std::string& fname : ideal_ab_search_filenames()) {
                        if (fname == "ideal.txt") continue;
                        const std::string block = search_in_map(embedded_ideal, fname);
                        if (!block.empty()) return block;
                }

                for (const std::string& fname : ideal_ab_search_filenames()) {
                        const std::string path = find_ideal_file_path(fname);
                        if (path.empty()) continue;
                        const std::string content = read_file_or_empty(path);
                        if (content.empty()) continue;
                        for (const std::string& t : tags) {
                                const std::string block =
                                    try_ideal_content_for_tag(content, block_id, t);
                                if (!block.empty()) return block;
                        }
                }

                if (const char* env_txt = std::getenv("SST_IDEAL_TXT")) {
                        if (env_txt[0] != '\0') {
                                const std::string content = read_file_or_empty(env_txt);
                                for (const std::string& t : tags) {
                                        const std::string block =
                                            try_ideal_content_for_tag(content, block_id, t);
                                        if (!block.empty()) return block;
                                }
                        }
                }

                return {};
        }

} // namespace sst
