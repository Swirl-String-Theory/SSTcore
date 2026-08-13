# Ridgerunner (portable, next to knotplotrc.kps)

This folder is a self-contained Windows bundle for tightening KnotPlot XYZ
`.txt` centerlines with ridgerunner.

## One-time setup

```powershell
cd <this-folder>
powershell -ExecutionPolicy Bypass -File .\install-user-path.ps1
```

Needs Python 3 on PATH for `.txt` runs.

## Quick commands (copy/paste)

From `KnotPlot\` (parent of this folder):

```bat
cd C:\workspace\projects\SST-Workbench\KnotPlot

rem --- single id ---
run_build.cmd knot_9.2
run_build.cmd knot_9.2 -rr
run_build.cmd knot_9.2 -rr --effort min -t8
run_build.cmd knot_9.2 -rr --effort normal -t8
run_build.cmd knot_9.2 -rr --effort extra -t8
run_build.cmd /list

rem --- batch all knot + link + torus (~49) ---
run_build_batch.cmd --all -rr --effort min -t8
run_build_batch.cmd --all -rr --effort normal -t8
run_build_batch.cmd --all -rr --effort extra -t8

rem --- batch filters ---
run_build_batch.cmd --all --kind knot -rr --effort min -t8
run_build_batch.cmd --all --kind link,torus -rr --effort min -t8
run_build_batch.cmd --ids knot_9.2,torus_6.9,link_0.2.1 -rr --effort min -t8

rem --- dry-run / parallel / KnotPlot-only ---
run_build_batch.cmd --all -rr --effort min -t8 --dry-run
run_build_batch.cmd --all -rr --effort min -t8 --jobs 2
run_build_batch.cmd --all --no-rr --effort min
run_build_batch.cmd --all -rr --effort min -t8 --fail-fast
```

Same batch from this folder: `run_build_batch.cmd …`  
Summary: `ridgerunner\out\batch_build_summary.json`  
Batch logs: `ridgerunner\out\build\<id>\batch_build.log`  
RR outputs: `KnotPlot\knots\<id>\*_rr_*.txt` (next to seeds)

| `--effort` | KnotPlot max ago | RR coarse / eq / polish | Ladder |
|------------|------------------|-------------------------|--------|
| `min` | **5000** (`trial_005k`) | 2000 / 5000 / 5000 | none |
| `normal` | 15000 | 10000 / 50000 / 30000 | none |
| `extra` | 15000 | same as normal | N600 only |

`-t8` → `bin\ridgerunner_multithread.exe` + `--Threads=8`. Batch defaults: `--effort min`, `-t8`, `--jobs 1`.

## Help

```bat
ridgerunner --help
```

Shows **wrapper** options (checkpoints, `--label`, `--verbose`, `--full-output`, …).
For native ridgerunner flags (`-c`, `--EqForceOn`, `--StopResidual`, …):

```bat
bin\ridgerunner.exe -h
```

## Usage

```bat
ridgerunner -a -s 1000 C:\pad\naar\knotplot.txt
```

- **New seed:** `-a` (autoscale to thickness 0.501).
- **Continue** from a previous RR XYZ output: `-c` (no rescaling).

During a `.txt` run the wrapper shows an ASCII progress bar with live elapsed
time (`t=12m34s`). Use `--verbose` for classic per-step `Rop:` lines plus a
timer heartbeat every ~30s. At the end of each stage (and on Ctrl+C) a **Stage
summary** prints wall time, last Rop/Thi/residual/struts. `run_ideal_knot` /
`run_catalog_knot` also print a **Campaign summary** with total elapsed.

Checkpoint tag comes from `-s` / `--StopSteps`:

| `-s` | tag | main outputs next to the input |
|------|-----|--------------------------------|
| 1000 | `001k` | `knotplot_rr_001k.txt`, `.metrics.json`, `.vect`, `.rr\` |
| 5000 | `005k` | `knotplot_rr_005k.txt`, … |
| 10000 | `010k` | `knotplot_rr_010k.txt`, … |
| 20 | `s20` | `knotplot_rr_s20.txt`, … |

Optional `--label NAME` appends `_{NAME}` so parallel runs do not overwrite:

```bat
ridgerunner -c -s 10000 --label plain prev_rr_005k.txt
→ prev_rr_005k_rr_010k_plain.txt
```

### Equilateralization

| Flag | When it matters |
|------|-----------------|
| `--EqOn` | Occasional eq when max/min edge **> 3** |
| `--EqForceOn` | Continuous equilateralization force (can interfere with stepper) |

### Recommended workflow (3-stage pipeline)

Do **not** start with a single huge `--EqForceOn` run on a fresh KnotPlot
seed. Prefer:

1. **coarse** — new seed, pure tightening (`--EqOn` only as emergency edge fix)
2. **eqfinal** — restore vertex spacing with `--EqForceOn`, drive residual to 0.01
3. **polish** — short unbiased run without continuous EqForce

Primary seed is chosen by the checkpoint gate (not blindly 5k/10k/15k).

```bat
rem Stage 1
ridgerunner -a --EqOn -s 10000 --StopResidual=0.05 --label coarse "seed.txt"

