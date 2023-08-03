"""Verify type hints behave corectly.

This doesn't have the test_ prefix, since runtime testing isn't particularly useful.
"""
from collections.abc import AsyncGenerator, Generator
from typing import List, NoReturn, Union

from typing_extensions import assert_type

import outcome
from outcome import Error, Maybe, Outcome, Value, acapture, capture

maybe: Maybe[float] = capture(len, [])
assert_type(maybe, Union[Value[float], Error])

outcome.__version__ = 'dev'  # type: ignore[misc]


def value_variance_test() -> None:
    """Check variance behaves as expected."""
    value: Value[int]
    value_sub: Value[bool] = Value(True)
    value_super: Value[object] = Value(None)
    value = value_sub  # Is covariant.
    value = value_super  # type: ignore[assignment]


def outcome_test() -> None:
    """Test assigning either type to the base class."""
    value: Value[List[str]] = Value(['a', 'b', 'c'])
    error: Error = Error(Exception())

    outcome_good: Outcome[List[str]] = value
    outcome_mismatch: Outcome[bool] = Value(48.3)  # type: ignore[arg-type]
    outcome_err: Outcome[List[str]] = error

    assert_type(outcome_good.unwrap(), List[str])
    assert_type(outcome_err.unwrap(), List[str])
    assert_type(value.unwrap(), List[str])
    assert_type(error.unwrap(), NoReturn)


def sync_raises() -> NoReturn:
    raise NotImplementedError


def sync_generator_one() -> Generator[int, str, List[str]]:
    word: str = (yield 5)
    assert len(word) == 3
    return ['a', 'b', 'c']


def sync_generator_two() -> Generator[str, int, List[str]]:
    three: int = (yield 'house')
    assert three.bit_length() == 2
    return ['a', 'b', 'c']


def sync_none() -> bool:
    return True


def sync_one(param: float) -> int:
    return round(param)


def sync_capture_test() -> None:
    """Test synchronous behaviour."""
    assert_type(capture(sync_none), Union[Value[bool], Error])
    assert_type(capture(sync_one, 3.14), Union[Value[int], Error])
    assert_type(capture(sync_one, param=3.14), Union[Value[int], Error])
    assert_type(capture(sync_raises), Error)
    capture(sync_one)  # type: ignore[call-arg]
    capture(sync_none, 1, 2)  # type: ignore[call-arg]


async def sync_gen_test() -> None:
    """Check send methods."""
    value_one: Value[str] = Value('abc')
    value_two: Value[int] = Value(3)
    error: Error = Error(Exception())
    outcome_one: Outcome[str] = [error, value_one][1]
    outcome_two: Outcome[int] = [error, value_two][1]

    assert_type(outcome_one.send(sync_generator_one()), int)
    assert_type(outcome_two.send(sync_generator_two()), str)
    outcome_one.send(sync_generator_two())  # type: ignore[arg-type]
    outcome_two.send(sync_generator_one())  # type: ignore[arg-type]

    assert_type(value_one.send(sync_generator_one()), int)
    assert_type(value_two.send(sync_generator_two()), str)
    value_one.send(sync_generator_two())  # type: ignore[arg-type]
    value_two.send(sync_generator_one())  # type: ignore[arg-type]

    # Error doesn't care.
    assert_type(error.send(sync_generator_one()), int)
    assert_type(error.send(sync_generator_two()), str)


async def async_none() -> bool:
    return True


async def async_raises() -> NoReturn:
    raise NotImplementedError


async def async_one(param: float) -> int:
    return round(param)


async def async_generator_one() -> AsyncGenerator[int, str]:
    assert_type((yield 5), str)


async def async_generator_two() -> AsyncGenerator[str, int]:
    assert_type((yield ''), int)


async def async_capture_test() -> None:
    """Test asynchronous behaviour."""
    assert_type(await acapture(async_none), Union[Value[bool], Error])
    assert_type(await acapture(async_one, 3.14), Union[Value[int], Error])
    assert_type(
        await acapture(async_one, param=3.14), Union[Value[int], Error]
    )
    assert_type(await acapture(async_raises), Error)
    capture(async_one)  # type: ignore[call-arg]
    capture(async_none, 1, 2)  # type: ignore[call-arg]


async def async_gen_test() -> None:
    value_one: Value[str] = Value('abc')
    value_two: Value[int] = Value(3)
    error: Error = Error(Exception())
    outcome_one: Outcome[str] = [error, value_one][1]
    outcome_two: Outcome[int] = [error, value_two][1]

    assert_type(await outcome_one.asend(async_generator_one()), int)
    assert_type(await outcome_two.asend(async_generator_two()), str)
    await outcome_one.asend(async_generator_two())  # type: ignore[arg-type]
    await outcome_two.asend(async_generator_one())  # type: ignore[arg-type]

    assert_type(await value_one.asend(async_generator_one()), int)
    assert_type(await value_two.asend(async_generator_two()), str)
    await value_one.asend(async_generator_two())  # type: ignore[arg-type]
    await value_two.asend(async_generator_one())  # type: ignore[arg-type]

    # Error doesn't care.
    assert_type(await error.asend(async_generator_one()), int)
    assert_type(await error.asend(async_generator_two()), str)
