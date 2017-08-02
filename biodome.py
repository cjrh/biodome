"""
biodome
=======

Controlled environments.

"""
import os
import logging
import ast
import typing
import functools
try:
    # Python 3
    from collections import UserDict  # pragma: no cover
except ImportError:  # pragma: no cover
    # Python 2
    from UserDict import IterableUserDict as UserDict  # pragma: no cover


if typing.TYPE_CHECKING:  # pragma: no cover
    from typing import Callable, Any


__version__ = '2017.8.1'
logger = logging.getLogger(__name__)


def biodome(name, default=None, cast=None):
    # type: (str, Any, Callable) -> Any
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default

    raw_value = raw_value.strip()

    # Use the same type as default as the cast
    type_ = cast or type(default)

    if bool in (cast, type_):
        return raw_value.lower() in (
            '1', 'y', 'yes', 'on', 'active', 'activated', 'enabled', 'true',
            't', 'ok', 'yeah',
        )

    try:
        if type_ in (dict, list, set, tuple):
            raw_value = ast.literal_eval(raw_value)
            return (type(raw_value) == type_ and raw_value) or default
        return type_(raw_value)
    except:
        logger.error(
            'Env var %s: cast "%s" to tyoe %s failed. The default will be'
            'used.', name, raw_value, str(type_)
        )
        return default


class _Environ(UserDict):
    def __init__(self, *args, **kwargs):
        self.data = os.environ

    def get(self, key, default=None, cast=None):
        # type: (str, Any, Callable) -> Callable
        return biodome(key, default, cast)

    def get_callable(self, key, default=None, cast=None):
        # type: (str, Any, Callable) -> Callable[[None], None]
        return functools.partial(
            self.get, key, default=default, cast=cast,
        )

    def __setitem__(self, key, value):
        os.environ[key] = str(value)


environ = _Environ()


import logging
import time
import threading
import pytest
import biodome
import contextlib
from insomniac.manager import perf_stats_worker


def test_perf_stats_worker(sneaky_filter):

    thread = threading.Thread(target=perf_stats_worker)
    thread.daemon = True
    thread.start()

    time.sleep(1.1)  # CPU percent sampling takes 1 second.

    # The log records should all have been saved. Now we check them.
    log_records = sneaky_filter.log_records

    print(log_records)

    cpu = log_records[0]
    assert type(cpu['cpu_user']) in (int, float)
    assert type(cpu['cpu_system']) in (int, float)
    assert type(cpu['cpu_user']) in (int, float)
    assert type(cpu['cpu_user']) in (int, float)
    assert type(cpu['cpu_user']) in (int, float)
    assert type(cpu['cpu_user']) in (int, float)

    assert type(log_records[1]['cpu_percent']) == float

    assert 'vmem_active' in log_records[2]
    assert 'vmem_available' in log_records[2]
    assert 'vmem_free' in log_records[2]
    assert 'vmem_inactive' in log_records[2]
    assert 'vmem_percent' in log_records[2]
    assert 'vmem_total' in log_records[2]
    assert 'vmem_used' in log_records[2]
    # BSD, OSX only:
    # assert 'vmem_wired' in log_records[2]

    assert 'net_bytes_recv' in log_records[3]
    assert 'net_bytes_sent' in log_records[3]
    assert 'net_dropin' in log_records[3]
    assert 'net_dropout' in log_records[3]
    assert 'net_errin' in log_records[3]
    assert 'net_errout' in log_records[3]
    assert 'net_packets_recv' in log_records[3]
    assert 'net_packets_sent' in log_records[3]

    assert type(log_records[4]['tot_connections']) == int

    # BSD, OSX only:
    # assert 'mem_pageins' in log_records[5]
    # assert 'mem_pfaults' in log_records[5]
    assert 'mem_rss' in log_records[5]
    assert 'mem_uss' in log_records[5]
    assert 'mem_vms' in log_records[5]


@pytest.fixture(scope='function')
def sneaky_filter():
    """Add (and later) remove a logging filter. This is used for "saving"
    all the emitted logrecords for a particular logger.  Then, the tests
    will assert that certain fields are present in the emitted logrecords."""

    manager_logger = logging.getLogger('insomniac.manager')

    class SneakyFilter(object):
        def __init__(self):
            self.log_records = []

        def filter(self, record):
            def skip(name):
                return name.startswith('_') or name in ('args', 'getMessage')

            d = {name: getattr(record, name) for name in dir(record) if not skip(name)}
            self.log_records.append(d)
            return True

    f = SneakyFilter()
    manager_logger.addFilter(filter=f)

    try:
        with env_change('PERF_LOGGING_ENABLED', True), \
             env_change('PERF_LOGGING_INTERVAL', 0.2):
            yield f
    finally:
        manager_logger.removeFilter(f)


@contextlib.contextmanager
def env_change(name, value):
    """Context manager to temporarily change the value of an env var."""
    # TODO: move this upstream to the biodome package
    if name in biodome.environ:
        old = biodome.environ[name]

        def reset():
            biodome.environ[name] = old

    else:
        def reset():
            del biodome.environ[name]

    try:
        biodome.environ[name] = value
        yield
    finally:
        reset()