rem Stage 2
ridgerunner -c --EqForceOn -s 50000 --StopResidual=0.005 --Stop20=0.000001 --label eqfinal "seed_rr_010k_coarse.txt"

rem Stage 3
ridgerunner -c --EqOn -s 30000 --StopResidual=0.005 --Stop20=0.0000001 --label polish "…_eqfinal.txt"
```

Or: `ridgerunner\run_three_stage.cmd path\to\seed.txt`

The **polish** output is the near-ideal candidate; keep eqfinal as checkpoint.

### KnotPlot build + seed gate (`run_build.cmd`)

```bat
cd C:\workspace\projects\SST-Workbench\KnotPlot

rem KnotPlot only: effort-truncated checkpoints (default --effort normal = 15k)
run_build.cmd torus_6.9

rem Auto-select one trial seed, then 3-stage ridgerunner
run_build.cmd torus_6.9 -rr

rem Scout pass: KnotPlot ≤5k ago + short RR + multithread
run_build.cmd knot_9.2 -rr --effort min -t8

rem Overrides
run_build.cmd knot_3.1 -rr --seed trial_009k
run_build.cmd knot_3.1 -rr --multistart
run_build.cmd knot_4.1 -rr --allow-unverified-topology
```

`--effort min|normal|extra` truncates the `build_*.kpc` ago-ladder at
runtime (committed scripts stay at 15k) and shortens RR three-stage
budgets. **min** = max ago **5000** (`trial_005k`) + coarse/eq/polish
2000/5000/5000; **normal** = current 15k + 10k/50k/30k; **extra** =
normal + N600 resolution ladder only. `-t N` / `--threads N` sets
`RIDGERUNNER_EXE` to `bin\ridgerunner_multithread.exe` and passes
`--Threads=N` into `run_three_stage.cmd`.

### KnotPlot catalog batch (`run_build_batch`)

See also **[Quick commands](#quick-commands-copypaste)** at the top.

Batch all (or filtered) `knot_*` / `link_*` / `torus_*` builds:

```bat
cd C:\workspace\projects\SST-Workbench\KnotPlot

rem Full scout campaign (recommended first pass)
run_build_batch.cmd --all -rr --effort min -t8

rem Heavier / with N600 ladder
run_build_batch.cmd --all -rr --effort normal -t8
run_build_batch.cmd --all -rr --effort extra -t8

rem Filters
run_build_batch.cmd --all --kind knot,link,torus -rr --effort min -t8
run_build_batch.cmd --ids knot_9.2,torus_6.9 -rr --effort min -t8

