import asyncio
import traceback

import pytest

import outcome
from outcome import AlreadyUsedError, Error, Value

pytestmark = pytest.mark.asyncio


async def test_acapture():
    async def add(x, y):
        await asyncio.sleep(0)
        return x + y

    v = await outcome.acapture(add, 3, y=4)
    assert v == Value(7)

    async def raise_ValueError(x):
        await asyncio.sleep(0)
        raise ValueError(x)

    e = await outcome.acapture(raise_ValueError, 9)
    assert type(e.error) is ValueError
    assert e.error.args == (9,)


async def test_asend():
    async def my_agen_func():
        assert (yield 1) == "value"
        with pytest.raises(KeyError):
            yield 2
        yield 3

    my_agen = my_agen_func().__aiter__()
    v = Value("value")
    e = Error(KeyError())
    assert (await my_agen.asend(None)) == 1
    assert (await v.asend(my_agen)) == 2
    with pytest.raises(AlreadyUsedError):
        await v.asend(my_agen)

    assert (await e.asend(my_agen)) == 3
    with pytest.raises(AlreadyUsedError):
        await e.asend(my_agen)
    with pytest.raises(StopAsyncIteration):
        await my_agen.asend(None)


async def test_traceback_frame_removal():
    async def raise_ValueError(x):
        raise ValueError(x)

    e = await outcome.acapture(raise_ValueError, 'abc')
    with pytest.raises(ValueError) as exc_info:
        e.unwrap()
    frames = traceback.extract_tb(exc_info.value.__traceback__)
    functions = [function for _, _, function, _ in frames]
    assert functions[-2:] == ['unwrap', 'raise_ValueError']
