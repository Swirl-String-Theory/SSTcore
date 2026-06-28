#!/usr/bin/env python3
# =============================================================================
#  fs_relax_xpu.py  -  Faddeev-Skyrme Hopfion relaxer, Intel-Arc (XPU) ready.
#
#  Mirrors the numpy reference (hopfion_tools.py / fs_relax2.py), which was
#  validated: Hopf meter -> integer & topologically conserved; analytic gradient
#  gradient-checked to 1.3e-8; fixed-E2 relaxer holds Q_H to 98% at N=72.
#  Here the gradient is taken by autograd, so the port is correct by construction;
#  run this file to SELF-VALIDATE on your hardware (it prints a gradient check,
#  axial Q-convergence, and fixed-E2 Q_H retention).
#
#  Intel Arc A770 (no CUDA): install one of
#     pip install torch --index-url https://download.pytorch.org/whl/xpu
#     # or IPEX route:
#     pip install torch==2.* intel-extension-for-pytorch==2.* \
#         --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/
#  then:  python fs_relax_xpu.py
# =============================================================================
import math
import numpy as np
import torch

# ---------------------------------------------------------------- device ----
def get_device(verbose=True):
    # Some setups need IPEX imported before torch.xpu is populated.
    try:
        import intel_extension_for_pytorch as _ipex  # noqa: F401
    except Exception:
        pass
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        dev = torch.device("xpu")
    elif torch.cuda.is_available():
        dev = torch.device("cuda")
    elif getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        dev = torch.device("mps")
    else:
        dev = torch.device("cpu")
    if verbose:
        print(f"[device] {dev}")
    return dev

DTYPE = torch.float64   # reset per-device in __main__ via pick_dtype(); fp32 on XPU/MPS

def pick_dtype(dev):
    # Consumer Intel Arc (XPU) and Apple MPS do NOT support fp64 in hardware.
    return torch.float32 if dev.type in ("xpu", "mps") else torch.float64

# ------------------------------------------------------------- operators ----
def deriv(f, axis, dx):
    """Central difference of a 3D SCALAR component along spatial axis (0,1,2)."""
    return (torch.roll(f, -1, axis) - torch.roll(f, 1, axis)) / (2 * dx)

def _cross(u, v):
    return torch.stack([u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]])

def grads_n(n, dx):
    """D[i] = d_i n  (each (3,N,N,N))."""
    return [torch.stack([deriv(n[a], i, dx) for a in range(3)]) for i in range(3)]

# --------------------------------------------------------------- energy -----
def energy(n, dx, k2=1.0, k4=1.0):
    D = grads_n(n, dx)
    E2 = sum((D[i]**2).sum() for i in range(3))
    F = lambda i, j: (n * _cross(D[i], D[j])).sum(0)
    E4 = sum((F(i, j)**2).sum() for i in range(3) for j in range(3))
    return k2*E2 + k4*E4, E2, E4

# --------------------------------------------------- Hopf charge meter ------
def hopf_charge(n, dx, fft_on_cpu=False):
    """Q_H meter with automatic CPU-FFT fallback (some XPU/MPS FFT paths are flaky)."""
    try:
        return _hopf_charge(n, dx, fft_on_cpu)
    except Exception as e:
        if not fft_on_cpu:
            return _hopf_charge(n, dx, True)
        raise e

def _hopf_charge(n, dx, fft_on_cpu=False):
    """Q_H = (1/16 pi^2) INT A.B,  curl A = B,  B_i = -1/2 eps_ijk F_jk."""
    D = grads_n(n, dx)
    F = lambda i, j: (n * _cross(D[i], D[j])).sum(0)
    B = torch.stack([-F(1, 2), -F(2, 0), -F(0, 1)])
    dev = torch.device("cpu") if fft_on_cpu else n.device
    Bc = B.to(dev)
    N = n.shape[1]
    k = (2*math.pi*torch.fft.fftfreq(N, d=dx)).to(device=dev, dtype=Bc.real.dtype)
    KX, KY, KZ = torch.meshgrid(k, k, k, indexing="ij")
    k2 = KX**2 + KY**2 + KZ**2
    k2[0, 0, 0] = 1.0
    Bh = torch.stack([torch.fft.fftn(Bc[i]) for i in range(3)])
    K = torch.stack([KX, KY, KZ]).to(Bh.dtype)
    crossKB = _cross(K, Bh)                      # (3,...), complex
    Ah = 1j * crossKB / k2
    A = torch.stack([torch.fft.ifftn(Ah[i]).real for i in range(3)])
    return ((1.0/(16*math.pi**2)) * (A*Bc).sum() * dx**3).item()