rem Dry-run, parallel workers, KnotPlot-only, fail-fast
run_build_batch.cmd --all -rr --effort min -t8 --dry-run
run_build_batch.cmd --all -rr --effort min -t8 --jobs 2
run_build_batch.cmd --all --no-rr --effort min
run_build_batch.cmd --all -rr --effort min -t8 --fail-fast
```

Defaults: `--effort min`, `-t8`, `--jobs 1`. Summary:
`ridgerunner\out\batch_build_summary.json`. Per-id batch log:
`ridgerunner\out\build\<id>\batch_build.log`. RR polish/TXT stays next to
the KnotPlot seed under `knots\<id>\` (same as single `run_build -rr`).

`-rr` does **not** pipeline every TXT. It runs `select_knotplot_seed.py`
(after `parse_knotplot_log.py`) and sends **one** seed to `run_three_stage.cmd`.
After polish, stage 4 writes a **separate** VortexLab copy via
`resample_closed_knot_txt.py --points 300` → `*_polish_uniform_N300.txt`
(+ VECT). Then `classify_catalog_status.py` writes `catalog_status.json` and
`build_knotplot_knots_data.py --from-rr-outdir` upserts that uniform file into
`knotplot_knots_data.js`. The Ridgerunner `*_polish.txt` is left untouched.

Catalog statuses: `relaxed-seed` → `near-ideal-candidate` → `near-ideal`
(optional `run_build … -rr --certify` for multi-start + N600/N1200).
`certified-ideal` is never automatic. See `KNOTPLOT_KNOTS_DATA_README.md`.

**Robuuste checkpoint-gate (summary):**

- Plateau on **`R_proxy = L/D_proxy`** deltas (`|ΔR/R| < 0.001` after the local min) → status `settled-after-local-minimum`; earliest 0.1%-tie only among candidates at/after that min. No plateau → pure min `R_proxy` (`best-so-far-no-plateau`); **no** earliest-tie without settle. Same path for `knot_*` / `torus_*` / `link_*`.
- Signed length gain is logged for diagnostics only (KnotPlot length often grows).
- Per-component flatness `√(λ3/λ1)`; 5% drop = soft penalty; ~20–25% + worse `D_proxy`/`R_proxy` = hard DQ
- `D_proxy = min(2·MinRad, d_self_nonlocal, d_inter)` from **segment–segment** distances (arc-length exclusion window)
- Rank by class A/B/C then lowest `R_proxy`
- Topology (`knot_*` / `torus_*` / `link_*`): 1-comp prefers **`knot_type`** from folder (`knot_X.Y` / `torus_p.q`); `link_*` prefers **`link_type`** from folder (then `linking_matrix`). If the primary field is missing, consistent non-empty **`dowker_code`** across checkpoints verifies. Hard fail if both are absent.
- No settle by 15k → `best-so-far-no-plateau` warning, still may RR

Check `*.metrics.json` after eqfinal/polish: residual ≤ 0.01, prefer
`edge_length_ratio` ≤ 1.10 and `edge_length_cv` ≤ 0.01.

### Quick single checkpoints (trefoil)

```bat
ridgerunner -a -s 1000 C:\workspace\projects\SST-Workbench\KnotPlot\knots\knot_3.1\T_2_3_trial_005k.txt
ridgerunner -a -s 5000 C:\workspace\projects\SST-Workbench\KnotPlot\knots\knot_3.1\T_2_3_trial_005k.txt
```

### Metrics

Each checkpoint writes JSON with length, thickness, ropelength, residual,
**strutcount** (contact struts, from `.final.struts` / `strutcount.dat` col 2 — not MRstruts),
edge_length_variance, **edge_length_min/max/ratio/mean/cv** (from
final XYZ), **mr_struts** (separate), flatness, component sizes, and paths.

### Multilink without blank-line separators

```bat
ridgerunner -a -s 1000 --component-count 3 link_900verts.txt
ridgerunner -a -s 1000 --component-size 300 link_900verts.txt
```

### Full ridgerunner file output

```bat
ridgerunner --full-output -a -s 1000 knot.txt
```

(`--keep-vectfiles` is a deprecated alias for `--full-output`.)

Plain VECT files still go straight to the native exe (no checkpoint renaming):

```bat
ridgerunner -a -s 1000 knot.vect
```

### Gilbert ideal AB (`run_ideal_knot`)

Parallel path that starts from Brian Gilbert Fourier coeffs in
`SST-Workbench\knots_ideal_favorites.txt` (not KnotPlot `load 3.1`). Does
**not** change `run_build.cmd -rr`.

| Role | Value | Convention |
|------|------:|------------|
| Gilbert seed `L` | 16.371637 | diameter `D=1` |
| Acceptance target `L_3_1` | 16.357467488 | diameter `D=1` |
| Target ropelength (RR) | ≈ 32.714934976 | radius units (`2 × L`) |

**Default policy:** resolutions stay **`300,600,1200`** (seed `n300.txt`). The
fseries-style ladder **`150,300,600,900,1200`** is opt-in via
`-r150,300,600,900,1200` / `--resolutions 150,300,600,900,1200`. Seed sample
count defaults to `min(--resolutions)` (so that list starts at `n150.txt`).
After each polish rung, `3:1:1` campaigns report `L_diam` vs
`16.357467488` (`--rel-tol`, default `1e-4`).

Usability: `gilbert_ab_to_xyz` / `run_ideal_knot` reject AB records with
`C_cont ≤ 0.05` (curvature-only Fourier artifacts; ~144/250 in the Gilbert
DB). Escape hatch: `--allow-curvature-only`. Shared helper:
`SST-Workbench/sst_gilbert_usability.py`.

```bat
cd C:\workspace\projects\SST-Workbench\KnotPlot\ridgerunner

