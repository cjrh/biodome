biodome
=======

*Controlled environments*

Reading environment variables with ``os.environ`` is pretty easy, but after
a while one gets pretty tired of having to cast variables to the right types
and handling fallback to defaults.

This library provides a clean way read environment variables and fall back
to defaults in a sane way. Typical usage looks like this:

.. code:: python

   from biodome import biodome

   MY_VAR = biodome('MY_VAR', 123)

In this case, the output ``MY_VAR`` will be created from the environment
variable *MY_VAR*:

- If the env var *MY_VAR* doesn't exist, the result will be the default value
  of ``123``.
- If the env var *MY_VAR* does exist, **and** it is the same type as the
  default, i.e., an ``int``, then the output, ``MY_VAR``, will be an int.
- If the env var *MY_VAR* does exist, but is not convertible to the same
  type as the default, i.e., an ``int``, then the result will be the default.

The key theme here is that the *type* of the default value is used to determine
how to cast the input value.  This works for the following types:

- ``int``
- ``float``
- ``str``
- ``list``
- ``dict``
- ``set``
- ``tuple``

For the containers, the ``eval()`` function is used. This might be a security
risk if you don't have control over how your environment variables are set.
It would be possible to add a flag to disable ``eval()``: PRs welcome.

The default can also be a bool, i.e., ``True`` or ``False``. In this case, the
following values, **and** their upper- or mixed-case equivalents will be
recognized as ``True``:

.. code:: python

   ['1', 'y', 'yes', 'on', 'active', 'activated', 'enabled', 'true',
   't', 'ok', 'yeah']

Anything not in this list will be considered as ``False``.
