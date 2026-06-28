#!/usr/bin/env python3
r"""
Route B BEM v3 R--T spectral falsifier.

This replaces the earlier 1D/centerline surrogate by a 3D knot-tube complement
boundary-integral candidate with:

1. Area-symmetric single-layer matrices:
       S_ij = sqrt(A_i) G(x_i,x_j) sqrt(A_j)

2. Parallel-transport/Bishop tube frames.

3. Screened self-patch diagonal:
       S_ii ≈ (1-exp(-mu*r_p))/(2*mu),  r_p=sqrt(A_i/pi),
   with the mu->0 limit S_ii=r_p/2.

It is an audit/falsifier harness, not an alpha derivation.
No observed alpha, charge, epsilon0, electron radius, or CODATA value is used.

Scale-role convention: r_c, R_horn, and a_tube
----------------------------------------------
Route-B BEM is a dimensionless certified-geometry programme.  Its numerical
normalizers use L_cert, M_max, and DeltaF_pair; they do not require inserting a
physical core radius into the BEM score.

When a physical radius is discussed, use

    r_c == R_horn

where R_horn is the horn-torus / return-flow circulation radius.  Do not
silently identify r_c with the local ideal-tube radius.  Use

    a_tube = R_horn / chi_h = r_c / chi_h
    ell_K_phys = 2 * a_tube * L_cert

The dimensionless Route-B normalizer remains

    N_RT = M_max * L_cert**2

while physical reconstruction uses

    L_phys**2 = 4 * a_tube**2 * L_cert**2
              = 4 * r_c**2 * L_cert**2 / chi_h**2

Only if chi_h is later made knot-dependent should a separate horn-effective
scan use M_max * (L_cert / chi_h(K))**2.  BEMv1--BEMv19 default mode is the
certified dimensionless geometry mode.

"""

from __future__ import annotations
import argparse, csv, hashlib, math, re, subprocess, sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    from scipy.linalg import eigh
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False

FLOAT_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


# ------------------------------- parsing ---------------------------------

def parse_ideal_file(path: Path) -> Dict[str, np.ndarray]:
    """Permissive parser for multi-knot ideal.txt blocks."""
    if not path.exists():
        raise FileNotFoundError(path)

    knots: Dict[str, List[List[float]]] = {}
    csv_rows: Dict[str, List[List[float]]] = {}
    cur_name: Optional[str] = None
    cur_pts: List[List[float]] = []
    anon = 1

    def flush():
        nonlocal cur_name, cur_pts, anon
        if cur_pts:
            nm = cur_name or f"knot_{anon}"
            anon += 1
            base, k = nm, 2
            while nm in knots:
                nm = f"{base}__{k}"; k += 1
            knots[nm] = cur_pts
        cur_name, cur_pts = None, []

    def comment_name(s: str) -> Optional[str]:
        s = s.strip().lstrip("#/;").strip()
        m = re.search(r"(?:knot|name|id)\s*[:=]\s*([A-Za-z0-9_+\-.]+)", s, re.I)
        if m:
            return m.group(1)
        m = re.match(r"^([0-9]+_[0-9]+|0_1|unknot|trefoil|figure[-_]?eight)\b", s, re.I)
        return m.group(1) if m else None

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            flush(); continue
        if line.startswith(("#", "//", ";")):
            nm = comment_name(line)
            if nm:
                flush(); cur_name = nm
            continue

        parts = [p for p in re.split(r"[,;\s]+", line) if p]
        if len(parts) >= 4:
            try:
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                if not FLOAT_RE.fullmatch(parts[0]):
                    csv_rows.setdefault(parts[0], []).append([x, y, z])
                    continue
            except Exception:
                pass

        vals = []
        for p in parts:
            try: vals.append(float(p))
            except Exception: pass
        if len(vals) >= 3:
            cur_pts.append(vals[-3:])
            continue

        if re.match(r"^[A-Za-z0-9_+\-.]+$", line):
            flush(); cur_name = line

    flush()
    for nm, pts in csv_rows.items():
        base, k = nm, 2
        while nm in knots:
            nm = f"{base}__{k}"; k += 1
        knots[nm] = pts

    out = {}
    for nm, pts in knots.items():
        arr = np.asarray(pts, float)
        if arr.ndim == 2 and arr.shape[1] == 3 and arr.shape[0] >= 8 and np.isfinite(arr).all():
            out[nm] = arr
    return out


