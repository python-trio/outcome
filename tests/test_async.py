import asyncio
import sys

import pytest
from async_generator import async_generator, yield_

import outcome
from outcome import Error, Value, AlreadyUsedError

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
    @async_generator
    async def my_agen_func():
        assert (await yield_(1)) == "value"
        with pytest.raises(KeyError):
            await yield_(2)
        await yield_(3)

    my_agen = my_agen_func().__aiter__()
    if sys.version_info < (3, 5, 2):
        my_agen = await my_agen
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
