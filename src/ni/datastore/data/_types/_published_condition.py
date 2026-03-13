"""Published Condition data type for the Data Store Client."""

from __future__ import annotations

from ni.measurements.data.v1.data_store_pb2 import (
    PublishedCondition as PublishedConditionProto,
)


class PublishedCondition:
    """Represents a condition that has been published to the data store.

    A published condition contains metadata about a condition value that was
    published, including an id for data retrieval and associated metadata
    like condition name, type, and associated step/test result IDs.
    """

    __slots__ = (
        "id",
        "name",
        "condition_type",
        "step_id",
        "test_result_id",
    )

    def __init__(
        self,
        *,
        id: str = "",
        name: str = "",
        condition_type: str = "",
        step_id: str = "",
        test_result_id: str = "",
    ) -> None:
        """Initialize a PublishedCondition instance.

        Args:
            id: The unique identifier of the condition. This
                can be used to reference and find the condition in the data store.
            name: The name of the condition.
            condition_type: The type of the condition. For example, "Setup" or
                "Environment".
            step_id: The ID of the step with which this condition is associated.
            test_result_id: The ID of the test result with which this condition
                is associated.
        """
        self.id = id
        self.name = name
        self.condition_type = condition_type
        self.step_id = step_id
        self.test_result_id = test_result_id

    @staticmethod
    def from_protobuf(published_condition_proto: PublishedConditionProto) -> "PublishedCondition":
        """Create a PublishedCondition instance from a protobuf PublishedCondition message."""
        return PublishedCondition(
            id=published_condition_proto.id,
            name=published_condition_proto.name,
            condition_type=published_condition_proto.condition_type,
            step_id=published_condition_proto.step_id,
            test_result_id=published_condition_proto.test_result_id,
        )

    def to_protobuf(self) -> PublishedConditionProto:
        """Convert this PublishedCondition instance to a protobuf PublishedCondition message."""
        return PublishedConditionProto(
            id=self.id,
            name=self.name,
            condition_type=self.condition_type,
            step_id=self.step_id,
            test_result_id=self.test_result_id,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, PublishedCondition):
            return NotImplemented
        return (
            self.id == other.id
            and self.name == other.name
            and self.condition_type == other.condition_type
            and self.step_id == other.step_id
            and self.test_result_id == other.test_result_id
        )

    def __str__(self) -> str:
        """Return a string representation of the PublishedCondition."""
        return str(self.to_protobuf())
