"""Data store client for publishing and reading data with NI Data Store Service V2."""

from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping, Sequence
from enum import Enum
from types import TracebackType
from typing import Any, overload, Type, TYPE_CHECKING, TypeVar
from uuid import UUID

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
from ni_grpc_extensions.channelpool import GrpcChannelPool

from ni.datastore.data.v2._grpc_conversion import (
    convert_measurement_value_from_protobuf,
    id_list,
    id_string,
    measurement_value_from_protobuf,
    string_list,
)
from ni.datastore.data.v2._types._condition import Condition
from ni.datastore.data.v2._types._create import (
    ConditionCreateFields,
    MeasurementCreateFields,
    StepCreateFields,
    TestResultCreateFields,
)
from ni.datastore.data.v2._types._measurement import Measurement
from ni.datastore.data.v2._types._measurement_value import MeasurementReadValue, MeasurementValue
from ni.datastore.data.v2._types._query_results import QueryResults
from ni.datastore.data.v2._types._read_fields import (
    MeasurementField,
    MeasurementValueField,
    StepField,
    TestResultField,
)
from ni.datastore.data.v2._types._step import Step
from ni.datastore.data.v2._types._test_result import TestResult
from ni.datastore.data.v2._types._update import (
    MeasurementUpdateBuilder,
    MeasurementUpdateFields,
    StepUpdateBuilder,
    StepUpdateFields,
    TestResultUpdateBuilder,
    TestResultUpdateFields,
)
from ni.datastore.data.v2._update_conversion import (
    MEASUREMENT_UPDATE_FIELDS,
    populate_update,
    resource_update_fields,
    STEP_RELATIONSHIPS,
    STEP_UPDATE_FIELDS,
    TEST_RESULT_RELATIONSHIPS,
    TEST_RESULT_UPDATE_FIELDS,
)

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        from typing import Self, Unpack
    else:
        from typing_extensions import Self, Unpack

