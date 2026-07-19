"""Smoke example for delay_mode_selector bindings."""
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

MODULE = "delay_mode_selector"


def main() -> int:
    sst, info = import_sstcore()
    if sst is None:
        import json
        print(json.dumps(info, indent=2))
        return 2
    print_example_header(MODULE, sst)

    sel = sst.DelayModeSelector()
    print("DelayModeSelector =", sel)
    res = sst.DelayModeResult()
    print("DelayModeResult =", res)

    print("OK:", MODULE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
