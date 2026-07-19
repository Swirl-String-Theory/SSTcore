"""Smoke example for field_kernels bindings."""
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

MODULE = "field_kernels"


def main() -> int:
    sst, info = import_sstcore()
    if sst is None:
        import json
        print(json.dumps(info, indent=2))
        return 2
    print_example_header(MODULE, sst)

    b = sst.dipole_field_at_point([0,0,0], [0,0,1], 1.0, [1,0,0])
    print("dipole_field_at_point =", b)

    print("OK:", MODULE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
