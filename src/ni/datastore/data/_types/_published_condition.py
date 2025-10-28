"""Published Condition data type for the Data Store Client."""

from __future__ import annotations

from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.measurements.data.v1.data_store_pb2 import (
    PublishedCondition as PublishedConditionProto,
)


class PublishedCondition:
    """Represents a condition that has been published to the data store.

    A published condition contains metadata about a condition value that was
    published, including a moniker for data retrieval and associated metadata
    like condition name, type, and associated step/test result IDs.

    Attributes:
        moniker: The moniker of the condition that this value is associated
            with. This moniker returns a Vector when read.
        published_condition_id: The unique identifier of the condition. This
            can be used to reference and find the condition in the data store.
        condition_name: The name of the condition.
        condition_type: The type of the condition. For example, "Setup" or
            "Environment".
        step_id: The ID of the step with which this condition is associated.
        test_result_id: The ID of the test result with which this condition
            is associated.
    """

    __slots__ = (
        "moniker",
        "id",
        "condition_name",
        "condition_type",
        "step_id",
        "test_result_id",
    )

    def __init__(
        self,
        *,
        moniker: Moniker | None = None,
        id: str = "",
        condition_name: str = "",
        condition_type: str = "",
        step_id: str = "",
        test_result_id: str = "",
    ) -> None:
        """Initialize a PublishedCondition instance."""
        self.moniker = moniker
        self.id = id
        self.condition_name = condition_name
        self.condition_type = condition_type
        self.step_id = step_id
        self.test_result_id = test_result_id

    @staticmethod
    def from_protobuf(published_condition_proto: PublishedConditionProto) -> "PublishedCondition":
        """Create a PublishedCondition instance from a protobuf PublishedCondition message."""
        return PublishedCondition(
            moniker=(
                published_condition_proto.moniker
                if published_condition_proto.HasField("moniker")
                else None
            ),
            id=published_condition_proto.id,
            condition_name=published_condition_proto.condition_name,
            condition_type=published_condition_proto.condition_type,
            step_id=published_condition_proto.step_id,
            test_result_id=published_condition_proto.test_result_id,
        )

    def to_protobuf(self) -> PublishedConditionProto:
        """Convert this PublishedCondition instance to a protobuf PublishedCondition message."""
        return PublishedConditionProto(
            moniker=self.moniker,
            id=self.id,
            condition_name=self.condition_name,
            condition_type=self.condition_type,
            step_id=self.step_id,
            test_result_id=self.test_result_id,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, PublishedCondition):
            return NotImplemented
        return (
            self.moniker == other.moniker
            and self.id == other.id
            and self.condition_name == other.condition_name
            and self.condition_type == other.condition_type
            and self.step_id == other.step_id
            and self.test_result_id == other.test_result_id
        )

    def __str__(self) -> str:
        """Return a string representation of the PublishedCondition."""
        return str(self.to_protobuf())
