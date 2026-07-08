#include "sst/knot.h"

#include "sst/knot/resource_loader.h"

#include <fstream>
#include <map>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
static inline std::string _sst_trim_copy(const std::string& s) {
    const char* ws = " \t\r\n";
    auto a = s.find_first_not_of(ws);
    if (a == std::string::npos) return "";
    auto b = s.find_last_not_of(ws);
    return s.substr(a, b - a + 1);
}
static inline std::string _sst_trim_copy2(const std::string& s) {
    const char* ws = " \t\r\n";
    auto a = s.find_first_not_of(ws);
    if (a == std::string::npos) return "";
    auto b = s.find_last_not_of(ws);
    return s.substr(a, b - a + 1);
}
static inline bool _sst_parse_vec3_csv(const std::string& in, sst::Vec3& v) {
    std::string s = in;
    for (char& c : s) if (c == ',') c = ' ';
    std::istringstream iss(s);
    return bool(iss >> v[0] >> v[1] >> v[2]);
}
static inline bool _sst_parse_vec3_csv2(const std::string& in, sst::Vec3& v) {
    std::string s = in;
    for (char& c : s) if (c == ',') c = ' ';
    std::istringstream iss(s);
    return bool(iss >> v[0] >> v[1] >> v[2]);
}
static inline double _sst_norm(const sst::Vec3& v) {
    return std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
}
static inline sst::Vec3 _sst_cross(const sst::Vec3& a, const sst::Vec3& b) {
    return sst::Vec3{a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]};
}
static inline double _sst_dot(const sst::Vec3& a, const sst::Vec3& b) {
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
}
static inline sst::Vec3 _sst_sub(const sst::Vec3& a, const sst::Vec3& b) {
    return sst::Vec3{a[0]-b[0], a[1]-b[1], a[2]-b[2]};
}

