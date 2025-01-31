"""Tests redirects from logging to logbook"""
from logging import getLogger, StreamHandler
from logbook.compat import LoggingHandler
from io import StringIO


log = getLogger("Test logger")


def run():
    out = StringIO()
    log.addHandler(StreamHandler(out))
    with LoggingHandler():
        for x in range(500):
            log.warning("this is not handled")
    assert out.getvalue().count("\n") == 500
