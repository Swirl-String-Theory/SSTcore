#!/usr/bin/env bash
set -euo pipefail
python routeB_RT_bem_v18_extended_local_scan_knotplot.py \
  --ideal "${1:-ideal.txt}" \
  --outdir "${2:-outputs_routeB_BEM_v18_knotplot_fast}" \
  --run \
  --n-center 8 \
  --n-theta 3 \
  --n-sphere 14 \
  --tube-fraction 0.34 \
  --outer-factor 2.4 \
  --pair-fit-min-M 4 \
  --length-samples 2000
