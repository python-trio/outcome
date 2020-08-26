import abc
from typing import (
    Any, AsyncGenerator, Awaitable, Callable, Generator, Generic, NoReturn,
    TypeVar
)

import attr

from ._util import AlreadyUsedError, remove_tb_frames

__all__ = ['Error', 'Outcome', 'Value', 'acapture', 'capture']

V = TypeVar('V', covariant=True)
Y = TypeVar('Y')
R = TypeVar('R')


@attr.s(
    repr=False,
    init=False,
    these={'_unwrapped': attr.ib(default=False, eq=False, init=False)},
)
class Outcome(Generic[V]):
    """An abstract class representing the result of a Python computation.

    This class has two concrete subclasses: :class:`Value` representing a
    value, and :class:`Error` representing an exception.

    In addition to the methods described below, comparison operators on
    :class:`Value` and :class:`Error` objects (``==``, ``<``, etc.) check that
    the other object is also a :class:`Value` or :class:`Error` object
    respectively, and then compare the contained objects.

    :class:`Outcome` objects are hashable if the contained objects are
    hashable.

    """

    # attrs has an issue with attr.ibs in the class body with subclasses of
    # Generic, so it is passed to attr.s(these=...) instead.
    # https://github.com/python-attrs/attrs/issues/313
    __slots__ = ('_unwrapped',)
    _unwrapped: bool

    def _set_unwrapped(self) -> None:
        if self._unwrapped:
            raise AlreadyUsedError
        object.__setattr__(self, '_unwrapped', True)

    @abc.abstractmethod
    def unwrap(self) -> V:
        """Return or raise the contained value or exception.

        These two lines of code are equivalent::

           x = fn(*args)
           x = outcome.capture(fn, *args).unwrap()

        """

    @abc.abstractmethod
    def send(self, gen: Generator[Y, V, R]) -> Y:
        """Send or throw the contained value or exception into the given
        generator object.

        Args:
          gen: A generator object supporting ``.send()`` and ``.throw()``
              methods.

        """

    @abc.abstractmethod
    async def asend(self, agen: AsyncGenerator[Y, V]) -> Y:
        """Send or throw the contained value or exception into the given async
        generator object.

        Args:
          agen: An async generator object supporting ``.asend()`` and
              ``.athrow()`` methods.

        """


@attr.s(frozen=True, repr=False, slots=True)
class Value(Outcome[V]):
    """Concrete :class:`Outcome` subclass representing a regular value.

    """

    value: V = attr.ib()
    """The contained value."""

    def __repr__(self) -> str:
        return f'Value({self.value!r})'

    def unwrap(self) -> V:
        self._set_unwrapped()
        return self.value

    def send(self, gen: Generator[Y, V, R]) -> Y:
        self._set_unwrapped()
        return gen.send(self.value)

    async def asend(self, agen: AsyncGenerator[Y, V]) -> Y:
        self._set_unwrapped()
        return await agen.asend(self.value)


@attr.s(frozen=True, repr=False, slots=True)
class Error(Outcome[NoReturn]):
    """Concrete :class:`Outcome` subclass representing a raised exception.

    """

    error: BaseException = attr.ib(
        validator=attr.validators.instance_of(BaseException)
    )
    """The contained exception object."""

    def __repr__(self) -> str:
        return f'Error({self.error!r})'

    def unwrap(self) -> NoReturn:
        self._set_unwrapped()
        # Tracebacks show the 'raise' line below out of context, so let's give
        # this variable a name that makes sense out of context.
        captured_error = self.error
        raise captured_error

    def send(self, gen: Generator[Y, NoReturn, R]) -> Y:
        self._set_unwrapped()
        # TODO: This ignore can be removed when this fix is released:
        # https://github.com/python/typeshed/pull/4253
        return gen.throw(self.error)  # type: ignore

    async def asend(self, agen: AsyncGenerator[Y, NoReturn]) -> Y:
        self._set_unwrapped()
        # TODO: This ignore can be removed when this fix is released:
        # https://github.com/python/typeshed/pull/4253
        return await agen.athrow(self.error)  # type: ignore


def capture(sync_fn: Callable[..., V], *args: Any,
            **kwargs: Any) -> Outcome[V]:
    """Run ``sync_fn(*args, **kwargs)`` and capture the result.

    Returns:
      Either a :class:`Value` or :class:`Error` as appropriate.

    """
    try:
        return Value(sync_fn(*args, **kwargs))
    except BaseException as exc:
        exc = remove_tb_frames(exc, 1)
        return Error(exc)


async def acapture(
        async_fn: Callable[..., Awaitable[V]],
        *args: Any,
        **kwargs: Any,
) -> Outcome[V]:
    """Run ``await async_fn(*args, **kwargs)`` and capture the result.

    Returns:
      Either a :class:`Value` or :class:`Error` as appropriate.

    """
    try:
        return Value(await async_fn(*args, **kwargs))
    except BaseException as exc:
        exc = remove_tb_frames(exc, 1)
        return Error(exc)
