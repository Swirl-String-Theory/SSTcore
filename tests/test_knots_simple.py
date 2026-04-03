#!/usr/bin/env python3
"""Smoke checks for ``VortexKnotSystem``; run the script directly for a method listing demo."""

from __future__ import annotations

import sys

import pytest


def test_vortex_knot_system_import() -> None:
    sstbindings = pytest.importorskip("sstbindings", exc_type=ImportError)
    assert hasattr(sstbindings, "VortexKnotSystem")


def test_initialize_knot_from_name_when_available() -> None:
    sstbindings = pytest.importorskip("sstbindings", exc_type=ImportError)
    cls = sstbindings.VortexKnotSystem
    if not hasattr(cls, "initialize_knot_from_name"):
        pytest.skip("initialize_knot_from_name not exposed by this build")
    system = cls()
    system.initialize_knot_from_name("3_1", resolution=32)
    positions = system.get_positions()
    assert len(positions) > 0


def _main() -> None:
    if "sstbindings" in sys.modules:
        del sys.modules["sstbindings"]
    import sstbindings

    print("Available VortexKnotSystem methods:")
    methods = [m for m in dir(sstbindings.VortexKnotSystem) if not m.startswith("_")]
    for m in sorted(methods):
        print(f"  - {m}")

    if "initialize_knot_from_name" in methods:
        print("\n✓ initialize_knot_from_name is available!")
        print("\nTesting knot loading...")
        try:
            system = sstbindings.VortexKnotSystem()
            system.initialize_knot_from_name("3_1", resolution=100)
            positions = system.get_positions()
            print(f"✓ Successfully loaded knot 3_1 with {len(positions)} points")
            print(f"  First point: {positions[0]}")
        except Exception as e:
            print(f"✗ Error loading knot: {e}")
    else:
        print("\n✗ initialize_knot_from_name is NOT available")
        print("  The module may need to be rebuilt")


if __name__ == "__main__":
    _main()
