#include "sst_pipeline_provenance.h"
#include "sst_sha256.h"

#include <sstream>

namespace sst {

const char* PipelineProvenanceAPI::stage_name(PipelineStage s) {
    switch (s) {
        case PipelineStage::KnotPlot: return "KnotPlot";
        case PipelineStage::Ridgerunner: return "Ridgerunner";
        case PipelineStage::Smoothing: return "Smoothing";
        case PipelineStage::SSTcore: return "SSTcore";
        case PipelineStage::VortexLab: return "VortexLab";
    }
    return "Unknown";
}

const char* PipelineProvenanceAPI::certification_name(PipelineCertificationStatus s) {
    switch (s) {
        case PipelineCertificationStatus::Unknown: return "Unknown";
        case PipelineCertificationStatus::Candidate: return "Candidate";
        case PipelineCertificationStatus::Certified: return "Certified";
    }
    return "Unknown";
}

std::string PipelineProvenanceAPI::fingerprint_hex(const std::string& payload) {
    return sha256_hex(payload);
}

bool PipelineProvenanceAPI::record_complete(const ProvenanceRecord& r) {
    return !r.tool_name.empty() && !r.tool_version.empty() &&
           !r.input_sha256.empty() && !r.output_sha256.empty() &&
           !r.parameter_sha256.empty() && !r.coordinate_convention.empty() &&
           !r.scale_convention.empty() && !r.timestamp_utc.empty();
}

namespace {

bool hashes_look_like_sha256(const ProvenanceRecord& r) {
    if (!is_sha256_hex(r.input_sha256) || !is_sha256_hex(r.output_sha256) ||
        !is_sha256_hex(r.parameter_sha256)) {
        return false;
    }
    if (!r.parent_record_sha256.empty() && !is_sha256_hex(r.parent_record_sha256)) {
        return false;
    }
    return true;
}

} // namespace

std::string PipelineProvenanceAPI::record_fingerprint(const ProvenanceRecord& r) {
    std::ostringstream oss;
    oss << stage_name(r.stage) << '|' << certification_name(r.certification) << '|'
        << r.tool_name << '|' << r.tool_version << '|'
        << r.input_sha256 << '|' << r.output_sha256 << '|' << r.parameter_sha256 << '|'
        << r.parent_record_sha256 << '|' << r.coordinate_convention << '|'
        << r.scale_convention << '|' << r.timestamp_utc;
    return fingerprint_hex(oss.str());
}

PipelineCertificationStatus PipelineProvenanceAPI::evaluate_chain(const std::vector<ProvenanceRecord>& records) {
    if (records.empty()) return PipelineCertificationStatus::Unknown;

    for (const auto& r : records) {
        if (!record_complete(r)) return PipelineCertificationStatus::Unknown;
    }

    // SHA-256 contract: non-empty hash fields must be 64-hex (parent may be empty on root).
    for (const auto& r : records) {
        if (!hashes_look_like_sha256(r)) {
            return PipelineCertificationStatus::Candidate;
        }
    }

    // First stage must be KnotPlot with empty parent.
    if (records.front().stage != PipelineStage::KnotPlot || !records.front().parent_record_sha256.empty()) {
        return PipelineCertificationStatus::Candidate;
    }

    for (std::size_t i = 1; i < records.size(); ++i) {
        const auto& prev = records[i - 1];
        const auto& cur = records[i];
        const std::string expected_parent = record_fingerprint(prev);
        if (cur.parent_record_sha256 != expected_parent) {
            return PipelineCertificationStatus::Candidate;
        }
        if (cur.input_sha256 != prev.output_sha256) {
            return PipelineCertificationStatus::Candidate;
        }
        // Stages should be nondecreasing along the ladder.
        if (static_cast<int>(cur.stage) < static_cast<int>(prev.stage)) {
            return PipelineCertificationStatus::Candidate;
        }
    }

    const auto last = records.back().stage;
    if (last == PipelineStage::SSTcore || last == PipelineStage::VortexLab) {
        return PipelineCertificationStatus::Certified;
    }
    return PipelineCertificationStatus::Candidate;
}

} // namespace sst
