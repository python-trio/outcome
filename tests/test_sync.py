# coding: utf-8
from __future__ import absolute_import, division, print_function
import sys

import pytest

import outcome
from outcome import Error, Value


def test_Outcome():
    v = Value(1)
    assert v.value == 1
    assert v.unwrap() == 1
    assert repr(v) == "Value(1)"

    exc = RuntimeError("oops")
    e = Error(exc)
    assert e.error is exc
    with pytest.raises(RuntimeError):
        e.unwrap()
    assert repr(e) == "Error({!r})".format(exc)

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

    def expect_RuntimeError():
        with pytest.raises(RuntimeError):
            yield
        yield "ok"

    it = iter(expect_RuntimeError())
    next(it)
    assert e.send(it) == "ok"


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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires python 3")
def test_Value_compare():
    assert Value(1) < Value(2)
    assert not Value(3) < Value(2)
    with pytest.raises(TypeError):
        Value(1) < Value("foo")


def test_capture():
    def return_arg(x):
        return x

    v = outcome.capture(return_arg, 2)
    assert type(v) == Value
    assert v.unwrap() == 2

    def raise_ValueError(x):
        raise ValueError(x)

    e = outcome.capture(raise_ValueError, "two")
    assert type(e) == Error
    assert type(e.error) is ValueError
    assert e.error.args == ("two",)
