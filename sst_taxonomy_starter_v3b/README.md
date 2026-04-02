
# SST Taxonomy Starter v3b

Standalone, non-destructive taxonomy builder for a **folder-based repository layout**.

Use this version when you have a local repository folder such as:

- `./SSTcore/`
- `./SSTcore/resources/`
- `./SSTcore/SST_Dashboard/`

and **do not** want to create or use a zip snapshot.

## Usage

Run from your local environment:

```bash
python ./SSTcore/sst_taxonomy_starter_v3b/taxonomy_builder_v3b.py --root ./SSTcore --out ./taxonomy_output
```

or from inside the starter folder:

```bash
python taxonomy_builder_v3b.py --root ../ --out ./taxonomy_output
```

## Outputs

- `taxonomy_identity.csv`
- `taxonomy_embeddings.csv`
- `taxonomy_complement_geometry.csv`
- `taxonomy_field_descriptors.csv`
- `taxonomy_validation.csv`
- `build_summary.json`

## Notes

This tool is intentionally conservative and non-destructive.

It separates five layers:

1. `knot_identity`
2. `geometric_realization`
3. `complement_geometry`
4. `induced_field_descriptors`
5. `numerical_validation`

It does **not** patch your repository and does **not** overwrite your existing code.
