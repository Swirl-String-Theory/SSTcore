#ifndef SSTCORE_SST_EXTENSIONS_H
#define SSTCORE_SST_EXTENSIONS_H

#pragma once

// Compatibility shim — prefer #include <sst/workbench.h>
#include "sst/workbench/extensions.h"

namespace sst {
namespace sstext {
using namespace workbench;
} // namespace sstext
} // namespace sst

#endif // SSTCORE_SST_EXTENSIONS_H
