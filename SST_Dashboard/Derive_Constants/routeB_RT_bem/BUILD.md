# SSTcore writhe kernel (pybind11)

C++ Gauss self-linking (writhe) integral, O(N^2). Validated identical to the
numpy reference (trefoil -3.41885); 18-48x faster (N=400: 0.64 ms vs 30.5 ms).

## Standalone build
```
g++ -O3 -march=native -shared -std=c++14 -fPIC $(python3 -m pybind11 --includes) \
    writhe_kernel.cpp -o sstcore_writhe$(python3-config --extension-suffix)
```
```python
import sstcore_writhe, numpy as np
W = sstcore_writhe.writhe(np.ascontiguousarray(curve))   # curve: (N,3) closed
```

## Folding into SSTcore
Add `writhe_kernel.cpp` to the SSTcore sources and expose under a geometry
namespace, e.g. `sst::geom::writhe`. The same O(N^2) pattern extends to the
linking number of two curves (links) by looping i over curve A, j over curve B
(no i==j skip, divide by 4*pi) -> needed for the boson/link sector.
Import style:  `import SSTcore as sst`  (never `import SSTcore as sc`).

## Link kernel (knots & links)  — link_kernel.cpp -> module `sstcore_link`
- `writhe(curve)`                      self-linking of one closed curve
- `linking_number(A, B)`               Gauss linking number of two curves
- `link_matrix([c1,c2,...])`           M x M: writhe on diagonal, pairwise Lk off-diagonal

VALIDATED: Hopf link 2:2:1 -> Lk = -1.000 ; triple link 6:2:3 -> all-zero matrix
=> BORROMEAN (pairwise unlinked, collectively linked). For Borromean/triple-gear the
pairwise matrix is zero by design; the collective invariant is Milnor's mu_123 (a triple
Gauss integral / Massey product) — the natural next kernel for the boson/link sector.
Build: g++ -O3 -march=native -shared -std=c++14 -fPIC $(python3 -m pybind11 --includes) link_kernel.cpp -o sstcore_link$(python3-config --extension-suffix)