TRead = TypeVar("TRead")
_T = TypeVar("_T")


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

    @overload
    def create_test_result(self, test_result: TestResult, /) -> TestResult: ...

    @overload
    def create_test_result(
        self, name: str, /, **fields: Unpack[TestResultCreateFields]
    ) -> TestResult: ...

    def create_test_result(
        self, test_result: TestResult | str, /, **fields: Unpack[TestResultCreateFields]
    ) -> TestResult:
        """Create a test result, including any nested steps.

        Pass either a TestResult, or its name and fields as keyword arguments.

        Args:
            test_result: The test result to create, or its name.

            **fields: The test result fields, when a name is given. Each has the
                same meaning as the matching TestResult argument.

        Returns:
            TestResult: The created test result as returned by the service, including
                its ID. Nested steps and expanded metadata are not included.

        Raises:
            TypeError: If fields are given with a TestResult.
        """
        if isinstance(test_result, TestResult):
            _reject_model_fields(fields, "a TestResult", "test result")
        else:
            test_result = TestResult(test_result, **fields)
        create_request = CreateTestResultRequest(test_result=test_result.to_protobuf())
        return TestResult.from_protobuf(
            self._get_data_store_client().create_test_result(create_request)
        )

    @overload
    def create_step(self, step: Step, /) -> Step: ...

    @overload
    def create_step(self, name: str, /, **fields: Unpack[StepCreateFields]) -> Step: ...

    def create_step(self, step: Step | str, /, **fields: Unpack[StepCreateFields]) -> Step:
        """Create a step, including any conditions, child steps, and measurements.

        Pass either a Step, or its name and fields as keyword arguments.

        Args:
            step: The step to create, or its name.

            **fields: The step fields, when a name is given, such as
                test_result_id. Each has the same meaning as the matching Step
                argument.

        Returns:
            Step: The created step as returned by the service, including its ID.
                Conditions, child steps, measurements, and expanded metadata are not
                included.

        Raises:
            TypeError: If fields are given with a Step.
        """
        if isinstance(step, Step):
            _reject_model_fields(fields, "a Step", "step")
        else:
            step = Step(step, **fields)
        create_request = CreateStepRequest(step=step.to_protobuf())
        return Step.from_protobuf(self._get_data_store_client().create_step(create_request))

    @overload
    def add_condition(self, step_id: str | UUID, condition: Condition, /) -> Step: ...

    @overload
    def add_condition(
        self,
        step_id: str | UUID,
        name: str,
        value: object,
        /,
        **fields: Unpack[ConditionCreateFields],
    ) -> Step: ...

    def add_condition(
        self,
        step_id: str | UUID,
        condition: Condition | str,
        /,
        *args: object,
        **fields: Unpack[ConditionCreateFields],
    ) -> Step:
        """Add a condition to a step, replacing any condition with the same name.

        Pass either a Condition, or its name, value, and fields as arguments.

        Args:
            step_id: The ID of the step that owns the condition.

            condition: The condition to add, or its name.

            *args: The condition value, when a name is given. See Condition for
                the supported value types.

            **fields: The condition fields, when a name is given, such as units.
                Each has the same meaning as the matching Condition argument.

        Returns:
            Step: The updated step.

        Raises:
            TypeError: If a value or fields are given with a Condition, or a name
                is given without a value.
        """
        if isinstance(condition, Condition):
            _reject_model_fields({**fields, **dict(enumerate(args))}, "a Condition", "condition")
        elif len(args) != 1:
            raise TypeError("Pass the condition value after its name, or pass a Condition.")
        else:
            condition = Condition(condition, args[0], **fields)
        add_request = AddConditionRequest(
            step_id=id_string(step_id), condition=condition.to_protobuf()
        )
        return Step.from_protobuf(self._get_data_store_client().add_condition(add_request).step)

    def remove_condition(self, step_id: str | UUID, condition_name: str) -> Step:
        """Remove a condition from a step.

        Args:
            step_id: The ID of the step that owns the condition.

            condition_name: The name of the condition to remove.

        Returns:
            Step: The updated step.
        """
        remove_request = RemoveConditionRequest(
            step_id=id_string(step_id), condition_name=condition_name
        )
        return Step.from_protobuf(
            self._get_data_store_client().remove_condition(remove_request).step
        )

    @overload
    def create_measurement(self, measurement: Measurement, /) -> Measurement: ...

    @overload
    def create_measurement(
        self,
        name: str,
        value: MeasurementValue,
        step_id: str | UUID,
        **fields: Unpack[MeasurementCreateFields],
    ) -> Measurement: ...

    def create_measurement(self, *args: Any, **kwargs: Any) -> Measurement:
        """Create a measurement associated with a test step.

        Pass either a Measurement, or the measurement fields as arguments. The
        fields after step_id are keyword arguments, typed by MeasurementCreateFields.

        Args:
            measurement: The measurement to create. It must include a step ID and
                value. Cannot be combined with the other arguments.

            name: The name used for grouping conceptually alike measurements.

            value: The measured value. Supported types are bool, int, float, str,
                Scalar, Vector, iterables of scalar values, AnalogWaveform,
                ComplexWaveform, Spectrum, DigitalWaveform, XYData, and JSON
                mappings.

            step_id: The ID of the step that owns the measurement.

            units: Engineering units of the value. Defaults to the units of a
                Scalar value.

            upper_limit: The publisher-supplied upper limit. Any supported value
                type is accepted. The service stores it but does not compare it
                with the value.

            lower_limit: The publisher-supplied lower limit. Any supported value
                type is accepted. The service stores it but does not compare it
                with the value.

            comparison_type: The publisher-defined comparison operation. The
                service stores it but does not derive the outcome from it.

            notes: Any notes to associate with the measurement.

            start_date_time: The start time of the measurement.

            end_date_time: The end time of the measurement.

            duration: The duration of the measurement.

            outcome: The outcome of the measurement.

            error_information: Error details for the measurement.

            extension: Custom JSON data for the measurement.

            schema_id: Schema that governs the extension. Reserved for future use.

            software_item_ids: The software item IDs for the measurement. These
                must already be linked to the owning test result.

            hardware_item_ids: The hardware item IDs for the measurement. These
                must already be linked to the owning test result.

            test_adapter_ids: The test adapter IDs for the measurement. These
                must already be linked to the owning test result.

            software_items: Software items to find or create as part of this
                request. Each item must already be linked to the owning test result.

            hardware_items: Hardware items to find or create as part of this
                request. Each item must already be linked to the owning test result.

            test_adapters: Test adapters to find or create as part of this
                request. Each item must already be linked to the owning test result.

        Returns:
            Measurement: The created measurement as returned by the service,
                including its ID. Expanded metadata is not included.

        Raises:
            TypeError: If fields are given with a Measurement.
        """
        if args and isinstance(args[0], Measurement):
            _reject_model_fields(
                {**kwargs, **dict(enumerate(args[1:]))}, "a Measurement", "measurement"
            )
            measurement: Measurement = args[0]
        else:
            measurement = _measurement_from_fields(*args, **kwargs)
        create_request = CreateMeasurementRequest(measurement=measurement.to_protobuf())
        return Measurement.from_protobuf(
            self._get_data_store_client().create_measurement(create_request)
        )

    def batch_create_test_results(self, test_results: Iterable[TestResult]) -> Sequence[TestResult]:
        """Create multiple test results, including any nested steps, in one atomic call.

        Args:
            test_results: The test results to create.

        Returns:
            Sequence[TestResult]: The created test results, in request order. Nested
                steps and expanded metadata are not included.
        """
        batch_request = BatchCreateTestResultsRequest(
            requests=[
                CreateTestResultRequest(test_result=test_result.to_protobuf())
                for test_result in test_results
            ]
        )
        batch_response = self._get_data_store_client().batch_create_test_results(batch_request)
        return [
            TestResult.from_protobuf(test_result) for test_result in batch_response.test_results
        ]

    def batch_create_steps(self, steps: Iterable[Step]) -> Sequence[Step]:
        """Create multiple steps, including any nested children, in one atomic call.

        Args:
            steps: The steps to create.

        Returns:
            Sequence[Step]: The created steps, in request order. Conditions, child
                steps, measurements, and expanded metadata are not included.
        """
        batch_request = BatchCreateStepsRequest(
            requests=[CreateStepRequest(step=step.to_protobuf()) for step in steps]
        )
        batch_response = self._get_data_store_client().batch_create_steps(batch_request)
        return [Step.from_protobuf(step) for step in batch_response.steps]

    def batch_create_measurements(
        self, measurements: Iterable[Measurement]
    ) -> Sequence[Measurement]:
        """Create multiple measurements in one atomic call.

        Args:
            measurements: The measurements to create. Each must include a step ID and
                value. They may target different steps or test results.

        Returns:
            Sequence[Measurement]: The created measurements, in request order.
                Expanded metadata is not included.
        """
        batch_request = BatchCreateMeasurementsRequest(
            requests=[
                CreateMeasurementRequest(measurement=measurement.to_protobuf())
                for measurement in measurements
            ]
        )
        batch_response = self._get_data_store_client().batch_create_measurements(batch_request)
        return [
            Measurement.from_protobuf(measurement) for measurement in batch_response.measurements
        ]

    @overload
    def read_measurement_value(
        self,
        read_source: Measurement | str | UUID,
        expected_type: Type[TRead],
    ) -> TRead: ...

    @overload
    def read_measurement_value(
        self,
        read_source: Measurement | str | UUID,
    ) -> MeasurementReadValue: ...

    def read_measurement_value(
        self,
        read_source: Measurement | str | UUID,
        expected_type: Type[TRead] | None = None,
    ) -> TRead | MeasurementReadValue:
        """Read the value of a measurement.

        Args:
            read_source: The measurement to read, or its ID. Only the ID is used.

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
            measurement_id=_resource_id(read_source), read_mask=FieldMask(paths=["value"])
        )
        response = self._get_data_store_client().read_measurement_values(read_request)
        read_value = convert_measurement_value_from_protobuf(response.value)
        if expected_type is not None and not isinstance(read_value, expected_type):
            raise TypeError(f"Expected type {expected_type}, got {type(read_value)}")
        return read_value

    def read_measurement_values(
        self,
        read_source: Measurement | str | UUID,
        *,
        read_fields: Iterable[MeasurementValueField] = (),
    ) -> Measurement:
        """Read the value and limits of a measurement.

        Args:
            read_source: The measurement to read, or its ID. Only the ID is used.

            read_fields: Optional fields to read, such as MeasurementValueField.VALUE.
                The value and both limits are read when empty.

        Returns:
            Measurement: A measurement with id, value, upper_limit, and
                lower_limit set. A limit that was not published is None.
        """
        measurement_id = _resource_id(read_source)
        read_request = ReadMeasurementValuesRequest(
            measurement_id=measurement_id, read_mask=_read_mask(read_fields)
        )
        response = self._get_data_store_client().read_measurement_values(read_request)
        return Measurement(
            id=measurement_id,
            value=measurement_value_from_protobuf(response, "value"),
            upper_limit=measurement_value_from_protobuf(response, "upper_limit"),
            lower_limit=measurement_value_from_protobuf(response, "lower_limit"),
        )

    def get_test_result(
        self, test_result_id: str | UUID, *, read_fields: Iterable[TestResultField | str] = ()
    ) -> TestResult:
        """Get the test result with the given ID.

        Args:
            test_result_id: The ID of the test result.

            read_fields: Optional fields to return, such as TestResultField.NAME. Field
                names as strings are also accepted. When empty, the service returns its
                default fields.

        Returns:
            TestResult: The requested test result.
        """
        get_request = GetTestResultRequest(
            test_result_id=id_string(test_result_id), read_mask=_read_mask(read_fields)
        )
        return TestResult.from_protobuf(self._get_data_store_client().get_test_result(get_request))

    def get_step(self, step_id: str | UUID, *, read_fields: Iterable[StepField | str] = ()) -> Step:
        """Get the step with the given ID.

        Args:
            step_id: The ID of the step.

            read_fields: Optional fields to return, such as StepField.CONDITIONS. Field
                names as strings are also accepted. When empty, the service returns its
                default fields.

        Returns:
            Step: The requested step.
        """
        get_request = GetStepRequest(step_id=id_string(step_id), read_mask=_read_mask(read_fields))
        return Step.from_protobuf(self._get_data_store_client().get_step(get_request))

    def get_measurement(
        self, measurement_id: str | UUID, *, read_fields: Iterable[MeasurementField | str] = ()
    ) -> Measurement:
        """Get the measurement with the given ID.

        Args:
            measurement_id: The ID of the measurement.

            read_fields: Optional fields to return, such as MeasurementField.CONDITIONS.
                Field names as strings are also accepted. When empty, the service returns
                its default fields.

        Returns:
            Measurement: The requested measurement.
        """
        get_request = GetMeasurementRequest(
            measurement_id=id_string(measurement_id), read_mask=_read_mask(read_fields)
        )
        return Measurement.from_protobuf(self._get_data_store_client().get_measurement(get_request))

    def query_test_results(
        self, odata_query: str = "", *, read_fields: Iterable[TestResultField | str] = ()
    ) -> QueryResults[TestResult]:
        """Query test results using OData query syntax.

        Args:
            odata_query: An OData query string. An empty string returns all test
                results. $select, $count, $expand, and $apply are not supported.

            read_fields: Optional fields to return for each test result, such as
                TestResultField.NAME. Field names as strings are also accepted.

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
        self, odata_query: str = "", *, read_fields: Iterable[StepField | str] = ()
    ) -> QueryResults[Step]:
        """Query steps using OData query syntax.

        Args:
            odata_query: An OData query string. An empty string returns all
                steps. $select, $count, $expand, and $apply are not supported.

            read_fields: Optional fields to return for each step, such as
                StepField.CONDITIONS. Field names as strings are also accepted.

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
        self, odata_query: str = "", *, read_fields: Iterable[MeasurementField | str] = ()
    ) -> QueryResults[Measurement]:
        """Query measurements using OData query syntax.

        Args:
            odata_query: An OData query string. An empty string returns all
                measurements. $select, $count, $expand, and $apply are not
                supported.

            read_fields: Optional fields to return for each measurement, such as
                MeasurementField.CONDITIONS. Field names as strings are also accepted.

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

    @overload
    def update_test_result(self, test_result: TestResultUpdateBuilder, /) -> TestResult: ...

    @overload
    def update_test_result(
        self, test_result: TestResult | str | UUID, /, **fields: Unpack[TestResultUpdateFields]
    ) -> TestResult: ...

    def update_test_result(
        self,
        test_result: TestResult | TestResultUpdateBuilder | str | UUID,
        /,
        **fields: Unpack[TestResultUpdateFields],
    ) -> TestResult:
        """Update mutable test result fields.

        Args:
            test_result: What to update. One of:

                * A TestResultUpdateBuilder. Only the fields selected on the
                  builder change.
                * An ID or a TestResult with keyword fields, such as
                  link="..." or outcome=Outcome.FAILED. Only those fields
                  change. A value of None clears the field.
                * A TestResult on its own. Every updatable field is set from
                  it, so empty fields are cleared. Stage 2 fields are sent only
                  when they have a value. When a relationship has both an ID
                  and inline metadata, only the ID is sent.

            **fields: The fields to change. Not allowed with a builder.

        Returns:
            TestResult: The updated test result.

        Raises:
            TypeError: If keyword fields are given with a builder.
            ValueError: If no fields are given or a field cannot be updated.
        """
        update_request = _test_result_update(test_result, fields)
        return TestResult.from_protobuf(
            self._get_data_store_client().update_test_result(update_request)
        )

    @overload
    def update_step(self, step: StepUpdateBuilder, /) -> Step: ...

    @overload
    def update_step(
        self, step: Step | str | UUID, /, **fields: Unpack[StepUpdateFields]
    ) -> Step: ...

    def update_step(
        self, step: Step | StepUpdateBuilder | str | UUID, /, **fields: Unpack[StepUpdateFields]
    ) -> Step:
        """Update mutable step fields.

        Args:
            step: What to update. One of:

                * A StepUpdateBuilder. Only the fields selected on the builder
                  change.
                * An ID or a Step with keyword fields, such as notes="...".
                  Only those fields change. A value of None clears the field.
                * A Step on its own. Every updatable field is set from it, so
                  empty fields are cleared. Stage 2 fields are sent only when
                  they have a value. When both test_id and test are set, only
                  test_id is sent.

            **fields: The fields to change. Not allowed with a builder.

        Returns:
            Step: The updated step.

        Raises:
            TypeError: If keyword fields are given with a builder.
            ValueError: If no fields are given or a field cannot be updated.
        """
        update_request = _step_update(step, fields)
        return Step.from_protobuf(self._get_data_store_client().update_step(update_request))

    @overload
    def update_measurement(self, measurement: MeasurementUpdateBuilder, /) -> Measurement: ...

    @overload
    def update_measurement(
        self, measurement: Measurement | str | UUID, /, **fields: Unpack[MeasurementUpdateFields]
    ) -> Measurement: ...

    def update_measurement(
        self,
        measurement: Measurement | MeasurementUpdateBuilder | str | UUID,
        /,
        **fields: Unpack[MeasurementUpdateFields],
    ) -> Measurement:
        """Update mutable measurement fields.

        The value, units, and limits cannot be updated.

        Args:
            measurement: What to update. One of:

                * A MeasurementUpdateBuilder. Only the fields selected on the
                  builder change.
                * An ID or a Measurement with keyword fields, such as
                  notes="...". Only those fields change. A value of None
                  clears the field.
                * A Measurement on its own. Every updatable field is set from
                  it, so empty fields are cleared. duration is sent only when
                  it has a value.

            **fields: The fields to change. Not allowed with a builder.

        Returns:
            Measurement: The updated measurement metadata.

        Raises:
            TypeError: If keyword fields are given with a builder.
            ValueError: If no fields are given or a field cannot be updated.
        """
        update_request = _measurement_update(measurement, fields)
        return Measurement.from_protobuf(
            self._get_data_store_client().update_measurement(update_request)
        )

    @overload
    def batch_update_test_results(
        self, updates: Mapping[UUID, TestResultUpdateFields]
    ) -> Sequence[TestResult]: ...

    @overload
    def batch_update_test_results(
        self, updates: Mapping[str, TestResultUpdateFields]
    ) -> Sequence[TestResult]: ...

    @overload
    def batch_update_test_results(
        self, updates: Iterable[TestResult | TestResultUpdateBuilder]
    ) -> Sequence[TestResult]: ...

    def batch_update_test_results(
        self,
        updates: (
            Mapping[str, TestResultUpdateFields]
            | Mapping[UUID, TestResultUpdateFields]
            | Iterable[TestResult | TestResultUpdateBuilder]
        ),
    ) -> Sequence[TestResult]:
        """Update multiple test results in one atomic call.

        Args:
            updates: Either the fields to change, keyed by test result ID, or
                builders and test results. Each item follows the
                update_test_result rules.

        Returns:
            Sequence[TestResult]: The updated test results, in request order.

        Raises:
            ValueError: If no updates are given, or an update has no fields or
                a field that cannot be updated.
        """
        requests = [
            _test_result_update(target, fields) for target, fields in _update_items(updates)
        ]
        batch_request = BatchUpdateTestResultsRequest(requests=requests)
        batch_response = self._get_data_store_client().batch_update_test_results(batch_request)
        return [TestResult.from_protobuf(proto) for proto in batch_response.test_results]

    @overload
    def batch_update_steps(self, updates: Mapping[UUID, StepUpdateFields]) -> Sequence[Step]: ...

    @overload
    def batch_update_steps(self, updates: Mapping[str, StepUpdateFields]) -> Sequence[Step]: ...

    @overload
    def batch_update_steps(self, updates: Iterable[Step | StepUpdateBuilder]) -> Sequence[Step]: ...

    def batch_update_steps(
        self,
        updates: (
            Mapping[str, StepUpdateFields]
            | Mapping[UUID, StepUpdateFields]
            | Iterable[Step | StepUpdateBuilder]
        ),
    ) -> Sequence[Step]:
        """Update multiple steps in one atomic call.

        Args:
            updates: Either the fields to change, keyed by step ID, or builders
                and steps. Each item follows the update_step rules.

        Returns:
            Sequence[Step]: The updated steps, in request order.

        Raises:
            ValueError: If no updates are given, or an update has no fields or
                a field that cannot be updated.
        """
        requests = [_step_update(target, fields) for target, fields in _update_items(updates)]
        batch_request = BatchUpdateStepsRequest(requests=requests)
        batch_response = self._get_data_store_client().batch_update_steps(batch_request)
        return [Step.from_protobuf(proto) for proto in batch_response.steps]

    @overload
    def batch_update_measurements(
        self, updates: Mapping[UUID, MeasurementUpdateFields]
    ) -> Sequence[Measurement]: ...

    @overload
    def batch_update_measurements(
        self, updates: Mapping[str, MeasurementUpdateFields]
    ) -> Sequence[Measurement]: ...

    @overload
    def batch_update_measurements(
        self, updates: Iterable[Measurement | MeasurementUpdateBuilder]
    ) -> Sequence[Measurement]: ...

    def batch_update_measurements(
        self,
        updates: (
            Mapping[str, MeasurementUpdateFields]
            | Mapping[UUID, MeasurementUpdateFields]
            | Iterable[Measurement | MeasurementUpdateBuilder]
        ),
    ) -> Sequence[Measurement]:
        """Update multiple measurements in one atomic call.

        Args:
            updates: Either the fields to change, keyed by measurement ID, or
                builders and measurements. Each item follows the
                update_measurement rules.

        Returns:
            Sequence[Measurement]: The updated measurements, in request order.

        Raises:
            ValueError: If no updates are given, or an update has no fields or
                a field that cannot be updated.
        """
        requests = [
            _measurement_update(target, fields) for target, fields in _update_items(updates)
        ]
        batch_request = BatchUpdateMeasurementsRequest(requests=requests)
        batch_response = self._get_data_store_client().batch_update_measurements(batch_request)
        return [Measurement.from_protobuf(proto) for proto in batch_response.measurements]

    def add_test_result_metadata(
        self,
        test_result_id: str | UUID,
        *,
        software_item_ids: Iterable[str | UUID] = (),
        hardware_item_ids: Iterable[str | UUID] = (),
        test_adapter_ids: Iterable[str | UUID] = (),
    ) -> TestResult:
        """Link existing software items, hardware items, or test adapters to a test result.

        The items become available to the test result's measurements, but are not
        linked to them. Link an item to a specific measurement with
        add_measurement_metadata.

        Args:
            test_result_id: The ID of the test result.

            software_item_ids: The software item IDs to link.

            hardware_item_ids: The hardware item IDs to link.

            test_adapter_ids: The test adapter IDs to link.

        Returns:
            TestResult: The updated test result.
        """
        add_request = AddTestResultMetadataRequest(
            test_result_id=id_string(test_result_id),
            software_item_ids=id_list(software_item_ids, "software_item_ids"),
            hardware_item_ids=id_list(hardware_item_ids, "hardware_item_ids"),
            test_adapter_ids=id_list(test_adapter_ids, "test_adapter_ids"),
        )
        return TestResult.from_protobuf(
            self._get_data_store_client().add_test_result_metadata(add_request).test_result
        )

    def remove_test_result_metadata(
        self,
        test_result_id: str | UUID,
        *,
        software_item_ids: Iterable[str | UUID] = (),
        hardware_item_ids: Iterable[str | UUID] = (),
        test_adapter_ids: Iterable[str | UUID] = (),
    ) -> TestResult:
        """Unlink software items, hardware items, or test adapters from a test result.

        An item cannot be unlinked from a test result while a measurement of that
        test result still references it. Unlink it from those measurements first
        with remove_measurement_metadata.

        Args:
            test_result_id: The ID of the test result.

            software_item_ids: The software item IDs to unlink.

            hardware_item_ids: The hardware item IDs to unlink.

            test_adapter_ids: The test adapter IDs to unlink.

        Returns:
            TestResult: The updated test result.
        """
        remove_request = RemoveTestResultMetadataRequest(
            test_result_id=id_string(test_result_id),
            software_item_ids=id_list(software_item_ids, "software_item_ids"),
            hardware_item_ids=id_list(hardware_item_ids, "hardware_item_ids"),
            test_adapter_ids=id_list(test_adapter_ids, "test_adapter_ids"),
        )
        return TestResult.from_protobuf(
            self._get_data_store_client().remove_test_result_metadata(remove_request).test_result
        )

    def add_measurement_metadata(
        self,
        measurement_id: str | UUID,
        *,
        software_item_ids: Iterable[str | UUID] = (),
        hardware_item_ids: Iterable[str | UUID] = (),
        test_adapter_ids: Iterable[str | UUID] = (),
    ) -> Measurement:
        """Link software items, hardware items, or test adapters to a measurement.

        Each item must already be linked to the measurement's owning test result.

        Args:
            measurement_id: The ID of the measurement.

            software_item_ids: The software item IDs to link.

            hardware_item_ids: The hardware item IDs to link.

            test_adapter_ids: The test adapter IDs to link.

        Returns:
            Measurement: The updated measurement.
        """
        add_request = AddMeasurementMetadataRequest(
            measurement_id=id_string(measurement_id),
            software_item_ids=id_list(software_item_ids, "software_item_ids"),
            hardware_item_ids=id_list(hardware_item_ids, "hardware_item_ids"),
            test_adapter_ids=id_list(test_adapter_ids, "test_adapter_ids"),
        )
        return Measurement.from_protobuf(
            self._get_data_store_client().add_measurement_metadata(add_request).measurement
        )

    def remove_measurement_metadata(
        self,
        measurement_id: str | UUID,
        *,
        software_item_ids: Iterable[str | UUID] = (),
        hardware_item_ids: Iterable[str | UUID] = (),
        test_adapter_ids: Iterable[str | UUID] = (),
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
            measurement_id=id_string(measurement_id),
            software_item_ids=id_list(software_item_ids, "software_item_ids"),
            hardware_item_ids=id_list(hardware_item_ids, "hardware_item_ids"),
            test_adapter_ids=id_list(test_adapter_ids, "test_adapter_ids"),
        )
        return Measurement.from_protobuf(
            self._get_data_store_client().remove_measurement_metadata(remove_request).measurement
        )

    def delete_test_result(
        self, test_result: TestResult | str | UUID, /, *, force: bool = False
    ) -> None:
        """Delete a test result.

        Args:
            test_result: The test result to delete, or its ID.

            force: If True, also delete the steps, measurements, and conditions that the
                test result owns. If False, the service rejects the delete with
                FAILED_PRECONDITION when owned children exist.
        """
        delete_request = DeleteTestResultRequest(
            test_result_id=_resource_id(test_result), force=force
        )
        self._get_data_store_client().delete_test_result(delete_request)

    def delete_step(self, step: Step | str | UUID, /, *, force: bool = False) -> None:
        """Delete a step.

        A step that has child steps cannot be deleted.

        Args:
            step: The step to delete, or its ID.

            force: If True, also delete the measurements of the step. If False, the
                service rejects the delete with FAILED_PRECONDITION when measurements exist.
        """
        delete_request = DeleteStepRequest(step_id=_resource_id(step), force=force)
        self._get_data_store_client().delete_step(delete_request)

    def delete_measurement(self, measurement: Measurement | str | UUID, /) -> None:
        """Delete a measurement.

        Args:
            measurement: The measurement to delete, or its ID.
        """
        delete_request = DeleteMeasurementRequest(measurement_id=_resource_id(measurement))
        self._get_data_store_client().delete_measurement(delete_request)

    def batch_delete_test_results(
        self,
        test_results: Iterable[TestResult | str | UUID],
        *,
        force: bool | Iterable[bool] = False,
    ) -> None:
        """Delete multiple test results in one atomic call.

        Args:
            test_results: The test results to delete, or their IDs.

            force: One flag for all test results, or one flag per test result.
                See delete_test_result for details on force behavior.

        Raises:
            ValueError: If one flag per item is given and the counts differ.
        """
        batch_request = BatchDeleteTestResultsRequest(
            requests=[
                DeleteTestResultRequest(test_result_id=test_result_id, force=item_force)
                for test_result_id, item_force in _with_force(test_results, force, "test_results")
            ]
        )
        self._get_data_store_client().batch_delete_test_results(batch_request)

    def batch_delete_steps(
        self, steps: Iterable[Step | str | UUID], *, force: bool | Iterable[bool] = False
    ) -> None:
        """Delete multiple steps in one atomic call.

        Args:
            steps: The steps to delete, or their IDs. A step and its ancestor or
                descendant cannot be deleted in the same call.

            force: One flag for all steps, or one flag per step. See delete_step
                for details on force behavior.

        Raises:
            ValueError: If one flag per item is given and the counts differ.
        """
        batch_request = BatchDeleteStepsRequest(
            requests=[
                DeleteStepRequest(step_id=step_id, force=item_force)
                for step_id, item_force in _with_force(steps, force, "steps")
            ]
        )
        self._get_data_store_client().batch_delete_steps(batch_request)

    def batch_delete_measurements(self, measurements: Iterable[Measurement | str | UUID]) -> None:
        """Delete multiple measurements in one atomic call.

        Args:
            measurements: The measurements to delete, or their IDs.
        """
        batch_request = BatchDeleteMeasurementsRequest(
            requests=[
                DeleteMeasurementRequest(measurement_id=measurement_id)
                for measurement_id in _resource_ids(measurements, "measurements")
            ]
        )
        self._get_data_store_client().batch_delete_measurements(batch_request)

    def _get_data_store_client(self) -> DataStoreServiceClient:
        if self._closed:
            raise RuntimeError(self._DATA_STORE_CLIENT_CLOSED_ERROR)
        return self._data_store_client


