"""Smoke example for field_ops bindings."""
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

MODULE = "field_ops"


def main() -> int:
    sst, info = import_sstcore()
    if sst is None:
        import json
        print(json.dumps(info, indent=2))
        return 2
    print_example_header(MODULE, sst)

    import numpy as np
    f = np.ones((4,4,4,3))
    curl = sst.curl3d_central(f, 1.0)
    print("curl3d_central shape =", getattr(curl, "shape", type(curl)))

    print("OK:", MODULE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
