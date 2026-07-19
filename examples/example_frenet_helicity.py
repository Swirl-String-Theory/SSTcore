"""Smoke example for frenet_helicity bindings."""
from __future__ import annotations

import sys
from pathlib import Path

_EXAMPLES = Path(__file__).resolve().parent
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from _example_bootstrap import (  # noqa: E402
    import_sstcore,
    load_fseries,
    print_example_header,
)

MODULE = "frenet_helicity"


def main() -> int:
    sst, info = import_sstcore()
    if sst is None:
        import json
        print(json.dumps(info, indent=2))
        return 2
    print_example_header(MODULE, sst)

    curve = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
    frames = sst.compute_frenet_frames(curve)
    print("compute_frenet_frames len =", len(frames))
    print("compute_helicity =", sst.compute_helicity([[1,0,0],[0,1,0]], [[1,0,0],[0,1,0]]))

    print("OK:", MODULE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