def _read_mask(fields: Iterable[str]) -> FieldMask | None:
    # Send the field name of an enum member, not its str() representation.
    paths = [
        str(field.value) if isinstance(field, Enum) else field
        for field in string_list(fields, "read_fields")
    ]
    return FieldMask(paths=paths) if paths else None


def _with_force(
    resources: Iterable[TestResult | Step | str | UUID], force: bool | Iterable[bool], name: str
) -> list[tuple[str, bool]]:
    id_list = _resource_ids(resources, name)
    if isinstance(force, bool):
        return [(resource_id, force) for resource_id in id_list]
    force_list = list(force)
    if len(force_list) != len(id_list):
        raise ValueError(
            f"Expected {len(id_list)} force flags, one per ID, but got {len(force_list)}."
        )
    return list(zip(id_list, force_list))


def _update_items(
    updates: Mapping[str, Mapping[str, Any]] | Mapping[UUID, Mapping[str, Any]] | Iterable[_T],
) -> list[tuple[_T | str | UUID, Mapping[str, Any]]]:
    items: list[tuple[_T | str | UUID, Mapping[str, Any]]]
    if isinstance(updates, Mapping):
        items = [(resource_id, fields) for resource_id, fields in updates.items()]
    else:
        items = [(target, {}) for target in updates]
    if not items:
        raise ValueError("At least one update must be supplied for a batch update.")
    return items


