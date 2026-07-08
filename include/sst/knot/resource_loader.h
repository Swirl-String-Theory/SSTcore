#ifndef SSTCORE_SST_KNOT_RESOURCE_LOADER_H
#define SSTCORE_SST_KNOT_RESOURCE_LOADER_H

#pragma once

#include <map>
#include <string>

namespace sst {

// Forward declaration for embedded knot files (generated during build)
std::map<std::string, std::string> get_embedded_knot_files();

// Embedded ideal database files (generated during build)
std::map<std::string, std::string> get_embedded_ideal_files();

// Convenience loader (supports basename fallback like "ideal.txt")
std::string load_embedded_ideal_text(const std::string& name = "ideal.txt");

// Resource path resolution: explicit path → env → build tree → installed share → legacy
// Returns full path to knot.${knot_id}.fseries, or empty if not found.
std::string find_knot_file_path(const std::string& knot_id, const std::string& explicit_base = "");
// Returns full path to ideal database file (e.g. "ideal.txt"), or empty if not found.
std::string find_ideal_file_path(const std::string& filename, const std::string& explicit_base = "");

// Search embedded + disk ideal*.txt (never knotplot) for <AB Id="ab_id"> block XML.
// Returns empty string if not found.
std::string find_ideal_ab_block_by_id(const std::string& ab_id);

// General Gilbert lookup: <AB>, <HT>, or <TL> by Id. tag empty => try AB, HT, TL in order.
std::string find_ideal_block_by_id(const std::string& block_id, const std::string& tag = "");

} // namespace sst

#endif // SSTCORE_SST_KNOT_RESOURCE_LOADER_H
