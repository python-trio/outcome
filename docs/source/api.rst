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
   :value: Value[T] | Error

   A convenience alias to a union of both results. This allows type checkers to perform
   exhaustiveness checking when ``isinstance()`` is used with either class.

.. autoclass:: Value
   :members:
   :inherited-members:

.. autoclass:: Error
   :members:
   :inherited-members:

.. autoclass:: AlreadyUsedError
