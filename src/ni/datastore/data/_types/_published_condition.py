"""Published Condition data type for the Data Store Client."""

from __future__ import annotations

from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.measurements.data.v1.data_store_pb2 import (
    PublishedCondition as PublishedConditionProto,
)


class PublishedCondition:
    """Information about a condition published to the data store."""

    __slots__ = (
        "moniker",
        "published_condition_id",
        "condition_name",
        "condition_type",
        "step_id",
        "test_result_id",
    )

    def __init__(
        self,
        *,
        moniker: Moniker | None = None,
        published_condition_id: str = "",
        condition_name: str = "",
        condition_type: str = "",
        step_id: str = "",
        test_result_id: str = "",
    ) -> None:
        """Initialize a PublishedCondition instance."""
        self.moniker = moniker
        self.published_condition_id = published_condition_id
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
            published_condition_id=published_condition_proto.published_condition_id,
            condition_name=published_condition_proto.condition_name,
            condition_type=published_condition_proto.condition_type,
            step_id=published_condition_proto.step_id,
            test_result_id=published_condition_proto.test_result_id,
        )

    def to_protobuf(self) -> PublishedConditionProto:
        """Convert this PublishedCondition instance to a protobuf PublishedCondition message."""
        return PublishedConditionProto(
            moniker=self.moniker,
            published_condition_id=self.published_condition_id,
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
            and self.published_condition_id == other.published_condition_id
            and self.condition_name == other.condition_name
            and self.condition_type == other.condition_type
            and self.step_id == other.step_id
            and self.test_result_id == other.test_result_id
        )

    def __str__(self) -> str:
        """Return a string representation of the PublishedCondition."""
        return str(self.to_protobuf())
