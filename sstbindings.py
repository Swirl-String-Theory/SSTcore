"""Deprecated shim: ``import sstbindings`` mirrors the full ``SSTcore`` API."""

import SSTcore as _sstcore_pkg

for _name in dir(_sstcore_pkg):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_sstcore_pkg, _name)

__all__ = [n for n in dir(_sstcore_pkg) if not n.startswith("_")]


def __getattr__(name):
    return getattr(_sstcore_pkg, name)
