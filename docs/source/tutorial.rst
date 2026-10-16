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

There's also :func:`acapture`::

    result = await outcome.acapture(f, *args, **kwargs)
    x = result.unwrap()

which, like before, is the same as::

    x = await f(*args, **kwargs)

When the callable is passed positionally to :func:`capture` or
:func:`acapture`, all keyword arguments (including ``sync_fn`` and
``async_fn``) are forwarded to it. For compatibility, the callable can also
be passed as ``capture(sync_fn=f, ...)`` or ``acapture(async_fn=f, ...)``
when there are no positional arguments; that keyword selects the callable
and the remaining keywords are forwarded.

An Outcome object can only be unwrapped once. A second attempt would raise an
:class:`AlreadyUsedError`.

See the :ref:`api-reference` for the types involved.
