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
from __future__ import annotations
import ast
import contextlib
import errno
import functools
import logging
import os
from collections import UserDict
import typing


if typing.TYPE_CHECKING:  # pragma: no cover
    from typing import Callable, TypeVar, ParamSpec

    T = TypeVar('T', str, list, dict, int, float, set, bool, tuple)
    P = ParamSpec('P')


__version__ = "2022.9.1"
logger = logging.getLogger(__name__)


@typing.overload
def biodome(name: str) -> str|None: ...  # pragma: no cover
@typing.overload
def biodome(name: str, default: None) -> str|None: ...  # pragma: no cover
@typing.overload
def biodome(name: str, *, cast: None) -> str|None: ...  # pragma: no cover
@typing.overload
def biodome(name: str, default: T) -> T: ...  # pragma: no cover
@typing.overload
def biodome(name: str, *, cast: Callable[[str|None], T]) -> T: ...  # pragma: no cover
# Finally, the full sig to work with callers that provide everything
@typing.overload
def biodome(name: str, default: T|None = None, *, cast: None|Callable[[str|None], T] = None) -> T|str|None: ...  # pragma: no cover
def biodome(name, default=None, *, cast=None):
    raw_value = os.environ.get(name)
    if default is None and cast is None:
        return raw_value

    if default is not None and cast is not None:
        raise ValueError("Either default or cast must be provided, not both.")

    if raw_value is None:
        if default is None and cast is not None:
            return cast(raw_value)
        else:
            return default

    raw_value = raw_value.strip()

    # Use the same type as default as the cast
    type_ = cast or type(default)

    if bool in (cast, type_):
        return raw_value.lower() in (
            "1",
            "y",
            "yes",
            "on",
            "active",
            "activated",
            "enabled",
            "true",
            "t",
            "ok",
            "yeah",
        )

    try:
        if type_ in (dict, list, set, tuple):
            raw_value = ast.literal_eval(raw_value)
            return (type(raw_value) == type_ and raw_value) or default
        return type_(raw_value)
    except:
        logger.error(
            'Env var %s: cast "%s" to type %s failed. The default will be used.',
            name,
            raw_value,
            str(type_),
        )
        return default


class _Environ(UserDict):
    def __init__(self):
        self.data = os.environ

    @typing.overload
    def get(self, key: str) -> str|None: ...  # pragma: no cover
    @typing.overload
    def get(self, key: str, default: None) -> str|None: ...  # pragma: no cover
    @typing.overload
    def get(self, key: str, *, cast: None) -> str|None: ...  # pragma: no cover
    @typing.overload
    def get(self, key: str, default: T) -> T: ...  # pragma: no cover
    @typing.overload
    def get(self, key: str, *, cast: Callable[[str|None], T]) -> T: ...  # pragma: no cover
    @typing.overload
    def get(self, key: str, default: T|None = None, *, cast: None|Callable[[str|None], T] = None) -> T|str|None: ...  # pragma: no cover
    def get(self, key, default=None, *, cast=None) -> T|str|None:
        return biodome(key, default, cast=cast)

    @typing.overload
    def get_callable(self, key: str) -> Callable[[], str|None]: ...  # pragma: no cover
    @typing.overload
    def get_callable(self, key: str, default: None) -> Callable[[], str|None]: ...  # pragma: no cover
    @typing.overload
    def get_callable(self, key: str, *, cast: None) -> Callable[[], str|None]: ...  # pragma: no cover
    @typing.overload
    def get_callable(self, key: str, default: T) -> Callable[[], T]: ...  # pragma: no cover
    @typing.overload
    def get_callable(self, key: str, *, cast: Callable[[str|None], T]) -> Callable[[], T]: ...  # pragma: no cover
    # Finally, the full sig to work with callers that provide everything
    @typing.overload
    def get_callable(self, key: str, default: T|None = None, *, cast: None|Callable[[str|None], T] = None) -> Callable[[], T|str|None]: ...  # pragma: no cover
    def get_callable(self, key, default=None, cast=None) -> Callable[[], T|str|None]:
        return functools.partial(self.get, key, default=default, cast=cast)

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


def load_env_file(path, raises=False):
    # type: (str, bool) -> None
    """
    Load an file which specifies the values of environment variables. An
    example:

        # This sets the log level for all the loggers in the program
        LOGGER_LEVEL=info

        # Hourly backups are stored at this path and named with a timestamp.
        BACKUP_PATH=/data/backups/

        # The number of times to retry outgoing HTTP requests if the status
        # code is > 500
        RETRY_TIME=5


    The name of the environment variable must be on the left and the value
    on the right. Each variable must be on its own line. Lines starting with
    a # are considered comments and are ignored.

    :raises - If true, this method with raise if there is no file at the
        specified path. If false, the method will return having done nothing.
    """
    try:
        with open(path) as f:
            for line in f:  # pragma: no branch
                line = line.strip()
                if not line or line[0] == "#":
                    continue
                name, _, value = line.partition("=")
                name = name.strip()
                value = value.strip()
                environ[name] = value
    except IOError as e:
        # Python 3 raises a FileNotFound and python 2 an IOError. So we can
        # check the error number to see if it was a missing file.
        if e.errno != errno.ENOENT or raises:
            raise
