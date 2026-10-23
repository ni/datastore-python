"""Data store client for publishing and reading data with NI Data Store Service V2."""

from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping, Sequence
from types import TracebackType
from typing import Any, cast, overload, Type, TYPE_CHECKING, TypeVar

import hightime as ht
from google.protobuf import json_format
from google.protobuf.field_mask_pb2 import FieldMask
from grpc import Channel
from ni.measurementlink.discovery.v1.client import DiscoveryClient
from ni.measurements.data.v2.client import DataStoreClient as DataStoreServiceClient
from ni.measurements.data.v2.data_store_pb2 import (
    Measurement as MeasurementProto,
    Step as StepProto,
    TestResult as TestResultProto,
)
from ni.measurements.data.v2.data_store_service_pb2 import (
    AddConditionRequest,
    CreateMeasurementRequest,
    CreateStepRequest,
    CreateTestResultRequest,
    GetMeasurementRequest,
    GetStepRequest,
    GetTestResultRequest,
    QueryMeasurementsRequest,
    QueryStepsRequest,
    QueryTestResultsRequest,
    ReadMeasurementValuesRequest,
    UpdateMeasurementRequest,
    UpdateStepRequest,
    UpdateTestResultRequest,
)
from ni.protobuf.types.precision_duration_conversion import hightime_timedelta_to_protobuf
from ni.protobuf.types.precision_timestamp_conversion import hightime_datetime_to_protobuf
from ni_grpc_extensions.channelpool import GrpcChannelPool

from ni.datastore.data.v2._grpc_conversion import (
    convert_measurement_value_from_protobuf,
    populate_measurement_value,
)
from ni.datastore.data.v2._types._condition import Condition
from ni.datastore.data.v2._types._error_information import ErrorInformation
from ni.datastore.data.v2._types._measurement import Measurement
from ni.datastore.data.v2._types._outcome import Outcome
from ni.datastore.data.v2._types._step import Step
from ni.datastore.data.v2._types._test_result import TestResult

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

TRead = TypeVar("TRead")


