#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace sst {

/** SHA-256 digest of raw bytes; returns lowercase 64-hex. */
[[nodiscard]] std::string sha256_hex(const std::uint8_t* data, std::size_t len);

[[nodiscard]] inline std::string sha256_hex(const std::string& s) {
    return sha256_hex(reinterpret_cast<const std::uint8_t*>(s.data()), s.size());
}

[[nodiscard]] inline std::string sha256_hex(const std::vector<std::uint8_t>& bytes) {
    return sha256_hex(bytes.data(), bytes.size());
}

/** True iff s is exactly 64 lowercase/uppercase hex digits. */
[[nodiscard]] bool is_sha256_hex(const std::string& s);

} // namespace sst
