"""Test Result data type for the Data Store Client."""

from __future__ import annotations

from typing import Iterable, MutableMapping

import hightime as ht
from ni.datastore.grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.data.v1.data_store_pb2 import (
    Outcome,
    TestResult as TestResultProto,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_from_protobuf,
    hightime_datetime_to_protobuf,
)


class TestResult:
    """Information about a test result."""

    __slots__ = (
        "test_result_id",
        "uut_instance_id",
        "operator_id",
        "test_station_id",
        "test_description_id",
        "software_item_ids",
        "hardware_item_ids",
        "test_adapter_ids",
        "test_result_name",
        "_start_date_time",
        "_end_date_time",
        "_outcome",
        "link",
        "extensions",
        "schema_id",
    )

    @property
    def start_date_time(self) -> ht.datetime | None:
        """Get the start date and time of the test execution."""
        return self._start_date_time

    @property
    def end_date_time(self) -> ht.datetime | None:
        """Get the end date and time of the test execution."""
        return self._end_date_time

    @property
    def outcome(self) -> Outcome.ValueType:
        """Get the outcome of the test execution."""
        return self._outcome

    def __init__(
        self,
        *,
        test_result_id: str = "",
        uut_instance_id: str = "",
        operator_id: str = "",
        test_station_id: str = "",
        test_description_id: str = "",
        software_item_ids: Iterable[str] | None = None,
        hardware_item_ids: Iterable[str] | None = None,
        test_adapter_ids: Iterable[str] | None = None,
        test_result_name: str = "",
        link: str = "",
        extensions: MutableMapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a TestResult instance."""
        self.test_result_id = test_result_id
        self.uut_instance_id = uut_instance_id
        self.operator_id = operator_id
        self.test_station_id = test_station_id
        self.test_description_id = test_description_id
        self.software_item_ids: Iterable[str] = (
            software_item_ids if software_item_ids is not None else []
        )
        self.hardware_item_ids: Iterable[str] = (
            hardware_item_ids if hardware_item_ids is not None else []
        )
        self.test_adapter_ids: Iterable[str] = (
            test_adapter_ids if test_adapter_ids is not None else []
        )
        self.test_result_name = test_result_name
        self.link = link
        self.extensions: MutableMapping[str, str] = extensions if extensions is not None else {}
        self.schema_id = schema_id

        self._start_date_time: ht.datetime | None = None
        self._end_date_time: ht.datetime | None = None
        self._outcome: Outcome.ValueType = Outcome.OUTCOME_UNSPECIFIED

    @staticmethod
    def from_protobuf(test_result_proto: TestResultProto) -> "TestResult":
        """Create a TestResult instance from a protobuf TestResult message."""
        test_result = TestResult(
            test_result_id=test_result_proto.test_result_id,
            uut_instance_id=test_result_proto.uut_instance_id,
            operator_id=test_result_proto.operator_id,
            test_station_id=test_result_proto.test_station_id,
            test_description_id=test_result_proto.test_description_id,
            software_item_ids=test_result_proto.software_item_ids,
            hardware_item_ids=test_result_proto.hardware_item_ids,
            test_adapter_ids=test_result_proto.test_adapter_ids,
            test_result_name=test_result_proto.test_result_name,
            link=test_result_proto.link,
            schema_id=test_result_proto.schema_id,
        )
        test_result._start_date_time = (
            hightime_datetime_from_protobuf(test_result_proto.start_date_time)
            if test_result_proto.HasField("start_date_time")
            else None
        )
        test_result._end_date_time = (
            hightime_datetime_from_protobuf(test_result_proto.end_date_time)
            if test_result_proto.HasField("end_date_time")
            else None
        )
        test_result._outcome = test_result_proto.outcome
        populate_from_extension_value_message_map(
            test_result.extensions, test_result_proto.extensions
        )
        return test_result

    def to_protobuf(self) -> TestResultProto:
        """Convert this TestResult to a protobuf TestResult message."""
        test_result_proto = TestResultProto(
            test_result_id=self.test_result_id,
            uut_instance_id=self.uut_instance_id,
            operator_id=self.operator_id,
            test_station_id=self.test_station_id,
            test_description_id=self.test_description_id,
            software_item_ids=self.software_item_ids,
            hardware_item_ids=self.hardware_item_ids,
            test_adapter_ids=self.test_adapter_ids,
            test_result_name=self.test_result_name,
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
        )
        populate_extension_value_message_map(test_result_proto.extensions, self.extensions)
        return test_result_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, TestResult):
            return NotImplemented
        return (
            self.test_result_id == other.test_result_id
            and self.uut_instance_id == other.uut_instance_id
            and self.operator_id == other.operator_id
            and self.test_station_id == other.test_station_id
            and self.test_description_id == other.test_description_id
            and list(self.software_item_ids) == list(other.software_item_ids)
            and list(self.hardware_item_ids) == list(other.hardware_item_ids)
            and list(self.test_adapter_ids) == list(other.test_adapter_ids)
            and self.test_result_name == other.test_result_name
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.outcome == other.outcome
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the TestResult."""
        return str(self.to_protobuf())