class DataStoreClient:
    """Data store client for publishing and reading data with the V2 service."""

    __slots__ = ("_closed", "_data_store_client")

    _DATA_STORE_CLIENT_CLOSED_ERROR = (
        "This DataStoreClient has been closed. Create a new DataStoreClient for further "
        "interaction with the data store."
    )

    _closed: bool
    _data_store_client: DataStoreServiceClient

    def __init__(
        self,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel: Channel | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
    ) -> None:
        """Initialize the DataStoreClient.

        Args:
            discovery_client: An optional discovery client (recommended).

            grpc_channel: An optional data store gRPC channel. Providing this channel will bypass
                discovery service resolution of the data store.

            grpc_channel_pool: An optional gRPC channel pool (recommended).
        """
        self._closed = False
        self._data_store_client = DataStoreServiceClient(
            discovery_client=discovery_client,
            grpc_channel=grpc_channel,
            grpc_channel_pool=grpc_channel_pool,
        )

    def __enter__(self) -> Self:
        """Enter the runtime context of the data store client."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the runtime context of the data store client."""
        self.close()

    def close(self) -> None:
        """Close the data store client and clean up resources that it owns."""
        self._closed = True
        self._data_store_client.close()

    def create_test_result(self, test_result: TestResult) -> str:
        """Create a test result.

        Args:
            test_result: The metadata of the test result to be created.

        Returns:
            str: The test result ID. Generated if not specified.
        """
        create_request = CreateTestResultRequest(test_result=test_result.to_protobuf())
        return self._get_data_store_client().create_test_result(create_request).id

    def create_step(self, step: Step) -> str:
        """Create a step, including any conditions on the step.

        Args:
            step: The metadata of the step to be created.

        Returns:
            str: The step ID. Generated if not specified.
        """
        create_request = CreateStepRequest(step=step.to_protobuf())
        return self._get_data_store_client().create_step(create_request).id

    def add_condition(self, step_id: str, condition: Condition) -> Step:
        """Add a condition to a step, replacing any condition with the same name.

        Args:
            step_id: The ID of the step that owns the condition.

            condition: The condition to add.

        Returns:
            Step: The updated step.
        """
        add_request = AddConditionRequest(step_id=step_id, condition=condition.to_protobuf())
        return Step.from_protobuf(self._get_data_store_client().add_condition(add_request).step)

    def create_measurement(
        self,
        name: str,
        value: object,
        step_id: str,
        *,
        units: str = "",
        notes: str = "",
        start_date_time: ht.datetime | None = None,
        end_date_time: ht.datetime | None = None,
        duration: ht.timedelta | None = None,
        outcome: Outcome = Outcome.UNSPECIFIED,
        error_information: ErrorInformation | None = None,
        software_item_ids: Iterable[str] = (),
        hardware_item_ids: Iterable[str] = (),
        test_adapter_ids: Iterable[str] = (),
    ) -> str:
        """Create a measurement associated with a test step.

        Args:
            name: The name used for grouping conceptually alike measurements.

            value: The measured value. Supported types are bool, int, float, str,
                Scalar, Vector, iterables of scalar values, AnalogWaveform,
                ComplexWaveform, Spectrum, DigitalWaveform, XYData, and JSON
                mappings.

            step_id: The ID of the step that owns the measurement.

            units: Engineering units of the value.

            notes: Any notes to associate with the measurement.

            start_date_time: The start time of the measurement.

            end_date_time: The end time of the measurement.

            duration: The duration of the measurement.

            outcome: The outcome of the measurement.

            error_information: Error details for the measurement.

            software_item_ids: The software item IDs for the measurement. These
                must already be linked to the test result.

            hardware_item_ids: The hardware item IDs for the measurement. These
                must already be linked to the test result.

            test_adapter_ids: The test adapter IDs for the measurement. These
                must already be linked to the test result.

        Returns:
            str: The measurement ID.
        """
        measurement = Measurement(
            name=name,
            step_id=step_id,
            units=units,
            notes=notes,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            duration=duration,
            outcome=outcome,
            error_information=error_information,
            software_item_ids=software_item_ids,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
        ).to_protobuf()
        populate_measurement_value(measurement.value, value)
        create_request = CreateMeasurementRequest(measurement=measurement)
        return self._get_data_store_client().create_measurement(create_request).id

    @overload
    def read_measurement_value(
        self,
        read_source: Measurement,
        expected_type: Type[TRead],
    ) -> TRead: ...

    @overload
    def read_measurement_value(
        self,
        read_source: Measurement,
    ) -> object: ...

    def read_measurement_value(
        self,
        read_source: Measurement,
        expected_type: Type[TRead] | None = None,
    ) -> TRead | object:
        """Read the value of a measurement.

        Args:
            read_source: The measurement to read. Only its id is used.

            expected_type: Optional type to validate the returned data against.

        Returns:
            The value converted to a Python or nitypes value.

        Raises:
            TypeError: If expected_type is provided and the actual data type
                doesn't match.
        """
        read_request = ReadMeasurementValuesRequest(
            measurement_id=read_source.id, read_mask=FieldMask(paths=["value"])
        )
        response = self._get_data_store_client().read_measurement_values(read_request)
        read_value = convert_measurement_value_from_protobuf(response.value)
        if expected_type is not None and not isinstance(read_value, expected_type):
            raise TypeError(f"Expected type {expected_type}, got {type(read_value)}")
        return read_value

    def get_test_result(
        self, test_result_id: str, *, read_fields: Iterable[str] = ()
    ) -> TestResult:
        """Get the test result with the given ID.

        Args:
            test_result_id: The ID of the test result.

            read_fields: Optional field names to return. All fields are returned
                when empty.

        Returns:
            TestResult: The requested test result.
        """
        get_request = GetTestResultRequest(
            test_result_id=test_result_id, read_mask=_read_mask(read_fields)
        )
        return TestResult.from_protobuf(self._get_data_store_client().get_test_result(get_request))

    def get_step(self, step_id: str, *, read_fields: Iterable[str] = ()) -> Step:
        """Get the step with the given ID.

        Args:
            step_id: The ID of the step.

            read_fields: Optional field names to return, such as "conditions".
                All default fields are returned when empty.

        Returns:
            Step: The requested step.
        """
        get_request = GetStepRequest(step_id=step_id, read_mask=_read_mask(read_fields))
        return Step.from_protobuf(self._get_data_store_client().get_step(get_request))

    def get_measurement(
        self, measurement_id: str, *, read_fields: Iterable[str] = ()
    ) -> Measurement:
        """Get the measurement with the given ID.

        Args:
            measurement_id: The ID of the measurement.

            read_fields: Optional field names to return, such as "conditions".
                All default fields are returned when empty.

        Returns:
            Measurement: The requested measurement metadata.
        """
        get_request = GetMeasurementRequest(
            measurement_id=measurement_id, read_mask=_read_mask(read_fields)
        )
        return Measurement.from_protobuf(self._get_data_store_client().get_measurement(get_request))

    def query_test_results(
        self, odata_query: str = "", *, read_fields: Iterable[str] = ()
    ) -> Sequence[TestResult]:
        """Query test results using OData query syntax.

        Args:
            odata_query: An OData query string. An empty string returns all test
                results. $select, $count, $expand, and $apply are not supported.

            read_fields: Optional field names to return for each test result.

        Returns:
            Sequence[TestResult]: The matching test results.
        """
        query_request = QueryTestResultsRequest(
            odata_query=odata_query, read_mask=_read_mask(read_fields)
        )
        query_response = self._get_data_store_client().query_test_results(query_request)
        return [TestResult.from_protobuf(proto) for proto in query_response.test_results]

    def query_steps(
        self, odata_query: str = "", *, read_fields: Iterable[str] = ()
    ) -> Sequence[Step]:
        """Query steps using OData query syntax.

        Args:
            odata_query: An OData query string. An empty string returns all
                steps. $select, $count, $expand, and $apply are not supported.

            read_fields: Optional field names to return for each step.

        Returns:
            Sequence[Step]: The matching steps.
        """
        query_request = QueryStepsRequest(
            odata_query=odata_query, read_mask=_read_mask(read_fields)
        )
        query_response = self._get_data_store_client().query_steps(query_request)
        return [Step.from_protobuf(proto) for proto in query_response.steps]

    def query_measurements(
        self, odata_query: str = "", *, read_fields: Iterable[str] = ()
    ) -> Sequence[Measurement]:
        """Query measurements using OData query syntax.

        Args:
            odata_query: An OData query string. An empty string returns all
                measurements. $select, $count, $expand, and $apply are not
                supported.

            read_fields: Optional field names to return for each measurement.

        Returns:
            Sequence[Measurement]: The matching measurements.
        """
        query_request = QueryMeasurementsRequest(
            odata_query=odata_query, read_mask=_read_mask(read_fields)
        )
        query_response = self._get_data_store_client().query_measurements(query_request)
        return [Measurement.from_protobuf(proto) for proto in query_response.measurements]

    def update_test_result(self, test_result_id: str, **fields: object) -> TestResult:
        """Update mutable test result fields.

        Args:
            test_result_id: The ID of the test result to update.

            **fields: The fields to change, such as link="..." or
                outcome=Outcome.FAILED. A value of None clears the field.

        Returns:
            TestResult: The updated test result.

        Raises:
            ValueError: If no fields are given or a field cannot be updated.
        """
        test_result = TestResultProto(id=test_result_id)
        mask = _populate_update(test_result, fields, _TEST_RESULT_UPDATE_FIELDS)
        update_request = UpdateTestResultRequest(test_result=test_result, update_mask=mask)
        return TestResult.from_protobuf(
            self._get_data_store_client().update_test_result(update_request)
        )

    def update_step(self, step_id: str, **fields: object) -> Step:
        """Update mutable step fields.

        Args:
            step_id: The ID of the step to update.

            **fields: The fields to change, such as notes="...". A value of None
                clears the field.

        Returns:
            Step: The updated step.

        Raises:
            ValueError: If no fields are given or a field cannot be updated.
        """
        step = StepProto(id=step_id)
        mask = _populate_update(step, fields, _STEP_UPDATE_FIELDS)
        update_request = UpdateStepRequest(step=step, update_mask=mask)
        return Step.from_protobuf(self._get_data_store_client().update_step(update_request))

    def update_measurement(self, measurement_id: str, **fields: object) -> Measurement:
        """Update mutable measurement fields.

        Args:
            measurement_id: The ID of the measurement to update.

            **fields: The fields to change, such as notes="...". A value of None
                clears the field.

        Returns:
            Measurement: The updated measurement metadata.

        Raises:
            ValueError: If no fields are given or a field cannot be updated.
        """
        measurement = MeasurementProto(id=measurement_id)
        mask = _populate_update(measurement, fields, _MEASUREMENT_UPDATE_FIELDS)
        update_request = UpdateMeasurementRequest(measurement=measurement, update_mask=mask)
        return Measurement.from_protobuf(
            self._get_data_store_client().update_measurement(update_request)
        )

    def _get_data_store_client(self) -> DataStoreServiceClient:
        if self._closed:
            raise RuntimeError(self._DATA_STORE_CLIENT_CLOSED_ERROR)
        return self._data_store_client


