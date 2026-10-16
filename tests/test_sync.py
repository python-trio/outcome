import sys
import traceback

import pytest

import outcome
from outcome import AlreadyUsedError, Error, Value


def test_Outcome():
    v = Value(1)
    assert v.value == 1
    assert v.unwrap() == 1
    assert repr(v) == "Value(1)"

    with pytest.raises(AlreadyUsedError):
        v.unwrap()

    v = Value(1)

    exc = RuntimeError("oops")
    e = Error(exc)
    assert e.error is exc
    with pytest.raises(RuntimeError):
        e.unwrap()
    with pytest.raises(AlreadyUsedError):
        e.unwrap()
    assert repr(e) == f"Error({exc!r})"

    e = Error(exc)
    with pytest.raises(TypeError):
        Error("hello")
    with pytest.raises(TypeError):
        Error(RuntimeError)

    def expect_1():
        assert (yield) == 1
        yield "ok"

    it = iter(expect_1())
    next(it)
    assert v.send(it) == "ok"
    with pytest.raises(AlreadyUsedError):
        v.send(it)

    def expect_RuntimeError():
        with pytest.raises(RuntimeError):
            yield
        yield "ok"

    it = iter(expect_RuntimeError())
    next(it)
    assert e.send(it) == "ok"
    with pytest.raises(AlreadyUsedError):
        e.send(it)


def test_Outcome_eq_hash():
    v1 = Value(["hello"])
    v2 = Value(["hello"])
    v3 = Value("hello")
    v4 = Value("hello")
    assert v1 == v2
    assert v1 != v3
    with pytest.raises(TypeError):
        {v1}
    assert {v3, v4} == {v3}

    # exceptions in general compare by identity
    exc1 = RuntimeError("oops")
    exc2 = KeyError("foo")
    e1 = Error(exc1)
    e2 = Error(exc1)
    e3 = Error(exc2)
    e4 = Error(exc2)
    assert e1 == e2
    assert e3 == e4
    assert e1 != e3
    assert {e1, e2, e3, e4} == {e1, e3}


def test_Value_compare():
    assert Value(1) < Value(2)
    assert not Value(3) < Value(2)
    with pytest.raises(TypeError):
        Value(1) < Value("foo")


def test_capture():
    def add(x, y):
        return x + y

    v = outcome.capture(add, 2, y=3)
    assert type(v) == Value
    assert v.unwrap() == 5

    def raise_ValueError(x):
        raise ValueError(x)

    e = outcome.capture(raise_ValueError, "two")
    assert type(e) == Error
    assert type(e.error) is ValueError
    assert e.error.args == ("two",)


def test_inheritance():
    assert issubclass(Value, outcome.Outcome)
    assert issubclass(Error, outcome.Outcome)


@pytest.mark.parametrize("raises", [False, True])
def test_capture_accepts_legacy_callable_keyword(raises):
    value = object()
    error = ValueError("captured")

    def fn(*, value):
        if raises:
            raise error
        return value

    result = outcome.capture(sync_fn=fn, value=value)
    if raises:
        assert isinstance(result, Error)
        assert result.error is error
    else:
        assert result.unwrap() is value


@pytest.mark.parametrize("raises", [False, True])
def test_capture_forwards_sync_fn_keyword(raises):
    value = object()
    error = ValueError("captured")

    def fn(*, sync_fn):
        assert sync_fn is value
        if raises:
            raise error
        return sync_fn

    result = outcome.capture(fn, sync_fn=value)
    if raises:
        assert isinstance(result, Error)
        assert result.error is error
    else:
        assert result.unwrap() is value


@pytest.mark.parametrize("legacy_keyword", [False, True])
def test_traceback_frame_removal(legacy_keyword):
    def raise_ValueError(x):
        raise ValueError(x)

    if legacy_keyword:
        e = outcome.capture(sync_fn=raise_ValueError, x='abc')
    else:
        e = outcome.capture(raise_ValueError, 'abc')
    with pytest.raises(ValueError) as exc_info:
        e.unwrap()
    frames = traceback.extract_tb(exc_info.value.__traceback__)
    functions = [function for _, _, function, _ in frames]
    assert functions[-2:] == ['unwrap', 'raise_ValueError']


def test_Error_unwrap_does_not_create_reference_cycles():
    # See comment in Error.unwrap for why reference cycles are tricky
    exc = ValueError()
    err = Error(exc)
    try:
        err.unwrap()
    except ValueError:
        pass
    # Top frame in the traceback is the current test function; we don't care
    # about its references
    assert exc.__traceback__.tb_frame is sys._getframe()
    # The next frame down is the 'unwrap' frame; we want to make sure it
    # doesn't reference the exception (or anything else for that matter, just
    # to be thorough)
    unwrap_frame = exc.__traceback__.tb_next.tb_frame
    assert unwrap_frame.f_code.co_name == "unwrap"
    assert unwrap_frame.f_locals == {}


@pytest.mark.parametrize("kwargs", [{}, {"unrelated": 1}])
def test_capture_requires_callable(kwargs):
    with pytest.raises(TypeError,
                       match="missing 1 required positional argument"):
        outcome.capture(**kwargs)