# -------------------------------------------------- fixed-E2 relaxer --------
def proj_sphere(g, n):
    return g - (g*n).sum(0) * n

def fixedE2_projected_step(n, dx, delta, E2_target, k2=1.0, k4=1.0, feedback=0.3):
    """One projected E4-descent step tangent to E2=const, with gentle E2 feedback."""
    n = n.detach().clone().requires_grad_(True)
    _, E2, E4 = energy(n, dx, k2, k4)
    g2, = torch.autograd.grad(E2, n, retain_graph=True)
    g4, = torch.autograd.grad(E4, n)
    with torch.no_grad():
        g2p = proj_sphere(g2, n)
        g4p = proj_sphere(g4, n)
        denom = (g2p*g2p).sum() + 1e-12
        gc = g4p - ((g4p*g2p).sum()/denom)*g2p
        gc = gc + feedback*((E2 - E2_target)/E2_target)*g2p
        gmax = torch.sqrt((gc**2).sum(0)).max() + 1e-12
        n_new = n - (delta/gmax)*gc
        n_new = n_new/torch.linalg.vector_norm(n_new, dim=0)
    return n_new.detach(), E2.detach(), E4.detach()


def relax_fixedE2_toposafe(n, dx, steps, delta=0.02, k2=1.0, k4=1.0, feedback=0.3,
                           report=40, fft_on_cpu=False, q_target=None,
                           q_hold_min=0.90, q_abs_tol=None, check_every=10,
                           min_delta=1e-4, max_rejects=12, return_info=False):
    """Topology-safe fixed-E2 relaxation.

    This is deliberately conservative: it does not pretend to compute a reliable
    differentiable Hopf-charge gradient on XPU. Instead it performs fixed-E2
    projected descent in short chunks, measures Q_H, and rejects/rolls back any
    chunk that leaks too much topology. Rejected chunks halve delta. If delta
    falls below min_delta, the run stops and reports TOPOLOGY_LEAK.

    Use this for production sector tests: energies are comparable only for runs
    that keep their initial Q_H sector.
    """
    n = n.detach().clone()
    with torch.no_grad():
        _, E2t, _ = energy(n, dx, k2, k4)
        E2_target = E2t.item()
    q0 = hopf_charge(n, dx, fft_on_cpu) if q_target is None else float(q_target)
    q0_abs = abs(q0) + 1e-12
    local_delta = float(delta)
    accepted = 0
    rejects = 0
    last_good = n.detach().clone()
    status = "OK"

    def q_is_ok(q):
        hold = abs(q)/q0_abs
        err = abs(abs(q) - q0_abs)
        return hold >= q_hold_min and (q_abs_tol is None or err <= q_abs_tol), hold, err

    while accepted < steps:
        chunk = min(max(1, check_every), steps - accepted)
        trial = n.detach().clone()
        for _ in range(chunk):
            trial, _, _ = fixedE2_projected_step(trial, dx, local_delta, E2_target, k2, k4, feedback)

        q_trial = hopf_charge(trial, dx, fft_on_cpu)
        ok, hold, qerr = q_is_ok(q_trial)
        if ok:
            n = trial.detach()
            last_good = n.detach().clone()
            accepted += chunk
            if accepted % report == 0 or accepted == steps:
                with torch.no_grad():
                    _, E2, E4 = energy(n, dx, k2, k4)
                print(f"   step {accepted:4d}  E2={E2.item()*dx**3:8.2f} (tgt {E2_target*dx**3:7.2f})"
                      f"  E4={E4.item()*dx**3:8.2f}  Q_H={q_trial:+.3f}"
                      f"  hold={hold:.3f}  delta={local_delta:.3g}")
        else:
            rejects += 1
            n = last_good.detach().clone()
            local_delta *= 0.5
            print(f"   reject at step {accepted+chunk:4d}: Q_H={q_trial:+.3f}"
                  f" hold={hold:.3f} err={qerr:.3f}; rollback, delta -> {local_delta:.3g}")
            if local_delta < min_delta or rejects > max_rejects:
                status = "TOPOLOGY_LEAK"
                print(f"   abort: {status}; accepted={accepted}, rejects={rejects}, delta={local_delta:.3g}")
                break

    qf = hopf_charge(n, dx, fft_on_cpu)
    info = {
        "status": status,
        "q0": q0,
        "q_final": qf,
        "hold": abs(qf)/q0_abs,
        "accepted_steps": accepted,
        "rejected_chunks": rejects,
        "delta_final": local_delta,
        "E2_target": E2_target,
    }
    return (n.detach(), info) if return_info else n.detach()


