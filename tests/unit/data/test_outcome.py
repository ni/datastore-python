"""Tests for the Outcome wrapper enum."""

from __future__ import annotations

from typing import cast

import pytest
from ni.datastore.data import Outcome
from ni.measurements.data.v1.data_store_pb2 import Outcome as OutcomeProto


def test___enum_values___match_protobuf_values() -> None:
    """Test that enum values match the protobuf enum values."""
    assert Outcome.UNSPECIFIED == OutcomeProto.OUTCOME_UNSPECIFIED
    assert Outcome.PASSED == OutcomeProto.OUTCOME_PASSED
    assert Outcome.FAILED == OutcomeProto.OUTCOME_FAILED
    assert Outcome.INDETERMINATE == OutcomeProto.OUTCOME_INDETERMINATE


def test___enum_values___have_expected_integer_values() -> None:
    """Test that enum has the expected integer values."""
    assert Outcome.UNSPECIFIED == 0
    assert Outcome.PASSED == 1
    assert Outcome.FAILED == 2
    assert Outcome.INDETERMINATE == 3


def test___to_protobuf___converts_enum_to_protobuf_value() -> None:
    """Test converting enum to protobuf value."""
    assert Outcome.UNSPECIFIED.to_protobuf() == OutcomeProto.OUTCOME_UNSPECIFIED
    assert Outcome.PASSED.to_protobuf() == OutcomeProto.OUTCOME_PASSED
    assert Outcome.FAILED.to_protobuf() == OutcomeProto.OUTCOME_FAILED
    assert Outcome.INDETERMINATE.to_protobuf() == OutcomeProto.OUTCOME_INDETERMINATE


def test___from_protobuf___converts_protobuf_value_to_enum() -> None:
    """Test converting protobuf value to enum."""
    assert Outcome.from_protobuf(OutcomeProto.OUTCOME_UNSPECIFIED) == Outcome.UNSPECIFIED
    assert Outcome.from_protobuf(OutcomeProto.OUTCOME_PASSED) == Outcome.PASSED
    assert Outcome.from_protobuf(OutcomeProto.OUTCOME_FAILED) == Outcome.FAILED
    assert Outcome.from_protobuf(OutcomeProto.OUTCOME_INDETERMINATE) == Outcome.INDETERMINATE


def test___round_trip_conversion___preserves_enum_value() -> None:
    """Test that converting to protobuf and back gives the same result."""
    for outcome in Outcome:
        pb_outcome = outcome.to_protobuf()
        back_to_enum = Outcome.from_protobuf(pb_outcome)
        assert outcome == back_to_enum


def test___invalid_value___from_protobuf___raises_value_error() -> None:
    """Test that from_protobuf raises ValueError for invalid values."""
    with pytest.raises(ValueError, match="Unknown outcome value"):
        Outcome.from_protobuf(cast(OutcomeProto.ValueType, 999))


def test___enum___is_iterable() -> None:
    """Test that the enum can be iterated over."""
    outcomes = list(Outcome)
    assert len(outcomes) == 4
    assert Outcome.UNSPECIFIED in outcomes
    assert Outcome.PASSED in outcomes
    assert Outcome.FAILED in outcomes
    assert Outcome.INDETERMINATE in outcomes


def test___enum___has_correct_name_and_value_attributes() -> None:
    """Test that enum has correct name and value attributes."""
    assert Outcome.PASSED.name == "PASSED"
    assert Outcome.PASSED.value == 1
    assert Outcome.FAILED.name == "FAILED"
    assert Outcome.FAILED.value == 2