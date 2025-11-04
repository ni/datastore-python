"""Tests for the Outcome wrapper enum."""

import pytest
from ni.datastore.data import Outcome
from ni.measurements.data.v1.data_store_pb2 import Outcome as OutcomeProto


class TestOutcome:
    """Test the Outcome enum wrapper."""

    def test_enum_values_match_protobuf(self):
        """Test that enum values match the protobuf enum values."""
        assert Outcome.UNSPECIFIED == OutcomeProto.OUTCOME_UNSPECIFIED
        assert Outcome.PASSED == OutcomeProto.OUTCOME_PASSED
        assert Outcome.FAILED == OutcomeProto.OUTCOME_FAILED
        assert Outcome.INDETERMINATE == OutcomeProto.OUTCOME_INDETERMINATE

    def test_enum_values(self):
        """Test that enum has the expected values."""
        assert Outcome.UNSPECIFIED == 0
        assert Outcome.PASSED == 1
        assert Outcome.FAILED == 2
        assert Outcome.INDETERMINATE == 3

    def test_to_protobuf(self):
        """Test converting enum to protobuf value."""
        assert Outcome.UNSPECIFIED.to_protobuf() == OutcomeProto.OUTCOME_UNSPECIFIED
        assert Outcome.PASSED.to_protobuf() == OutcomeProto.OUTCOME_PASSED
        assert Outcome.FAILED.to_protobuf() == OutcomeProto.OUTCOME_FAILED
        assert Outcome.INDETERMINATE.to_protobuf() == OutcomeProto.OUTCOME_INDETERMINATE

    def test_from_protobuf(self):
        """Test converting protobuf value to enum."""
        assert Outcome.from_protobuf(OutcomeProto.OUTCOME_UNSPECIFIED) == Outcome.UNSPECIFIED
        assert Outcome.from_protobuf(OutcomeProto.OUTCOME_PASSED) == Outcome.PASSED
        assert Outcome.from_protobuf(OutcomeProto.OUTCOME_FAILED) == Outcome.FAILED
        assert Outcome.from_protobuf(OutcomeProto.OUTCOME_INDETERMINATE) == Outcome.INDETERMINATE

    def test_round_trip_conversion(self):
        """Test that converting to protobuf and back gives the same result."""
        for outcome in Outcome:
            pb_outcome = outcome.to_protobuf()
            back_to_enum = Outcome.from_protobuf(pb_outcome)
            assert outcome == back_to_enum

    def test_from_protobuf_invalid_value(self):
        """Test that from_protobuf raises ValueError for invalid values."""
        from typing import cast
        with pytest.raises(ValueError, match="Unknown outcome value"):
            Outcome.from_protobuf(cast(OutcomeProto.ValueType, 999))

    def test_enum_is_iterable(self):
        """Test that the enum can be iterated over."""
        outcomes = list(Outcome)
        assert len(outcomes) == 4
        assert Outcome.UNSPECIFIED in outcomes
        assert Outcome.PASSED in outcomes
        assert Outcome.FAILED in outcomes
        assert Outcome.INDETERMINATE in outcomes

    def test_enum_name_and_value_attributes(self):
        """Test that enum has correct name and value attributes."""
        assert Outcome.PASSED.name == "PASSED"
        assert Outcome.PASSED.value == 1
        assert Outcome.FAILED.name == "FAILED"
        assert Outcome.FAILED.value == 2