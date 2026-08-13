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

bool timestamp_looks_utc(const std::string& ts) {
    // Minimal ISO-8601 UTC: YYYY-MM-DDTHH:MM:SSZ (optionally with fractional seconds).
    if (ts.size() < 20 || ts.back() != 'Z') return false;
    if (ts[4] != '-' || ts[7] != '-' || ts[10] != 'T' || ts[13] != ':' || ts[16] != ':') return false;
    for (std::size_t i = 0; i < ts.size() - 1; ++i) {
        if (i == 4 || i == 7 || i == 10 || i == 13 || i == 16) continue;
        if (i == 19 && ts[i] == '.') continue;
        if (i > 19 && ts[i] == '.') continue;
        if (i > 19) {
            if (!(ts[i] >= '0' && ts[i] <= '9')) return false;
            continue;
        }
        if (!(ts[i] >= '0' && ts[i] <= '9')) return false;
    }
    return true;
}

bool exact_stage_step(PipelineStage prev, PipelineStage cur) {
    // Exact adjacent transitions on the KnotPlot → … → VortexLab ladder (no skips).
    return static_cast<int>(cur) == static_cast<int>(prev) + 1 || cur == prev;
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

    for (const auto& r : records) {
        if (!hashes_look_like_sha256(r) || !timestamp_looks_utc(r.timestamp_utc)) {
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
        if (!exact_stage_step(prev.stage, cur.stage)) {
            return PipelineCertificationStatus::Candidate;
        }
        if (prev.coordinate_convention != cur.coordinate_convention ||
            prev.scale_convention != cur.scale_convention) {
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