def relax_fixedE2(n, dx, steps, delta=0.02, k2=1.0, k4=1.0, feedback=0.3,
                  report=40, fft_on_cpu=False):
    """Minimise E4 at pinned E2 (kills scale collapse). Returns relaxed n."""
    n = n.detach().clone().requires_grad_(True)
    with torch.no_grad():
        _, E2t, _ = energy(n, dx, k2, k4)
        E2_target = E2t.item()
    for s in range(steps + 1):
        _, E2, E4 = energy(n, dx, k2, k4)
        g2, = torch.autograd.grad(E2, n, retain_graph=True)
        g4, = torch.autograd.grad(E4, n)
        with torch.no_grad():
            g2p = proj_sphere(g2, n); g4p = proj_sphere(g4, n)
            denom = (g2p*g2p).sum() + 1e-12
            gc = g4p - ((g4p*g2p).sum()/denom)*g2p          # tangent to E2=const
            gc = gc + feedback*((E2 - E2_target)/E2_target)*g2p
            gmax = torch.sqrt((gc**2).sum(0)).max() + 1e-12
            if s % report == 0:
                q = hopf_charge(n, dx, fft_on_cpu)
                print(f"   step {s:4d}  E2={E2.item()*dx**3:8.2f} (tgt {E2_target*dx**3:7.2f})"
                      f"  E4={E4.item()*dx**3:8.2f}  Q_H={q:+.3f}")
            n.data -= (delta/gmax)*gc
            n.data /= torch.linalg.vector_norm(n, dim=0)
        n.grad = None
    return n.detach()

# --------------------------------------------------------- field builders ---
def build_mn(N, box, a, m, nn, device):
    # complex inverse-stereographic map built on CPU (XPU complex support is partial),
    # then the real unit field is moved to the device.
    dt = pick_dtype(device); cpu = torch.device("cpu")
    x = torch.linspace(-box/2, box/2, N+1, dtype=torch.float64, device=cpu)[:-1]
    dx = (x[1]-x[0]).item()
    X, Y, Z = torch.meshgrid(x, x, x, indexing="ij")
    r2 = X**2+Y**2+Z**2; den = r2+a**2
    Z1 = (2*a*(X + 1j*Y))/den
    Z2 = (2*a*Z + 1j*(r2 - a**2))/den
    u = Z1**m; v = Z2**nn; nrm = (u.abs()**2 + v.abs()**2)
    n = torch.stack([2*(u.conj()*v).real/nrm, 2*(u.conj()*v).imag/nrm,
                     (u.abs()**2 - v.abs()**2)/nrm])
    n = n/torch.linalg.vector_norm(n, dim=0)
    return n.to(device=device, dtype=dt), dx

def torus_knot_curve(p=2, q=3, M=600, scale=1.0, device="cpu"):
    """Self-contained (p,q) torus knot; trefoil = (2,3). Returns (M,3) tensor."""
    dt = pick_dtype(device)
    t = torch.linspace(0, 2*math.pi, M+1, dtype=dt, device=device)[:-1]
    R = (2 + torch.cos(q*t))
    g = torch.stack([R*torch.cos(p*t), R*torch.sin(p*t), torch.sin(q*t)], 1)
    g = g - g.mean(0)
    return g * (scale/torch.linalg.vector_norm(g, dim=1).max())

