# Backward compatibility: older name for the SSTcore Python API.
# Prefer ``import SSTcore`` or ``from SSTcore import ...``.

try:
    from SSTcore import *  # noqa: F401, F403
    import SSTcore as _pkg

    __all__ = getattr(_pkg, "__all__", None)
except ImportError:
    try:
        import sstcore as _native
        from sstcore import *  # noqa: F401, F403

        __all__ = getattr(_native, "__all__", None)
    except ImportError:
        import sstbindings as _native
        from sstbindings import *  # noqa: F401, F403

        __all__ = getattr(_native, "__all__", None)
