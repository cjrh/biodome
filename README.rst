.. image:: https://img.shields.io/badge/stdlib--only-yes-green.svg
    :target: https://img.shields.io/badge/stdlib--only-yes-green.svg

.. image:: https://travis-ci.org/cjrh/biodome.svg?branch=master
    :target: https://travis-ci.org/cjrh/biodomebiodome

.. image:: https://coveralls.io/repos/github/cjrh/biodome/badge.svg?branch=master
    :target: https://coveralls.io/github/cjrh/biodome?branch=master

.. image:: https://img.shields.io/pypi/pyversions/biodome.svg
    :target: https://pypi.python.org/pypi/biodome

.. image:: https://img.shields.io/github/tag/cjrh/biodome.svg
    :target: https://img.shields.io/github/tag/cjrh/biodome.svg

.. image:: https://img.shields.io/badge/install-pip%20install%20biodome-ff69b4.svg
    :target: https://img.shields.io/badge/install-pip%20install%20biodome-ff69b4.svg

.. image:: https://img.shields.io/pypi/v/biodome.svg
    :target: https://img.shields.io/pypi/v/biodome.svg

.. image:: https://img.shields.io/badge/calver-YYYY.MM.MINOR-22bfda.svg
    :target: http://calver.org/

biodome
=======

*Controlled environments*

Reading environment variables with ``os.environ`` is pretty easy, but after
a while one gets pretty tired of having to cast variables to the right types
and handling fallback to defaults.

This library provides a clean way read environment variables and fall back
to defaults in a sane way.

**How you were doing it:**

.. code:: python

    import os

    try:
        TIMEOUT = int(os.environ.get('TIMEOUT', 10))
    except ValueError:
        TIMEOUT = 10

Wordy, boilerplate, DRY violation, etc.

**How you will be doing it:**

.. code:: python

    import biodome

    TIMEOUT = biodome.environ.get('TIMEOUT', 10)

That's right, it becomes a single line. But there's a magic trick here: how
does ``biodome`` know that ``TIMEOUT`` should be set to an ``int``? It knows
because it looks at the type of the default arguments. This works for a bunch
of different things:

.. code:: python

    # Lists
    os.environ['IGNORE_KEYS'] = '[1, 2, 3]'
    biodome.environ.get('TIMEOUT', []) == [1, 2, 3]

    # Dicts
    os.environ['SETTINGS'] = '{"a": 1, "b": 2}'
    biodome.environ.get('SETTINGS', {}) == dict(a=1, b=2)

If you look carefully at the above, you can see that we *set* the data via
the stdlib ``os.environ`` dictionary; that's right, ``biodome.environ`` is a
**drop-in replacement** for ``os.environ``. You don't even have to switch out
your entire codebase, you can do it piece by piece.

And while we're on the subject of *setting* env vars, with ``biodome`` you
don't have to cast them first, it does string casting internally automatically,
unlike ``os.environ``:

.. code:: python

    # Dicts
    biodome.environ['SETTINGS'] = dict(b=2, a=1)  # No cast required
    biodome.environ.get('SETTINGS', {}) == dict(a=1, b=2)

Loading env files
-----------------

``biodome`` also provides a function to load a file which specifies the
values of environment variables. An example of such an *env* file::

    # myconfig.env
    # This sets the log level for all the loggers in the program
    LOGGER_LEVEL=info

    # Hourly backups are stored at this path and named with a timestamp.
    BACKUP_PATH=/data/backups/

    # The number of times to retry outgoing HTTP requests if the status
    # code is > 500
    RETRY_TIME=5

The name of the environment variable must be on the left and the value
on the right. Each variable must be on its own line. Lines starting with
a ``#`` are considered comments and are ignored.

This *env* file can be loaded like this:

.. code-block:: python

    >>> import biodome
    >>> biodome.load_env_file('myconfig.env')
    >>> print(biodome.environ['RETRY_TIME'])
    5

True and False
--------------

I don't know about you, but I use bool settings a LOT in environment variables,
so handling this properly is really important to me. When calling
``biodome.environ.get('SETTING', default=<value>)``, the default value
can also be a bool, i.e., ``True`` or ``False``. In this case, *any of the
following values*, **and** their upper- or mixed-case equivalents will be
recognized as ``True``:

.. code:: python

   ['1', 'y', 'yes', 'on', 'active', 'activated', 'enabled', 'true',
   't', 'ok', 'yeah']

Anything not in this list will be considered as ``False``.  Do you have ideas
for more things that should be considered as ``True``? I take PRs!

Callables
---------

For explictness it is often convenient to declare and load environment
variables at the top of the module in which they're used:

.. code:: python

    """ My new module """
    import biodome

    ENABLE_SETTING_XYZ = biodome.environ.get('ENABLE_SETTING_XYZ', True)

    def blah():
        print(ENABLE_SETTING_XYZ)

You *could* call ``environ.get()`` inside the functions and methods where it
is used, but then you would lose the convenience of documenting all the
available environment variables at the top of the module.  As a solution to
this problem, *biodome* provides a way to produce a callable for a particular
setting.  An extra advantage of doing this is that it becomes quite easy to
make use of changes in environment variables on the fly.  Here's the
modified example:

.. code:: python

    """ My new module """
    import biodome

    ENABLE_SETTING_XYZ = biodome.environ.get_callable(
        # Same as before
        'ENABLE_SETTING_XYZ', True
        )

    def blah():
        print(ENABLE_SETTING_XYZ())  # Now a callable!

How it works internally
-----------------------

The key theme here is that the *type* of the default value is used to determine
how to cast the input value.  This works for the following types:

- ``int``
- ``float``
- ``str``
- ``list``
- ``dict``
- ``set`` (**NOTE**: only supported in Python 3+ due to ``ast.literal_eval()``)
- ``tuple``

For the containers, we use ``ast.literal_eval()`` which is much safer than
using ``eval()`` because code is not evaluated. Safety first! (thanks to
@nickdirienzo for the tip)
