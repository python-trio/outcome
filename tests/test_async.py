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


@pytest.mark.parametrize("raises", [False, True])
async def test_acapture_accepts_legacy_callable_keyword(raises):
    value = object()
    error = ValueError("captured")

    async def fn(*, value):
        await asyncio.sleep(0)
        if raises:
            raise error
        return value

    result = await outcome.acapture(async_fn=fn, value=value)
    if raises:
        assert isinstance(result, Error)
        assert result.error is error
    else:
        assert result.unwrap() is value


@pytest.mark.parametrize("raises", [False, True])
async def test_acapture_forwards_async_fn_keyword(raises):
    value = object()
    error = ValueError("captured")

    async def fn(*, async_fn):
        await asyncio.sleep(0)
        assert async_fn is value
        if raises:
            raise error
        return async_fn

    result = await outcome.acapture(fn, async_fn=value)
    if raises:
        assert isinstance(result, Error)
        assert result.error is error
    else:
        assert result.unwrap() is value


@pytest.mark.parametrize("legacy_keyword", [False, True])
async def test_traceback_frame_removal(legacy_keyword):
    async def raise_ValueError(x):
        raise ValueError(x)

    if legacy_keyword:
        e = await outcome.acapture(async_fn=raise_ValueError, x='abc')
    else:
        e = await outcome.acapture(raise_ValueError, 'abc')
    with pytest.raises(ValueError) as exc_info:
        e.unwrap()
    frames = traceback.extract_tb(exc_info.value.__traceback__)
    functions = [function for _, _, function, _ in frames]
    assert functions[-2:] == ['unwrap', 'raise_ValueError']


@pytest.mark.parametrize("kwargs", [{}, {"unrelated": 1}])
async def test_acapture_requires_callable(kwargs):
    with pytest.raises(TypeError,
                       match="missing 1 required positional argument"):
        await outcome.acapture(**kwargs)
