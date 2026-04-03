# Backward compatibility: older name for the SSTcore Python API.
# Prefer ``import SSTcore`` or ``from SSTcore import ...``.

try:
    from SSTcore import *  # noqa: F401, F403
    import SSTcore as _pkg

    _all = list(getattr(_pkg, "__all__", None) or [])
    # Wheels split the old monolithic extension: helpers/resources on SSTcore._native,
    # Biot–Savart / vortex / fluid API on SSTcore._bindings. Re-export bindings here so
    # ``import swirl_string_core`` matches legacy scripts and comprehensive tests.
    try:
        from sstbindings import *  # noqa: F401, F403
        import sstbindings as _sb

        _b_all = getattr(_sb, "__all__", None) or []
        if _b_all:
            _all = list(dict.fromkeys(_all + list(_b_all)))
    except ImportError:
        pass
    __all__ = _all
except ImportError:
    try:
        import sstcore as _native
        from sstcore import *  # noqa: F401, F403

        __all__ = getattr(_native, "__all__", None)
    except ImportError:
        import sstbindings as _native
        from sstbindings import *  # noqa: F401, F403

        __all__ = getattr(_native, "__all__", None)
