"""Tests with a logging handler becoming a noop for comparison"""
from logging import getLogger, StreamHandler, ERROR
from io import StringIO


log = getLogger("Testlogger")
log.setLevel(ERROR)


def run():
    out = StringIO()
    handler = StreamHandler(out)
    log.addHandler(handler)
    for x in range(500):
        log.warning("this is not handled")
