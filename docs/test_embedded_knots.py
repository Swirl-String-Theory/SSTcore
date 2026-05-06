#!/usr/bin/env python3
"""
Simple test script to verify embedded knots are accessible.
This tests that knots can be loaded by name without needing .fseries files.
"""

import os
import sys

BUILD_DIR = os.path.join(os.path.dirname(__file__), "build", "Release")
if os.path.exists(BUILD_DIR):
    sys.path.insert(0, BUILD_DIR)


def _load_bindings():
    try:
        import swirl_string_core as bindings

        return bindings, bindings.VortexKnotSystem, "swirl_string_core"
    except ImportError:
        try:
            import sstbindings as bindings

            return bindings, bindings.VortexKnotSystem, "sstbindings"
        except ImportError:
            return None


_bindings = _load_bindings()
if _bindings is not None:
    _, VortexKnotSystem, _IMPORTED_FROM = _bindings
else:
    VortexKnotSystem = None  # type: ignore[assignment,misc]
    _IMPORTED_FROM = None

TEST_KNOTS = ["3_1", "3_1p", "3_1u", "4_1", "5_1", "5_2", "6_1", "7_1"]


def test_embedded_knot_access():
    # Deferred import so `python docs/test_embedded_knots.py` works without pytest installed.
    import pytest

    if VortexKnotSystem is None:
        pytest.skip(
            "Could not import swirl_string_core or sstbindings. "
            "Build the C++ module first.",
        )
    for knot_id in TEST_KNOTS:
        system = VortexKnotSystem()
        system.initialize_knot_from_name(knot_id, resolution=100)
        positions = system.get_positions()
        assert positions is not None and len(positions) > 0, knot_id


def main():
    if _bindings is None:
        print("✗ ERROR: Could not import swirl_string_core or sstbindings")
        print("  Make sure you've built the C++ module first!")
        print(f"  Tried to load from: {BUILD_DIR}")
        return 1

    print(f"✓ Successfully imported {_IMPORTED_FROM}")
    print("\n" + "=" * 70)
    print("Testing Embedded Knot Access")
    print("=" * 70)
    print(f"\nTesting {len(TEST_KNOTS)} knots...\n")

    success_count = 0
    failed_knots = []

    for knot_id in TEST_KNOTS:
        try:
            print(f"Testing knot '{knot_id}'...", end=" ")
            system = VortexKnotSystem()
            system.initialize_knot_from_name(knot_id, resolution=100)
            positions = system.get_positions()

            if positions is not None and len(positions) > 0:
                print(f"✓ SUCCESS - Loaded {len(positions)} points")
                success_count += 1
            else:
                print("✗ FAILED - No positions returned")
                failed_knots.append(knot_id)
        except Exception as exc:
            print(f"✗ FAILED - Error: {exc}")
            failed_knots.append(knot_id)

    print("=" * 70)
    print(f"Results: {success_count}/{len(TEST_KNOTS)} knots loaded successfully")
    print("=" * 70)

    if failed_knots:
        print(f"\nFailed knots: {', '.join(failed_knots)}")
        return 1

    print("\n✓ All knots loaded successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
