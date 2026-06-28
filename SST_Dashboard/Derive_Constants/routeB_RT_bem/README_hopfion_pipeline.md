# SST Hopfion / knot pipeline — file index (status-pure)

## GPU run (Intel Arc A770 — XPU, no CUDA)
- `fs_relax_xpu.py`  Device-agnostic PyTorch port (XPU/CUDA/MPS/CPU auto-detect).
  Contains: Hopf-charge meter (torch.fft), Faddeev–Skyrme energy (autograd grad),
  **fixed-E2 constrained relaxer**, axial (m,n) builder, **parametric (p,q) torus-knot
  seed builder** (self-contained, no data file needed). Gradient is autograd → correct
  by construction. **Self-validates on run**: prints gradient check, axial Q-convergence,
  and fixed-E2 Q_H retention on YOUR hardware.
  Install (one of):
  ```
  pip install torch --index-url https://download.pytorch.org/whl/xpu
  # or IPEX:
  pip install torch==2.* intel-extension-for-pytorch==2.* \
      --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/
  ```
  Run:  `python fs_relax_xpu.py`   (production: edit N>=128, DTYPE=float32)

## numpy reference (validated in-sandbox)
- `hopfion_tools.py`     Hopf-charge meter (→integer w/ resolution, topologically
                         conserved, Q=mn for axial), Faddeev–Skyrme energy, (m,n) builder.
- `fs_hopfion_pipeline.py`  Faddeev–Skyrme energy + **analytic gradient, gradient-checked
                         to 1.3e-8** (manual reverse-mode). [no relaxer/seed here — those
                         live in fs_relax2.py (relaxer) and fs_relax_xpu.py (relaxer+seed)]
- `fs_relax2.py`         Component gradients (E2,g2 / E4,g4) + **fixed-E2 constrained
                         relaxer**. Validated: Q_H retention 59→71→98% at N=40→56→72.

## C++ (pybind11, SSTcore-ready) — sstcore_ext/
- `writhe_kernel.cpp`    module `sstcore_writhe`: writhe(curve). 18–48× vs numpy. (now #include <vector>)
- `link_kernel.cpp`      module `sstcore_link`: writhe, linking_number(A,B), link_matrix([...]).
                         Validated: Hopf link 2:2:1 Lk=−1; triple 6:2:3 = Borromean (zero matrix).
- `BUILD.md`             build + SSTcore integration; note on Milnor μ₁₂₃ for Borromean sector.

## Status block (honest)
- Hopf charge meter ............ VALIDATED on axial (m,n) ansatz (numpy)
- Faddeev–Skyrme gradient ...... GRADIENT-CHECKED (numpy 1.3e-8); autograd in torch port
- fixed-E2 relaxation .......... VALIDATED; Q_H retention 98% at N=72 (numpy)
- pairwise link kernel ......... VALIDATED (Hopf link, Borromean detection)
- trefoil Q_H=7 SST run ........ READY FOR GPU; NOT YET EXECUTED
- N≥128 charge conservation .... EXPECTED from 59→71→98% trend; NOT YET VERIFIED
- θ=π parity taxonomy .......... EXECUTABLE, COMPUTE-BOUND (not yet executed)
- Milnor μ₁₂₃ (Borromean) ...... NEXT boson-sector tool (not built)

## Workflow rule (hard)
Hopf charge of knotted seeds must be set by the Seifert/self-linking framing, NOT naive
tube offsets — wrong framing gives wrong Q_H with visually-fine geometry. Verify every
seed with hopf_charge() and let fixed-E2 relaxation settle the energy-minimal framing.

## Order of operations
1. GPU-port self-test (run fs_relax_xpu.py on the Arc)  2. N=128 axial Q=1,2,3 validation
3. Q=7 trefoil seed → relax → Hopf readout              4. Q=11 / 5_1 seed → relax → readout
5. then Milnor μ₁₂₃ for the link/boson sector
