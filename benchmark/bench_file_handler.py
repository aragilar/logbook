"""Benchmarks the file handler"""
from logbook import Logger, FileHandler
from tempfile import NamedTemporaryFile


log = Logger("Test logger")


def run():
    f = NamedTemporaryFile()
    with FileHandler(f.name) as handler:
        for x in range(500):
            log.warning("this is handled")
