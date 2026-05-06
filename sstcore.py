"""Compatibility shim: ``import sstcore`` mirrors the full ``SSTcore`` API."""

import SSTcore as _sstcore_pkg

# Re-export all public attributes from SSTcore, not only SSTcore.__all__.
# This keeps compatibility even when native symbols are present but not listed
# in __all__ by the extension module.
for _name in dir(_sstcore_pkg):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_sstcore_pkg, _name)

__all__ = [n for n in dir(_sstcore_pkg) if not n.startswith("_")]


def __getattr__(name):
    return getattr(_sstcore_pkg, name)
