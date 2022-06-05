"""Benchmarks too low logger levels"""
from logbook import Logger, StreamHandler, ERROR
from io import StringIO


log = Logger("Test logger")
log.level = ERROR


def run():
    out = StringIO()
    with StreamHandler(out):
        for x in range(500):
            log.warning("this is not handled")
