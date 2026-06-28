#!/usr/bin/env bash
set -euo pipefail
python routeB_RT_bem_v19_link_geometry_parser.py \
  --ideal "${1:-ideal.txt}" \
  --outdir "${2:-outputs_routeB_BEM_v19_links}" \
  --links L2a1,L4a1,L5a1,L6a1,L8a1,L6a4,L6n1
