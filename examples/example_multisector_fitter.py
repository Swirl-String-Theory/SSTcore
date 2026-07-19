"""Smoke example for multisector_fitter bindings."""
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

MODULE = "multisector_fitter"


def main() -> int:
    sst, info = import_sstcore()
    if sst is None:
        import json
        print(json.dumps(info, indent=2))
        return 2
    print_example_header(MODULE, sst)

    mf = sst.MultisectorFitter()
    print("MultisectorFitter =", mf)
    na = sst.NodeAnalyzer()
    print("NodeAnalyzer =", na)
    tf = sst.TraceFormula()
    print("TraceFormula =", tf)
    mf2 = sst.MultisectorFitterV2()
    print("MultisectorFitterV2 =", mf2)

    print("OK:", MODULE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