# ------------------------------- geometry --------------------------------

def close_curve(P: np.ndarray) -> np.ndarray:
    P = np.asarray(P, float)
    return np.vstack([P, P[0]]) if np.linalg.norm(P[0] - P[-1]) > 1e-12 else P

def arclength(P: np.ndarray) -> float:
    C = close_curve(P)
    return float(np.sum(np.linalg.norm(np.diff(C, axis=0), axis=1)))

def resample_closed_curve(P: np.ndarray, n: int, normalize_length=True) -> np.ndarray:
    C = close_curve(P)
    seg = np.linalg.norm(np.diff(C, axis=0), axis=1)
    total = float(seg.sum())
    if total <= 0: raise ValueError("zero-length curve")
    s = np.r_[0.0, np.cumsum(seg)]
    targets = np.linspace(0.0, total, n, endpoint=False)
    Q = np.column_stack([np.interp(targets, s, C[:,j]) for j in range(3)])
    Q -= Q.mean(axis=0)
    if normalize_length:
        Q /= max(arclength(Q), 1e-30)
    return Q

def tangents(P: np.ndarray) -> np.ndarray:
    T = np.roll(P, -1, axis=0) - np.roll(P, 1, axis=0)
    return T / np.maximum(np.linalg.norm(T, axis=1)[:,None], 1e-30)

