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
    AddMeasurementMetadataRequest,
    AddTestResultMetadataRequest,
    BatchCreateMeasurementsRequest,
    BatchCreateStepsRequest,
    BatchCreateTestResultsRequest,
    BatchDeleteMeasurementsRequest,
    BatchDeleteStepsRequest,
    BatchDeleteTestResultsRequest,
    BatchUpdateMeasurementsRequest,
    BatchUpdateStepsRequest,
    BatchUpdateTestResultsRequest,
    CreateMeasurementRequest,
    CreateStepRequest,
    CreateTestResultRequest,
    DeleteMeasurementRequest,
    DeleteStepRequest,
    DeleteTestResultRequest,
    GetMeasurementRequest,
    GetStepRequest,
    GetTestResultRequest,
    QueryMeasurementsRequest,
    QueryStepsRequest,
    QueryTestResultsRequest,
    ReadMeasurementValuesRequest,
    RemoveConditionRequest,
    RemoveMeasurementMetadataRequest,
    RemoveTestResultMetadataRequest,
    UpdateMeasurementRequest,
    UpdateStepRequest,
    UpdateTestResultRequest,
)
from ni.protobuf.types.precision_duration_conversion import hightime_timedelta_to_protobuf
from ni.protobuf.types.precision_timestamp_conversion import hightime_datetime_to_protobuf
from ni_grpc_extensions.channelpool import GrpcChannelPool

