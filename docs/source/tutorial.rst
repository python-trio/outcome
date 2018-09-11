========
Tutorial
========

.. currentmodule:: outcome

Outcome provides a function for capturing the outcome of a Python
function call, so that it can be passed around. The basic rule is::

    result = outcome.capture(f, *args, **kwargs)
    x = result.unwrap()

is the same as::

    x = f(*args, **kwargs)

even if ``f`` raises an error.

On Python 3.5+, there's also :func:`acapture`::

    result = await outcome.acapture(f, *args, **kwargs)
    x = result.unwrap()

which, like before, is the same as::

    x = await f(*args, **kwargs)

An Outcome object can only be unwrapped once. A second attempt would raise an
:class:`AlreadyUsedError`.

See the :ref:`api-reference` for the types involved.
