# -*- coding: utf-8 -*-
"""
    test utils for logbook
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2010 by Armin Ronacher, Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""
import functools
from io import StringIO
import os
import sys
from contextlib import contextmanager

import logbook

import pytest

_missing = object()

LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def require_module(module_name):
    found = True
    try:
        __import__(module_name)
    except ImportError:
        found = False

    return pytest.mark.skipif(
        not found, reason="Module {0} is required".format(module_name)
    )


def make_fake_mail_handler(**kwargs):
    class FakeMailHandler(logbook.MailHandler):
        mails = []

        def get_connection(self):
            return self

        def close_connection(self, con):
            pass

        def sendmail(self, fromaddr, recipients, mail):
            self.mails.append((fromaddr, recipients, mail))

    kwargs.setdefault("level", logbook.ERROR)
    return FakeMailHandler("foo@example.com", ["bar@example.com"], **kwargs)


def missing(name):
    def decorate(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            old = sys.modules.get(name, _missing)
            sys.modules[name] = None
            try:
                f(*args, **kwargs)
            finally:
                if old is _missing:
                    del sys.modules[name]
                else:
                    sys.modules[name] = old

        return wrapper

    return decorate


def activate_via_with_statement(handler):
    return handler


@contextmanager
def activate_via_push_pop(handler):
    handler.push_thread()
    try:
        yield handler
    finally:
        handler.pop_thread()


@contextmanager
def capturing_stderr_context():
    original = sys.stderr
    sys.stderr = StringIO()
    try:
        yield sys.stderr
    finally:
        sys.stderr = original
