#!/usr/bin/env python3
from geometry.sawbowl import build_sawbowl_3phase
from geometry.rodin6lane import build_rodin6lane
from geometry.validators import validate_geometry

for coil in [build_sawbowl_3phase(mode='curved'), build_sawbowl_3phase(mode='chord'), build_rodin6lane(n_path=600)]:
    rep=validate_geometry(coil)
    print(coil.name, 'lanes=', rep['lane_count'], 'length=', f"{rep['total_length_m']:.4f}", 'passes=', rep.get('passes_basic'))
    if 'mirror_z_pair_errors' in rep:
        print(' mirror errors:', rep['mirror_z_pair_errors'])
