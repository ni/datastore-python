"""Data types for the Data Store Client."""

from __future__ import annotations

from typing import Iterable, MutableMapping

from hightime import datetime as hightime_datetime
from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    PublishedCondition,
    PublishedMeasurement as PublishedMeasurementProto,
    Step as StepProto,
    TestResult as TestResultProto,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import ExtensionValue
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
    def start_date_time(self) -> hightime_datetime | None:
        """Get the start date and time of the step execution."""
        return self._start_date_time

    @property
    def end_date_time(self) -> hightime_datetime | None:
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
        extensions: MutableMapping[str, ExtensionValue] | None = None,
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
        self.extensions: MutableMapping[str, ExtensionValue] = (
            extensions if extensions is not None else {}
        )
        self.schema_id = schema_id

        self._start_date_time: hightime_datetime | None = None
        self._end_date_time: hightime_datetime | None = None

    @staticmethod
    def from_protobuf(step: StepProto) -> "Step":
        """Create a Step instance from a protobuf Step message."""
        converted_step = Step(
            step_id=step.step_id,
            parent_step_id=step.parent_step_id,
            test_result_id=step.test_result_id,
            test_id=step.test_id,
            step_name=step.step_name,
            step_type=step.step_type,
            notes=step.notes,
            link=step.link,
            extensions=step.extensions,
            schema_id=step.schema_id,
        )
        converted_step._start_date_time = (
            hightime_datetime_from_protobuf(step.start_date_time)
            if step.HasField("start_date_time")
            else None
        )
        converted_step._end_date_time = (
            hightime_datetime_from_protobuf(step.end_date_time)
            if step.HasField("end_date_time")
            else None
        )
        return converted_step

    def to_protobuf(self) -> StepProto:
        """Convert this Step to a protobuf Step message."""
        return StepProto(
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
            extensions=self.extensions,
            schema_id=self.schema_id,
        )

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
        "outcome",
        "link",
        "extensions",
        "schema_id",
    )

    @property
    def start_date_time(self) -> hightime_datetime | None:
        """Get the start date and time of the test execution."""
        return self._start_date_time

    @property
    def end_date_time(self) -> hightime_datetime | None:
        """Get the end date and time of the test execution."""
        return self._end_date_time

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
        outcome: Outcome.ValueType = Outcome.OUTCOME_UNSPECIFIED,
        link: str = "",
        extensions: MutableMapping[str, ExtensionValue] | None = None,
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
        self.outcome = outcome
        self.link = link
        self.extensions: MutableMapping[str, ExtensionValue] = (
            extensions if extensions is not None else {}
        )
        self.schema_id = schema_id

        self._start_date_time: hightime_datetime | None = None
        self._end_date_time: hightime_datetime | None = None

    @staticmethod
    def from_protobuf(test_result: TestResultProto) -> "TestResult":
        """Create a TestResult instance from a protobuf TestResult message."""
        converted_test_result = TestResult(
            test_result_id=test_result.test_result_id,
            uut_instance_id=test_result.uut_instance_id,
            operator_id=test_result.operator_id,
            test_station_id=test_result.test_station_id,
            test_description_id=test_result.test_description_id,
            software_item_ids=test_result.software_item_ids,
            hardware_item_ids=test_result.hardware_item_ids,
            test_adapter_ids=test_result.test_adapter_ids,
            test_result_name=test_result.test_result_name,
            outcome=test_result.outcome,
            link=test_result.link,
            extensions=test_result.extensions,
            schema_id=test_result.schema_id,
        )
        converted_test_result._start_date_time = (
            hightime_datetime_from_protobuf(test_result.start_date_time)
            if test_result.HasField("start_date_time")
            else None
        )
        converted_test_result._end_date_time = (
            hightime_datetime_from_protobuf(test_result.end_date_time)
            if test_result.HasField("end_date_time")
            else None
        )
        return converted_test_result

    def to_protobuf(self) -> TestResultProto:
        """Convert this TestResult to a protobuf TestResult message."""
        return TestResultProto(
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
            outcome=self.outcome if self.outcome is not None else Outcome.OUTCOME_UNSPECIFIED,
            link=self.link,
            extensions=self.extensions,
            schema_id=self.schema_id,
        )

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
            and self.software_item_ids == other.software_item_ids
            and self.hardware_item_ids == other.hardware_item_ids
            and self.test_adapter_ids == other.test_adapter_ids
            and self.test_result_name == other.test_result_name
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.outcome == other.outcome
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )


