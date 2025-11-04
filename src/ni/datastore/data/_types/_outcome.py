"""Outcome data type for the Data Store Client."""

from __future__ import annotations

from enum import IntEnum

from ni.measurements.data.v1.data_store_pb2 import Outcome as OutcomeProto


class Outcome(IntEnum):
    """Represents the outcome of a measurement or test operation.

    The Outcome enum indicates whether a measurement or test passed, failed,
    or had an indeterminate result.
    """

    UNSPECIFIED = OutcomeProto.OUTCOME_UNSPECIFIED
    """The outcome is not specified or unknown."""

    PASSED = OutcomeProto.OUTCOME_PASSED
    """The measurement or test passed successfully."""

    FAILED = OutcomeProto.OUTCOME_FAILED  
    """The measurement or test failed."""

    INDETERMINATE = OutcomeProto.OUTCOME_INDETERMINATE
    """The measurement or test result is indeterminate or inconclusive."""

    @classmethod
    def from_protobuf(cls, outcome_proto: OutcomeProto.ValueType) -> "Outcome":
        """Create an Outcome instance from a protobuf Outcome value.
        
        Args:
            outcome_proto: The protobuf Outcome value.
            
        Returns:
            The corresponding Outcome enum value.
            
        Raises:
            ValueError: If the protobuf value doesn't correspond to a known Outcome.
        """
        try:
            return cls(outcome_proto)
        except ValueError as e:
            raise ValueError(f"Unknown outcome value: {outcome_proto}") from e

    def to_protobuf(self) -> OutcomeProto.ValueType:
        """Convert this Outcome instance to a protobuf Outcome value.
        
        Returns:
            The corresponding protobuf Outcome value.
        """
        return OutcomeProto.ValueType(self.value)