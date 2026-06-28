# Scale-role convention: r_c, R_horn, and a_tube
# ----------------------------------------------
# Route-B BEM is a dimensionless certified-geometry programme.  Its numerical
# normalizers use L_cert, M_max, and DeltaF_pair; they do not require inserting a
# physical core radius into the BEM score.
#
# When a physical radius is discussed, use
#
#     r_c == R_horn
#
# where R_horn is the horn-torus / return-flow circulation radius.  Do not
# silently identify r_c with the local ideal-tube radius.  Use
#
#     a_tube = R_horn / chi_h = r_c / chi_h
#     ell_K_phys = 2 * a_tube * L_cert
#
# The dimensionless Route-B normalizer remains
#
#     N_RT = M_max * L_cert**2
#
# while physical reconstruction uses
#
#     L_phys**2 = 4 * a_tube**2 * L_cert**2
#               = 4 * r_c**2 * L_cert**2 / chi_h**2
#
# Only if chi_h is later made knot-dependent should a separate horn-effective
# scan use M_max * (L_cert / chi_h(K))**2.  BEMv1--BEMv19 default mode is the
# certified dimensionless geometry mode.

#!/usr/bin/env python3
r'''
routeB_RT_bem_v14_multirun_grids.py
===================================

Wrapper around BEMv14 certified-length convergence runs.

Why this exists
---------------
A single convergence grid only tests stability inside one discretization
family.  For a stronger Route-B falsifier, we also want agreement across
multiple independent grid families (for example coarse / medium / fine,
or paired vs cartesian).

This wrapper launches BEMv14 multiple times, one time per grid family,
and aggregates the resulting selected normalizers and blind alpha budgets.
No observed alpha is used.

Outputs
-------
  multigrid_run_manifest.csv
      One row per BEMv14 subrun.

  multigrid_selected_normalizers.csv
      Selected normalizer summary per grid family.

  multigrid_budget_aggregate.csv
      Aggregated run-level selected-normalizer budgets across all grids.

  multigrid_consensus_summary.csv
      Cross-grid consensus statistics per normalizer.

  multigrid_report.md
      Human-readable report.
'''

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text('', encoding='utf-8')
        return
    keys: List[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def as_float(x: Any, default: float = float('nan')) -> float:
    try:
        return float(x)
    except Exception:
        return default


def resolve_script(primary: str, local_name: str, fallback: str) -> Path:
    if primary:
        p = Path(primary)
        if p.exists():
            return p
        raise FileNotFoundError(p)
    p = Path(__file__).with_name(local_name)
    if p.exists():
        return p
    p = Path(fallback)
    if p.exists():
        return p
    raise FileNotFoundError(f"could not find {local_name} or {fallback}")


def builtin_suite(profile: str) -> List[Dict[str, Any]]:
    if profile == 'quick':
        return [
            {
                'label': 'paired_coarse',
                'args': {
                    'grid_mode': 'paired',
                    'n_center_list': '8,10,12',
                    'n_theta_list': '3,3,4',
                    'n_sphere_list': '14,18,24',
                    'tube_fraction_list': '0.38,0.32,0.28',
                    'outer_factor_list': '2.2,2.6,3.0',
                },
            },
            {
                'label': 'paired_medium',
                'args': {
                    'grid_mode': 'paired',
                    'n_center_list': '12,16,20',
                    'n_theta_list': '4,5,6',
                    'n_sphere_list': '24,36,48',
                    'tube_fraction_list': '0.32,0.28,0.24',
                    'outer_factor_list': '2.4,2.8,3.2',
                },
            },
            {
                'label': 'cartesian_small',
                'args': {
                    'grid_mode': 'cartesian',
                    'n_center_list': '10,12',
                    'n_theta_list': '4,5',
                    'n_sphere_list': '18,24',
                    'tube_fraction_list': '0.32,0.28',
                    'outer_factor_list': '2.6,3.0',
                },
            },
        ]
    if profile == 'standard':
        return [
            {
                'label': 'paired_coarse',
                'args': {
                    'grid_mode': 'paired',
                    'n_center_list': '16,20,24,28',
                    'n_theta_list': '4,5,6,7',
                    'n_sphere_list': '36,48,72,96',
                    'tube_fraction_list': '0.35,0.31,0.27,0.24',
                    'outer_factor_list': '2.3,2.7,3.1,3.5',
                },
            },
            {
                'label': 'paired_fine',
                'args': {
                    'grid_mode': 'paired',
                    'n_center_list': '24,32,40,48',
                    'n_theta_list': '5,6,7,8',
                    'n_sphere_list': '96,144,196,256',
                    'tube_fraction_list': '0.35,0.30,0.25,0.20',
                    'outer_factor_list': '2.4,2.8,3.2,3.6',
                    'pair_fit_min_M': 10,
                },
            },
            {
                'label': 'cartesian_crosscheck',
                'args': {
                    'grid_mode': 'cartesian',
                    'n_center_list': '20,28',
                    'n_theta_list': '5,7',
                    'n_sphere_list': '48,96',
                    'tube_fraction_list': '0.30,0.24',
                    'outer_factor_list': '2.6,3.2',
                    'pair_fit_min_M': 8,
                },
            },
        ]
    raise ValueError(f'unknown suite profile: {profile}')


def load_suite(args) -> List[Dict[str, Any]]:
    if args.grid_suite_json:
        return json.loads(Path(args.grid_suite_json).read_text(encoding='utf-8'))
    return builtin_suite(args.suite_profile)


def run_subgrid(v14_script: Path, common: Dict[str, Any], entry: Dict[str, Any], grid_outdir: Path, timeout: int) -> Dict[str, Any]:
    label = entry['label']
    grid_args = dict(entry.get('args', {}))
    cmd = [sys.executable, str(v14_script), '--outdir', str(grid_outdir)]

    for key, value in common.items():
        if value is None:
            continue
        if isinstance(value, bool):
            if value:
                cmd.append(f'--{key.replace("_", "-")}')
        else:
            cmd += [f'--{key.replace("_", "-")}', str(value)]

    for key, value in grid_args.items():
        if value is None:
            continue
        if isinstance(value, bool):
            if value:
                cmd.append(f'--{key.replace("_", "-")}')
        else:
            cmd += [f'--{key.replace("_", "-")}', str(value)]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    (grid_outdir / 'v14_stdout.txt').write_text(proc.stdout, encoding='utf-8', errors='replace')
    (grid_outdir / 'v14_stderr.txt').write_text(proc.stderr, encoding='utf-8', errors='replace')
    return {
        'label': label,
        'returncode': proc.returncode,
        'outdir': str(grid_outdir),
        'command': ' '.join(cmd),
    }


def aggregate(outdir: Path, manifest_rows: List[Dict[str, Any]]) -> None:
    sel_rows: List[Dict[str, Any]] = []
    budget_rows: List[Dict[str, Any]] = []
    by_norm: Dict[str, List[float]] = defaultdict(list)
    by_norm_corr: Dict[str, List[float]] = defaultdict(list)
    by_norm_labels: Dict[str, List[str]] = defaultdict(list)
    chosen_counter: Counter = Counter()

    for m in manifest_rows:
        grid_outdir = Path(m['outdir'])
        label = m['label']
        summ = read_csv(grid_outdir / 'certified_stability_summary.csv')
        selected_rows = read_csv(grid_outdir / 'alpha_budget_v14_convergence.csv')
        report_rows = read_csv(grid_outdir / 'certified_convergence_grid.csv')

        selected_norm = None
        selected_gate = None
        if selected_rows:
            selected_norm = selected_rows[0].get('selected_normalizer', '')
            chosen_counter[selected_norm] += 1
            gates = [r.get('gate', '') for r in selected_rows]
            selected_gate = 'PASS_SUBLEADING_CORRECTION' if all(g == 'PASS_SUBLEADING_CORRECTION' for g in gates) else 'MIXED'
            for r in selected_rows:
                rr = dict(r)
                rr['grid_label'] = label
                budget_rows.append(rr)
                by_norm[selected_norm].append(as_float(r.get('alpha_inv_pred_blind_v13')))
                by_norm_corr[selected_norm].append(abs(as_float(r.get('correction_to_leading_ratio'))))
                by_norm_labels[selected_norm].append(label)

        chosen_summary = None
        for r in summ:
            if r.get('normalizer') == selected_norm:
                chosen_summary = r
                break
        if chosen_summary is None and summ:
            chosen_summary = summ[0]

        sel_row = {
            'grid_label': label,
            'grid_returncode': m['returncode'],
            'selected_normalizer': selected_norm or '',
            'selected_gate': selected_gate or '',
            'outdir': str(grid_outdir),
        }
        if chosen_summary:
            sel_row.update({
                'stability_gate': chosen_summary.get('stability_gate', ''),
                'n_runs': chosen_summary.get('n_runs', ''),
                'pass_fraction': chosen_summary.get('pass_fraction', ''),
                'alpha_inv_blind_mean': chosen_summary.get('alpha_inv_blind_v13_mean', ''),
                'alpha_inv_blind_cv_abs': chosen_summary.get('alpha_inv_blind_v13_cv_abs', ''),
                'abs_correction_ratio_max': chosen_summary.get('abs_correction_ratio_max', ''),
            })
        # add some info from full grid rows
        sel_row['n_candidate_rows'] = len(report_rows)
        sel_rows.append(sel_row)

    write_csv(outdir / 'multigrid_selected_normalizers.csv', sel_rows)
    write_csv(outdir / 'multigrid_budget_aggregate.csv', budget_rows)

    consensus_rows: List[Dict[str, Any]] = []
    for norm, vals in by_norm.items():
        arr = np.asarray(vals, dtype=float)
        carr = np.asarray(by_norm_corr[norm], dtype=float)
        labels = sorted(set(by_norm_labels[norm]))
        mean = float(np.mean(arr)) if len(arr) else float('nan')
        std = float(np.std(arr, ddof=1)) if len(arr) > 1 else (0.0 if len(arr) == 1 else float('nan'))
        span = float(np.max(arr) - np.min(arr)) if len(arr) else float('nan')
        cv = abs(std / mean) if math.isfinite(mean) and abs(mean) > 1e-300 else float('nan')
        cmax = float(np.max(carr)) if len(carr) else float('nan')
        consensus_rows.append({
            'normalizer': norm,
            'n_grid_families_selected': chosen_counter[norm],
            'grid_labels': ','.join(labels),
            'aggregate_mean': mean,
            'aggregate_std': std,
            'aggregate_span': span,
            'aggregate_cv_abs': cv,
            'aggregate_abs_correction_ratio_max': cmax,
            'cross_grid_gate': 'PASS_CROSS_GRID_CONSENSUS' if chosen_counter[norm] >= 2 and math.isfinite(cv) and cv <= 0.01 and math.isfinite(cmax) and cmax <= 0.05 else 'FAIL_CROSS_GRID_CONSENSUS',
        })
    write_csv(outdir / 'multigrid_consensus_summary.csv', consensus_rows)

    lines = []
    lines.append('# BEMv14 multigrid report')
    lines.append('')
    lines.append('This wrapper runs BEMv14 over multiple independent grid families.')
    lines.append('')
    lines.append('## Why this matters')
    lines.append('')
    lines.append('A single grid can only show intra-family stability. Multiple grids test whether the same normalizer and blind budget survive across independent discretization choices.')
    lines.append('')
    lines.append('## Per-grid selected normalizers')
    lines.append('')
    for r in sel_rows:
        lines.append(f"- `{r.get('grid_label')}`: normalizer `{r.get('selected_normalizer')}`, stability `{r.get('stability_gate')}`, mean `{r.get('alpha_inv_blind_mean')}`, CV `{r.get('alpha_inv_blind_cv_abs')}`")
    lines.append('')
    lines.append('## Cross-grid consensus')
    lines.append('')
    if consensus_rows:
        for r in consensus_rows:
            lines.append(f"- `{r['normalizer']}`: selected by `{r['n_grid_families_selected']}` grid families; gate `{r['cross_grid_gate']}`; aggregate CV `{r['aggregate_cv_abs']}`")
    else:
        lines.append('- no consensus rows available')
    lines.append('')
    lines.append('## Files')
    lines.append('')
    lines.append('- `multigrid_run_manifest.csv`')
    lines.append('- `multigrid_selected_normalizers.csv`')
    lines.append('- `multigrid_budget_aggregate.csv`')
    lines.append('- `multigrid_consensus_summary.csv`')
    lines.append('- `multigrid_report.md`')
    (outdir / 'multigrid_report.md').write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--v14-script', default='')
    ap.add_argument('--ideal', default='ideal.txt')
    ap.add_argument('--outdir', default='outputs_routeB_BEM_v14_multirun')
    ap.add_argument('--grid-suite-json', default='')
    ap.add_argument('--suite-profile', choices=['quick', 'standard'], default='quick')
    ap.add_argument('--multirun-timeout', type=int, default=7200)

    # common pass-through args for v14
    ap.add_argument('--v13-script', default='')
    ap.add_argument('--v8-script', default='')
    ap.add_argument('--from-bemv13-outdirs', default='')
    ap.add_argument('--ideal-xml-knot-ids', default='0:1:1,3:1:1,4:1:1')
    ap.add_argument('--target', default='3_1')
    ap.add_argument('--reference', default='0_1')
    ap.add_argument('--mu-mode', default='inverse_outer_radius')
    ap.add_argument('--mu-value', type=float, default=1.0)
    ap.add_argument('--boundary-subspace', default='all')
    ap.add_argument('--keep-constant', action='store_true')
    ap.add_argument('--no-auto-add-unknot', action='store_true')
    ap.add_argument('--max-raw-modes', type=int, default=0)
    ap.add_argument('--fit-min-M', type=int, default=4)
    ap.add_argument('--counterterm-fit-min-M', type=int, default=4)
    ap.add_argument('--fit-tail-frac', type=float, default=0.75)
    ap.add_argument('--counterterm-tail-frac', type=float, default=0.75)
    ap.add_argument('--fit-models', default='sqrt,sqrt+inv,sqrt+inv+threehalf')
    ap.add_argument('--counterterm-models', default='hk,hk+inv_sqrt,hk+inv_sqrt+inv')
    ap.add_argument('--soft-index-count', type=int, default=4)
    ap.add_argument('--soft-volume-mode', default='unit_ball')
    ap.add_argument('--soft-volume-value', type=float, default=0.0)
    ap.add_argument('--length-samples', type=int, default=4000)
    ap.add_argument('--length-fit-model', default='hk+inv_sqrt+inv')
    ap.add_argument('--length-coeff', default='A_M')
    ap.add_argument('--length-fit-min-M', type=int, default=4)
    ap.add_argument('--length-fit-tail-frac', type=float, default=0.75)
    ap.add_argument('--pair-fit-model', default='hk+inv_sqrt+inv')
    ap.add_argument('--pair-fit-min-M', type=int, default=4)
    ap.add_argument('--pair-fit-tail-frac', type=float, default=0.75)
    ap.add_argument('--normalizers', default='raw,Mmax,sqrtM,Lcert,Lcert2,Lcert3,NsoftV,NsoftV_Lcert,leading_full_cert,leading_half_cert,M_Lcert,sqrtM_Lcert,M_Lcert2')
    ap.add_argument('--preferred-normalizer', default='M_Lcert2')
    ap.add_argument('--subleading-threshold', type=float, default=0.05)
    ap.add_argument('--alpha-cv-threshold', type=float, default=0.01)
    ap.add_argument('--min-grid-runs', type=int, default=3)
    ap.add_argument('--subrun-timeout', type=int, default=180)
    ap.add_argument('--grid-run-timeout', type=int, default=260)

    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    v14_script = resolve_script(args.v14_script, 'routeB_RT_bem_v14_certified_convergence.py', '/mnt/data/routeB_RT_bem_v14_certified_convergence.py')
    suite = load_suite(args)
    common = vars(args).copy()
    for k in ['v14_script', 'outdir', 'grid_suite_json', 'suite_profile', 'multirun_timeout']:
        common.pop(k, None)

    manifest_rows: List[Dict[str, Any]] = []
    grids_root = outdir / 'grids'
    grids_root.mkdir(parents=True, exist_ok=True)

    reuse_dirs = [s.strip() for s in str(args.from_bemv13_outdirs).split(',') if s.strip()]
    if reuse_dirs and len(reuse_dirs) not in (1, len(suite)):
        raise SystemExit('when using --from-bemv13-outdirs in multirun mode, provide either 1 shared directory or one per grid family')

    for i, entry in enumerate(suite):
        label = entry['label']
        subdir = grids_root / label
        subdir.mkdir(parents=True, exist_ok=True)
        common_i = dict(common)
        if reuse_dirs:
            common_i['from_bemv13_outdirs'] = reuse_dirs[i] if len(reuse_dirs) == len(suite) else reuse_dirs[0]
        m = run_subgrid(v14_script, common_i, entry, subdir, args.multirun_timeout)
        manifest_rows.append(m)

    write_csv(outdir / 'multigrid_run_manifest.csv', manifest_rows)
    aggregate(outdir, manifest_rows)
    (outdir / 'run_config_multigrid.json').write_text(json.dumps({'args': vars(args), 'suite': suite}, indent=2, sort_keys=True), encoding='utf-8')

    print('=' * 78)
    print('BEMv14 multigrid wrapper complete')
    print('=' * 78)
    print(f'outdir: {outdir}')
    print('wrote: multigrid_run_manifest.csv, multigrid_selected_normalizers.csv,')
    print('       multigrid_budget_aggregate.csv, multigrid_consensus_summary.csv, multigrid_report.md')


if __name__ == '__main__':
    main()
