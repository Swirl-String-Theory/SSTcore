
# SST Taxonomy Starter v2

Standalone, non-destructive toolkit to build an **orthodox knot taxonomy** plus a separated
**numerical validation layer** from your existing project zips.

This v2 extends the starter with:

- extraction of `taxonomy_validation.csv` from `trefoil_closure/exports/...`
- support for:
  - `robustness_summary*.csv`
  - `final_best_estimate*.csv`
  - `shiftfree_postcheck*.csv`
  - `run_metadata*.json`

It still does **not** modify `SSTcore`, `SST_Dashboard`, or `resources`.

## Outputs

- `taxonomy_identity.csv`
- `taxonomy_embeddings.csv`
- `taxonomy_complement_geometry.csv`
- `taxonomy_field_descriptors.csv`
- `taxonomy_validation.csv`

## Philosophy

Five distinct data layers are kept separate:

1. `knot_identity`
2. `geometric_realization`
3. `complement_geometry`
4. `induced_field_descriptors`
5. `numerical_validation`

## Usage

```bash
python taxonomy_builder_v2.py \
  --resources /path/to/resources.zip \
  --dashboard /path/to/SST_Dashboard.zip \
  --out ./taxonomy_output
```

Optional:
```bash
python taxonomy_builder_v2.py \
  --resources /path/to/resources.zip \
  --dashboard /path/to/SST_Dashboard.zip \
  --sstcore /path/to/SSTcore.zip \
  --out ./taxonomy_output
```