def rotate_about(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    axis = axis / max(np.linalg.norm(axis), 1e-30)
    return v*math.cos(angle) + np.cross(axis, v)*math.sin(angle) + axis*np.dot(axis, v)*(1-math.cos(angle))

def parallel_transport_frames(P: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Closed approximate Bishop/parallel-transport frames."""
    T = tangents(P); n = len(P)
    N1 = np.zeros_like(P); N2 = np.zeros_like(P)
    axes = np.eye(3)
    ref = axes[np.argmin(np.abs(axes @ T[0]))]
    N1[0] = ref - np.dot(ref, T[0])*T[0]
    N1[0] /= max(np.linalg.norm(N1[0]), 1e-30)
    N2[0] = np.cross(T[0], N1[0])

    for i in range(n-1):
        a, b = T[i], T[i+1]
        ax = np.cross(a,b); an = np.linalg.norm(ax)
        if an < 1e-14: v = N1[i].copy()
        else: v = rotate_about(N1[i], ax, math.atan2(an, np.clip(np.dot(a,b), -1, 1)))
        v -= np.dot(v,b)*b; v /= max(np.linalg.norm(v), 1e-30)
        N1[i+1] = v; N2[i+1] = np.cross(b, v)

    # holonomy correction
    a, b = T[-1], T[0]
    ax = np.cross(a,b); an = np.linalg.norm(ax)
    if an < 1e-14: vclose = N1[-1].copy()
    else: vclose = rotate_about(N1[-1], ax, math.atan2(an, np.clip(np.dot(a,b), -1, 1)))
    vclose -= np.dot(vclose,T[0])*T[0]; vclose /= max(np.linalg.norm(vclose), 1e-30)
    hol = math.atan2(np.dot(T[0], np.cross(vclose, N1[0])), np.dot(vclose, N1[0]))
    for i in range(n):
        N1[i] = rotate_about(N1[i], T[i], hol*i/n)
        N1[i] -= np.dot(N1[i],T[i])*T[i]; N1[i] /= max(np.linalg.norm(N1[i]), 1e-30)
        N2[i] = np.cross(T[i], N1[i]); N2[i] /= max(np.linalg.norm(N2[i]), 1e-30)
    return T, N1, N2

def reach_radius(P: np.ndarray, neighbor_skip: int) -> float:
    n = len(P); dmin = float("inf")
    for i in range(n):
        d = np.linalg.norm(P[i] - P, axis=1)
        mask = np.ones(n, bool)
        for k in range(-neighbor_skip, neighbor_skip+1): mask[(i+k) % n] = False
        if mask.any(): dmin = min(dmin, float(d[mask].min()))
    return max(0.5*dmin if np.isfinite(dmin) else 1/n, 1e-5)

def fibonacci_sphere(n: int, radius: float):
    pts = np.zeros((n,3)); gr = (1+math.sqrt(5))/2
    for i in range(n):
        z = 1 - 2*(i+0.5)/n
        phi = 2*math.pi*(i/gr)
        r = math.sqrt(max(0, 1-z*z))
        pts[i] = radius*np.array([r*math.cos(phi), r*math.sin(phi), z])
    return pts, pts/radius, np.full(n, 4*math.pi*radius*radius/n)

def make_mesh(P_raw, n_center, n_theta, n_sphere, tube_fraction, outer_factor):
    C = resample_closed_curve(P_raw, n_center, True)
    _, N1, N2 = parallel_transport_frames(C)
    ds = 1/n_center
    a = max(tube_fraction * reach_radius(C, max(3, int(0.04*n_center))), 1e-5)

    pts=[]; normals=[]; areas=[]
    for i in range(n_center):
        for j in range(n_theta):
            phi = 2*math.pi*j/n_theta
            radial = math.cos(phi)*N1[i] + math.sin(phi)*N2[i]
            pts.append(C[i] + a*radial)
            normals.append(-radial)  # complement outward normal at inner boundary
            areas.append(2*math.pi*a*ds/n_theta)

    tube = np.asarray(pts); tube_a = np.asarray(areas)
    R = outer_factor * max(float(np.linalg.norm(tube, axis=1).max()), 1e-6)
    sph, sph_n, sph_a = fibonacci_sphere(n_sphere, R)
    X = np.vstack([tube, sph])
    A = np.r_[tube_a, sph_a]
    labels = np.array(["tube"]*len(tube) + ["sphere"]*len(sph), object)
    return {"points":X, "areas":A, "labels":labels, "tube_radius":a, "outer_radius":R}


# ------------------------------- BEM v3 ----------------------------------

def self_term(A: np.ndarray, mu: float, self_scale: float) -> np.ndarray:
    rp = np.sqrt(np.maximum(A, 1e-300)/math.pi)
    if abs(mu) < 1e-14:
        val = 0.5*rp
    else:
        val = (1 - np.exp(-mu*rp))/(2*mu)
    return self_scale*val

def single_layer_sym(X: np.ndarray, A: np.ndarray, mu: float, self_scale: float):
    D = np.linalg.norm(X[:,None,:] - X[None,:,:], axis=2)
    G = np.exp(-mu*np.maximum(D,0))/(4*math.pi*np.maximum(D,1e-300))
    sA = np.sqrt(np.maximum(A, 1e-300))
    S = (sA[:,None]*G)*sA[None,:]
    np.fill_diagonal(S, self_term(A, mu, self_scale))
    return 0.5*(S+S.T)

def spd_inv(S: np.ndarray, ridge_rel: float):
    w, V = np.linalg.eigh(0.5*(S+S.T))
    ridge = ridge_rel*max(float(np.max(np.abs(w))), 1.0)
    w = np.maximum(w, ridge)
    return 0.5*((V/w)@V.T + ((V/w)@V.T).T)

def remove_constant(A: np.ndarray, B: np.ndarray):
    n = A.shape[0]
    c = np.ones((n,1))/math.sqrt(n)
    M = np.eye(n); M[:,0:1] = c
    Q,_ = np.linalg.qr(M)
    Q = Q[:,1:]
    return Q.T@A@Q, Q.T@B@Q

def invariant_from_mesh(mesh, args):
    X, A, labels = mesh["points"], mesh["areas"], mesh["labels"]
    if args.boundary_subspace != "all":
        idx = np.where(labels == args.boundary_subspace)[0]
        X, A = X[idx], A[idx]

    a, R = mesh["tube_radius"], mesh["outer_radius"]
    if args.mu_mode == "inverse_tube_radius": mu = 1/max(a,1e-30)
    elif args.mu_mode == "inverse_outer_radius": mu = 1/max(R,1e-30)
    elif args.mu_mode == "fixed": mu = args.mu_value
    else: mu = 0.0

    SR = single_layer_sym(X, A, 0.0, args.self_scale)
    ST = single_layer_sym(X, A, mu, args.self_scale)
    LR = spd_inv(SR, args.ridge_rel)
    LT = spd_inv(ST, args.ridge_rel)
    if not args.keep_constant:
        LR, LT = remove_constant(LR, LT)

    if HAVE_SCIPY:
        ev = eigh(LR, LT, eigvals_only=True)
    else:
        ev = np.linalg.eigvals(np.linalg.solve(LT + args.ridge_rel*np.eye(LT.shape[0]), LR)).real
    ev = np.sort(np.real(ev[np.isfinite(ev)]))
    ev = ev[ev > 1e-14]
    use = ev[:min(args.modes, len(ev))]
    if len(use) < max(3, min(6, args.modes)):
        raise ValueError("too few positive generalized eigenvalues")

    return {
        "S_logdet": float(-np.sum(np.log(np.maximum(use, 1e-300)))),
        "S_trace": float(np.sum(use)),
        "S_mean_impedance": float(np.mean(use)),
        "S_rel_spread": float(np.std(use)/max(abs(float(np.mean(use))),1e-30)),
        "min_impedance_eig": float(np.min(use)),
        "max_impedance_eig": float(np.max(use)),
        "positive_spectrum": bool(np.all(use > 0)),
        "n_modes_used": int(len(use)),
        "boundary_nodes": int(len(mesh["points"])),
        "selected_nodes": int(len(X)),
        "tube_radius": float(a),
        "outer_radius": float(R),
        "screening_mu": float(mu),
        "operator_backend": "BEM_V3_AREA_SYMMETRIC_STEKLOV",
    }


# ------------------------------- gates -----------------------------------

def random_rotation(rng):
    A = rng.normal(size=(3,3)); Q,_ = np.linalg.qr(A)
    if np.linalg.det(Q) < 0: Q[:,0] *= -1
    return Q

def transform(P, rng):
    return float(np.exp(rng.normal(0,0.7))) * (P @ random_rotation(rng).T) + rng.normal(size=3)

def rel_range(vals):
    vals = np.asarray(vals, float)
    if len(vals) < 2: return 0.0
    return float((vals.max()-vals.min())/max(abs(vals.mean()),1e-30))

def compute(P, args, n_center=None):
    mesh = make_mesh(P, n_center or args.n_center, args.n_theta, args.n_sphere,
                     args.tube_fraction, args.outer_factor)
    return invariant_from_mesh(mesh, args)

def audit_one(name, P, args):
    inv = compute(P, args)
    rng = np.random.default_rng(args.seed)

    ivals = [float(compute(transform(P, rng), args)["S_logdet"]) for _ in range(args.n_invariance_trials)]
    irel = rel_range(ivals)
    rvals = [float(compute(P, args, nc)["S_logdet"]) for nc in args.center_resolution_list]
    rrel = rel_range(rvals)

    return {
        "knot": name,
        "raw_points": int(P.shape[0]),
        "raw_arclength": arclength(P),
        "parse_gate_G1": "PASS",
        "alpha_blind_gate_G2": "PASS_NO_ALPHA_OR_EM_CONSTANTS_USED",
        "operator_gate_G3": "PASS" if inv["positive_spectrum"] else "FAIL",
        "invariance_gate_G4": "PASS" if irel <= args.invariance_tol else "FAIL",
        "invariance_rel_range_S_logdet": irel,
        "resolution_gate_G5": "PASS" if rrel <= args.resolution_tol else "FAIL",
        "resolution_rel_range_S_logdet": rrel,
        "candidate_status": "BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION",
        **inv,
    }

def find_like(rows, pats):
    for pat in pats:
        rx = re.compile(pat, re.I)
        for r in rows:
            if rx.search(str(r.get("knot",""))): return r
    return None

def gate6(rows, tol):
    unk = find_like(rows, [r"^0[:_]1(?:[:_]1)?$", r"^0_1$", r"unknot", r"circle"])
    tre = find_like(rows, [r"^3[:_]1(?:[:_]1)?$", r"^3_1$", r"trefoil"])
    fig = find_like(rows, [r"^4[:_]1(?:[:_]1)?$", r"^4_1$", r"figure"])
    if unk is None or tre is None:
        return {"global_control_gate_G6":"SKIP", "global_control_note":"Need 0_1 and 3_1 controls",
                "alpha_map_status":"NO_CANONICAL_ALPHA_MAP_SPECIFIED__NO_FIT_PERFORMED"}
    out = {"alpha_map_status":"NO_CANONICAL_ALPHA_MAP_SPECIFIED__NO_FIT_PERFORMED"}
    S0, S3 = float(unk["S_logdet"]), float(tre["S_logdet"])
    d03 = abs(S3-S0)/max(1.0, abs(S3), abs(S0))
    out["rel_sep_3_1_vs_0_1_S_logdet"] = d03
    notes = []
    if d03 <= tol: notes.append("trefoil not separated from unknot")
    if fig is not None:
        S4 = float(fig["S_logdet"])
        d34 = abs(S3-S4)/max(1.0, abs(S3), abs(S4))
        out["rel_sep_3_1_vs_4_1_S_logdet"] = d34
        if d34 <= tol: notes.append("trefoil not separated from figure-eight")
    out["global_control_gate_G6"] = "FAIL" if notes else "PASS"
    out["global_control_note"] = "; ".join(notes) if notes else "Trefoil separated from available controls"
    return out



# ----------------------------- SSTcore loader -----------------------------

def parse_id_csv(s: str):
    return [x.strip() for x in str(s).split(",") if x.strip()]

def import_sstcore(try_pip: bool = False):
    """
    Import SSTcore using the user's preferred package name.

    Optional pip install is only attempted when --pip-install-sstcore is passed.
    """
    try:
        import SSTcore as sst
        return sst
    except ImportError:
        if not try_pip:
            raise
        subprocess.check_call([sys.executable, "-m", "pip", "install", "SSTcore"])
        import SSTcore as sst
        return sst

def sstcore_block_id(block):
    return str(getattr(block, "id", getattr(block, "Id", "")))

def sstcore_display_name(block):
    """
    Convert SSTcore ideal.txt AB Ids into names that the control gates recognize.
    Examples:
        0:1:1 -> 0_1
        3:1:1 -> 3_1
        4:1:1 -> 4_1
        5:2:1 -> 5_2_1
    """
    bid = sstcore_block_id(block)
    parts = bid.split(":")
    if len(parts) >= 2 and parts[0] in {"0", "3", "4"} and parts[1] == "1":
        return f"{parts[0]}_1"
    return bid.replace(":", "_")

def list_sstcore_ideal_blocks(args):
    sst = import_sstcore(args.pip_install_sstcore)
    ideal_path = Path(sst.get_ideal_txt_path())
    blocks = sst.parse_ideal_txt_multi(str(ideal_path))
    print(f"SSTcore ideal.txt: {ideal_path}")
    print(f"blocks: {len(blocks)}")
    for i, b in enumerate(blocks[:args.sstcore_max_knots]):
        bid = sstcore_block_id(b)
        conway = getattr(b, "conway", "")
        L = getattr(b, "L", "")
        D = getattr(b, "D", "")
        print(f"{i:4d}  Id={bid:12s} Conway={str(conway):8s} L={L} D={D}")
    if len(blocks) > args.sstcore_max_knots:
        print(f"... truncated at --sstcore-max-knots={args.sstcore_max_knots}")

def load_knots_from_sstcore(args) -> Dict[str, np.ndarray]:
    """
    Load and sample ideal Fourier blocks from SSTcore.

    Requires installed SSTcore:
        pip install SSTcore

    Uses:
        SSTcore.get_ideal_txt_path()
        SSTcore.parse_ideal_txt_multi(...)
        SSTcore.index_of_ideal_id(...)
        SSTcore.evaluate_fourier_block(...)
    """
    sst = import_sstcore(args.pip_install_sstcore)
    ideal_path = Path(sst.get_ideal_txt_path())
    blocks = sst.parse_ideal_txt_multi(str(ideal_path))

    if args.list_sstcore_knots:
        list_sstcore_ideal_blocks(args)
        raise SystemExit(0)

    targets = parse_id_csv(args.sstcore_knot_ids)
    selected = []

    if len(targets) == 1 and targets[0].lower() == "all":
        for b in blocks:
            # Keep single-component AB blocks when possible.
            if int(getattr(b, "n", 1) or 1) == 1:
                selected.append(b)
            if len(selected) >= args.sstcore_max_knots:
                break
    else:
        for tid in targets:
            idx = -1
            if hasattr(sst, "index_of_ideal_id"):
                idx = int(sst.index_of_ideal_id(blocks, tid))
            if idx < 0:
                for j, b in enumerate(blocks):
                    if sstcore_block_id(b) == tid:
                        idx = j
                        break
            if idx < 0:
                raise ValueError(f"SSTcore ideal block Id={tid!r} not found in {ideal_path}")
            selected.append(blocks[idx])

    out: Dict[str, np.ndarray] = {}
    s = np.linspace(0.0, 2.0 * math.pi, args.sstcore_samples, endpoint=False)
    for b in selected:
        name = sstcore_display_name(b)
        # Avoid duplicate names.
        base, k = name, 2
        while name in out:
            name = f"{base}__{k}"
            k += 1
        pts = np.asarray(sst.evaluate_fourier_block(b.fourier, s.tolist()), dtype=float)
        if pts.ndim != 2 or pts.shape[1] != 3:
            raise ValueError(f"SSTcore evaluate_fourier_block returned invalid shape for {sstcore_block_id(b)}: {pts.shape}")
        out[name] = pts
    return out

def write_sampled_coordinate_file(path: Path, knots: Dict[str, np.ndarray], source_note: str):
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# Sampled coordinate file generated by routeB_RT_bem_v3_1_sstcore_falsifier.py\n")
        f.write(f"# Source: {source_note}\n\n")
        for name, P in knots.items():
            f.write(f"# Knot: {name}\n")
            for x, y, z in np.asarray(P, float):
                f.write(f"{x:.12g} {y:.12g} {z:.12g}\n")
            f.write("\n")

def load_knots_from_args(args, outdir: Path):
    """
    Source policy:
      --source file    : use --ideal only
      --source sstcore : load ideal Fourier data from SSTcore
      --source auto    : use --ideal if it exists, otherwise SSTcore
    """
    if args.make_demo:
        ideal = outdir / "routeB_demo_ideal.txt"
        make_demo(ideal)
        return parse_ideal_file(ideal), ideal, "demo-file"

    ideal = Path(args.ideal)
    if args.source == "file":
        return parse_ideal_file(ideal), ideal, f"file:{ideal}"

    if args.source == "sstcore" or (args.source == "auto" and not ideal.exists()):
        knots = load_knots_from_sstcore(args)
        sampled = outdir / "sstcore_sampled_ideal_used.txt"
        write_sampled_coordinate_file(sampled, knots, f"SSTcore ideal.txt; ids={args.sstcore_knot_ids}; samples={args.sstcore_samples}")
        return knots, sampled, "SSTcore"

    return parse_ideal_file(ideal), ideal, f"file:{ideal}"


# ------------------------------- output ----------------------------------

def write_csv(path, rows):
    if not rows: return
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows)

def write_report(path, input_path, rows, global_row, args):
    sha = hashlib.sha256(Path(input_path).read_bytes()).hexdigest() if Path(input_path).exists() else "missing"
    L = []
    L += ["# Route B BEM v3 audit", "", f"Input: `{input_path}`", f"SHA256: `{sha}`", ""]
    L += ["## Backend", "Area-symmetric BEM/Steklov with parallel-transport tube frames and screened self terms.", ""]
    L += ["## Global G6"]
    for k,v in global_row.items(): L.append(f"- `{k}`: `{v}`")
    L.append("")
    L += ["## Per-knot"]
    for r in rows:
        L += [f"### {r['knot']}",
              f"- `S_logdet`: `{float(r['S_logdet']):.12g}`",
              f"- `S_trace`: `{float(r['S_trace']):.12g}`",
              f"- `G3`: `{r['operator_gate_G3']}`",
              f"- `G4`: `{r['invariance_gate_G4']}` rel `{float(r['invariance_rel_range_S_logdet']):.3e}`",
              f"- `G5`: `{r['resolution_gate_G5']}` rel `{float(r['resolution_rel_range_S_logdet']):.3e}`",
              f"- status: `{r['candidate_status']}`", ""]
    L += ["## Interpretation", "Passing this audit does not derive alpha. It only means this BEM v3 candidate survives the chosen falsifiers."]
    Path(path).write_text("\n".join(L), encoding="utf-8")

def make_demo(path, n=160):
    t = np.linspace(0, 2*np.pi, n, endpoint=False)
    unk = np.c_[np.cos(t), np.sin(t), np.zeros_like(t)]
    R,r = 2.0,0.75
    tre = np.c_[(R+r*np.cos(3*t))*np.cos(2*t), (R+r*np.cos(3*t))*np.sin(2*t), r*np.sin(3*t)]
    fig = np.c_[(2+np.cos(2*t))*np.cos(3*t), (2+np.cos(2*t))*np.sin(3*t), np.sin(4*t)]
    with open(path, "w", encoding="utf-8") as f:
        for nm,P in [("0_1",unk),("3_1",tre),("4_1",fig)]:
            f.write(f"# Knot: {nm}\n")
            for x,y,z in P: f.write(f"{x:.12g} {y:.12g} {z:.12g}\n")
            f.write("\n")

def parse_ints(s): return [int(x) for x in s.split(",") if x.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v3")
    ap.add_argument("--make-demo", action="store_true")
    ap.add_argument("--source", choices=["auto", "file", "sstcore"], default="auto", help="auto: use --ideal if present, else SSTcore")
    ap.add_argument("--sstcore-knot-ids", default="0:1:1,3:1:1,4:1:1", help="comma SSTcore ideal AB Ids, or all")
    ap.add_argument("--sstcore-samples", type=int, default=1200, help="raw Fourier samples per SSTcore knot before BEM resampling")
    ap.add_argument("--sstcore-max-knots", type=int, default=20, help="limit for --sstcore-knot-ids all and --list-sstcore-knots")
    ap.add_argument("--list-sstcore-knots", action="store_true", help="list SSTcore ideal.txt blocks and exit")
    ap.add_argument("--pip-install-sstcore", action="store_true", help="try `pip install SSTcore` if import fails")
    ap.add_argument("--n-center", type=int, default=32)
    ap.add_argument("--n-theta", type=int, default=6)
    ap.add_argument("--n-sphere", type=int, default=144)
    ap.add_argument("--modes", type=int, default=24)
    ap.add_argument("--center-resolution-list", default="24,32,40")
    ap.add_argument("--tube-fraction", type=float, default=0.30)
    ap.add_argument("--outer-factor", type=float, default=2.6)
    ap.add_argument("--mu-mode", choices=["inverse_tube_radius","inverse_outer_radius","fixed","zero"], default="inverse_outer_radius")
    ap.add_argument("--mu-value", type=float, default=1.0)
    ap.add_argument("--boundary-subspace", choices=["all","tube","sphere"], default="all")
    ap.add_argument("--ridge-rel", type=float, default=1e-9)
    ap.add_argument("--self-scale", type=float, default=1.0)
    ap.add_argument("--keep-constant", action="store_true")
    ap.add_argument("--n-invariance-trials", type=int, default=3)
    ap.add_argument("--invariance-tol", type=float, default=5e-4)
    ap.add_argument("--resolution-tol", type=float, default=0.20)
    ap.add_argument("--control-separation-tol", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=12345)
    args = ap.parse_args()
    args.center_resolution_list = parse_ints(args.center_resolution_list)

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    knots, ideal, source_note = load_knots_from_args(args, outdir)
    rows=[]
    for nm,P in knots.items():
        try: rows.append(audit_one(nm,P,args))
        except Exception as e:
            rows.append({"knot":nm, "parse_gate_G1":"FAIL_EXCEPTION",
                         "alpha_blind_gate_G2":"PASS_NO_ALPHA_OR_EM_CONSTANTS_USED",
                         "operator_gate_G3":"FAIL_EXCEPTION", "invariance_gate_G4":"FAIL_EXCEPTION",
                         "resolution_gate_G5":"FAIL_EXCEPTION",
                         "candidate_status":f"EXCEPTION {type(e).__name__}: {e}"})
    grow = gate6(rows, args.control_separation_tol)
    write_csv(outdir/"routeB_BEM_v3_per_knot_invariants.csv", rows)
    write_csv(outdir/"routeB_BEM_v3_global_gates.csv", [grow])
    write_report(outdir/"routeB_BEM_v3_audit_report.md", ideal, rows, grow, args)

    print("="*78)
    print("Route B BEM v3 R--T falsifier audit complete")
    print("="*78)
    print(f"Input: {ideal}")
    print(f"Source: {source_note}")
    print(f"Knots parsed: {len(rows)}")
    print(f"G6 controls: {grow.get('global_control_gate_G6')} -- {grow.get('global_control_note')}")
    for r in rows:
        v = float(r.get("S_logdet", float("nan"))) if "S_logdet" in r else float("nan")
        print(f"{str(r.get('knot')):16s} S_logdet={v: .8g} G3={r.get('operator_gate_G3')} G4={r.get('invariance_gate_G4')} G5={r.get('resolution_gate_G5')}")
    print(f"Outputs: {outdir}")

if __name__ == "__main__":
    main()
