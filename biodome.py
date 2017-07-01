"""
biodome
=======

Controlled environments.

"""
import os
import logging
import ast
try:
    # Python 3
    from collections import UserDict
except ImportError:
    # Python 2
    from UserDict import IterableUserDict as UserDict
from typing import Any

__version__ = '2017.6.4'
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
        return default


class _Environ(UserDict):
    def __init__(self, *args, **kwargs):
        super(_Environ, self).__init__(*args, **kwargs)
        self.data = os.environ

    def get(self, key, default=None, cast=None):
        return biodome(key, default, cast)

    def __setitem__(self, key, value):
        os.environ[key] = str(value)


environ = _Environ()
