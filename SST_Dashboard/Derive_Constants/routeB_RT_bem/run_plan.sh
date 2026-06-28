#!/usr/bin/env bash
set -euo pipefail
python routeB_RT_bem_v18_extended_local_scan_knotplot.py \
  --ideal "${1:-ideal.txt}" \
  --outdir "${2:-outputs_routeB_BEM_v18_knotplot_plan}" \
  --dry-run-plan
