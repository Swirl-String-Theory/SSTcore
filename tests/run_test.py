"""
Local dev smoke: Frenet frames + helicity via ``sstbindings``.

- **Pytest**: no tests here (intentionally); nothing runs on import.
- **Run directly** (needs bindings on the path): ``python tests/run_test.py``

After ``pip install SSTcore``, you usually do not need a build dir; otherwise prepend
your CMake output folder (the one containing ``sstbindings*.pyd`` / ``sstbindings*.so``)
to ``PYTHONPATH``, or rely on the common relative paths tried below.

Legacy note: older monolithic builds exposed the extension as ``swirl_string_core``;
current SSTcore uses the ``sstbindings`` shim (``SSTcore._bindings`` in wheels).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _prepend_first_existing_build_dir() -> bool:
    """If a typical CMake build output exists next to the repo root, prepend it to sys.path."""
    here = Path(__file__).resolve().parent
    root = here.parent
    candidates = [
        root / "build" / "Debug",
        root / "build" / "Release",
        root / "build" / "RelWithDebInfo",
        root / "cmake-build-debug",
        root / "cmake-build-release",
        root / "cmake-build-relwithdebinfo",
    ]
    for d in candidates:
        if d.is_dir():
            p = str(d.resolve())
            if p not in sys.path:
                sys.path.insert(0, p)
            return True
    return False


def main() -> None:
    _prepend_first_existing_build_dir()

    import sstbindings

    X = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [-1.0, 0.0, 0.0],
        [0.0, -1.0, 0.0],
        [1.0, 0.0, 0.0],
    ]

    T, N, B = sstbindings.compute_frenet_frames(X)
    kappa, tau = sstbindings.compute_curvature_torsion(T, N)
    print("Curvature:", kappa)
    print("Torsion:", tau)

    print("Helicity:", sstbindings.compute_helicity(T, T))  # toy: w = v = T


if __name__ == "__main__":
    main()