rem Sample AB 3:1:1 → N=300 three-stage → N=600/N=1200 ladder (default)
run_ideal_knot.cmd --3:1:1

rem Opt-in fseries-style ladder from N=150
run_ideal_knot.cmd --3:1:1 -r150,300,600,900,1200 -t12

rem N=300 only (alias also: run_gilbert_three_stage.cmd)
run_ideal_knot.cmd --3:1:1 --resolutions 300

rem Full per-step Rop lines (passed through to ridgerunner)
run_ideal_knot.cmd --3:1:1 --verbose

rem Resume: skip stages whose checkpoint TXT already exists
run_ideal_knot.cmd --3:1:1

rem Fresh unique run directory (does not overwrite prior out\3_1_1\t1\ files)
run_ideal_knot.cmd --3:1:1 --fresh
run_ideal_knot.cmd --3:1:1 --fresh --run-id try2

rem Force re-run even when checkpoints exist
run_ideal_knot.cmd --3:1:1 --force

rem Multithread binary + native --Threads=N; auto outdir t8\
run_ideal_knot.cmd --3:1:1 -t8
run_ideal_knot.cmd --3:1:1 --threads=8 --run-id MyMT

rem Full ladder through N=4800
run_ideal_knot.cmd --3:1:1 -r3,6,12,24,48 -t8
```

Default outputs under `out\ideal\3_1_1\t1\` (stock `ridgerunner.exe`; older flat
`out\3_1_1\` / `out\i3_1_1\` are not auto-migrated). Re-runs **resume** by
skipping finished stages. Use `--fresh` for `out\3_1_1\rYYYYMMDD_HHMMSS\`
(or `r_<id>\`) so prior results stay untouched. With `--threads=N`, results
go under `tN\` (or `r_<run-id>\`) using `bin\ridgerunner_multithread.exe`
and native `--Threads=N`. After each polish level the driver reports
`L_diam` vs `16.357467488`.

**Short naming** (keeps Windows paths under MAX_PATH):

| Role | Path |
|------|------|
| Campaign base | `out/ideal/3_1_1/` |
| Single-thread run | `out/ideal/3_1_1/t1/` |
| Threads run | `out/ideal/3_1_1/t8/` |
| Seed (default) | `n300.txt` |
| Seed (opt-in 150 ladder) | `n150.txt` |
| Base polish | `n{N}c.txt` → `n{N}e.txt` → `n{N}p.txt` (+ `p{N}.txt`) |
| Ladder N600 | `u600.txt` → `n600c.txt` → `n600e.txt` → `n600p.txt` (+ `p600.txt`) |
| Ladder N1200+ | `u{N}.txt` → `n{N}c` → **`n{N}s`** → `n{N}e` → `n{N}p` (+ `p{N}`) for N≥1200 |
| LA recover seed | `n{N}r.txt` |

RR one-shot files use labels `c` / `e` / `p` (e.g. `n300c_rr_050k_e.rr`).
Old long stacked names under `out/ideal_*` / `run_threadsN` are not resume
targets.

**Ropelength display:** `Rop = L / Thi`. Small step-to-step Rop zigzags are
normal when thickness and length both move; the polygonal length often still
decreases. A large Rop jump after `Max edgelength/min edgelength > 3` is the
`--EqOn` rediscretization restart — usually a symptom of bad parameterization.

**Resolution ladder:** Default stops at N=1200. Full chain:
N=600 ← `p300`; N=1200 ← `p600`; N=2400 ← `p1200`; N=4800 ← `p2400`.
Request with `--resolutions 300,600,1200,2400,4800` or `-r3,6,12,24,48`.
Ladder upsamples use **`spline_repair`** (`resample_closed_knot_txt.py
--method auto`): periodic cubic spline followed by iterative Rawdon-MinRad
restore so discrete Rop stays within `|ΔRop/R| < 1e-3` of the source (bare
spline alone often drops thickness ~3% on tight knots; midpoint `subdivide`
halves MinRad and roughly doubles Rop). Strict gates: edge-ratio, length,
minrad, and Rop. Sidecars from older bare **spline** / **subdivide** transfers
are treated as stale and rebuilt by the ladder / `run_ideal_knot` /
`run_catalog_knot` without requiring `--force` on earlier rungs.

**N≥1200 contact avalanche / stabilize:** After a bad (legacy spline) upsample the first
coarse pass (`-a --EqOn`, `StopResidual=0.1`) often hits a sudden strut flood
(`Str: 0` → 1000+) and repeated:

```text
tsnnls: Fallback tried all solvers without success.
resolve_force: Linear algebra failure. Returning control to stepper.
```

That is a local NNLS/rigidity failure, not necessarily a dead run — Rop can
still fall while thickness stays above overstep. Treat coarse as a
**contact-rebuild seed**, not certified criticality. The ladder then runs
**stabilize** before eqfinal:

```text
-a  -s 50000  --StopResidual=0.01  --label s   (no --EqOn)
```

OpenMP threads for stabilize default to 8 and are capped at 12 even if the
parent passed `--Threads=16`. `count_rr_la_failures.py` prints a gate after
stabilize (`failures/steps`): `<0.01` OK, `>0.1` warning, `≥0.5` fatal (blocks
eqfinal). Coarse itself is not gated fatally.

| Role | Path |
|------|------|
| Ladder N≥1200 | `u{N}` → `n{N}c` → **`n{N}s`** → `n{N}e` → `n{N}p` |

### Catalog knots (`run_catalog_knot`)

Same three_stage → ladder pipeline as `run_ideal_knot`, but seeds from
KnotPlot trial TXT or KnotPlot Fourier `.fseries` (not Gilbert AB). Does
**not** change `run_build.cmd -rr`.

**Id / outdir convention**

| Source | Id | Outdir example | Flag |
|--------|----|----------------|------|
| Ideal (Gilbert) | `3_1_1` | `out/ideal/3_1_1/t1/` | `--3:1:1` |
| KnotPlot knot | `K3.1` | `out/knotplot/K3.1/g1k/t1/` | `--knot3.1` |
| KnotPlot torus | `T2.3` | `out/knotplot/T2.3/g1k/t1/` | `--torus2.3` |
| KnotPlot link | `L6.3.3` | `out/knotplot/L6.3.3/g1k/t1/` | `--link6.3.3` |
| Fourier fseries | `3_1` / `3_1p` | `out/fseries/3_1/t1/` / `out/fseries/3_1p/t1/` | `--3_1` / `--3_1p` |

KnotPlot `--go` defaults to `1k` → `trial_001k.txt` and subdir `g1k`.
`--go` is invalid with fseries flags.

```bat
cd C:\workspace\projects\SST-Workbench\KnotPlot\ridgerunner