static sst::FourierKnot::IdealABComponent _sst_parse_component_block(
    const std::string& comp_open_tag,
    const std::string& comp_body)
{
    using namespace sst;
    FourierKnot::IdealABComponent comp{};

    static const std::regex comp_I_re(R"(I="\s*([0-9]+)\")", std::regex::icase);
    static const std::regex coeff_re(
        R"(<Coeff\s+I="\s*([0-9]+)\"\s+A="([^"]+)\"\s+B="([^"]+)\"\s*/?>)",
        std::regex::icase
    );

    std::smatch m;
    if (std::regex_search(comp_open_tag, m, comp_I_re)) {
        comp.component_index = std::stoi(m[1].str());
    }

    std::map<int, std::pair<Vec3, Vec3>> coeff_map;
    for (std::sregex_iterator it(comp_body.begin(), comp_body.end(), coeff_re), end; it != end; ++it) {
        int j = std::stoi((*it)[1].str());
        Vec3 A{0,0,0}, B{0,0,0};
        if (!_sst_parse_vec3_csv2((*it)[2].str(), A)) continue;
        if (!_sst_parse_vec3_csv2((*it)[3].str(), B)) continue;
        coeff_map[j] = {A, B};
    }

    auto it0 = coeff_map.find(0);
    if (it0 != coeff_map.end()) {
        comp.A0 = it0->second.first;
        comp.B0 = it0->second.second;
    }

    int maxJ = 0;
    for (const auto& kv : coeff_map) {
        if (kv.first > 0) maxJ = std::max(maxJ, kv.first);
    }

    comp.fourier.header = "% ideal component";
    comp.fourier.a_x.assign(maxJ, 0.0); comp.fourier.b_x.assign(maxJ, 0.0);
    comp.fourier.a_y.assign(maxJ, 0.0); comp.fourier.b_y.assign(maxJ, 0.0);
    comp.fourier.a_z.assign(maxJ, 0.0); comp.fourier.b_z.assign(maxJ, 0.0);

    for (const auto& kv : coeff_map) {
        const int j = kv.first;
        if (j <= 0) continue;
        const int k = j - 1;
        const auto& A = kv.second.first;
        const auto& B = kv.second.second;
        comp.fourier.a_x[k] = A[0]; comp.fourier.b_x[k] = B[0];
        comp.fourier.a_y[k] = A[1]; comp.fourier.b_y[k] = B[1];
        comp.fourier.a_z[k] = A[2]; comp.fourier.b_z[k] = B[2];
    }

    return comp;
}

static std::vector<sst::FourierKnot::IdealABComponent> _sst_parse_ab_components_from_body(const std::string& ab_body)
{
    using namespace sst;
    std::vector<FourierKnot::IdealABComponent> comps;

    static const std::regex comp_full_re(R"(<Component\b([^>]*)>([\s\S]*?)</Component>)",
                                         std::regex::icase);

    for (std::sregex_iterator it(ab_body.begin(), ab_body.end(), comp_full_re), end; it != end; ++it) {
        std::string comp_attrs = "<Component" + (*it)[1].str() + ">";
        std::string comp_body  = (*it)[2].str();
        comps.push_back(_sst_parse_component_block(comp_attrs, comp_body));
    }

    if (comps.empty()) {
        const std::string marker = "<STRING";
        size_t pos = 0;
        while (pos < ab_body.size()) {
            const size_t s0 = ab_body.find(marker, pos);
            if (s0 == std::string::npos) break;
            const size_t s1 = ab_body.find('>', s0);
            if (s1 == std::string::npos) break;
            const std::string open_tag = ab_body.substr(s0, s1 - s0 + 1);
            const size_t content_start = s1 + 1;
            const size_t next_string = ab_body.find(marker, content_start);
            const size_t close_string = ab_body.find("</STRING>", content_start);
            size_t content_end = ab_body.size();
            if (close_string != std::string::npos &&
                (next_string == std::string::npos || close_string < next_string)) {
                content_end = close_string;
            } else if (next_string != std::string::npos) {
                content_end = next_string;
            }
            const std::string comp_body = ab_body.substr(content_start, content_end - content_start);
            comps.push_back(_sst_parse_component_block(open_tag, comp_body));
            if (close_string != std::string::npos && content_end == close_string) {
                pos = close_string + 9;
            } else {
                pos = content_end;
            }
        }
    }

    if (!comps.empty()) return comps;

    FourierKnot::IdealABComponent single;
    single.component_index = 1;
    single = _sst_parse_component_block("<Component I=\"1\">", ab_body);
    comps.push_back(std::move(single));
    return comps;
}

static sst::FourierKnot::IdealABBlock _sst_parse_gilbert_open_body(
    const std::string& open_tag,
    const std::string& body,
    const std::string& tag_name)
{
    using AB = sst::FourierKnot::IdealABBlock;
    AB blk;
    blk.source_tag = tag_name;

    static const std::regex id_re(R"re(Id="([^"]+)")re", std::regex::icase);
    static const std::regex conway_re(R"re(Conway="([^"]*)")re", std::regex::icase);
    static const std::regex L_re(R"re(L="([^"]+)")re", std::regex::icase);
    static const std::regex D_re(R"re(D="([^"]+)")re", std::regex::icase);
    static const std::regex n_re(R"re(n="([^"]+)")re", std::regex::icase);

    std::smatch m;
    if (std::regex_search(open_tag, m, id_re))     blk.id     = m[1].str();
    if (std::regex_search(open_tag, m, conway_re)) blk.conway = m[1].str();
    if (std::regex_search(open_tag, m, L_re)) {
        try { blk.L = std::stod(_sst_trim_copy2(m[1].str())); } catch (...) { blk.L = 0.0; }
    }
    if (std::regex_search(open_tag, m, D_re)) {
        try { blk.D = std::stod(_sst_trim_copy2(m[1].str())); } catch (...) { blk.D = 0.0; }
    }
    if (std::regex_search(open_tag, m, n_re)) {
        try { blk.n = std::max(1, std::stoi(_sst_trim_copy2(m[1].str()))); } catch (...) { blk.n = 1; }
    }

    blk.components = _sst_parse_ab_components_from_body(body);
    if (!blk.components.empty()) {
        blk.fourier = blk.components.front().fourier;
        if (blk.n < 1) blk.n = static_cast<int>(blk.components.size());
    } else {
        blk.n = 0;
    }
    return blk;
}

static void _sst_collect_gilbert_blocks(const std::string& content,
                                        const std::string& tag_name,
                                        std::vector<sst::FourierKnot::IdealABBlock>& out)
{
    const std::string open_needle = "<" + tag_name;
    const std::string close_tag = "</" + tag_name + ">";
    size_t pos = 0;
    while (true) {
        const size_t a0 = content.find(open_needle, pos);
        if (a0 == std::string::npos) break;
        const size_t a1 = content.find('>', a0);
        if (a1 == std::string::npos) break;
        const size_t z0 = content.find(close_tag, a1);
        if (z0 == std::string::npos) break;

        const std::string open_tag = content.substr(a0, a1 - a0 + 1);
        const std::string body = content.substr(a1 + 1, z0 - (a1 + 1));
        out.push_back(_sst_parse_gilbert_open_body(open_tag, body, tag_name));
        pos = z0 + close_tag.size();
    }
}
}

std::vector<sst::FourierKnot::IdealABBlock>
sst::FourierKnot::parse_ideal_txt_multi(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("parse_ideal_txt_multi: cannot open file: " + path);
    std::ostringstream ss; ss << in.rdbuf();
    return parse_ideal_txt_from_string(ss.str());
}

std::vector<sst::FourierKnot::IdealABBlock>
sst::FourierKnot::parse_ideal_gilbert_from_string(const std::string& content) {
    std::vector<IdealABBlock> out;
    _sst_collect_gilbert_blocks(content, "AB", out);
    _sst_collect_gilbert_blocks(content, "HT", out);
    _sst_collect_gilbert_blocks(content, "TL", out);
    return out;
}

std::vector<sst::FourierKnot::IdealABBlock>
sst::FourierKnot::parse_ideal_txt_from_string(const std::string& content) {
    std::vector<IdealABBlock> out;
    for (const IdealABBlock& blk : parse_ideal_gilbert_from_string(content)) {
        if (blk.source_tag == "AB") out.push_back(blk);
    }
    return out;
}

sst::FourierKnot::IdealABBlock
sst::FourierKnot::parse_ideal_ab_by_id_from_string(const std::string& content, const std::string& ab_id) {
    const std::string needle = "Id=\"" + ab_id + "\"";
    size_t pos = 0;
    while (true) {
        size_t a0 = content.find("<AB", pos);
        if (a0 == std::string::npos) break;
        size_t a1 = content.find('>', a0);
        if (a1 == std::string::npos) break;

        std::string open_tag = content.substr(a0, a1 - a0 + 1);
        if (open_tag.find(needle) == std::string::npos) {
            pos = a1 + 1;
            continue;
        }

        size_t z0 = content.find("</AB>", a1);
        if (z0 == std::string::npos) break;

        std::string one_block = content.substr(a0, (z0 + 5) - a0);
        auto parsed = parse_ideal_txt_from_string(one_block);
        if (!parsed.empty()) return parsed.front();

        break;
    }

    throw std::runtime_error("parse_ideal_ab_by_id_from_string: AB Id not found: " + ab_id);
}

sst::FourierKnot::IdealABBlock
sst::FourierKnot::parse_ideal_ab_by_id_from_embedded(const std::string& ab_id, const std::string& embedded_name) {
    return parse_ideal_ab_by_id_from_string(sst::load_embedded_ideal_text(embedded_name), ab_id);
}

int sst::FourierKnot::index_of_ideal_id(const std::vector<FourierKnot::IdealABBlock>& blocks, const std::string& id) {
    for (size_t i = 0; i < blocks.size(); ++i) if (blocks[i].id == id) return static_cast<int>(i);
    return -1;
}

std::string sst::FourierKnot::format_ideal_ab_header(const IdealABBlock& ab) {
    std::ostringstream os;
    os.setf(std::ios::fixed);
    os.precision(6);
    os << "AB Id=\"" << ab.id
       << "\" Conway=\"" << ab.conway
       << "\" L=\"" << ab.L
       << "\" D=\"" << ab.D
       << "\" n=\"" << ab.n << "\"";
    return os.str();
}

std::vector<sst::Vec3>
sst::FourierKnot::evaluate_ideal_component(const IdealABComponent& comp, const std::vector<double>& s) {
    std::vector<Vec3> pts = evaluate(comp.fourier, s);
    for (auto& p : pts) {
        p[0] += comp.A0[0] + comp.B0[0];
        p[1] += comp.A0[1] + comp.B0[1];
        p[2] += comp.A0[2] + comp.B0[2];
    }
    return pts;
}

std::vector<std::vector<sst::Vec3>>
sst::FourierKnot::evaluate_ideal_ab_components(const IdealABBlock& ab, const std::vector<double>& s) {
    std::vector<std::vector<Vec3>> out;
    out.reserve(ab.components.size());
    for (const auto& c : ab.components) out.push_back(evaluate_ideal_component(c, s));
    return out;
}

