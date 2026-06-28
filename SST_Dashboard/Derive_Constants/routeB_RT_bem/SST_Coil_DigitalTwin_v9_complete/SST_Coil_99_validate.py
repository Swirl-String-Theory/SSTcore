#!/usr/bin/env python3
from __future__ import annotations
from SST_Coil_10_geometry_sawbowl import build_sawbowl_3phase
from SST_Coil_11_geometry_rodin6lane import build_rodin_6lane
from SST_Coil_00_common import summarize_lanes


def main():
    saw=build_sawbowl_3phase()
    rod=build_rodin_6lane()
    print('SawBowl summary:', summarize_lanes(saw))
    print('Rodin 6-lane summary:', summarize_lanes(rod))
    assert len(saw)==3
    assert len(rod)==6
    assert saw[0]['points'].shape[1]==3
    assert rod[0]['points'].shape[1]==3
    print('OK')
if __name__=='__main__': main()