class PublishedMeasurement:
    """Information about a measurement published to the data store."""

    __slots__ = (
        "moniker",
        "published_conditions",
        "published_measurement_id",
        "test_result_id",
        "step_id",
        "software_item_ids",
        "hardware_item_ids",
        "test_adapter_ids",
        "measurement_name",
        "data_type",
        "measurement_notes",
        "start_date_time",
        "end_date_time",
        "outcome",
        "parametric_index",
        "error_information",
    )

    def __init__(
        self,
        *,
        moniker: Moniker | None = None,
        published_conditions: Iterable[PublishedCondition] | None = None,
        published_measurement_id: str = "",
        test_result_id: str = "",
        step_id: str = "",
        software_item_ids: Iterable[str] | None = None,
        hardware_item_ids: Iterable[str] | None = None,
        test_adapter_ids: Iterable[str] | None = None,
        measurement_name: str = "",
        data_type: str = "",
        measurement_notes: str = "",
        start_date_time: hightime_datetime | None = None,
        end_date_time: hightime_datetime | None = None,
        outcome: Outcome.ValueType = Outcome.OUTCOME_UNSPECIFIED,
        parametric_index: int = 0,
        error_information: ErrorInformation | None = None,
    ) -> None:
        """Initialize a PublishedMeasurement instance."""
        self.moniker = moniker
        self.published_conditions: Iterable[PublishedCondition] = (
            published_conditions if published_conditions is not None else []
        )
        self.published_measurement_id = published_measurement_id
        self.test_result_id = test_result_id
        self.step_id = step_id
        self.software_item_ids: Iterable[str] = (
            software_item_ids if software_item_ids is not None else []
        )
        self.hardware_item_ids: Iterable[str] = (
            hardware_item_ids if hardware_item_ids is not None else []
        )
        self.test_adapter_ids: Iterable[str] = (
            test_adapter_ids if test_adapter_ids is not None else []
        )
        self.measurement_name = measurement_name
        self.data_type = data_type
        self.measurement_notes = measurement_notes
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.outcome = outcome
        self.parametric_index = parametric_index
        self.error_information = error_information

    @staticmethod
    def from_protobuf(published_measurement: PublishedMeasurementProto) -> "PublishedMeasurement":
        """Create a PublishedMeasurement instance from a protobuf PublishedMeasurement message."""
        return PublishedMeasurement(
            moniker=(
                published_measurement.moniker if published_measurement.HasField("moniker") else None
            ),
            published_conditions=published_measurement.published_conditions,
            published_measurement_id=published_measurement.published_measurement_id,
            test_result_id=published_measurement.test_result_id,
            step_id=published_measurement.step_id,
            software_item_ids=published_measurement.software_item_ids,
            hardware_item_ids=published_measurement.hardware_item_ids,
            test_adapter_ids=published_measurement.test_adapter_ids,
            measurement_name=published_measurement.measurement_name,
            data_type=published_measurement.data_type,
            measurement_notes=published_measurement.measurement_notes,
            start_date_time=(
                hightime_datetime_from_protobuf(published_measurement.start_date_time)
                if published_measurement.HasField("start_date_time")
                else None
            ),
            end_date_time=(
                hightime_datetime_from_protobuf(published_measurement.end_date_time)
                if published_measurement.HasField("end_date_time")
                else None
            ),
            outcome=published_measurement.outcome,
            parametric_index=published_measurement.parametric_index,
            error_information=(
                published_measurement.error_information
                if published_measurement.HasField("error_information")
                else None
            ),
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, PublishedMeasurement):
            return NotImplemented
        return (
            self.moniker == other.moniker
            and self.published_conditions == other.published_conditions
            and self.published_measurement_id == other.published_measurement_id
            and self.test_result_id == other.test_result_id
            and self.step_id == other.step_id
            and self.software_item_ids == other.software_item_ids
            and self.hardware_item_ids == other.hardware_item_ids
            and self.test_adapter_ids == other.test_adapter_ids
            and self.measurement_name == other.measurement_name
            and self.data_type == other.data_type
            and self.measurement_notes == other.measurement_notes
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.outcome == other.outcome
            and self.parametric_index == other.parametric_index
            and self.error_information == other.error_information
        )
