"""Step data type for the Data Store Client."""

from __future__ import annotations

from typing import Mapping, MutableMapping

import hightime as ht
from ni.datastore.data._types._error_information import ErrorInformation
from ni.datastore.data._types._outcome import Outcome
from ni.datastore.metadata._grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.data.v1.data_store_pb2 import Step as StepProto
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_from_protobuf,
    hightime_datetime_to_protobuf,
)


class Step:
    """Information about a step into which measurements and conditions are published.

    Represents a hierarchical execution step within a test result that can
    contain measurements and conditions. Steps are linked to a test result and
    can be organized into hierarchical structures using parent_step_id. Each
    step has test execution time, metadata, and optional extensions for custom
    metadata.
    """

    __slots__ = (
        "id",
        "parent_step_id",
        "test_result_id",
        "test_id",
        "name",
        "step_type",
        "notes",
        "start_date_time",
        "end_date_time",
        "link",
        "_extension",
        "schema_id",
        "error_information",
        "outcome",
    )

    @property
    def extension(self) -> MutableMapping[str, str]:
        """The extension of the step."""
        return self._extension

    def __init__(
        self,
        *,
        id: str = "",
        parent_step_id: str = "",
        test_result_id: str = "",
        test_id: str = "",
        name: str = "",
        step_type: str = "",
        notes: str = "",
        start_date_time: ht.datetime | None = None,
        end_date_time: ht.datetime | None = None,
        link: str = "",
        extension: Mapping[str, str] | None = None,
        schema_id: str = "",
        error_information: ErrorInformation | None = None,
        outcome: Outcome = Outcome.UNSPECIFIED,
    ) -> None:
        """Initialize a Step instance.

        Args:
            id: Unique identifier for the step.
            parent_step_id: ID of the parent step if this is a nested step.
            test_result_id: ID of the test result this step belongs to.
            test_id: ID of the test associated with this step.
            name: Human-readable name of the step.
            step_type: Type or category of the step.
            notes: Additional notes or comments about the step.
            start_date_time: The start date and time of the step execution.
            end_date_time: The end date and time of the step execution.
            link: Optional link to external resources for this step.
            extension: Additional extension attributes as key-value pairs.
            schema_id: ID of the extension schema for validating extensions.
            error_information: Error or exception information in case of
                step failure.
            outcome: The outcome of the step (PASSED, FAILED,
                INDETERMINATE, or UNSPECIFIED).
        """
        self.id = id
        self.parent_step_id = parent_step_id
        self.test_result_id = test_result_id
        self.test_id = test_id
        self.name = name
        self.step_type = step_type
        self.notes = notes
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.link = link
        self._extension: MutableMapping[str, str] = dict(extension) if extension is not None else {}
        self.schema_id = schema_id
        self.error_information = error_information
        self.outcome = outcome

    @staticmethod
    def from_protobuf(step_proto: StepProto) -> "Step":
        """Create a Step instance from a protobuf Step message."""
        step = Step(
            id=step_proto.id,
            parent_step_id=step_proto.parent_step_id,
            test_result_id=step_proto.test_result_id,
            test_id=step_proto.test_id,
            name=step_proto.name,
            step_type=step_proto.step_type,
            notes=step_proto.notes,
            start_date_time=(
                hightime_datetime_from_protobuf(step_proto.start_date_time)
                if step_proto.HasField("start_date_time")
                else None
            ),
            end_date_time=(
                hightime_datetime_from_protobuf(step_proto.end_date_time)
                if step_proto.HasField("end_date_time")
                else None
            ),
            link=step_proto.link,
            schema_id=step_proto.schema_id,
            error_information=(
                ErrorInformation.from_protobuf(step_proto.error_information)
                if step_proto.HasField("error_information")
                else None
            ),
            outcome=Outcome.from_protobuf(step_proto.outcome),
        )
        populate_from_extension_value_message_map(step.extension, step_proto.extension)
        return step

    def to_protobuf(self) -> StepProto:
        """Convert this Step to a protobuf Step message."""
        step_proto = StepProto(
            id=self.id,
            parent_step_id=self.parent_step_id,
            test_result_id=self.test_result_id,
            test_id=self.test_id,
            name=self.name,
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
            error_information=(
                self.error_information.to_protobuf() if self.error_information is not None else None
            ),
            outcome=self.outcome.to_protobuf(),
        )
        populate_extension_value_message_map(step_proto.extension, self.extension)
        return step_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Step):
            return NotImplemented
        return (
            self.id == other.id
            and self.parent_step_id == other.parent_step_id
            and self.test_result_id == other.test_result_id
            and self.test_id == other.test_id
            and self.name == other.name
            and self.step_type == other.step_type
            and self.notes == other.notes
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.link == other.link
            and self.extension == other.extension
            and self.schema_id == other.schema_id
            and self.error_information == other.error_information
            and self.outcome == other.outcome
        )

    def __str__(self) -> str:
        """Return a string representation of the Step."""
        return str(self.to_protobuf())
