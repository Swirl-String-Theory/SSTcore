"""Re-exports for examples — embedded-first resource access (Patch C)."""

from __future__ import annotations

try:
    from SSTcore import (
        find_ideal_ab_block_by_id,
        find_ideal_by_id,
        get_ideal_ab,
        get_knot_fseries,
        get_knots_fourier_series_dir,
        get_resources_dir,
        list_embedded_fseries_ids,
        list_ideal_source_files,
        load_fseries_knot,
        load_ideal_ab_embedded,
        parse_fseries_knot,
        use_disk_resources,
    )
except ImportError:
    from sstcore import (  # type: ignore
        find_ideal_ab_block_by_id,
        find_ideal_by_id,
        get_ideal_ab,
        get_knot_fseries,
        get_knots_fourier_series_dir,
        get_resources_dir,
        list_embedded_fseries_ids,
        list_ideal_source_files,
        load_fseries_knot,
        load_ideal_ab_embedded,
        parse_fseries_knot,
        use_disk_resources,
    )

__all__ = [
    "find_ideal_ab_block_by_id",
    "find_ideal_by_id",
    "get_ideal_ab",
    "get_knot_fseries",
    "get_knots_fourier_series_dir",
    "get_resources_dir",
    "list_embedded_fseries_ids",
    "list_ideal_source_files",
    "load_fseries_knot",
    "load_ideal_ab_embedded",
    "parse_fseries_knot",
    "use_disk_resources",
]
