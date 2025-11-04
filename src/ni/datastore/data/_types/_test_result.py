"""Test Result data type for the Data Store Client."""

from __future__ import annotations

from typing import Iterable, Mapping, MutableMapping, MutableSequence

import hightime as ht
from ni.datastore.metadata._grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    TestResult as TestResultProto,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_from_protobuf,
    hightime_datetime_to_protobuf,
)


class TestResult:
    """Information about a test result.

    Represents the results of executing a test sequence, including metadata
    about the execution environment (UUT, operator, test station), test
    execution time, outcome, and associations with hardware/software components
    and test adapters. Each step which references measurement data and
    conditions is associated with a test result.
    """

    __slots__ = (
        "id",
        "uut_instance_id",
        "operator_id",
        "test_station_id",
        "test_description_id",
        "_software_item_ids",
        "_hardware_item_ids",
        "_test_adapter_ids",
        "name",
        "start_date_time",
        "end_date_time",
        "outcome",
        "link",
        "_extensions",
        "schema_id",
        "error_information",
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
    def extensions(self) -> MutableMapping[str, str]:
        """The extensions of the test result."""
        return self._extensions

    def __init__(
        self,
        *,
        id: str = "",
        uut_instance_id: str = "",
        operator_id: str = "",
        test_station_id: str = "",
        test_description_id: str = "",
        software_item_ids: Iterable[str] | None = None,
        hardware_item_ids: Iterable[str] | None = None,
        test_adapter_ids: Iterable[str] | None = None,
        name: str = "",
        start_date_time: ht.datetime | None = None,
        end_date_time: ht.datetime | None = None,
        outcome: Outcome.ValueType = Outcome.OUTCOME_UNSPECIFIED,
        link: str = "",
        extensions: Mapping[str, str] | None = None,
        schema_id: str = "",
        error_information: ErrorInformation | None = None,
    ) -> None:
        """Initialize a TestResult instance.

        Args:
            id: Unique identifier for the test result.
            uut_instance_id: ID of the UUT instance that was tested.
            operator_id: ID of the operator who ran the test.
            test_station_id: ID of the test station used.
            test_description_id: ID of the test description that was executed.
            software_item_ids: IDs of software items used in the test.
            hardware_item_ids: IDs of hardware items used in the test.
            test_adapter_ids: IDs of test adapters used in the test.
            name: Human-readable name for the test result.
            start_date_time: The start date and time of the test execution.
            end_date_time: The end date and time of the test execution.
            outcome: The outcome of the test execution (PASSED, FAILED,
                INDETERMINATE, or UNSPECIFIED).
            link: Optional link to external resources for this test result.
            extensions: Additional custom metadata as key-value pairs.
            schema_id: ID of the extension schema for validating extensions.
            error_information: Error or exception information in case of
                test result failure.
        """
        self.id = id
        self.uut_instance_id = uut_instance_id
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
        self.name = name
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.outcome = outcome
        self.link = link
        self._extensions: MutableMapping[str, str] = (
            dict(extensions) if extensions is not None else {}
        )
        self.schema_id = schema_id
        self.error_information = error_information

    @staticmethod
    def from_protobuf(test_result_proto: TestResultProto) -> "TestResult":
        """Create a TestResult instance from a protobuf TestResult message."""
        test_result = TestResult(
            id=test_result_proto.id,
            uut_instance_id=test_result_proto.uut_instance_id,
            operator_id=test_result_proto.operator_id,
            test_station_id=test_result_proto.test_station_id,
            test_description_id=test_result_proto.test_description_id,
            software_item_ids=test_result_proto.software_item_ids,
            hardware_item_ids=test_result_proto.hardware_item_ids,
            test_adapter_ids=test_result_proto.test_adapter_ids,
            name=test_result_proto.name,
            start_date_time=(
                hightime_datetime_from_protobuf(test_result_proto.start_date_time)
                if test_result_proto.HasField("start_date_time")
                else None
            ),
            end_date_time=(
                hightime_datetime_from_protobuf(test_result_proto.end_date_time)
                if test_result_proto.HasField("end_date_time")
                else None
            ),
            outcome=test_result_proto.outcome,
            link=test_result_proto.link,
            schema_id=test_result_proto.schema_id,
            error_information=(
                test_result_proto.error_information
                if test_result_proto.HasField("error_information")
                else None
            ),
        )
        populate_from_extension_value_message_map(
            test_result.extensions, test_result_proto.extensions
        )
        return test_result

    def to_protobuf(self) -> TestResultProto:
        """Convert this TestResult to a protobuf TestResult message."""
        test_result_proto = TestResultProto(
            id=self.id,
            uut_instance_id=self.uut_instance_id,
            operator_id=self.operator_id,
            test_station_id=self.test_station_id,
            test_description_id=self.test_description_id,
            software_item_ids=self.software_item_ids,
            hardware_item_ids=self.hardware_item_ids,
            test_adapter_ids=self.test_adapter_ids,
            name=self.name,
            start_date_time=(
                hightime_datetime_to_protobuf(self.start_date_time)
                if self.start_date_time
                else None
            ),
            end_date_time=(
                hightime_datetime_to_protobuf(self.end_date_time) if self.end_date_time else None
            ),
            outcome=self.outcome,
            link=self.link,
            schema_id=self.schema_id,
            error_information=self.error_information,
        )
        populate_extension_value_message_map(test_result_proto.extensions, self.extensions)
        return test_result_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, TestResult):
            return NotImplemented
        return (
            self.id == other.id
            and self.uut_instance_id == other.uut_instance_id
            and self.operator_id == other.operator_id
            and self.test_station_id == other.test_station_id
            and self.test_description_id == other.test_description_id
            and self.software_item_ids == other.software_item_ids
            and self.hardware_item_ids == other.hardware_item_ids
            and self.test_adapter_ids == other.test_adapter_ids
            and self.name == other.name
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.outcome == other.outcome
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
            and self.error_information == other.error_information
        )

    def __str__(self) -> str:
        """Return a string representation of the TestResult."""
        return str(self.to_protobuf())
