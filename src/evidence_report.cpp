#include "sst_evidence_report.h"
#include "sstcore_version.h"

#include <fstream>
#include <sstream>

namespace sst {
namespace {

std::string escape_json(const std::string& s) {
    std::ostringstream o;
    for (char c : s) {
        switch (c) {
            case '"': o << "\\\""; break;
            case '\\': o << "\\\\"; break;
            case '\n': o << "\\n"; break;
            case '\r': o << "\\r"; break;
            case '\t': o << "\\t"; break;
            default: o << c; break;
        }
    }
    return o.str();
}

} // namespace

std::string EvidenceReportAPI::build_report_json(
    const EvidenceReportMeta& meta,
    const std::vector<CheckResult>& checks) {
    std::ostringstream o;
    o << "{\n";
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
        o << "      \"residual\": " << c.residual << ",\n";
        o << "      \"supports_empirical_claim\": " << (c.supports_empirical_claim ? "true" : "false") << ",\n";
        o << "      \"tolerance\": " << c.tolerance << "\n";
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