def _test_result_update(
    target: TestResult | TestResultUpdateBuilder | str | UUID, fields: Mapping[str, Any]
) -> UpdateTestResultRequest:
    if isinstance(target, TestResultUpdateBuilder):
        _reject_builder_fields(fields)
        return target.build_update()
    if isinstance(target, TestResult) and not fields:
        fields = resource_update_fields(
            target,
            TestResultProto.DESCRIPTOR,
            TEST_RESULT_UPDATE_FIELDS,
            TEST_RESULT_RELATIONSHIPS,
        )
    test_result = TestResultProto(id=_resource_id(target))
    mask = populate_update(test_result, fields, TEST_RESULT_UPDATE_FIELDS)
    return UpdateTestResultRequest(test_result=test_result, update_mask=mask)


def _step_update(
    target: Step | StepUpdateBuilder | str | UUID, fields: Mapping[str, Any]
) -> UpdateStepRequest:
    if isinstance(target, StepUpdateBuilder):
        _reject_builder_fields(fields)
        return target.build_update()
    if isinstance(target, Step) and not fields:
        fields = resource_update_fields(
            target, StepProto.DESCRIPTOR, STEP_UPDATE_FIELDS, STEP_RELATIONSHIPS
        )
    step = StepProto(id=_resource_id(target))
    mask = populate_update(step, fields, STEP_UPDATE_FIELDS)
    return UpdateStepRequest(step=step, update_mask=mask)


