#ifndef SSTCORE_SST_KNOT_H
#define SSTCORE_SST_KNOT_H

#pragma once

#include "sst/knot/fourier_types.h"
#include "sst/knot/invariants.h"
#include "sst/knot/resource_loader.h"
#include "sst/types.h"

#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace sst {

class FourierKnot {
public:
#include "sst/knot/fourier_parser.h"
#include "sst/knot/ideal_parser.h"
#include "sst/knot/fourier_eval.h"
};

} // namespace sst

#endif // SSTCORE_SST_KNOT_H