# Mutable update-mask paths from the V2 mutability design, including Stage 2 resource fields.
_TEST_RESULT_UPDATE_FIELDS = frozenset(
    {
        "uut_instance_id",
        "uut_id",
        "operator_id",
        "test_station_id",
        "test_description_id",
        "start_date_time",
        "end_date_time",
        "duration",
        "outcome",
        "status",
        "error_information",
        "link",
        "keywords",
        "extension",
    }
)
_STEP_UPDATE_FIELDS = frozenset(
    {
        "test_id",
        "notes",
        "start_date_time",
        "end_date_time",
        "duration",
        "outcome",
        "status",
        "error_information",
        "link",
        "keywords",
        "extension",
    }
)
_MEASUREMENT_UPDATE_FIELDS = frozenset(
    {
        "notes",
        "outcome",
        "error_information",
        "extension",
        "start_date_time",
        "end_date_time",
        "duration",
    }
)


def _read_mask(fields: Iterable[str]) -> FieldMask | None:
    paths = list(fields)
    return FieldMask(paths=paths) if paths else None


def _populate_update(
    resource: TestResultProto | StepProto | MeasurementProto,
    fields: Mapping[str, object],
    allowed: frozenset[str],
) -> FieldMask:
    if not fields:
        raise ValueError("At least one field must be supplied for an update.")
    unknown_fields = fields.keys() - allowed
    if unknown_fields:
        raise ValueError(f"Fields cannot be updated: {', '.join(sorted(unknown_fields))}.")

    target = cast(Any, resource)
    for name, value in fields.items():
        if value is None:
            target.ClearField(name)
        elif name in {"start_date_time", "end_date_time"}:
            getattr(target, name).CopyFrom(hightime_datetime_to_protobuf(cast(ht.datetime, value)))
        elif name == "duration":
            target.duration.CopyFrom(hightime_timedelta_to_protobuf(cast(ht.timedelta, value)))
        elif name == "keywords":
            target.keywords[:] = cast(Iterable[str], value)
        elif name == "extension":
            json_format.ParseDict(dict(cast(Mapping[str, Any], value)), target.extension)
        elif name == "error_information":
            target.error_information.CopyFrom(cast(ErrorInformation, value).to_protobuf())
        else:
            setattr(target, name, value)

    return FieldMask(paths=list(fields))