def _measurement_update(
    target: Measurement | MeasurementUpdateBuilder | str | UUID, fields: Mapping[str, Any]
) -> UpdateMeasurementRequest:
    if isinstance(target, MeasurementUpdateBuilder):
        _reject_builder_fields(fields)
        return target.build_update()
    if isinstance(target, Measurement) and not fields:
        fields = resource_update_fields(
            target, MeasurementProto.DESCRIPTOR, MEASUREMENT_UPDATE_FIELDS, {}
        )
    measurement = MeasurementProto(id=_resource_id(target))
    mask = populate_update(measurement, fields, MEASUREMENT_UPDATE_FIELDS)
    return UpdateMeasurementRequest(measurement=measurement, update_mask=mask)


def _resource_id(target: TestResult | Step | Measurement | str | UUID) -> str:
    return id_string(target) if isinstance(target, (str, UUID)) else target.id


def _reject_builder_fields(fields: Mapping[str, Any]) -> None:
    if fields:
        raise TypeError(
            "Keyword fields cannot be combined with an update builder. "
            "Select the fields on the builder instead."
        )


def _resource_ids(
    resources: Iterable[TestResult | Step | Measurement | str | UUID], name: str
) -> list[str]:
    # A str is itself an iterable of one-character strings.
    if isinstance(resources, (str, UUID)):
        raise TypeError(
            f"{name} must be a list or other iterable of resources or IDs, "
            f"not a single {type(resources).__name__}."
        )
    return [_resource_id(resource) for resource in resources]


def _reject_model_fields(fields: Mapping[Any, Any], model: str, resource_name: str) -> None:
    if fields:
        raise TypeError(
            f"Pass either {model} or the {resource_name} fields as arguments, not both."
        )


def _measurement_from_fields(
    name: str, value: MeasurementValue, step_id: str | UUID, **fields: Any
) -> Measurement:
    return Measurement(name=name, value=value, step_id=step_id, **fields)
