#!/usr/bin/env bash
set -euo pipefail
python routeB_RT_bem_v19_link_geometry_parser.py \
  --ideal "${1:-ideal.txt}" \
  --outdir "${2:-outputs_routeB_BEM_v19_all_links}" \
  --include-all-links
