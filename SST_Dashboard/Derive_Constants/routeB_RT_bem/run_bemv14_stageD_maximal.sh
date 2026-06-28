#!/usr/bin/env bash
set -euo pipefail

IDEAL="${1:-ideal.txt}"
OUTROOT="${2:-outputs_routeB_BEM_v14_multirun_extensive_D}"

echo "Running BEMv14 Stage D maximal suite. This may take a long time."
python routeB_RT_bem_v14_multirun_grids.py \
  --ideal "$IDEAL" \
  --outdir "$OUTROOT" \
  --grid-suite-json BEMv14_suite_stageD_maximal.json \
  --subrun-timeout 7200 \
  --grid-run-timeout 9000 \
  --multirun-timeout 86400
