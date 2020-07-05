import asyncio
import traceback
from typing import (
    TYPE_CHECKING, Any, AsyncGenerator, NoReturn, Optional, TypeVar
)

import pytest

import outcome
from outcome import AlreadyUsedError, Error, Outcome, Value

pytestmark = pytest.mark.asyncio

V = TypeVar('V')
E = TypeVar('E', bound=BaseException)

if TYPE_CHECKING:
    TValue = Value[V, BaseException]
    TError = Error[NoReturn, E]
else:
    TValue = TError = Any


async def test_acapture() -> None:
    async def add(x: int, y: int) -> int:
        await asyncio.sleep(0)
        return x + y

    v: Outcome[int, BaseException] = await outcome.acapture(add, 3, y=4)
    assert v == Value(7)

    async def raise_ValueError(x: str) -> NoReturn:
        await asyncio.sleep(0)
        raise ValueError(x)

    e: Outcome[NoReturn, ValueError] = await outcome.acapture(
        raise_ValueError, 9
    )
    assert isinstance(e, Error)
    assert type(e.error) is ValueError
    assert e.error.args == (9,)


async def test_asend() -> None:
    async def my_agen_func() -> AsyncGenerator[int, Optional[str]]:
        assert (yield 1) == "value"
        with pytest.raises(KeyError):
            yield 2
        yield 3

    my_agen = my_agen_func().__aiter__()
    v: TValue[str] = Value("value")
    e: TError[KeyError] = Error(KeyError())
    assert (await my_agen.asend(None)) == 1
    assert (await v.asend(my_agen)) == 2
    with pytest.raises(AlreadyUsedError):
        await v.asend(my_agen)

    assert (await e.asend(my_agen)) == 3
    with pytest.raises(AlreadyUsedError):
        await e.asend(my_agen)
    with pytest.raises(StopAsyncIteration):
        await my_agen.asend(None)


async def test_traceback_frame_removal() -> None:
    async def raise_ValueError(x: str) -> NoReturn:
        raise ValueError(x)

    e: Outcome[NoReturn, ValueError] = await outcome.acapture(
        raise_ValueError, 'abc'
    )
    with pytest.raises(ValueError) as exc_info:
        e.unwrap()
    frames = traceback.extract_tb(exc_info.value.__traceback__)
    functions = [function for _, _, function, _ in frames]
    assert functions[-2:] == ['unwrap', 'raise_ValueError']
