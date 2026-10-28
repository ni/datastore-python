"""Test Result data type for the V2 Data Store Client."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, MutableMapping, MutableSequence

import hightime as ht
from ni.measurements.data.v2.data_store_pb2 import TestResult as TestResultProto

from ni.datastore.data.v2._grpc_conversion import (
    duration_from_protobuf,
    duration_to_protobuf,
    extension_from_protobuf,
    extension_to_protobuf,
    timestamp_from_protobuf,
    timestamp_to_protobuf,
)
from ni.datastore.data.v2._types._error_information import ErrorInformation
from ni.datastore.data.v2._types._outcome import Outcome
from ni.datastore.data.v2._types._status import Status
from ni.datastore.data.v2._types._step import Step
from ni.datastore.metadata import (
    HardwareItem,
    Operator,
    SoftwareItem,
    TestAdapter,
    TestDescription,
    TestStation,
    Uut,
    UutInstance,
)


class TestResult:
    """Information about one execution of a test process.

    A test result records the UUT, operator, test station, and other metadata
    for a test run, along with its timing, status, and outcome. Steps, and the
    measurements and conditions they own, belong to a test result.
    """

    __slots__ = (
        "name",
        "id",
        "uut_instance_id",
        "uut_id",
        "operator_id",
        "test_station_id",
        "test_description_id",
        "uut_instance",
        "uut",
        "operator",
        "test_station",
        "test_description",
        "_software_item_ids",
        "_hardware_item_ids",
        "_test_adapter_ids",
        "_software_items",
        "_hardware_items",
        "_test_adapters",
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
        "_steps",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    @property
    def software_item_ids(self) -> MutableSequence[str]:
        """The software item IDs associated with the test result."""
        return self._software_item_ids

    @property
    def hardware_item_ids(self) -> MutableSequence[str]:
        """The hardware item IDs associated with the test result."""
        return self._hardware_item_ids

    @property
    def test_adapter_ids(self) -> MutableSequence[str]:
        """The test adapter IDs associated with the test result."""
        return self._test_adapter_ids

    @property
    def software_items(self) -> MutableSequence[SoftwareItem]:
        """Software items to find or create on create, or expand on read."""
        return self._software_items

    @property
    def hardware_items(self) -> MutableSequence[HardwareItem]:
        """Hardware items to find or create on create, or expand on read."""
        return self._hardware_items

    @property
    def test_adapters(self) -> MutableSequence[TestAdapter]:
        """Test adapters to find or create on create, or expand on read."""
        return self._test_adapters

    @property
    def steps(self) -> MutableSequence[Step]:
        """Steps created with the test result, or expand on read."""
        return self._steps

    @property
    def keywords(self) -> MutableSequence[str]:
        """Labels used to classify the test result."""
        return self._keywords

    @property
    def extension(self) -> MutableMapping[str, Any]:
        """Custom JSON data associated with the test result."""
        return self._extension

    def __init__(
        self,
        name: str,
        *,
        id: str = "",
        uut_instance_id: str = "",
        uut_id: str = "",
        operator_id: str = "",
        test_station_id: str = "",
        test_description_id: str = "",
        uut_instance: UutInstance | None = None,
        uut: Uut | None = None,
        operator: Operator | None = None,
        test_station: TestStation | None = None,
        test_description: TestDescription | None = None,
        software_item_ids: Iterable[str] | None = None,
        hardware_item_ids: Iterable[str] | None = None,
        test_adapter_ids: Iterable[str] | None = None,
        software_items: Iterable[SoftwareItem] | None = None,
        hardware_items: Iterable[HardwareItem] | None = None,
        test_adapters: Iterable[TestAdapter] | None = None,
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
        steps: Iterable[Step] | None = None,
        created_at: ht.datetime | None = None,
        updated_at: ht.datetime | None = None,
        created_by: str = "",
        updated_by: str = "",
    ) -> None:
        """Initialize a TestResult instance.

        Args:
            name: Human-readable name for the test result.
            id (optional): Unique identifier for the test result.
            uut_instance_id (optional): ID or registered alias of the UUT instance that
                was tested. Reads return the ID.
            uut_id (optional): ID of the UUT product definition.
            operator_id (optional): ID or registered alias of the operator who ran the
                test. Reads return the ID.
            test_station_id (optional): ID or registered alias of the test station used.
                Reads return the ID.
            test_description_id (optional): ID or registered alias of the test
                description executed. Reads return the ID.
            uut_instance (optional): UUT instance to find or create on create, or expand
                on read.
            uut (optional): UUT to find or create on create, or expand on read.
            operator (optional): Operator to find or create on create, or expand on read.
            test_station (optional): Test station to find or create on create, or expand
                on read.
            test_description (optional): Test description to find or create on create, or
                expand on read.
            software_item_ids (optional): IDs of software items used in the test.
            hardware_item_ids (optional): IDs of hardware items used in the test.
            test_adapter_ids (optional): IDs of test adapters used in the test.
            software_items (optional): Software items to find or create on create.
            hardware_items (optional): Hardware items to find or create on create.
            test_adapters (optional): Test adapters to find or create on create.
            start_date_time (optional): The start date and time of the test execution.
            end_date_time (optional): The end date and time of the test execution.
            duration (optional): The duration of the test execution.
            outcome (optional): The terminal outcome of the test execution.
            status (optional): The lifecycle status of the test execution.
            link (optional): A URI associated with the test result.
            keywords (optional): Labels used to classify the test result.
            extension (optional): Custom JSON data for the test result.
            schema_id (optional): Schema that governs the extension. Reserved for
                future use.
            error_information (optional): Error details for the test result.
            steps (optional): Steps created with the test result.
            created_at (optional): Output only. When the test result was created.
            updated_at (optional): Output only. When the test result was last updated.
            created_by (optional): Output only. Who created the test result.
            updated_by (optional): Output only. Who last updated the test result.
        """
        self.name = name
        self.id = id
        self.uut_instance_id = uut_instance_id
        self.uut_id = uut_id
        self.operator_id = operator_id
        self.test_station_id = test_station_id
        self.test_description_id = test_description_id
        self.uut_instance = uut_instance
        self.uut = uut
        self.operator = operator
        self.test_station = test_station
        self.test_description = test_description
        self._software_item_ids: MutableSequence[str] = (
            list(software_item_ids) if software_item_ids is not None else []
        )
        self._hardware_item_ids: MutableSequence[str] = (
            list(hardware_item_ids) if hardware_item_ids is not None else []
        )
        self._test_adapter_ids: MutableSequence[str] = (
            list(test_adapter_ids) if test_adapter_ids is not None else []
        )
        self._software_items: MutableSequence[SoftwareItem] = (
            list(software_items) if software_items is not None else []
        )
        self._hardware_items: MutableSequence[HardwareItem] = (
            list(hardware_items) if hardware_items is not None else []
        )
        self._test_adapters: MutableSequence[TestAdapter] = (
            list(test_adapters) if test_adapters is not None else []
        )
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
        self._steps: MutableSequence[Step] = list(steps) if steps is not None else []
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.updated_by = updated_by

    @staticmethod
    def from_protobuf(test_result_proto: TestResultProto) -> "TestResult":
        """Create a TestResult instance from a protobuf TestResult message."""
        proto = test_result_proto
        return TestResult(
            name=proto.name,
            id=proto.id,
            uut_instance_id=proto.uut_instance_id,
            uut_id=proto.uut_id,
            operator_id=proto.operator_id,
            test_station_id=proto.test_station_id,
            test_description_id=proto.test_description_id,
            uut_instance=(
                UutInstance.from_protobuf(proto.uut_instance)
                if proto.HasField("uut_instance")
                else None
            ),
            uut=Uut.from_protobuf(proto.uut) if proto.HasField("uut") else None,
            operator=Operator.from_protobuf(proto.operator) if proto.HasField("operator") else None,
            test_station=(
                TestStation.from_protobuf(proto.test_station)
                if proto.HasField("test_station")
                else None
            ),
            test_description=(
                TestDescription.from_protobuf(proto.test_description)
                if proto.HasField("test_description")
                else None
            ),
            software_item_ids=proto.software_item_ids,
            hardware_item_ids=proto.hardware_item_ids,
            test_adapter_ids=proto.test_adapter_ids,
            software_items=[SoftwareItem.from_protobuf(item) for item in proto.software_items],
            hardware_items=[HardwareItem.from_protobuf(item) for item in proto.hardware_items],
            test_adapters=[TestAdapter.from_protobuf(adapter) for adapter in proto.test_adapters],
            start_date_time=timestamp_from_protobuf(proto, "start_date_time"),
            end_date_time=timestamp_from_protobuf(proto, "end_date_time"),
            duration=duration_from_protobuf(proto, "duration"),
            outcome=Outcome.from_protobuf(proto.outcome),
            status=Status.from_protobuf(proto.status),
            link=proto.link,
            keywords=proto.keywords,
            extension=extension_from_protobuf(proto.extension),
            schema_id=proto.schema_id,
            error_information=(
                ErrorInformation.from_protobuf(proto.error_information)
                if proto.HasField("error_information")
                else None
            ),
            steps=[Step.from_protobuf(step) for step in proto.steps],
            created_at=timestamp_from_protobuf(proto, "created_at"),
            updated_at=timestamp_from_protobuf(proto, "updated_at"),
            created_by=proto.created_by,
            updated_by=proto.updated_by,
        )

    def to_protobuf(self) -> TestResultProto:
        """Convert this TestResult to a protobuf TestResult message.

        Output-only fields, such as created_at, are not included.
        """
        return TestResultProto(
            name=self.name,
            id=self.id,
            uut_instance_id=self.uut_instance_id,
            uut_id=self.uut_id,
            operator_id=self.operator_id,
            test_station_id=self.test_station_id,
            test_description_id=self.test_description_id,
            uut_instance=_optional_to_protobuf(self.uut_instance),
            uut=_optional_to_protobuf(self.uut),
            operator=_optional_to_protobuf(self.operator),
            test_station=_optional_to_protobuf(self.test_station),
            test_description=_optional_to_protobuf(self.test_description),
            software_item_ids=self.software_item_ids,
            hardware_item_ids=self.hardware_item_ids,
            test_adapter_ids=self.test_adapter_ids,
            software_items=[item.to_protobuf() for item in self.software_items],
            hardware_items=[item.to_protobuf() for item in self.hardware_items],
            test_adapters=[adapter.to_protobuf() for adapter in self.test_adapters],
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
            steps=[step.to_protobuf() for step in self.steps],
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, TestResult):
            return NotImplemented
        return (
            self.name == other.name
            and self.id == other.id
            and self.uut_instance_id == other.uut_instance_id
            and self.uut_id == other.uut_id
            and self.operator_id == other.operator_id
            and self.test_station_id == other.test_station_id
            and self.test_description_id == other.test_description_id
            and self.uut_instance == other.uut_instance
            and self.uut == other.uut
            and self.operator == other.operator
            and self.test_station == other.test_station
            and self.test_description == other.test_description
            and self.software_item_ids == other.software_item_ids
            and self.hardware_item_ids == other.hardware_item_ids
            and self.test_adapter_ids == other.test_adapter_ids
            and self.software_items == other.software_items
            and self.hardware_items == other.hardware_items
            and self.test_adapters == other.test_adapters
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
            and self.steps == other.steps
            and self.created_at == other.created_at
            and self.updated_at == other.updated_at
            and self.created_by == other.created_by
            and self.updated_by == other.updated_by
        )

    def __str__(self) -> str:
        """Return a string representation of the TestResult."""
        return str(self.to_protobuf())


def _optional_to_protobuf(item: Any) -> Any:
    return item.to_protobuf() if item is not None else None
