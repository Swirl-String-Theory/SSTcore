#!/usr/bin/env bash
set -euo pipefail
python routeB_RT_bem_v18_extended_local_scan_knotplot.py \
  --ideal "${1:-ideal.txt}" \
  --outdir "${2:-outputs_routeB_BEM_v18_knotplot}" \
  --run \
  --n-center 24 \
  --n-theta 5 \
  --n-sphere 96 \
  --tube-fraction 0.30 \
  --outer-factor 3.0 \
  --pair-fit-min-M 8 \
  --length-samples 12000