run_catalog_knot.cmd --knot3.1
run_catalog_knot.cmd --link6.3.3 -v -t8
run_catalog_knot.cmd --torus2.3 --fresh
run_catalog_knot.cmd --knot3.1 --go 2k
run_catalog_knot.cmd --3_1
run_catalog_knot.cmd --3_1p -r3
run_catalog_knot.cmd --3_1p --resolutions 300,600,900 -t10
run_catalog_knot.cmd --3_1u -t8
run_catalog_knot.cmd --knot3.1 -r3,6,12,24,48 -t8
```

### Fourier catalog batch (`run_catalog_batch`)

Run **all** Fourier-series seeds under `../Knots_FourierSeries`
(or a comma-separated subset). Default ladder is the **triple**
**N=300 → 600 → 900** with **`-t12`**. Outputs land under
`out/fseries/<stem>/t12/`. Seed points default to `min(--resolutions)`.
Short three_stage aliases work for any `n{N}.txt`. Gilbert /
`run_ideal_knot` still defaults to resolutions **300,600,1200** under
`out/ideal/`; opt-in the same 150 ladder with `-r150,300,600,900,1200`.

```bat
run_catalog_batch.cmd --all-fseries
run_catalog_batch.cmd --all-fseries -r300,600,900 -t12
run_catalog_batch.cmd --all-fseries --jobs 2 -t8
run_catalog_batch.cmd --all-fseries --dry-run
run_catalog_batch.cmd --stems 3_1,3_1p,12a_1202 -r300,600 -t12
```

- Resume-friendly per stem via existing checkpoints under `out/fseries/<stem>/t12/`.
- `--jobs N` / `-j N`: process pool of N stem workers (default **1** =
  sequential console). Clamped so `jobs * threads ≤` logical CPU count
  (e.g. `-t12` on a 12-core box → at most `--jobs 1`). With `jobs > 1`,
  each stem’s stdout/stderr goes to
  `out/fseries/<stem>/tN/batch_stem.log`.
- **Windows tip:** keep the product of jobs and threads at or below CPU
  count; parallel RR campaigns are also disk-heavy on a single SSD.
- On failure: continue to the next stem unless `--fail-fast` (cancels
  pending workers when `jobs > 1`).
- Summary: `out/fseries/batch_fseries_summary.json` (atomic write;
  status, Rop per N, wall time, `jobs`).
- KnotPlot knot/link/torus batch: see **`run_build_batch`** above
  (`--all -rr --effort min -t8`). Gilbert 150-ladder is available on
  `run_ideal_knot` via `-r150,300,600,900,1200` (default remains
  `300,600,1200`).

Single-knot examples (same pipeline):

```bat
run_catalog_knot.cmd --3_1
run_catalog_knot.cmd --3_1 -r300,600,900 -t12
run_catalog_knot.cmd --12a_1202z6 -r300,600
```

Unit tests:

```bat
python -m unittest test_gilbert_ab_to_xyz.py test_run_ideal_knot.py test_run_catalog_knot.py test_run_catalog_batch.py test_run_knotplot_txt.py test_fseries_to_xyz.py test_recover_ladder_coarse.py test_resample_closed_knot_txt.py test_count_rr_la_failures.py -v
```

## Layout

| Path | Role |
|------|------|
| `ridgerunner.cmd` | Entry point (put this folder on PATH) |
| `run_three_stage.cmd` | coarse → eqfinal → polish for one seed TXT (`n{N}` short aliases) |
| `run_resolution_ladder.cmd` | ladder from polish base N (`--ns`; stabilize for N≥1200) |
| `count_rr_la_failures.py` | LA-failure gates + stabilize thread cap |
| `run_ideal_knot.cmd` / `.py` | Gilbert AB sample + multi-resolution RR |
| `run_catalog_knot.cmd` / `.py` | KnotPlot trial / fseries → multi-resolution RR |
| `run_catalog_batch.cmd` / `.py` | Batch all / selected fseries stems |
| `fseries_to_xyz.py` | KnotPlot Fourier `.fseries` → XYZ |
| `run_gilbert_three_stage.cmd` | N=300-only alias for `run_ideal_knot` |
| `gilbert_ab_to_xyz.py` | Gilbert Fourier → XYZ + target compare |
| `select_knotplot_seed.py` | checkpoint gate → one trial seed |
| `parse_knotplot_log.py` | KnotPlot log → `*.knotplot.json` sidecars |
| `run_knotplot_txt.py` | txt → VECT → ridgerunner → `{stem}_rr_{tag}[_{label}].*` |
| `out\ideal\` / `out\knotplot\` / `out\fseries\` | Campaign outputs by source |
| `out\fseries\batch_fseries_summary.json` | Batch campaign summary |
| `bin\ridgerunner.exe` | Native binary + MinGW DLLs |
| `bin\ridgerunner_multithread.exe` | Same binary; used via `--threads=N` |
| `bin\*.dll` | OpenBLAS / GSL / runtime deps |

Do not place `ridgerunner.cmd` inside `bin\` next to the `.exe` — Windows
prefers `.exe` over `.cmd` in the same directory.

## Command reference

Copy-paste lookup for campaign drivers. Paths are relative to
`KnotPlot\ridgerunner` unless noted.

### Quick start

```bat
cd C:\workspace\projects\SST-Workbench\KnotPlot\ridgerunner