def curve_min_distance(curve, exclude_neighbors=8, chunk=1024):
    """Minimum nonlocal curve-point distance, excluding nearby samples on a closed curve."""
    g = curve.detach()
    M = g.shape[0]
    dev = g.device
    all_j = torch.arange(M, device=dev)
    best = torch.tensor(float("inf"), dtype=g.dtype, device=dev)
    for start in range(0, M, chunk):
        stop = min(M, start + chunk)
        gi = g[start:stop]
        ii = torch.arange(start, stop, device=dev)
        d2 = ((gi[:, None, :] - g[None, :, :])**2).sum(-1)
        sep = torch.abs(ii[:, None] - all_j[None, :])
        sep = torch.minimum(sep, M - sep)
        d2 = d2.masked_fill(sep <= exclude_neighbors, float("inf"))
        best = torch.minimum(best, d2.min())
    return float(torch.sqrt(best).item())


def curve_spacing_stats(curve):
    """Consecutive-sample spacing statistics for a closed curve."""
    ds = torch.linalg.vector_norm(torch.roll(curve, -1, 0) - curve, dim=1)
    return {"ds_min": float(ds.min().item()), "ds_mean": float(ds.mean().item()),
            "ds_max": float(ds.max().item())}


def seed_geometry_diagnostics(curve, N, box, R_tube, exclude_neighbors=8):
    """Diagnostics for whether a tubular seed is geometrically resolvable."""
    dx = box/float(N)
    dmin = curve_min_distance(curve, exclude_neighbors=exclude_neighbors)
    stats = curve_spacing_stats(curve)
    return {
        "dx": dx,
        "d_min": dmin,
        "R_tube": float(R_tube),
        "tube_over_dmin": float(R_tube)/(dmin + 1e-12),
        "tube_voxels": float(R_tube)/(dx + 1e-12),
        "ds_min": stats["ds_min"],
        "ds_mean": stats["ds_mean"],
        "ds_max": stats["ds_max"],
        "dsmax_over_tube": stats["ds_max"]/(float(R_tube) + 1e-12),
        "ok_tube_separation": float(R_tube) <= 0.25*dmin,
        "ok_tube_resolution": float(R_tube) >= 2.0*dx,
        "ok_curve_sampling": stats["ds_max"] <= 0.50*float(R_tube),
    }


def knot_seed(curve, N, box, R_tube, framing_twists, device):
    dt = pick_dtype(device)
    """Tubular n-field around a knot curve. NB: Q_H of the seed depends on the
    framing; framing_twists adds longitudinal turns relative to the
    parallel-transport frame. Seifert/self-linking framing is the correct
    convention (see BUILD.md) — verify the seed Q_H with hopf_charge() and let
    relaxation pick the energy-minimal framing in the chosen sector."""
    g = curve.to(device)
    M = g.shape[0]
    T = torch.roll(g, -1, 0) - torch.roll(g, 1, 0); T = T/torch.linalg.vector_norm(T, dim=1, keepdim=True)
    e1 = torch.zeros_like(g); v0 = torch.tensor([1.0, 0, 0], dtype=dt, device=device)
    if abs(float(v0 @ T[0])) > 0.9: v0 = torch.tensor([0, 1.0, 0], dtype=dt, device=device)
    e = v0 - (v0 @ T[0])*T[0]; e1[0] = e/torch.linalg.vector_norm(e)
    for kk in range(1, M):                       # parallel transport
        e = e1[kk-1] - (e1[kk-1] @ T[kk])*T[kk]; e1[kk] = e/torch.linalg.vector_norm(e)
    e2 = torch.cross(T, e1, dim=1)
    x = torch.linspace(-box/2, box/2, N+1, dtype=dt, device=device)[:-1]
    dx = (x[1]-x[0]).item()
    X, Y, Z = torch.meshgrid(x, x, x, indexing="ij")
    P = torch.stack([X, Y, Z], -1).reshape(-1, 3)
    idx = torch.empty(P.shape[0], dtype=torch.long, device=device)
    rho = torch.empty(P.shape[0], dtype=dt, device=device)
    chunk = 8192                                               # chunk to avoid (P x M) memory spike
    for c in range(0, P.shape[0], chunk):
        d2 = ((P[c:c+chunk, None, :] - g[None, :, :])**2).sum(-1)   # (chunk, M)
        mn, ii = d2.min(1); idx[c:c+chunk] = ii; rho[c:c+chunk] = torch.sqrt(mn)
    dvec = P - g[idx]
    a1 = (dvec*e1[idx]).sum(1); a2 = (dvec*e2[idx]).sum(1)
    thm = torch.atan2(a2, a1)
    psi = thm + framing_twists*(2*math.pi*idx.to(dt)/M)
    Theta = math.pi*torch.clamp(1 - rho/R_tube, 0, 1)
    s = torch.sin(Theta)
    n = torch.stack([s*torch.cos(psi), s*torch.sin(psi), torch.cos(Theta)]).reshape(3, N, N, N)
    return n/torch.linalg.vector_norm(n, dim=0), dx

