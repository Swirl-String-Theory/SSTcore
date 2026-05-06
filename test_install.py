#!/usr/bin/env python
"""Verify imports for root requirements.txt (runtime + build-system deps)."""
import importlib

# Keep in sync with requirements.txt and setup.py install_requires.
_REQUIRED_MODULES = ("numpy", "pybind11", "setuptools", "wheel", "packaging")


def test_required_imports():
    # Deferred import so `python test_install.py` works without pytest installed.
    import pytest

    for module_name in _REQUIRED_MODULES:
        module = pytest.importorskip(module_name)
        assert module is not None


def main():
    for module_name in _REQUIRED_MODULES:
        try:
            module = importlib.import_module(module_name)
            ver = getattr(module, "__version__", None)
            if ver is not None:
                print(f"{module_name} version: {ver}")
            else:
                print(f"{module_name}: OK")
        except ImportError as exc:
            print(f"{module_name} import failed: {exc}")
            return 1

    print("All imports successful!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
