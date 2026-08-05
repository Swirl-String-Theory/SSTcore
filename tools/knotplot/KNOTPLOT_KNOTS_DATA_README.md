# KnotPlot / VortexLab catalog (`knotplot_knots_data.js`)

This package builds a Fourier catalog for VortexLab from **uniform N=300**
centerlines produced by the Ridgerunner pipeline — not from raw KnotPlot
relaxations alone.

## Pipeline (recommended)

```bat
cd C:\workspace\projects\SST-Workbench\KnotPlot
run_build.cmd knot_3.1 -rr
```

That:

1. Runs KnotPlot `build_*.kpc` (15k checkpoints + sidecars)
2. Selects one seed (`select_knotplot_seed.py`)
3. Runs three-stage Ridgerunner → `*_polish.txt` (audit geometry)
4. Resamples → `*_polish_uniform_N300.txt` (+ VECT) for VortexLab
5. Writes `catalog_status.json`
6. Upserts the uniform file into `knotplot_knots_data.js`

Canonical catalog IDs are folder names: `knot_3.1`, `torus_6.9`, `link_0.2.1`.
There is **no** `Tlink_6_9` entry (legacy mistake; use `torus_6.9`).

Strict convergence (expensive):

```bat
run_build.cmd knot_3.1 -rr --certify
```

Adds multi-start + independent N=600 / N=1200 ladders from the N=300 polish.

## Manual upsert after an existing `-rr` folder

```bat
python ridgerunner\classify_catalog_status.py knots\knot_3.1
python build_knotplot_knots_data.py --from-rr-outdir knots\knot_3.1 --output knotplot_knots_data.js --force
```

## Status levels

| Status | Meaning |
|--------|---------|
| `relaxed-seed` | KnotPlot geometry only / RR gates failed |
| `near-ideal-candidate` | Topology OK, residual ≤ 0.01 |
| `near-ideal` | residual ≤ 0.005, ε_R ≤ 0.05%, multi-start + resolution convergence, uniform mesh OK |
| `certified-ideal` | Never assigned automatically |

`ideal` stays `false` until an external formal certification.

Raw Ridgerunner edge-ratio/CV may be uneven (WARN only). The **uniform** VortexLab export should satisfy approximately:

```text
edge_ratio ≤ 1.02
edge_cv    ≤ 0.5%
```

Do **not** re-run Ridgerunner on `*_polish_uniform_N300.txt`.

## Data model

Each component uses the same Fourier coefficient shape as the ideal/fseries catalogs:

```javascript
components: [{
  I: 1,
  L: …,
  pointCount: 300,
  coeffs: [
    { I: 0, A: [/* x,y,z */], B: [0,0,0] },
    { I: 1, A: [/* x,y,z */], B: [/* x,y,z */] }
  ]
}]
```

Entries also store `sourceRole: "vortexlab-uniform-N300"`, SHA-256, optional
`catalogStatus` diagnostics (ε_R, checks), and pairwise Gauss linking.

## Scan uniforms only

```bat
python build_knotplot_knots_data.py --scan .\knots --glob "*_polish_uniform_N300.txt" --output .\knotplot_knots_data.js --force
```

## VortexLab integration

`vortexring-lab` currently loads `ideal_knots_data.js` and `fourier_knots_data.js`.
To use this catalog:

1. Add:

```html
<script src="./knotplot_knots_data.js" onerror="void 0"></script>
```

2. Register `KNOTPLOT_KNOT_IDS` / `KNOTPLOT_KNOT_DB` as a third catalog source.

Do not label entries as globally ideal/tight without the `--certify` gates (and
formal certification for `certified-ideal`).