# ================================ self-test =================================
if __name__ == "__main__":
    dev = get_device()
    DTYPE = pick_dtype(dev)
    print(f"[dtype]  {DTYPE}" + ("  (fp64 unsupported on this device -> fp32)"
                                 if DTYPE == torch.float32 and dev.type in ("xpu", "mps") else ""))
    torch.manual_seed(0)

    print("\n[1] gradient check (autograd vs finite diff), random unit field, N=12:")
    eps = 1e-3 if DTYPE == torch.float32 else 1e-5
    tol = 2e-2 if DTYPE == torch.float32 else 1e-4
    n = torch.randn(3, 12, 12, 12, dtype=DTYPE, device=dev)
    n = (n/torch.linalg.vector_norm(n, dim=0)).requires_grad_(True)
    E, _, _ = energy(n, 0.4); E.backward()
    g = n.grad.detach()
    worst = 0.0
    for _ in range(8):
        a = int(torch.randint(3, (1,))); idx = tuple(int(torch.randint(12, (1,))) for _ in range(3))
        with torch.no_grad():
            # fp32 FD often rounds Ep==Em; reference FD in fp64 on CPU when needed.
            if DTYPE == torch.float32:
                base = n.detach().double().cpu()
                fd_eps = 1e-5
                np_ = base.clone(); np_[a][idx] += fd_eps
                nm = base.clone(); nm[a][idx] -= fd_eps
                Ep, _, _ = energy(np_, 0.4); Em, _, _ = energy(nm, 0.4)
            else:
                np_ = n.detach().clone(); np_[a][idx] += eps; Ep, _, _ = energy(np_, 0.4)
                nm = n.detach().clone(); nm[a][idx] -= eps; Em, _, _ = energy(nm, 0.4)
                fd_eps = eps
        fd = ((Ep-Em)/(2*fd_eps)).item(); an = g[a][idx].item()
        worst = max(worst, abs(fd-an)/(abs(fd)+abs(an)+1e-12))
    ref = "fp64-CPU FD" if DTYPE == torch.float32 else "same-device FD"
    print(f"    max relative error = {worst:.2e}  (tol {tol:.0e}, {ref}) ->",
          "PASS" if worst < tol else "FAIL")

    print("\n[2] Hopf meter on axial (m,n), expect Q_H ~ m*n (deficit = resolution):")
    for (m, nn) in [(1, 1), (2, 1), (1, 2), (2, 2)]:
        nf, dx = build_mn(64, 8.0, 1.2, m, nn, dev)
        print(f"    (m,n)=({m},{nn})  Q_H={hopf_charge(nf, dx):+.3f}  expected {m*nn}")

    print("\n[3] fixed-E2 relaxation, axial Q=2, N=72 (expect Q_H retained ~>=95%):")
    nf, dx = build_mn(72, 9.0, 1.8, 2, 1, dev)
    q0 = hopf_charge(nf, dx)
    nf = relax_fixedE2(nf, dx, steps=100, delta=0.02, report=50)
    q1 = hopf_charge(nf, dx)
    print(f"    Q_H {q0:+.3f} -> {q1:+.3f}   retained {100*q1/q0:.0f}%")

    print("\n[4] trefoil (2,3) knotted seed -> measured Q_H (emergent after relax):")
    curve = torus_knot_curve(2, 3, M=600, scale=9.0*0.30, device=dev)
    nf, dx = knot_seed(curve, 64, 9.0, R_tube=1.4, framing_twists=7, device=dev)
    print(f"    seed Q_H = {hopf_charge(nf, dx):+.2f}  (framing-dependent; relax on N>=128 to settle)")
    print("\nDone. For production: N>=128, DTYPE=float32, seed Q=7 (trefoil) & Q=11 (5_1).")