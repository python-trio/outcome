.. _api-reference:

=============
API Reference
=============

.. module:: outcome

.. autofunction:: capture

.. autofunction:: acapture

.. autoclass:: Outcome
   :members:
   :inherited-members:

.. py:data:: Maybe
   :value: Value[ResultT] | Error

A convenience alias to a union of both results. This allows type checkers to perform
exhaustiveness checking when ``isinstance()`` is used with either class::

    outcome: Maybe[int] = capture(some_function, 1, 2, 3)
    if isinstance(outcome, Value):
        # Type checkers know it's a Value[int] here.
    else:
        # It must be an Error.

.. autoclass:: Value
   :members:
   :inherited-members:

.. autoclass:: Error
   :members:
   :inherited-members:

.. autoclass:: AlreadyUsedError