from ni.datastore.data.v2._grpc_conversion import (
    convert_measurement_value_from_protobuf,
    measurement_value_from_protobuf,
)
from ni.datastore.data.v2._types._condition import Condition
from ni.datastore.data.v2._types._error_information import ErrorInformation
from ni.datastore.data.v2._types._measurement import Measurement
from ni.datastore.data.v2._types._outcome import Outcome
from ni.datastore.data.v2._types._query_results import QueryResults
from ni.datastore.data.v2._types._step import Step
from ni.datastore.data.v2._types._test_result import TestResult
from ni.datastore.metadata import HardwareItem, SoftwareItem, TestAdapter

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

    def remove_condition(self, step_id: str, condition_name: str) -> Step:
        """Remove a condition from a step.

        Args:
            step_id: The ID of the step that owns the condition.

            condition_name: The name of the condition to remove.

        Returns:
            Step: The updated step.
        """
        remove_request = RemoveConditionRequest(step_id=step_id, condition_name=condition_name)
        return Step.from_protobuf(
            self._get_data_store_client().remove_condition(remove_request).step
        )

    def create_measurement(
        self,
        name: str,
        value: object,
        step_id: str,
        *,
        units: str = "",
        upper_limit: object = None,
        lower_limit: object = None,
        comparison_type: str = "",
        notes: str = "",
        start_date_time: ht.datetime | None = None,
        end_date_time: ht.datetime | None = None,
        duration: ht.timedelta | None = None,
        outcome: Outcome = Outcome.UNSPECIFIED,
        error_information: ErrorInformation | None = None,
        extension: Mapping[str, Any] | None = None,
        schema_id: str = "",
        software_item_ids: Iterable[str] = (),
        hardware_item_ids: Iterable[str] = (),
        test_adapter_ids: Iterable[str] = (),
        software_items: Iterable[SoftwareItem] = (),
        hardware_items: Iterable[HardwareItem] = (),
        test_adapters: Iterable[TestAdapter] = (),
    ) -> str:
        """Create a measurement associated with a test step.

        Args:
            name: The name used for grouping conceptually alike measurements.

            value: The measured value. Supported types are bool, int, float, str,
                Scalar, Vector, iterables of scalar values, AnalogWaveform,
                ComplexWaveform, Spectrum, DigitalWaveform, XYData, and JSON
                mappings.

            step_id: The ID of the step that owns the measurement.

            units: Engineering units of the value. Defaults to the units of a
                Scalar value.

            upper_limit: The publisher-supplied upper limit. Any supported value
                type is accepted.

            lower_limit: The publisher-supplied lower limit. Any supported value
                type is accepted.

            comparison_type: The publisher-defined comparison operation. The
                service stores it but does not derive the outcome from it.

            notes: Any notes to associate with the measurement.

            start_date_time: The start time of the measurement.

            end_date_time: The end time of the measurement.

            duration: The duration of the measurement.

            outcome: The outcome of the measurement.

            error_information: Error details for the measurement.

            extension: Custom JSON data for the measurement.

            schema_id: Schema that governs the extension. Reserved by the service
                for future support.

            software_item_ids: The software item IDs for the measurement. These
                must already be linked to the test result.

            hardware_item_ids: The hardware item IDs for the measurement. These
                must already be linked to the test result.

            test_adapter_ids: The test adapter IDs for the measurement. These
                must already be linked to the test result.

            software_items: Software items to find or create as part of this
                request. Each item must already be linked to the test result.

            hardware_items: Hardware items to find or create as part of this
                request. Each item must already be linked to the test result.

            test_adapters: Test adapters to find or create as part of this
                request. Each item must already be linked to the test result.

        Returns:
            str: The measurement ID.
        """
        measurement = Measurement(
            name=name,
            value=value,
            step_id=step_id,
            units=units,
            upper_limit=upper_limit,
            lower_limit=lower_limit,
            comparison_type=comparison_type,
            notes=notes,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            duration=duration,
            outcome=outcome,
            error_information=error_information,
            extension=extension,
            schema_id=schema_id,
            software_item_ids=software_item_ids,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
            software_items=software_items,
            hardware_items=hardware_items,
            test_adapters=test_adapters,
        )
        create_request = CreateMeasurementRequest(measurement=measurement.to_protobuf())
        return self._get_data_store_client().create_measurement(create_request).id

    def batch_create_test_results(self, test_results: Iterable[TestResult]) -> Sequence[str]:
        """Create several test results, including any nested steps, in one atomic call.

        Args:
            test_results: The test results to create.

        Returns:
            Sequence[str]: The test result IDs, in request order.
        """
        batch_request = BatchCreateTestResultsRequest(
            requests=[
                CreateTestResultRequest(test_result=test_result.to_protobuf())
                for test_result in test_results
            ]
        )
        batch_response = self._get_data_store_client().batch_create_test_results(batch_request)
        return [test_result.id for test_result in batch_response.test_results]

    def batch_create_steps(self, steps: Iterable[Step]) -> Sequence[str]:
        """Create several steps, including any nested children, in one atomic call.

        Args:
            steps: The steps to create.

        Returns:
            Sequence[str]: The step IDs, in request order.
        """
        batch_request = BatchCreateStepsRequest(
            requests=[CreateStepRequest(step=step.to_protobuf()) for step in steps]
        )
        batch_response = self._get_data_store_client().batch_create_steps(batch_request)
        return [step.id for step in batch_response.steps]

    def batch_create_measurements(self, measurements: Iterable[Measurement]) -> Sequence[str]:
        """Create several measurements in one atomic call.

        Args:
            measurements: The measurements to create. Each must set step_id and
                value, and may target a different step or test result.

        Returns:
            Sequence[str]: The measurement IDs, in request order.
        """
        batch_request = BatchCreateMeasurementsRequest(
            requests=[
                CreateMeasurementRequest(measurement=measurement.to_protobuf())
                for measurement in measurements
            ]
        )
        batch_response = self._get_data_store_client().batch_create_measurements(batch_request)
        return [measurement.id for measurement in batch_response.measurements]

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
            The value converted to a nitypes or Python value. A single value is
            always returned as a Scalar, with or without units. A list of
            values is returned as a Vector.

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

    def read_measurement_values(
        self, read_source: Measurement, *, read_fields: Iterable[str] = ()
    ) -> Measurement:
        """Read the value and limits of a measurement.

        Args:
            read_source: The measurement to read. Only its id is used.

            read_fields: Optional fields to read: "value", "upper_limit", and
                "lower_limit". All three are read when empty.

        Returns:
            Measurement: A measurement with id, value, upper_limit, and
                lower_limit set. A limit that was not published is None.
        """
        read_request = ReadMeasurementValuesRequest(
            measurement_id=read_source.id, read_mask=_read_mask(read_fields)
        )
        response = self._get_data_store_client().read_measurement_values(read_request)
        return Measurement(
            id=read_source.id,
            value=measurement_value_from_protobuf(response, "value"),
            upper_limit=measurement_value_from_protobuf(response, "upper_limit"),
            lower_limit=measurement_value_from_protobuf(response, "lower_limit"),
        )

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
    ) -> QueryResults[TestResult]:
        """Query test results using OData query syntax.

        Args:
            odata_query: An OData query string. An empty string returns all test
                results. $select, $count, $expand, and $apply are not supported.

            read_fields: Optional field names to return for each test result.

        Returns:
            QueryResults[TestResult]: The matching test results, with next_link
                set when more results are available.
        """
        query_request = QueryTestResultsRequest(
            odata_query=odata_query, read_mask=_read_mask(read_fields)
        )
        query_response = self._get_data_store_client().query_test_results(query_request)
        return QueryResults(
            (TestResult.from_protobuf(proto) for proto in query_response.test_results),
            query_response.next_link,
        )

    def query_steps(
        self, odata_query: str = "", *, read_fields: Iterable[str] = ()
    ) -> QueryResults[Step]:
        """Query steps using OData query syntax.

        Args:
            odata_query: An OData query string. An empty string returns all
                steps. $select, $count, $expand, and $apply are not supported.

            read_fields: Optional field names to return for each step.

        Returns:
            QueryResults[Step]: The matching steps, with next_link set when more
                results are available.
        """
        query_request = QueryStepsRequest(
            odata_query=odata_query, read_mask=_read_mask(read_fields)
        )
        query_response = self._get_data_store_client().query_steps(query_request)
        return QueryResults(
            (Step.from_protobuf(proto) for proto in query_response.steps),
            query_response.next_link,
        )

    def query_measurements(
        self, odata_query: str = "", *, read_fields: Iterable[str] = ()
    ) -> QueryResults[Measurement]:
        """Query measurements using OData query syntax.

        Args:
            odata_query: An OData query string. An empty string returns all
                measurements. $select, $count, $expand, and $apply are not
                supported.

            read_fields: Optional field names to return for each measurement.

        Returns:
            QueryResults[Measurement]: The matching measurements, with next_link
                set when more results are available.
        """
        query_request = QueryMeasurementsRequest(
            odata_query=odata_query, read_mask=_read_mask(read_fields)
        )
        query_response = self._get_data_store_client().query_measurements(query_request)
        return QueryResults(
            (Measurement.from_protobuf(proto) for proto in query_response.measurements),
            query_response.next_link,
        )

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

    def batch_update_test_results(
        self, updates: Mapping[str, Mapping[str, object]]
    ) -> Sequence[TestResult]:
        """Update several test results in one atomic call.

        Args:
            updates: The fields to change, keyed by test result ID. Each value
                follows the update_test_result field rules.

        Returns:
            Sequence[TestResult]: The updated test results, in request order.

        Raises:
            ValueError: If no updates are given, or an update has no fields or
                a field that cannot be updated.
        """
        requests = []
        for test_result_id, fields in _require_items(updates).items():
            test_result = TestResultProto(id=test_result_id)
            mask = _populate_update(test_result, fields, _TEST_RESULT_UPDATE_FIELDS)
            requests.append(UpdateTestResultRequest(test_result=test_result, update_mask=mask))
        batch_request = BatchUpdateTestResultsRequest(requests=requests)
        batch_response = self._get_data_store_client().batch_update_test_results(batch_request)
        return [TestResult.from_protobuf(proto) for proto in batch_response.test_results]

    def batch_update_steps(self, updates: Mapping[str, Mapping[str, object]]) -> Sequence[Step]:
        """Update several steps in one atomic call.

        Args:
            updates: The fields to change, keyed by step ID. Each value follows
                the update_step field rules.

        Returns:
            Sequence[Step]: The updated steps, in request order.

        Raises:
            ValueError: If no updates are given, or an update has no fields or
                a field that cannot be updated.
        """
        requests = []
        for step_id, fields in _require_items(updates).items():
            step = StepProto(id=step_id)
            mask = _populate_update(step, fields, _STEP_UPDATE_FIELDS)
            requests.append(UpdateStepRequest(step=step, update_mask=mask))
        batch_request = BatchUpdateStepsRequest(requests=requests)
        batch_response = self._get_data_store_client().batch_update_steps(batch_request)
        return [Step.from_protobuf(proto) for proto in batch_response.steps]

    def batch_update_measurements(
        self, updates: Mapping[str, Mapping[str, object]]
    ) -> Sequence[Measurement]:
        """Update several measurements in one atomic call.

        Args:
            updates: The fields to change, keyed by measurement ID. Each value
                follows the update_measurement field rules.

        Returns:
            Sequence[Measurement]: The updated measurements, in request order.

        Raises:
            ValueError: If no updates are given, or an update has no fields or
                a field that cannot be updated.
        """
        requests = []
        for measurement_id, fields in _require_items(updates).items():
            measurement = MeasurementProto(id=measurement_id)
            mask = _populate_update(measurement, fields, _MEASUREMENT_UPDATE_FIELDS)
            requests.append(UpdateMeasurementRequest(measurement=measurement, update_mask=mask))
        batch_request = BatchUpdateMeasurementsRequest(requests=requests)
        batch_response = self._get_data_store_client().batch_update_measurements(batch_request)
        return [Measurement.from_protobuf(proto) for proto in batch_response.measurements]

    def add_test_result_metadata(
        self,
        test_result_id: str,
        *,
        software_item_ids: Iterable[str] = (),
        hardware_item_ids: Iterable[str] = (),
        test_adapter_ids: Iterable[str] = (),
    ) -> TestResult:
        """Link existing software items, hardware items, or test adapters to a test result.

        The service also links each newly linked item to every existing
        measurement of the test result. Items that are already linked are
        ignored.

        Args:
            test_result_id: The ID of the test result.

            software_item_ids: The software item IDs or aliases to link.

            hardware_item_ids: The hardware item IDs or aliases to link.

            test_adapter_ids: The test adapter IDs or aliases to link.

        Returns:
            TestResult: The updated test result.
        """
        add_request = AddTestResultMetadataRequest(
            test_result_id=test_result_id,
            software_item_ids=software_item_ids,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
        )
        return TestResult.from_protobuf(
            self._get_data_store_client().add_test_result_metadata(add_request).test_result
        )

    def remove_test_result_metadata(
        self,
        test_result_id: str,
        *,
        software_item_ids: Iterable[str] = (),
        hardware_item_ids: Iterable[str] = (),
        test_adapter_ids: Iterable[str] = (),
    ) -> TestResult:
        """Unlink software items, hardware items, or test adapters from a test result.

        The service also unlinks each item from every measurement of the test
        result. Each item must currently be linked to the test result.

        Args:
            test_result_id: The ID of the test result.

            software_item_ids: The software item IDs or aliases to unlink.

            hardware_item_ids: The hardware item IDs or aliases to unlink.

            test_adapter_ids: The test adapter IDs or aliases to unlink.

        Returns:
            TestResult: The updated test result.
        """
        remove_request = RemoveTestResultMetadataRequest(
            test_result_id=test_result_id,
            software_item_ids=software_item_ids,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
        )
        return TestResult.from_protobuf(
            self._get_data_store_client().remove_test_result_metadata(remove_request).test_result
        )

    def add_measurement_metadata(
        self,
        measurement_id: str,
        *,
        software_item_ids: Iterable[str] = (),
        hardware_item_ids: Iterable[str] = (),
        test_adapter_ids: Iterable[str] = (),
    ) -> Measurement:
        """Link software items, hardware items, or test adapters to a measurement.

        Each item must already be linked to the measurement's test result.

        Args:
            measurement_id: The ID of the measurement.

            software_item_ids: The software item IDs to link.

            hardware_item_ids: The hardware item IDs to link.

            test_adapter_ids: The test adapter IDs to link.

        Returns:
            Measurement: The updated measurement.
        """
        add_request = AddMeasurementMetadataRequest(
            measurement_id=measurement_id,
            software_item_ids=software_item_ids,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
        )
        return Measurement.from_protobuf(
            self._get_data_store_client().add_measurement_metadata(add_request).measurement
        )

    def remove_measurement_metadata(
        self,
        measurement_id: str,
        *,
        software_item_ids: Iterable[str] = (),
        hardware_item_ids: Iterable[str] = (),
        test_adapter_ids: Iterable[str] = (),
    ) -> Measurement:
        """Unlink software items, hardware items, or test adapters from a measurement.

        Args:
            measurement_id: The ID of the measurement.

            software_item_ids: The software item IDs to unlink.

            hardware_item_ids: The hardware item IDs to unlink.

            test_adapter_ids: The test adapter IDs to unlink.

        Returns:
            Measurement: The updated measurement.
        """
        remove_request = RemoveMeasurementMetadataRequest(
            measurement_id=measurement_id,
            software_item_ids=software_item_ids,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
        )
        return Measurement.from_protobuf(
            self._get_data_store_client().remove_measurement_metadata(remove_request).measurement
        )

    def delete_test_result(self, test_result_id: str, *, force: bool = False) -> None:
        """Delete a test result.

        Args:
            test_result_id: The ID of the test result to delete.

            force: If True, also delete the steps, measurements, and conditions that the
                test result owns. If False, the service rejects the delete with
                FAILED_PRECONDITION when owned children exist.
        """
        delete_request = DeleteTestResultRequest(test_result_id=test_result_id, force=force)
        self._get_data_store_client().delete_test_result(delete_request)

    def delete_step(self, step_id: str, *, force: bool = False) -> None:
        """Delete a step.

        A step that has child steps cannot be deleted.

        Args:
            step_id: The ID of the step to delete.

            force: If True, also delete the measurements of the step. If False, the
                service rejects the delete with FAILED_PRECONDITION when measurements exist.
        """
        delete_request = DeleteStepRequest(step_id=step_id, force=force)
        self._get_data_store_client().delete_step(delete_request)

    def delete_measurement(self, measurement_id: str) -> None:
        """Delete a measurement.

        Args:
            measurement_id: The ID of the measurement to delete.
        """
        delete_request = DeleteMeasurementRequest(measurement_id=measurement_id)
        self._get_data_store_client().delete_measurement(delete_request)

    def batch_delete_test_results(
        self, test_result_ids: Iterable[str], *, force: bool | Iterable[bool] = False
    ) -> None:
        """Delete several test results in one atomic call.

        Args:
            test_result_ids: The IDs of the test results to delete.

            force: One flag for every test result, or one flag per test result.
                See delete_test_result.

        Raises:
            ValueError: If one flag per item is given and the counts differ.
        """
        batch_request = BatchDeleteTestResultsRequest(
            requests=[
                DeleteTestResultRequest(test_result_id=test_result_id, force=item_force)
                for test_result_id, item_force in _with_force(test_result_ids, force)
            ]
        )
        self._get_data_store_client().batch_delete_test_results(batch_request)

    def batch_delete_steps(
        self, step_ids: Iterable[str], *, force: bool | Iterable[bool] = False
    ) -> None:
        """Delete several steps in one atomic call.

        Args:
            step_ids: The IDs of the steps to delete. A step and its ancestor or
                descendant cannot be deleted in the same call.

            force: One flag for every step, or one flag per step. See delete_step.

        Raises:
            ValueError: If one flag per item is given and the counts differ.
        """
        batch_request = BatchDeleteStepsRequest(
            requests=[
                DeleteStepRequest(step_id=step_id, force=item_force)
                for step_id, item_force in _with_force(step_ids, force)
            ]
        )
        self._get_data_store_client().batch_delete_steps(batch_request)

    def batch_delete_measurements(self, measurement_ids: Iterable[str]) -> None:
        """Delete several measurements in one atomic call.

        Args:
            measurement_ids: The IDs of the measurements to delete.
        """
        batch_request = BatchDeleteMeasurementsRequest(
            requests=[
                DeleteMeasurementRequest(measurement_id=measurement_id)
                for measurement_id in measurement_ids
            ]
        )
        self._get_data_store_client().batch_delete_measurements(batch_request)

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
        "uut_instance",
        "operator",
        "test_station",
        "test_description",
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
        "test",
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


# Update fields that take a metadata model, such as Operator, and are sent as its protobuf.
_METADATA_UPDATE_FIELDS = frozenset(
    {"uut_instance", "operator", "test_station", "test_description", "test"}
)


def _read_mask(fields: Iterable[str]) -> FieldMask | None:
    paths = list(fields)
    return FieldMask(paths=paths) if paths else None


def _require_items(
    updates: Mapping[str, Mapping[str, object]],
) -> Mapping[str, Mapping[str, object]]:
    if not updates:
        raise ValueError("At least one update must be supplied for a batch update.")
    return updates


def _with_force(ids: Iterable[str], force: bool | Iterable[bool]) -> list[tuple[str, bool]]:
    id_list = list(ids)
    if isinstance(force, bool):
        return [(resource_id, force) for resource_id in id_list]
    force_list = list(force)
    if len(force_list) != len(id_list):
        raise ValueError(
            f"Expected {len(id_list)} force flags, one per ID, but got {len(force_list)}."
        )
    return list(zip(id_list, force_list))


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
        elif name in _METADATA_UPDATE_FIELDS:
            getattr(target, name).CopyFrom(cast(Any, value).to_protobuf())
        else:
            setattr(target, name, value)

    return FieldMask(paths=list(fields))
