r"""
Logbook
-------

An awesome logging implementation that is fun to use.

Quickstart
``````````

::

    from logbook import Logger
    log = Logger('A Fancy Name')

    log.warn('Logbook is too awesome for most applications')
    log.error("Can't touch this")

Works for web apps too
``````````````````````

::

    from logbook import MailHandler, Processor

    mailhandler = MailHandler(from_addr='servererror@example.com',
                              recipients=['admin@example.com'],
                              level='ERROR', format_string=u'''\
    Subject: Application Error for {record.extra[path]} [{record.extra[method]}]

    Message type:       {record.level_name}
    Location:           {record.filename}:{record.lineno}
    Module:             {record.module}
    Function:           {record.func_name}
    Time:               {record.time:%Y-%m-%d %H:%M:%S}
    Remote IP:          {record.extra[ip]}
    Request:            {record.extra[path]} [{record.extra[method]}]

    Message:

    {record.message}
    ''')

    def handle_request(request):
        def inject_extra(record, handler):
            record.extra['ip'] = request.remote_addr
            record.extra['method'] = request.method
            record.extra['path'] = request.path

        with Processor(inject_extra):
            with mailhandler:
                # execute code that might fail in the context of the
                # request.
"""

from itertools import chain
import os
import platform
import sys

from distutils.command.build_ext import build_ext
from distutils.errors import (
    CCompilerError,
    DistutilsExecError,
    DistutilsPlatformError,
)
from setuptools import (
    Distribution as _Distribution,
    Extension,
    setup,
    find_packages,
)

cmdclass = {}

cpython = platform.python_implementation() == "CPython"

ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)


class BuildFailed(Exception):
    def __init__(self):
        self.cause = sys.exc_info()[1]  # work around py 2/3 different syntax


class ve_build_ext(build_ext):
    """This class allows C extension building to fail."""

    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            raise BuildFailed()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except ext_errors:
            raise BuildFailed()
        except ValueError:
            # this can happen on Windows 64 bit, see Python issue 7511
            if "'path'" in str(sys.exc_info()[1]):  # works with both py 2/3
                raise BuildFailed()
            raise


cmdclass["build_ext"] = ve_build_ext


class Distribution(_Distribution):
    def has_ext_modules(self):
        # We want to always claim that we have ext_modules. This will be fine
        # if we don't actually have them (such as on PyPy) because nothing
        # will get built, however we don't want to provide an overally broad
        # Wheel package when building a wheel without C support. This will
        # ensure that Wheel knows to treat us as if the build output is
        # platform specific.
        return True


def status_msgs(*msgs):
    print("*" * 75)
    for msg in msgs:
        print(msg)
    print("*" * 75)


version_file_path = os.path.join(
    os.path.dirname(__file__), "src/logbook", "__version__.py"
)

with open(version_file_path) as version_file:
    exec(version_file.read())  # pylint: disable=W0122

extras_require = dict()

extras_require["execnet"] = set(["execnet>=1.0.9"])
extras_require["sqlalchemy"] = set(["sqlalchemy"])
extras_require["redis"] = set(["redis"])
extras_require["zmq"] = set(["pyzmq"])
extras_require["jinja"] = set(["Jinja2"])
extras_require["compression"] = set(["brotli"])
extras_require["riemann"] = {"riemann_client"}

extras_require["all"] = set(chain.from_iterable(extras_require.values()))

# sort items to make requires.txt reproducible
extras_require = {key: sorted(value) for key, value in extras_require.items()}


def run_setup(with_cext):
    kwargs = {}
    if with_cext:
        from Cython.Build import cythonize

        kwargs["ext_modules"] = cythonize(
            [
                Extension(
                    "logbook._speedups", sources=["src/logbook/_speedups.pyx"]
                )
            ]
        )
    else:
        kwargs["ext_modules"] = []

    setup(
        name="Logbook",
        version=__version__,
        license="BSD",
        url="https://logbook.readthedocs.io/en/stable/",
        project_urls={
            "Source": "https://github.com/getlogbook/logbook",
        },
        author="Armin Ronacher, Georg Brandl",
        author_email="armin.ronacher@active-4.com",
        description="A logging replacement for Python",
        long_description=__doc__,
        packages=find_packages("src"),
        package_dir={"": "src"},
        zip_safe=False,
        platforms="any",
        cmdclass=cmdclass,
        classifiers=[
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
        ],
        extras_require=extras_require,
        distclass=Distribution,
        include_package_data=True,
        **kwargs
    )


if not cpython:
    run_setup(False)
    status_msgs(
        "WARNING: C extensions are not supported on "
        + "this Python platform, speedups are not enabled.",
        "Plain-Python build succeeded.",
    )
elif os.environ.get("DISABLE_LOGBOOK_CEXT"):
    run_setup(False)
    status_msgs(
        "DISABLE_LOGBOOK_CEXT is set; "
        + "not attempting to build C extensions.",
        "Plain-Python build succeeded.",
    )
else:
    try:
        run_setup(True)
    except BuildFailed as exc:
        status_msgs(
            exc.cause,
            "WARNING: The C extension could not be compiled, "
            + "speedups are not enabled.",
            "Failure information, if any, is above.",
            "Retrying the build without the C extension now.",
        )

        run_setup(False)

        status_msgs(
            "WARNING: The C extension could not be compiled, "
            + "speedups are not enabled.",
            "Plain-Python build succeeded.",
        )
