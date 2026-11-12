"""Check runtime annotations after public metadata normalization."""

from typing import get_args, get_type_hints

import attr
import pytest

import outcome
from outcome import _impl, _util, _version


def test_value_runtime_type_hints():
    hints = get_type_hints(outcome.Value)
    assert hints["value"] is outcome.Value.__parameters__[0]
    assert hints["_unwrapped"] is bool


@pytest.mark.skipif(
    not hasattr(attr, "resolve_types"),
    reason="attrs.resolve_types is unavailable in this attrs version",
)
def test_value_attrs_type_resolution():
    assert attr.resolve_types(outcome.Value) is outcome.Value
    assert attr.fields(outcome.Value
                       ).value.type is outcome.Value.__parameters__[0]


@pytest.mark.parametrize("cls", [outcome.Outcome, outcome.Error])
def test_other_public_class_type_hints(cls):
    assert get_type_hints(cls)["_unwrapped"] is bool


def test_public_metadata_preserves_objects_and_alias():
    assert outcome.Value is _impl.Value
    assert outcome.Outcome is _impl.Outcome
    assert outcome.Error is _impl.Error
    assert outcome.capture is _impl.capture
    assert outcome.acapture is _impl.acapture
    assert outcome.AlreadyUsedError is _util.AlreadyUsedError
    assert outcome.__version__ == _version.__version__
    for name in ("Value", "Outcome", "Error", "AlreadyUsedError", "capture",
                 "acapture"):
        assert getattr(outcome, name).__module__ == "outcome"
    assert set(outcome.__all__) == {
        "Error", "Outcome", "Value", "Maybe", "acapture", "capture",
        "AlreadyUsedError"
    }
    value_alias, error_alias = get_args(outcome.Maybe)
    assert value_alias.__origin__ is outcome.Value
    assert error_alias is outcome.Error
    assert not hasattr(outcome, "fixup_module_metadata")
