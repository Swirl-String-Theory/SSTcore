# SST Coil Digital Twin v8 — exact Rodin 6-lane geometry

This patch corrects the Rodin sector to follow the uploaded `rodin_6lane_channel_guide_knot512.py` logic exactly:

- `(p,q)=(5,12)` torus knot.
- 3 phase lanes via `CELL_PHASES = [0, 1/3, 2/3]` of one q-sector.
- Mirrored counterpart is `z -> -z`.
- Total: 6 continuous lanes on the torus guide envelope.

Run:

```bash
python SST_Coil_90_RunAll.py
```

Outputs go to `exports/SST-Coil/run_YYYYMMDD_HHMMSS/`.
