#include "sst_evidence_report.h"
#include "sstcore_version.h"

#include <cmath>
#include <fstream>
#include <iomanip>
#include <limits>
#include <sstream>

namespace sst {
namespace {

std::string escape_json(const std::string& s) {
    std::ostringstream o;
    for (unsigned char c : s) {
        switch (c) {
            case '"': o << "\\\""; break;
            case '\\': o << "\\\\"; break;
            case '\b': o << "\\b"; break;
            case '\f': o << "\\f"; break;
            case '\n': o << "\\n"; break;
            case '\r': o << "\\r"; break;
            case '\t': o << "\\t"; break;
            default:
                if (c < 0x20) {
                    o << "\\u" << std::hex << std::setw(4) << std::setfill('0') << static_cast<int>(c)
                      << std::dec;
                } else {
                    o << static_cast<char>(c);
                }
                break;
        }
    }
    return o.str();
}

void write_json_number(std::ostringstream& o, double v) {
    if (!std::isfinite(v)) {
        o << "null";
        return;
    }
    o << std::setprecision(std::numeric_limits<double>::max_digits10) << v;
}

} // namespace

std::string EvidenceReportAPI::build_report_json(
    const EvidenceReportMeta& meta,
    const std::vector<CheckResult>& checks) {
    std::ostringstream o;
    o << "{\n";
    o << "  \"schema_version\": \"1.0\",\n";
    o << "  \"sstcore_version\": \"" << escape_json(meta.sstcore_version.empty() ? SSTCORE_VERSION : meta.sstcore_version) << "\",\n";
    o << "  \"canon_version\": \"" << escape_json(meta.canon_version.empty() ? SSTCORE_CANON_VERSION : meta.canon_version) << "\",\n";
    o << "  \"git_commit\": \"" << escape_json(meta.git_commit) << "\",\n";
    o << "  \"numeric_profile\": \"" << escape_json(meta.numeric_profile) << "\",\n";
    o << "  \"compiler\": \"" << escape_json(meta.compiler) << "\",\n";
    o << "  \"platform\": \"" << escape_json(meta.platform) << "\",\n";
    o << "  \"checks\": [\n";
    for (std::size_t i = 0; i < checks.size(); ++i) {
        const auto& c = checks[i];
        o << "    {\n";
        o << "      \"kind\": \"" << check_kind_export_string(c.kind) << "\",\n";
        o << "      \"message\": \"" << escape_json(c.message) << "\",\n";
        o << "      \"name\": \"" << escape_json(c.name) << "\",\n";
        o << "      \"passed\": " << (c.passed ? "true" : "false") << ",\n";
        o << "      \"residual\": ";
        write_json_number(o, c.residual);
        o << ",\n";
        o << "      \"supports_empirical_claim\": " << (c.supports_empirical_claim ? "true" : "false") << ",\n";
        o << "      \"tolerance\": ";
        write_json_number(o, c.tolerance);
        o << "\n";
        o << "    }" << (i + 1 < checks.size() ? "," : "") << "\n";
    }
    o << "  ]\n";
    o << "}\n";
    return o.str();
}

bool EvidenceReportAPI::write_evidence_report(
    const std::string& path,
    const EvidenceReportMeta& meta,
    const std::vector<CheckResult>& checks) {
    if (path.empty()) return false;
    std::ofstream out(path, std::ios::binary);
    if (!out) return false;
    out << build_report_json(meta, checks);
    return static_cast<bool>(out);
}

} // namespace sst
