#pragma once

#include "sst_check_kind.h"
#include <string>
#include <vector>

namespace sst {

struct EvidenceReportMeta {
    std::string sstcore_version;
    std::string canon_version;
    std::string git_commit;
    std::string numeric_profile;
    std::string compiler;
    std::string platform;
};

class EvidenceReportAPI {
public:
    // Deterministic JSON document (sorted keys within each check). Returns JSON string.
    [[nodiscard]] static std::string build_report_json(
        const EvidenceReportMeta& meta,
        const std::vector<CheckResult>& checks);

    // Write JSON to path; returns true on success.
    [[nodiscard]] static bool write_evidence_report(
        const std::string& path,
        const EvidenceReportMeta& meta,
        const std::vector<CheckResult>& checks);
};

} // namespace sst
