#pragma once

#include <string>

namespace sst {

enum class CertificateStatus {
    Pass = 0,
    Fail = 1,
    Indeterminate = 2,
    NotEvaluated = 3
};

inline const char* certificate_status_name(CertificateStatus s) {
    switch (s) {
        case CertificateStatus::Pass: return "Pass";
        case CertificateStatus::Fail: return "Fail";
        case CertificateStatus::Indeterminate: return "Indeterminate";
        case CertificateStatus::NotEvaluated: return "NotEvaluated";
    }
    return "NotEvaluated";
}

} // namespace sst
