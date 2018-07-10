Release history
===============

.. currentmodule:: outcome

.. towncrier release notes start

Outcome 0.1.0 (2018-07-10)
--------------------------

Features
~~~~~~~~

- An Outcome may only be unwrapped or sent once.

  Attempting to do so a second time will raise an :class:`AlreadyUsedError`. (`#7 <https://github.com/python-trio/outcome/issues/7>`__)
