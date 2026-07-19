#!/usr/bin/env node
'use strict';

/**
 * Optional Python ↔ Node numeric parity checks against the same C++ kernels.
 * Skips cleanly when Python or the SSTcore Python module is unavailable
 * so `npm test` does not require Python.
 */

const { spawnSync } = require('child_process');

const ATOL = 1e-9;
const RTOL = 1e-9;

function close(a, b, atol, rtol) {
  const aa = Math.abs(a);
  const bb = Math.abs(b);
  return Math.abs(a - b) <= atol + rtol * Math.max(aa, bb);
}

const PY_SCRIPT = `
import json, math
try:
    import SSTcore as s
except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)}))
    raise SystemExit(0)
curve = [[0.0,0.0,0.0],[1.0,0.0,0.0],[1.0,1.0,0.0],[0.0,1.0,0.0]]
grid = [[0.5,0.5,0.5]]
out = {"ok": True, "atol": 1e-9, "rtol": 1e-9}
fn = getattr(s, "compute_velocity", None) or getattr(s, "biot_savart_velocity_grid", None)
if fn is None:
    out["ok"] = False
    out["error"] = "no compute_velocity in Python SSTcore"
    print(json.dumps(out))
    raise SystemExit(0)
try:
    v = fn(curve, grid)
    if hasattr(v, "tolist"):
        v = v.tolist()
    flat = []
    if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
        for row in v:
            flat.extend([float(x) for x in row])
    else:
        flat = [float(x) for x in v]
    out["velocity"] = flat
except Exception as e:
    out["ok"] = False
    out["error"] = "velocity: " + str(e)
ring = [[math.cos(2*math.pi*i/32), math.sin(2*math.pi*i/32), 0.0] for i in range(32)]
wfn = getattr(s, "compute_writhe", None)
if wfn is not None:
    try:
        out["writhe"] = float(wfn(ring))
    except Exception as e:
        out["writhe_error"] = str(e)
print(json.dumps(out))
`;

function tryPython() {
  const py = spawnSync('python', ['-c', PY_SCRIPT], { encoding: 'utf8' });
  if (py.error || py.status !== 0) {
    return null;
  }
  try {
    const lines = (py.stdout || '').trim().split(/\r?\n/).filter(Boolean);
    return JSON.parse(lines[lines.length - 1]);
  } catch (_) {
    return null;
  }
}

console.log('Python/Node parity check (optional)...');
console.log(`Tolerance: |a-b| <= atol + rtol*max(|a|,|b|) with atol=${ATOL}, rtol=${RTOL}`);

const py = tryPython();
if (!py || !py.ok) {
  console.log('SKIP: Python SSTcore not available —', py && py.error ? py.error : 'python failed');
  process.exit(0);
}

const sst = require('../index.js');
if (!sst.isAvailable) {
  console.error('Node SSTcore not available');
  process.exit(1);
}

let failed = 0;

if (py.velocity && typeof sst.computeVelocity === 'function') {
  const curve = [
    [0, 0, 0],
    [1, 0, 0],
    [1, 1, 0],
    [0, 1, 0],
  ];
  const grid = [[0.5, 0.5, 0.5]];
  const nv = sst.computeVelocity(curve, grid);
  const flat = Array.from(nv);
  const n = Math.min(flat.length, py.velocity.length);
  for (let i = 0; i < n; i++) {
    if (!close(flat[i], py.velocity[i], ATOL, RTOL)) {
      console.error(
        `velocity[${i}] mismatch: node=${flat[i]} python=${py.velocity[i]} (atol=${ATOL}, rtol=${RTOL})`,
      );
      failed++;
      break;
    }
  }
  if (!failed) console.log(`✓ computeVelocity parity (atol=${ATOL}, rtol=${RTOL})`);
}

if (py.writhe != null && typeof sst.computeWrithe === 'function') {
  const ring = [];
  for (let i = 0; i < 32; i++) {
    const t = (i / 32) * 2 * Math.PI;
    ring.push([Math.cos(t), Math.sin(t), 0]);
  }
  const nw = sst.computeWrithe(ring);
  if (!close(nw, py.writhe, ATOL, RTOL)) {
    console.error(`writhe mismatch: node=${nw} python=${py.writhe} (atol=${ATOL}, rtol=${RTOL})`);
    failed++;
  } else {
    console.log(`✓ computeWrithe parity (atol=${ATOL}, rtol=${RTOL})`);
  }
}

if (failed) {
  console.error(`Parity failed (${failed})`);
  process.exit(1);
}
console.log('Parity OK (or no overlapping metrics)');
process.exit(0);
