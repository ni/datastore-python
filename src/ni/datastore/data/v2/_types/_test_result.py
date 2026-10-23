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
        "_software_item_ids",
        "_hardware_item_ids",
        "_test_adapter_ids",
        "start_date_time",
        "end_date_time",
        "duration",
        "outcome",
        "status",
        "link",
        "_keywords",
        "_extension",
        "error_information",
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
        software_item_ids: Iterable[str] | None = None,
        hardware_item_ids: Iterable[str] | None = None,
        test_adapter_ids: Iterable[str] | None = None,
        start_date_time: ht.datetime | None = None,
        end_date_time: ht.datetime | None = None,
        duration: ht.timedelta | None = None,
        outcome: Outcome = Outcome.UNSPECIFIED,
        status: Status = Status.UNSPECIFIED,
        link: str = "",
        keywords: Iterable[str] | None = None,
        extension: Mapping[str, Any] | None = None,
        error_information: ErrorInformation | None = None,
        created_at: ht.datetime | None = None,
        updated_at: ht.datetime | None = None,
        created_by: str = "",
        updated_by: str = "",
    ) -> None:
        """Initialize a TestResult instance.

        Args:
            name: Human-readable name for the test result.
            id (optional): Unique identifier for the test result.
            uut_instance_id (optional): ID or alias of the UUT instance that was tested.
            uut_id (optional): ID of the UUT product definition.
            operator_id (optional): ID or alias of the operator who ran the test.
            test_station_id (optional): ID or alias of the test station used.
            test_description_id (optional): ID or alias of the test description executed.
            software_item_ids (optional): IDs of software items used in the test.
            hardware_item_ids (optional): IDs of hardware items used in the test.
            test_adapter_ids (optional): IDs of test adapters used in the test.
            start_date_time (optional): The start date and time of the test execution.
            end_date_time (optional): The end date and time of the test execution.
            duration (optional): The duration of the test execution.
            outcome (optional): The terminal outcome of the test execution.
            status (optional): The lifecycle status of the test execution.
            link (optional): A URI associated with the test result.
            keywords (optional): Labels used to classify the test result.
            extension (optional): Custom JSON data for the test result.
            error_information (optional): Error details for the test result.
            created_at (optional): Output only. When the service created the test result.
            updated_at (optional): Output only. When the service last updated the test result.
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
        self._software_item_ids: MutableSequence[str] = (
            list(software_item_ids) if software_item_ids is not None else []
        )
        self._hardware_item_ids: MutableSequence[str] = (
            list(hardware_item_ids) if hardware_item_ids is not None else []
        )
        self._test_adapter_ids: MutableSequence[str] = (
            list(test_adapter_ids) if test_adapter_ids is not None else []
        )
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.duration = duration
        self.outcome = outcome
        self.status = status
        self.link = link
        self._keywords: MutableSequence[str] = list(keywords) if keywords is not None else []
        self._extension: MutableMapping[str, Any] = dict(extension) if extension is not None else {}
        self.error_information = error_information
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.updated_by = updated_by

    @staticmethod
    def from_protobuf(test_result_proto: TestResultProto) -> "TestResult":
        """Create a TestResult instance from a protobuf TestResult message."""
        return TestResult(
            name=test_result_proto.name,
            id=test_result_proto.id,
            uut_instance_id=test_result_proto.uut_instance_id,
            uut_id=test_result_proto.uut_id,
            operator_id=test_result_proto.operator_id,
            test_station_id=test_result_proto.test_station_id,
            test_description_id=test_result_proto.test_description_id,
            software_item_ids=test_result_proto.software_item_ids,
            hardware_item_ids=test_result_proto.hardware_item_ids,
            test_adapter_ids=test_result_proto.test_adapter_ids,
            start_date_time=timestamp_from_protobuf(test_result_proto, "start_date_time"),
            end_date_time=timestamp_from_protobuf(test_result_proto, "end_date_time"),
            duration=duration_from_protobuf(test_result_proto, "duration"),
            outcome=Outcome.from_protobuf(test_result_proto.outcome),
            status=Status.from_protobuf(test_result_proto.status),
            link=test_result_proto.link,
            keywords=test_result_proto.keywords,
            extension=extension_from_protobuf(test_result_proto.extension),
            error_information=(
                ErrorInformation.from_protobuf(test_result_proto.error_information)
                if test_result_proto.HasField("error_information")
                else None
            ),
            created_at=timestamp_from_protobuf(test_result_proto, "created_at"),
            updated_at=timestamp_from_protobuf(test_result_proto, "updated_at"),
            created_by=test_result_proto.created_by,
            updated_by=test_result_proto.updated_by,
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
            software_item_ids=self.software_item_ids,
            hardware_item_ids=self.hardware_item_ids,
            test_adapter_ids=self.test_adapter_ids,
            start_date_time=timestamp_to_protobuf(self.start_date_time),
            end_date_time=timestamp_to_protobuf(self.end_date_time),
            duration=duration_to_protobuf(self.duration),
            outcome=self.outcome.to_protobuf(),
            status=self.status.to_protobuf(),
            link=self.link,
            keywords=self.keywords,
            extension=extension_to_protobuf(self.extension),
            error_information=(
                self.error_information.to_protobuf() if self.error_information is not None else None
            ),
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
            and self.software_item_ids == other.software_item_ids
            and self.hardware_item_ids == other.hardware_item_ids
            and self.test_adapter_ids == other.test_adapter_ids
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.duration == other.duration
            and self.outcome == other.outcome
            and self.status == other.status
            and self.link == other.link
            and self.keywords == other.keywords
            and self.extension == other.extension
            and self.error_information == other.error_information
            and self.created_at == other.created_at
            and self.updated_at == other.updated_at
            and self.created_by == other.created_by
            and self.updated_by == other.updated_by
        )

    def __str__(self) -> str:
        """Return a string representation of the TestResult."""
        return str(self.to_protobuf())
