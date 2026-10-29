"""Step data type for the V2 Data Store Client."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, MutableMapping, MutableSequence

import hightime as ht
from ni.measurements.data.v2.data_store_pb2 import Step as StepProto

from ni.datastore.data.v2._grpc_conversion import (
    duration_from_protobuf,
    duration_to_protobuf,
    extension_from_protobuf,
    extension_to_protobuf,
    timestamp_from_protobuf,
    timestamp_to_protobuf,
)
from ni.datastore.data.v2._types._condition import Condition
from ni.datastore.data.v2._types._error_information import ErrorInformation
from ni.datastore.data.v2._types._measurement import Measurement
from ni.datastore.data.v2._types._outcome import Outcome
from ni.datastore.data.v2._types._status import Status
from ni.datastore.metadata import Test


class Step:
    """Information about one execution of a test step.

    A step belongs to a test result and owns measurements and conditions. Steps
    can be nested by using parent_step_id, or created together by using
    children and measurements.
    """

    __slots__ = (
        "name",
        "id",
        "parent_step_id",
        "test_result_id",
        "test_id",
        "test",
        "step_type",
        "notes",
        "start_date_time",
        "end_date_time",
        "duration",
        "outcome",
        "status",
        "link",
        "_keywords",
        "_extension",
        "schema_id",
        "error_information",
        "_conditions",
        "_measurements",
        "_children",
        "_path",
        "_path_ids",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    @property
    def keywords(self) -> MutableSequence[str]:
        """Labels used to classify the step."""
        return self._keywords

    @property
    def extension(self) -> MutableMapping[str, Any]:
        """Custom JSON data associated with the step."""
        return self._extension

    @property
    def conditions(self) -> MutableSequence[Condition]:
        """The conditions owned by the step."""
        return self._conditions

    @property
    def measurements(self) -> MutableSequence[Measurement]:
        """Measurements created with the step, or expand on read."""
        return self._measurements

    @property
    def children(self) -> MutableSequence[Step]:
        """Child steps created with the step, or expand on read."""
        return self._children

    @property
    def path(self) -> MutableSequence[str]:
        """Output only. Names of this Step and its ancestors, ordered root-first."""
        return self._path

    @property
    def path_ids(self) -> MutableSequence[str]:
        """Output only. IDs of this Step and its ancestors, ordered root-first."""
        return self._path_ids

    def __init__(
        self,
        name: str,
        *,
        id: str = "",
        parent_step_id: str = "",
        test_result_id: str = "",
        test_id: str = "",
        test: Test | None = None,
        step_type: str = "",
        notes: str = "",
        start_date_time: ht.datetime | None = None,
        end_date_time: ht.datetime | None = None,
        duration: ht.timedelta | None = None,
        outcome: Outcome = Outcome.UNSPECIFIED,
        status: Status = Status.UNSPECIFIED,
        link: str = "",
        keywords: Iterable[str] | None = None,
        extension: Mapping[str, Any] | None = None,
        schema_id: str = "",
        error_information: ErrorInformation | None = None,
        conditions: Iterable[Condition] | None = None,
        measurements: Iterable[Measurement] | None = None,
        children: Iterable[Step] | None = None,
        path: Iterable[str] | None = None,
        path_ids: Iterable[str] | None = None,
        created_at: ht.datetime | None = None,
        updated_at: ht.datetime | None = None,
        created_by: str = "",
        updated_by: str = "",
    ) -> None:
        """Initialize a Step instance.

        Args:
            name: Human-readable name of the step.
            id (optional): Unique identifier for the step.
            parent_step_id (optional): ID of the parent step if this is a nested step.
            test_result_id (optional): ID of the test result this step belongs to.
            test_id (optional): ID or registered alias of the test associated with this
                step. Reads return the ID.
            test (optional): Test to find or create on create, or expand on read.
            step_type (optional): Free-form classification of the step.
            notes (optional): Additional notes about the step.
            start_date_time (optional): The start date and time of the step execution.
            end_date_time (optional): The end date and time of the step execution.
            duration (optional): The duration of the step execution.
            outcome (optional): The terminal outcome of the step.
            status (optional): The lifecycle status of the step.
            link (optional): A URI associated with the step.
            keywords (optional): Labels used to classify the step.
            extension (optional): Custom JSON data for the step.
            schema_id (optional): Schema that governs the extension. Reserved for
                future use.
            error_information (optional): Error details for the step.
            conditions (optional): Conditions created with the step.
            measurements (optional): Measurements created with the step.
            children (optional): Child steps created with the step.
            path (optional): Output only. The step-name path, including this step.
            path_ids (optional): Output only. The step-identifier path, including this step.
            created_at (optional): Output only. When the step was created.
            updated_at (optional): Output only. When the step was last updated.
            created_by (optional): Output only. Who created the step.
            updated_by (optional): Output only. Who last updated the step.
        """
        self.name = name
        self.id = id
        self.parent_step_id = parent_step_id
        self.test_result_id = test_result_id
        self.test_id = test_id
        self.test = test
        self.step_type = step_type
        self.notes = notes
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.duration = duration
        self.outcome = outcome
        self.status = status
        self.link = link
        self._keywords: MutableSequence[str] = list(keywords) if keywords is not None else []
        self._extension: MutableMapping[str, Any] = dict(extension) if extension is not None else {}
        self.schema_id = schema_id
        self.error_information = error_information
        self._conditions: MutableSequence[Condition] = (
            list(conditions) if conditions is not None else []
        )
        self._measurements: MutableSequence[Measurement] = (
            list(measurements) if measurements is not None else []
        )
        self._children: MutableSequence[Step] = list(children) if children is not None else []
        self._path: MutableSequence[str] = list(path) if path is not None else []
        self._path_ids: MutableSequence[str] = list(path_ids) if path_ids is not None else []
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.updated_by = updated_by

    @staticmethod
    def from_protobuf(step_proto: StepProto) -> "Step":
        """Create a Step instance from a protobuf Step message."""
        return Step(
            name=step_proto.name,
            id=step_proto.id,
            parent_step_id=step_proto.parent_step_id,
            test_result_id=step_proto.test_result_id,
            test_id=step_proto.test_id,
            test=Test.from_protobuf(step_proto.test) if step_proto.HasField("test") else None,
            step_type=step_proto.step_type,
            notes=step_proto.notes,
            start_date_time=timestamp_from_protobuf(step_proto, "start_date_time"),
            end_date_time=timestamp_from_protobuf(step_proto, "end_date_time"),
            duration=duration_from_protobuf(step_proto, "duration"),
            outcome=Outcome.from_protobuf(step_proto.outcome),
            status=Status.from_protobuf(step_proto.status),
            link=step_proto.link,
            keywords=step_proto.keywords,
            extension=extension_from_protobuf(step_proto.extension),
            schema_id=step_proto.schema_id,
            error_information=(
                ErrorInformation.from_protobuf(step_proto.error_information)
                if step_proto.HasField("error_information")
                else None
            ),
            conditions=[Condition.from_protobuf(condition) for condition in step_proto.conditions],
            measurements=[
                Measurement.from_protobuf(measurement) for measurement in step_proto.measurements
            ],
            children=[Step.from_protobuf(child) for child in step_proto.children],
            path=step_proto.path,
            path_ids=step_proto.path_ids,
            created_at=timestamp_from_protobuf(step_proto, "created_at"),
            updated_at=timestamp_from_protobuf(step_proto, "updated_at"),
            created_by=step_proto.created_by,
            updated_by=step_proto.updated_by,
        )

    def to_protobuf(self) -> StepProto:
        """Convert this Step to a protobuf Step message.

        Output-only fields, such as path and created_at, are not included.
        """
        return StepProto(
            name=self.name,
            id=self.id,
            parent_step_id=self.parent_step_id,
            test_result_id=self.test_result_id,
            test_id=self.test_id,
            test=self.test.to_protobuf() if self.test is not None else None,
            step_type=self.step_type,
            notes=self.notes,
            start_date_time=timestamp_to_protobuf(self.start_date_time),
            end_date_time=timestamp_to_protobuf(self.end_date_time),
            duration=duration_to_protobuf(self.duration),
            outcome=self.outcome.to_protobuf(),
            status=self.status.to_protobuf(),
            link=self.link,
            keywords=self.keywords,
            extension=extension_to_protobuf(self.extension),
            schema_id=self.schema_id,
            error_information=(
                self.error_information.to_protobuf() if self.error_information is not None else None
            ),
            conditions=[condition.to_protobuf() for condition in self.conditions],
            measurements=[measurement.to_protobuf() for measurement in self.measurements],
            children=[child.to_protobuf() for child in self.children],
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Step):
            return NotImplemented
        return (
            self.name == other.name
            and self.id == other.id
            and self.parent_step_id == other.parent_step_id
            and self.test_result_id == other.test_result_id
            and self.test_id == other.test_id
            and self.test == other.test
            and self.step_type == other.step_type
            and self.notes == other.notes
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.duration == other.duration
            and self.outcome == other.outcome
            and self.status == other.status
            and self.link == other.link
            and self.keywords == other.keywords
            and self.extension == other.extension
            and self.schema_id == other.schema_id
            and self.error_information == other.error_information
            and self.conditions == other.conditions
            and self.measurements == other.measurements
            and self.children == other.children
            and self.path == other.path
            and self.path_ids == other.path_ids
            and self.created_at == other.created_at
            and self.updated_at == other.updated_at
            and self.created_by == other.created_by
            and self.updated_by == other.updated_by
        )

    def __str__(self) -> str:
        """Return a string representation of the Step."""
        return str(self.to_protobuf())
