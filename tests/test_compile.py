import os

from logbook.base import _has_speedups


def test_compile():
    if os.environ.get("DISABLE_LOGBOOK_CEXT"):
        assert not _has_speedups, "Speedups enabled when they should not be"
    else:
        assert _has_speedups, "Speedups missing when they should enabled"
