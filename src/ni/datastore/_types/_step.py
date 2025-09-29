"""Step data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

import hightime as ht
from ni.datastore.grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.data.v1.data_store_pb2 import (
    Step as StepProto,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_from_protobuf,
    hightime_datetime_to_protobuf,
)


class Step:
    """Information about a step into which measurements and conditions are published."""

    __slots__ = (
        "step_id",
        "parent_step_id",
        "test_result_id",
        "test_id",
        "step_name",
        "step_type",
        "notes",
        "_start_date_time",
        "_end_date_time",
        "link",
        "extensions",
        "schema_id",
    )

    @property
    def start_date_time(self) -> ht.datetime | None:
        """Get the start date and time of the step execution."""
        return self._start_date_time

    @property
    def end_date_time(self) -> ht.datetime | None:
        """Get the end date and time of the step execution."""
        return self._end_date_time

    def __init__(
        self,
        *,
        step_id: str = "",
        parent_step_id: str = "",
        test_result_id: str = "",
        test_id: str = "",
        step_name: str = "",
        step_type: str = "",
        notes: str = "",
        link: str = "",
        extensions: MutableMapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a Step instance."""
        self.step_id = step_id
        self.parent_step_id = parent_step_id
        self.test_result_id = test_result_id
        self.test_id = test_id
        self.step_name = step_name
        self.step_type = step_type
        self.notes = notes
        self.link = link
        self.extensions: MutableMapping[str, str] = extensions if extensions is not None else {}
        self.schema_id = schema_id

        self._start_date_time: ht.datetime | None = None
        self._end_date_time: ht.datetime | None = None

    @staticmethod
    def from_protobuf(step_proto: StepProto) -> "Step":
        """Create a Step instance from a protobuf Step message."""
        step = Step(
            step_id=step_proto.step_id,
            parent_step_id=step_proto.parent_step_id,
            test_result_id=step_proto.test_result_id,
            test_id=step_proto.test_id,
            step_name=step_proto.step_name,
            step_type=step_proto.step_type,
            notes=step_proto.notes,
            link=step_proto.link,
            schema_id=step_proto.schema_id,
        )
        step._start_date_time = (
            hightime_datetime_from_protobuf(step_proto.start_date_time)
            if step_proto.HasField("start_date_time")
            else None
        )
        step._end_date_time = (
            hightime_datetime_from_protobuf(step_proto.end_date_time)
            if step_proto.HasField("end_date_time")
            else None
        )
        populate_from_extension_value_message_map(step.extensions, step_proto.extensions)
        return step

    def to_protobuf(self) -> StepProto:
        """Convert this Step to a protobuf Step message."""
        step_proto = StepProto(
            step_id=self.step_id,
            parent_step_id=self.parent_step_id,
            test_result_id=self.test_result_id,
            test_id=self.test_id,
            step_name=self.step_name,
            step_type=self.step_type,
            notes=self.notes,
            start_date_time=(
                hightime_datetime_to_protobuf(self.start_date_time)
                if self.start_date_time
                else None
            ),
            end_date_time=(
                hightime_datetime_to_protobuf(self.end_date_time) if self.end_date_time else None
            ),
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(step_proto.extensions, self.extensions)
        return step_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Step):
            return NotImplemented
        return (
            self.step_id == other.step_id
            and self.parent_step_id == other.parent_step_id
            and self.test_result_id == other.test_result_id
            and self.test_id == other.test_id
            and self.step_name == other.step_name
            and self.step_type == other.step_type
            and self.notes == other.notes
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the Step."""
        return str(self.to_protobuf())
