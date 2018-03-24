import abc

from ._sync import (
    Error as ErrorBase, Outcome as OutcomeBase, Value as ValueBase
)

__all__ = ['Error', 'Outcome', 'Value', 'acapture', 'capture']


def capture(sync_fn, *args):
    """Run ``sync_fn(*args)`` and capture the result.

    Returns:
      Either a :class:`Value` or :class:`Error` as appropriate.

    """
    # _sync.capture references ErrorBase and ValueBase
    try:
        return Value(sync_fn(*args))
    except BaseException as exc:
        return Error(exc)


async def acapture(async_fn, *args):
    """Run ``await async_fn(*args)`` and capture the result.

    Returns:
      Either a :class:`Value` or :class:`Error` as appropriate.

    """
    try:
        return Value(await async_fn(*args))
    except BaseException as exc:
        return Error(exc)


class Outcome(OutcomeBase):
    @abc.abstractmethod
    async def asend(self, agen):
        """Send or throw the contained value or exception into the given async
        generator object.

        Args:
          agen: An async generator object supporting ``.asend()`` and
              ``.athrow()`` methods.

        """


class Value(ValueBase):
    async def asend(self, agen):
        return await agen.asend(self.value)


class Error(ErrorBase):
    async def asend(self, agen):
        return await agen.athrow(self.error)


# We don't need this for Sphinx, but do it anyway for IPython, IDEs, etc
Outcome.__doc__ = OutcomeBase.__doc__
Value.__doc__ = ValueBase.__doc__
Error.__doc__ = ErrorBase.__doc__
