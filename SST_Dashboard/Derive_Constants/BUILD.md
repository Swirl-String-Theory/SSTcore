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
