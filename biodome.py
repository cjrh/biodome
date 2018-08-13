"""
biodome
=======

Controlled environments.

   Copyright 2018 Caleb Hattingh

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""
import os
import logging
import ast
import typing
import functools
import contextlib
try:
    # Python 3
    from collections import UserDict  # pragma: no cover
except ImportError:  # pragma: no cover
    # Python 2
    from UserDict import IterableUserDict as UserDict  # pragma: no cover


if typing.TYPE_CHECKING:  # pragma: no cover
    from typing import Callable, Any


__version__ = '2017.12.1'
logger = logging.getLogger(__name__)


def biodome(name, default=None, cast=None):
    # type: (str, Any, Callable) -> Any
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default

    if default is None and cast is None:
        # No type information. Just pass through.
        return raw_value

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
            'Env var %s: cast "%s" to type %s failed. The default will be'
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


@contextlib.contextmanager
def env_change(name, value):
    """Context manager to temporarily change the value of an env var."""
    # TODO: move this upstream to the biodome package
    if name in environ:
        old = environ[name]

        def reset():
            environ[name] = old

    else:
        def reset():
            del environ[name]

    try:
        environ[name] = value
        yield
    finally:
        reset()
