"""Test with no handler active"""
from logbook import Logger, StreamHandler, NullHandler, ERROR
from io import StringIO


log = Logger("Test logger")


def run():
    out = StringIO()
    with NullHandler():
        with StreamHandler(out, level=ERROR) as handler:
            for x in range(500):
                log.warning("this is not handled")
    assert not out.getvalue()
