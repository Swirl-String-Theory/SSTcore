# Resource breakage probe report (deelplan res-0)

## Baseline

- `python -m pytest tests/ -q -rA`: **81 passed, 25 skipped** (pre-existing skips: legacy `sstcore` import / helicity modules)
- `npm test`: **FAIL** — pre-existing version pin (`package.json` 0.8.18 vs engine/canon 0.8.28); out of scope for this epic (no version bump)
- `npm run test:parity`: **OK**

## Probe 1a — `resources/knotplot/` moved aside (existing build)

| Test | Outcome | Match prediction |
|------|---------|------------------|
| `test_knotplot_ideal_files_load_via_public_api` | FAIL (`knotplot_dir is None`) | yes |
| `test_build_source_zip_smoke` | FAIL (required dir empty) | yes |
| `test_unpack_roundtrip` | FAIL (required dir empty) | yes |
| `test_knotplot_ideal_not_used_for_ab_lookup` | SKIP | yes |
| `test_resolve_knot_ref_knotplot_legacy` | SKIP | yes |
| `test_assert_canon_ideal_rejects_knotplot` | SKIP | yes |
| `test_knotplot_raw_length_factor` | SKIP | yes |
| ParticleEvaluator reject tests | PASS | yes |
| Synthetic `test_source_zip` path filters | PASS | yes |

**No unexpected couplings.** Summary: 3 failed, 25 passed, 4 skipped on the coupled subset.

## Probe 1b — embed vs disk

Existing native/wheel build still embeds knotplot ideal texts (`any_knotplot_embed=True`). Disk-backed APIs (`get_knotplot_dir`, `get_knotplot_ideal_path`) are what the four skip sites and install test use. Canon AB lookup (`find_ideal_ab_block_by_id`) remains True without disk knotplot.

Full `pip install -e .` with knotplot absent was deferred: rebuild cost is high and 1a already isolates the disk coupling the guard layer must close. Embed retarget is owned by deelplan res-4.

## Guard re-probe (after fixtures + inventory)

With `resources/knotplot/` moved aside again:

| Test | Outcome |
|------|---------|
| `test_knotplot_ideal_not_used_for_ab_lookup` | ERROR (fixture fail — no skip) |
| `test_resolve_knot_ref_knotplot_legacy` | ERROR (fixture fail — no skip) |
| `test_assert_canon_ideal_rejects_knotplot` | ERROR (fixture fail — no skip) |
| `test_knotplot_raw_length_factor` | ERROR (fixture fail — no skip) |
| `test_knotplot_ideal_files_load_via_public_api` | FAIL |
| `test_every_manifest_entry_exists_with_matching_sha256` | FAIL (names each missing knotplot file) |
| `test_knotplot_ids_resolve_via_api` | FAIL |

**Zero silent skips** on the coupled set. Guard layer exit criteria met.

---

# Resource breakage probe report (deelplan res-5 final)

Post-epic tree: nested `resources/ideal/`, Workbench-export `resources/knotplot/` with `INDEX.json` + AB-XML API, vendored `tools/knotplot/` (repo-only).

## Baseline (res-5 start)

- `python -m pytest tests/ -q`: **114 passed, 26 skipped** (then 121 after new tests)
- `npm test`: still pre-existing version pin fail (`0.8.18` vs `0.8.28`); out of scope
- `npm run test:parity`: **OK**
- `npm run pack:check`: **OK** (16.1 MB, 356 files)
- `npm run wheel:preflight`: **OK**

## Probe — `resources/knotplot/` moved aside

| Outcome | Count / notes |
|---------|----------------|
| ERROR (fixtures / require_knotplot / index) | 15 — named hard failures, not skips |
| FAILED | inventory SHA256, `test_knotplot_ids_resolve_via_api`, install load |
| Silent skips on coupled set | **0** |

Artifact: `validation/resource_probe/res5_knotplot_aside.txt`

## Probe — `resources/ideal/` moved aside

| Outcome | Count / notes |
|---------|----------------|
| ERROR (layout migration fixtures) | 4 |
| FAILED | inventory SHA256, ideal keys API, `test_resources_dir_and_ideal_txt` |
| Silent skips on coupled set | **0** |
| Still OK | embed-backed AB find / ParticleEvaluator (disk layout absent; native embed remains) |

Artifact: `validation/resource_probe/res5_ideal_aside.txt`

## Restore

Trees restored; full suite **121 passed, 25 skipped**. Artifact: `validation/resource_probe/res5_restore_green.txt` (from the restore run; final count after packaging tests).

**Verdict:** before-and-after confirms the epic delivers named hard failures and zero silent skips for both resource trees.

