"""Outcome data type for the V2 Data Store Client."""

from __future__ import annotations

from enum import IntEnum

from ni.measurements.data.v2.data_store_pb2 import Outcome as OutcomeProto


class Outcome(IntEnum):
    """Represents the terminal result of a test result, step, or measurement."""

    UNSPECIFIED = OutcomeProto.OUTCOME_UNSPECIFIED
    """The outcome is not specified."""

    PASSED = OutcomeProto.OUTCOME_PASSED
    """The operation passed."""

    FAILED = OutcomeProto.OUTCOME_FAILED
    """The operation failed."""

    SKIPPED = OutcomeProto.OUTCOME_SKIPPED
    """The operation was skipped."""

    TERMINATED = OutcomeProto.OUTCOME_TERMINATED
    """The operation was terminated."""

    ERRORED = OutcomeProto.OUTCOME_ERRORED
    """The operation reported an error."""

    TIMED_OUT = OutcomeProto.OUTCOME_TIMED_OUT
    """The operation timed out."""

    USER_DEFINED = OutcomeProto.OUTCOME_USER_DEFINED
    """The outcome is defined by the user."""

    @classmethod
    def from_protobuf(cls, outcome_proto: OutcomeProto.ValueType) -> "Outcome":
        """Create an Outcome from a protobuf Outcome value."""
        try:
            return cls(outcome_proto)
        except ValueError as e:
            raise ValueError(f"Unknown outcome value: {outcome_proto}") from e

    def to_protobuf(self) -> OutcomeProto.ValueType:
        """Convert this Outcome to a protobuf Outcome value."""
        return OutcomeProto.ValueType(self.value)
