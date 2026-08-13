#pragma once

#include <string>
#include <vector>

namespace sst {

enum class PipelineStage {
    KnotPlot,
    Ridgerunner,
    Smoothing,
    SSTcore,
    VortexLab
};

enum class PipelineCertificationStatus {
    Unknown,
    Candidate,
    Certified
};

struct ProvenanceRecord {
    PipelineStage stage = PipelineStage::KnotPlot;
    PipelineCertificationStatus certification = PipelineCertificationStatus::Unknown;
    std::string tool_name;
    std::string tool_version;
    std::string input_sha256;
    std::string output_sha256;
    std::string parameter_sha256;
    std::string parent_record_sha256;
    std::string coordinate_convention;
    std::string scale_convention;
    std::string timestamp_utc;
};

class PipelineProvenanceAPI {
public:
    [[nodiscard]] static const char* stage_name(PipelineStage s);
    [[nodiscard]] static const char* certification_name(PipelineCertificationStatus s);
    [[nodiscard]] static std::string fingerprint_hex(const std::string& payload);

    // Canonical record fingerprint over normalized fields (deterministic).
    [[nodiscard]] static std::string record_fingerprint(const ProvenanceRecord& r);

    // Certified only if chain is complete contiguous KnotPlot→…→SSTcore (or VortexLab)
    // with parent hashes linking and all required fields present.
    [[nodiscard]] static PipelineCertificationStatus evaluate_chain(const std::vector<ProvenanceRecord>& records);

    [[nodiscard]] static bool record_complete(const ProvenanceRecord& r);
};

} // namespace sst