rem Ideal Gilbert AB (default ladder to N=1200, out\ideal\3_1_1\t1\)
run_ideal_knot.cmd --3:1:1

rem Opt-in N=150..1200 ladder (seed n150.txt)
run_ideal_knot.cmd --3:1:1 -r150,300,600,900,1200 -t12

rem Full ladder + 8 OpenMP threads
run_ideal_knot.cmd --3:1:1 -r3,6,12,24,48 -t8

rem KnotPlot trial / Fourier catalog
run_catalog_knot.cmd --knot3.1
run_catalog_knot.cmd --3_1p -r3,6,9 -t8
run_catalog_batch.cmd --all-fseries
```

### Shared driver options

| Flag | Short | Meaning |
|------|-------|---------|
| `--resolutions LIST` | `-r3,6,9,12,24,48` or `-r150,300,600,900,1200` | Any vertex counts in `32..100000`. Catalog/batch default `300,600,900`; ideal default `300,600,1200` (opt-in 150 ladder). Short codes `3→300`…`9→900`…`48→4800`; literals allowed. Classic prepend of `300` when only higher N are listed and no N below 300 is present. |
| `--threads=N` | `-t8` | Use `bin\ridgerunner_multithread.exe` + native `--Threads=N`; outdir `tN\`. Without this: stock `ridgerunner.exe`, outdir `t1\`. |
| `--verbose` | `-v` | Full per-step Rop lines. |
| `--fresh` | | New `rYYYYMMDD_HHMMSS\` (or `r_<id>\` with `--run-id`) under campaign base. |
| `--run-id NAME` | | Subdir `r_NAME\` instead of timestamp / `tN`. |
| `--force` | | Re-run stages even when checkpoints exist. |
| `--outdir PATH` | | Explicit outdir (no auto `t1`/`tN`). |
| `--points N` | | Seed sample count / `n{N}.txt` (ideal and catalog default: `min(--resolutions)`). |

**Outdir matrix** (under campaign base, e.g. `out\3_1_1\` or `out\K3.1\g1k\`):

| Invocation | Outdir |
|------------|--------|
| default | `t1\` (stock exe) |
| `--threads=8` / `-t8` | `t8\` (multithread exe) |
| `--fresh` / `--run-id` | `r…\` (sibling of `tN`) |
| `--outdir PATH` | `PATH` as-is |

### `run_ideal_knot.cmd`

| Flag | Meaning |
|------|---------|
| `--3:1:1` / `--id X:Y:Z` | Gilbert AB id (default `3:1:1`) |
| `--ideal PATH` | Override `knots_ideal_favorites.txt` |
| `--rel-tol FLOAT` | Relative tolerance vs `L_3_1` target (default `1e-4`); compared per polish rung for `3:1:1` |
| *(shared)* | `--resolutions`/`-r`, `--threads`/`-t`, `-v`, `--fresh`, `--run-id`, `--force`, `--outdir`, `--points` |

```bat
run_ideal_knot.cmd --3:1:1
run_ideal_knot.cmd --3:1:1 -r3
run_ideal_knot.cmd --3:1:1 -r150,300,600,900,1200 -t12
run_ideal_knot.cmd --3:1:1 -r3,6,12,24,48 -t8
run_ideal_knot.cmd --3:1:1 --resolutions 300,600,1200,2400,4800 --threads=8
run_ideal_knot.cmd --3:1:1 --fresh --run-id try2
run_ideal_knot.cmd --3:1:1 --force -v
```

### `run_catalog_knot.cmd`

| Flag | Meaning |
|------|---------|
| `--knotX.Y` / `--linkX.Y.Z` / `--torusX.Y` | KnotPlot trial seed (`--go` default `1k` → `trial_001k.txt`) |
| `--go TAG` | Trial tag (`1k`→`001k`); KnotPlot mode only |
| `--3_1` / `--3_1p` / `--3_1u` / `--4_1` … | Fourier `.fseries` stem |
| `--knots-root` / `--fseries-root` | Override catalog roots |
| *(shared)* | same as ideal (`-r`, `-t`, `-v`, …) |

```bat
run_catalog_knot.cmd --knot3.1
run_catalog_knot.cmd --link6.3.3 -v -t8
run_catalog_knot.cmd --torus2.3 --go 2k --fresh
run_catalog_knot.cmd --3_1
run_catalog_knot.cmd --3_1p -r3
run_catalog_knot.cmd --knot3.1 -r3,6,12,24,48 -t8
```

Outdirs: `out\K3.1\g1k\t1\`, `out\L6.3.3\g1k\t8\`, `out\3_1\t1\`, …

### `run_resolution_ladder.cmd`

Direct ladder from an existing N=300 polish (`p300.txt` / `n300p.txt`):

```bat
run_resolution_ladder.cmd path\to\p300.txt
run_resolution_ladder.cmd path\to\p300.txt --ns="600,900,1200" --verbose --Threads=8
run_resolution_ladder.cmd path\to\p300.txt --to=4800 --verbose --Threads=8
run_resolution_ladder.cmd path\to\p300.txt --to=600 --force
```

On CMD, quote `--ns="600,900,1200"` (commas are argument delimiters). Drivers (`run_catalog_knot` / `run_ideal_knot`) quote automatically via `cmd_c_command`.

| Flag | Meaning |
|------|---------|
| `--ns=N1,N2,…` | Exact ladder targets (any N>300), each resampled from the previous polish |
| `--to=N` | Legacy classic chain stop at `600` / `1200` (default) / `2400` / `4800` |
| `--verbose` / `-v` | Pass through to ridgerunner |
| `--force` | Re-run existing checkpoints |
| `--Threads=N` | Native OpenMP (stabilize capped at 12) |

### `run_three_stage.cmd`

```bat
run_three_stage.cmd path\to\n300.txt
run_three_stage.cmd path\to\n300.txt --verbose --force --Threads=8
```

Stages (N1200-style precision on eqfinal/polish):

1. coarse: `-a --EqOn -s 10000 --StopResidual=0.05`
2. eqfinal: `-c --EqForceOn -s 50000 --StopResidual=0.005`
3. polish: `-c --EqOn -s 30000 --StopResidual=0.005`

### Full ladder examples

```bat
run_ideal_knot.cmd --3:1:1 -r3,6,12,24,48 -t8
run_ideal_knot.cmd --3:1:1 --resolutions 300,600,1200,2400,4800 --threads=8
run_catalog_knot.cmd --knot3.1 -r3,6,12,24,48 -v
```