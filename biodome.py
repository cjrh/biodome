"""
biodome
=======

Controlled environments.

"""
import os
import logging


__version__ = '0.1.0'
logger = logging.getLogger(__name__)


def biodome(name, default=None, cast=None):
    # type: (str, Any, Callable) -> Any
    raw_value = os.environ.get(name).strip()
    print(raw_value)
    if raw_value is None:
        return default

    # Use the same type as default as the cast
    type_ = cast or type(default)

    if bool in (cast, type_):
        return raw_value.lower() in (
            '1', 'y', 'yes', 'on', 'active', 'activated', 'enabled', 'true',
            't', 'ok', 'yeah',
        )

    try:
        if type_ in (dict, list, set, tuple):
            raw_value = eval(raw_value)
            return (type(raw_value) == type_ and raw_value) or default
        return type_(raw_value)
    except:
        return default
