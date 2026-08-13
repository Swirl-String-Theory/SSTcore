"""Text IO helpers that stay compatible with Python 3.9+.

Path.write_text(..., newline=) only exists from 3.10. Resource payloads under
resources/ are pinned by byte-exact sha256, so writers must emit LF without
relying on that kwarg.
"""

from __future__ import annotations

from pathlib import Path


def write_text_lf(path: Path, text: str) -> None:
    """Write ``text`` as UTF-8 with the given newlines unchanged (no CRLF rewrite)."""
    path.write_bytes(text.encode("utf-8"))
