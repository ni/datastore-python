"""Data store client for publishing and reading data."""

from __future__ import annotations

import logging
import sys
from collections.abc import Iterable, Sequence
from threading import Lock
from types import TracebackType
from typing import TYPE_CHECKING, Type, TypeVar, overload
from urllib.parse import urlparse

import hightime as ht
from grpc import Channel
from ni.datamonikers.v1.client import MonikerClient
from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.datastore.data._grpc_conversion import (
    get_publish_measurement_timestamp,
    populate_publish_condition_batch_request_values,
    populate_publish_condition_request_value,
    populate_publish_measurement_batch_request_values,
    populate_publish_measurement_request_value,
    unpack_and_convert_from_protobuf_any,
)
from ni.datastore.data._types._published_condition import PublishedCondition
from ni.datastore.data._types._published_measurement import PublishedMeasurement
from ni.datastore.data._types._step import Step
from ni.datastore.data._types._test_result import TestResult
from ni.measurementlink.discovery.v1.client import DiscoveryClient
from ni.measurements.data.v1.client import DataStoreClient as DataStoreServiceClient
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
)
from ni.measurements.data.v1.data_store_service_pb2 import (
    CreateStepRequest,
    CreateTestResultRequest,
    GetStepRequest,
    GetTestResultRequest,
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
    QueryConditionsRequest,
    QueryMeasurementsRequest,
    QueryStepsRequest,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_to_protobuf,
)
from ni_grpc_extensions.channelpool import GrpcChannelPool

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

TRead = TypeVar("TRead")

_logger = logging.getLogger(__name__)


class DataStoreClient:
    """Data store client for publishing and reading data."""

    __slots__ = (
        "_closed",
        "_discovery_client",
        "_grpc_channel",
        "_grpc_channel_pool",
        "_data_store_client",
        "_data_store_client_lock",
        "_moniker_clients_by_service_location",
        "_moniker_clients_lock",
    )

    _DATA_STORE_CLIENT_CLOSED_ERROR = "This DataStoreClient has been closed. Create a new DataStoreClient for further interaction with the data store."

    _closed: bool
    _discovery_client: DiscoveryClient | None
    _grpc_channel: Channel | None
    _grpc_channel_pool: GrpcChannelPool | None
    _data_store_client: DataStoreServiceClient | None
    _moniker_clients_by_service_location: dict[str, MonikerClient]
    _data_store_client_lock: Lock
    _moniker_clients_lock: Lock

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
                discovery service resolution of the data store. (Note: Reading data from a moniker
                will still always use a channel corresponding to the service location specified by
                that moniker.)

            grpc_channel_pool: An optional gRPC channel pool (recommended).
        """
        self._discovery_client = discovery_client
        self._grpc_channel = grpc_channel
        self._grpc_channel_pool = grpc_channel_pool

        self._data_store_client = None
        self._moniker_clients_by_service_location = {}

        self._data_store_client_lock = Lock()
        self._moniker_clients_lock = Lock()

        self._closed = False

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

        with self._data_store_client_lock:
            if self._data_store_client is not None:
                self._data_store_client.close()
                self._data_store_client = None

        with self._moniker_clients_lock:
            for _, moniker_client in self._moniker_clients_by_service_location.items():
                moniker_client.close()
            self._moniker_clients_by_service_location.clear()

    def publish_condition(
        self,
        condition_name: str,
        type: str,
        value: object,
        step_id: str,
    ) -> PublishedCondition:
        """Publish a condition value to the data store.

        Args:
            condition_name: An identifier describing the condition value.
                For example, "Voltage" or "Temperature".

            type: The type of this condition. For example, "Upper Limit",
                "Environment", or "Setup".

            value: The single value for this condition to publish on the test
                step. This should be a scalar value that can be converted to
                the appropriate protobuf scalar type.

            step_id: The ID of the step associated with this condition. This
                value is expected to be a parsable GUID.

        Returns:
            PublishedCondition: The published condition containing:
                - A moniker for retrieving the condition data (returns a
                  Vector)
                - The unique ID of the condition for referencing in queries
                - Metadata including condition name, type, step ID and test
                  result ID
        """
        publish_request = PublishConditionRequest(
            condition_name=condition_name,
            type=type,
            step_id=step_id,
        )
        populate_publish_condition_request_value(publish_request, value)
        publish_response = self._get_data_store_client().publish_condition(publish_request)
        return PublishedCondition.from_protobuf(publish_response.published_condition)

    def publish_condition_batch(
        self, condition_name: str, type: str, values: object, step_id: str
    ) -> PublishedCondition:
        """Publish a batch of N values for a condition to the data store.

        Args:
            condition_name: An identifier describing the condition values.
                For example, "Voltage" or "Temperature".

            type: The type of this condition. For example, "Upper Limit",
                "Environment", or "Setup".

            values: The values for this condition across all publishes on the
                test step. This should be a Vector of N values.
            step_id: The ID of the step associated with this batch of condition
                values. This value is expected to be a parsable GUID.

        Returns:
            PublishedCondition: Represents all the values published with
                this call, containing:

                - A moniker for retrieving the condition data (returns a
                  Vector)
                - The unique ID of the condition for referencing in queries
                - Metadata including condition name, type, step ID and test
                  result ID
        """
        publish_request = PublishConditionBatchRequest(
            condition_name=condition_name,
            type=type,
            step_id=step_id,
        )
        populate_publish_condition_batch_request_values(publish_request, values)
        publish_response = self._get_data_store_client().publish_condition_batch(publish_request)
        return PublishedCondition.from_protobuf(publish_response.published_condition)

    def publish_measurement(
        self,
        measurement_name: str,
        value: object,  # More strongly typed Union[bool, AnalogWaveform] can be used if needed
        step_id: str,
        timestamp: ht.datetime | None = None,
        outcome: Outcome.ValueType = Outcome.OUTCOME_UNSPECIFIED,
        error_information: ErrorInformation | None = None,
        hardware_item_ids: Iterable[str] = tuple(),
        test_adapter_ids: Iterable[str] = tuple(),
        software_item_ids: Iterable[str] = tuple(),
        notes: str = "",
    ) -> PublishedMeasurement:
        """Publish a single measurement value associated with a test step.

        Args:
            measurement_name: The name used for associating/grouping
                conceptually alike measurements across multiple publish
                iterations. For example, "Temperature" can be used for
                associating temperature readings across multiple iterations.

            value: The value of the measurement being published. Supported types:

                - Scalar: Single float, int, str or boolean
                - Vector: Array of float, int, str or boolean values
                - DoubleAnalogWaveform: Analog waveform with double precision
                - DoubleXYData: XY coordinate data with double precision
                - I16AnalogWaveform: Analog waveform with 16-bit integer precision
                - DoubleComplexWaveform: Complex waveform with double precision
                - I16ComplexWaveform: Complex waveform with 16-bit integer precision
                - DoubleSpectrum: Frequency spectrum data with double precision
                - DigitalWaveform: Digital waveform data

            step_id: The ID of the step associated with this measurement. This
                value is expected to be a parsable GUID.

            timestamp: The timestamp of the measurement. If None, the current
                time will be used.

            outcome: The outcome of the measurement (PASSED, FAILED,
                INDETERMINATE, or UNSPECIFIED).

            error_information: Error or exception information in case of
                measurement failure.

            hardware_item_ids: The IDs of the hardware items associated with
                this measurement. These values are expected to be parsable
                GUIDs or aliases.

            test_adapter_ids: The IDs of the test adapters associated with this
                measurement. These values are expected to be parsable GUIDs or
                aliases.

            software_item_ids: The IDs of the software items associated with
                this measurement. These values are expected to be parsable
                GUIDs or aliases.

            notes: Any notes to be associated with the captured measurement.

        Returns:
            PublishedMeasurement: The moniker of the published measurement and
                its metadata, including:
                - A moniker for retrieving the measurement data
                - Associated conditions from the test step
                - Measurement metadata (name, type, timestamps, outcome)
                - Associated hardware, software, and test adapter IDs
        """
        publish_request = PublishMeasurementRequest(
            measurement_name=measurement_name,
            step_id=step_id,
            outcome=outcome,
            error_information=error_information,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
            software_item_ids=software_item_ids,
            notes=notes,
        )
        populate_publish_measurement_request_value(publish_request, value)
        publish_request.timestamp.CopyFrom(
            get_publish_measurement_timestamp(publish_request, timestamp)
        )
        publish_response = self._get_data_store_client().publish_measurement(publish_request)
        return PublishedMeasurement.from_protobuf(publish_response.published_measurement)

    def publish_measurement_batch(
        self,
        measurement_name: str,
        values: object,
        step_id: str,
        timestamps: Iterable[ht.datetime] = tuple(),
        outcomes: Iterable[Outcome.ValueType] = tuple(),
        error_information: Iterable[ErrorInformation] = tuple(),
        hardware_item_ids: Iterable[str] = tuple(),
        test_adapter_ids: Iterable[str] = tuple(),
        software_item_ids: Iterable[str] = tuple(),
    ) -> Sequence[PublishedMeasurement]:
        """Publish multiple scalar measurements at once for parametric sweeps.

        Args:
            measurement_name: The name used for associating/grouping
                conceptually alike measurements across multiple publish
                iterations. For example, "Temperature" can be used for
                associating temperature readings across multiple iterations.

            values: The values of the (scalar) measurement being published
                across N iterations.

            step_id: The ID of the step associated with this measurement. This
                value is expected to be a parsable GUID.

            timestamps: The timestamps corresponding to the N iterations of
                batched measurement being published. Can be empty (no timestamp
                info), single value (applied to all), or N values (one per
                measurement).

            outcomes: The outcomes corresponding to the N iterations of batched
                measurement being published. Can be empty (no outcome info),
                single value (applied to all), or N values (one per
                measurement).

            error_information: The error information corresponding to the N
                iterations of batched measurement being published. Can be empty
                (no error info), single value (applied to all), or N values
                (one per measurement).

            hardware_item_ids: The IDs of the hardware items associated with
                this measurement. These values are expected to be parsable
                GUIDs or aliases.

            test_adapter_ids: The IDs of the test adapters associated with this
                measurement. These values are expected to be parsable GUIDs or
                aliases.

            software_item_ids: The IDs of the software items associated with
                this measurement. These values are expected to be parsable
                GUIDs or aliases.

        Returns:
            Sequence[PublishedMeasurement]: The monikers of the published
                measurements and their corresponding metadata. NOTE: Using
                a Sequence is for future flexibility. This sequence
                will currently always have a single PublishedMeasurement
                returned.
        """
        publish_request = PublishMeasurementBatchRequest(
            measurement_name=measurement_name,
            step_id=step_id,
            timestamp=[hightime_datetime_to_protobuf(ts) for ts in timestamps],
            outcome=outcomes,
            error_information=error_information,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
            software_item_ids=software_item_ids,
        )
        populate_publish_measurement_batch_request_values(publish_request, values)
        publish_response = self._get_data_store_client().publish_measurement_batch(publish_request)
        return [
            PublishedMeasurement.from_protobuf(pm) for pm in publish_response.published_measurements
        ]

    @overload
    def read_data(
        self,
        moniker_source: Moniker | PublishedMeasurement | PublishedCondition,
        expected_type: Type[TRead],
    ) -> TRead: ...

    @overload
    def read_data(
        self,
        moniker_source: Moniker | PublishedMeasurement | PublishedCondition,
    ) -> object: ...

    def read_data(
        self,
        moniker_source: Moniker | PublishedMeasurement | PublishedCondition,
        expected_type: Type[TRead] | None = None,
    ) -> TRead | object:
        """Read data published to the data store.

        Args:
            moniker_source: The source from which to read data. Can be:
                - A Moniker directly
                - A PublishedMeasurement (uses its moniker)
                - A PublishedCondition (uses its moniker)

            expected_type: Optional type to validate the returned data against.
                If provided, a TypeError will be raised if the actual data type
                doesn't match.

        Returns:
            The data retrieved from the data store. The return type depends on
            what was originally published:
            - Scalar measurements return as Vectors
            - Other types are returned as originally published
            If expected_type is specified, the return value is guaranteed to be
            of that type.

        Raises:
            ValueError: If the moniker_source doesn't have a valid moniker.
            TypeError: If expected_type is provided and the actual data type
                doesn't match.
        """
        if isinstance(moniker_source, Moniker):
            moniker = moniker_source
        elif isinstance(moniker_source, PublishedMeasurement):
            if moniker_source.moniker is None:
                raise ValueError("PublishedMeasurement must have a Moniker to read data")
            moniker = moniker_source.moniker
        elif isinstance(moniker_source, PublishedCondition):
            if moniker_source.moniker is None:
                raise ValueError("PublishedCondition must have a Moniker to read data")
            moniker = moniker_source.moniker

        moniker_client = self._get_moniker_client(moniker.service_location)
        read_result = moniker_client.read_from_moniker(moniker)
        converted_data = unpack_and_convert_from_protobuf_any(read_result.value)
        if expected_type is not None and not isinstance(converted_data, expected_type):
            raise TypeError(f"Expected type {expected_type}, got {type(converted_data)}")
        return converted_data

    def create_step(self, step: Step) -> str:
        """Create a new step in the data store.

        A step is owned by a test result and is a logical grouping of published
        measurements and conditions. All measurements and conditions must be
        associated with a step.

        Args:
            step: The metadata of the step to be created.

        Returns:
            str: The identifier of the created step.
        """
        create_request = CreateStepRequest(step=step.to_protobuf())
        create_response = self._get_data_store_client().create_step(create_request)
        return create_response.step_id

    def get_step(self, step_id: str) -> Step:
        """Get the step associated with the given identifier.

        Args:
            step_id: The identifier of the desired step.

        Returns:
            Step: The metadata of the requested step.
        """
        get_request = GetStepRequest(step_id=step_id)
        get_response = self._get_data_store_client().get_step(get_request)
        return Step.from_protobuf(get_response.step)

    def create_test_result(self, test_result: TestResult) -> str:
        """Create a test result object for publishing measurements.

        Once a test result is created, you can publish an arbitrary number of
        measurements and conditions to a step which is owned by the test result.

        Args:
            test_result: The metadata of the test result to be created.

        Returns:
            str: The test result ID. Generated if not specified in the request.
        """
        create_request = CreateTestResultRequest(test_result=test_result.to_protobuf())
        create_response = self._get_data_store_client().create_test_result(create_request)
        return create_response.test_result_id

    def get_test_result(self, test_result_id: str) -> TestResult:
        """Get the test result associated with the given identifier.

        Args:
            test_result_id: The ID of the desired test result. This value is
                expected to be a parsable GUID.

        Returns:
            TestResult: The TestResult object that corresponds to the
                requested ID.
        """
        get_request = GetTestResultRequest(test_result_id=test_result_id)
        get_response = self._get_data_store_client().get_test_result(get_request)
        return TestResult.from_protobuf(get_response.test_result)

    def query_conditions(self, odata_query: str = "") -> Sequence[PublishedCondition]:
        """Query conditions using OData query syntax.

        Args:
            odata_query: An OData query string. Example: "$filter=name eq
                'Value'". An empty string will return all conditions. $expand,
                $count, and $select are not supported. For more information,
                see https://learn.microsoft.com/en-us/odata/concepts/
                queryoptions-overview.

        Returns:
            Sequence[PublishedCondition]: The list of matching conditions. Each
                item contains a moniker for retrieving the condition
                measurements, as well as the metadata associated with the
                condition.
        """
        query_request = QueryConditionsRequest(odata_query=odata_query)
        query_response = self._get_data_store_client().query_conditions(query_request)
        return [
            PublishedCondition.from_protobuf(published_condition)
            for published_condition in query_response.published_conditions
        ]

    def query_measurements(self, odata_query: str = "") -> Sequence[PublishedMeasurement]:
        """Query measurements using OData query syntax.

        Args:
            odata_query: An OData query string. Example: "$filter=name eq
                'Value'". An empty string will return all measurements.
                $expand, $count, and $select are not supported. For more
                information, see https://learn.microsoft.com/en-us/odata/
                concepts/queryoptions-overview.

        Returns:
            Sequence[PublishedMeasurement]: The list of matching measurements.
                Each item contains a moniker for retrieving the measurement, as
                well as the metadata associated with the measurement.
        """
        query_request = QueryMeasurementsRequest(odata_query=odata_query)
        query_response = self._get_data_store_client().query_measurements(query_request)
        return [
            PublishedMeasurement.from_protobuf(published_measurement)
            for published_measurement in query_response.published_measurements
        ]

    def query_steps(self, odata_query: str = "") -> Sequence[Step]:
        """Query for steps matching the given OData query.

        Args:
            odata_query: An OData query string. Example: "$filter=name eq
                'Value'". An empty string will return all steps. $expand,
                $count, and $select are not supported. For more information,
                see https://learn.microsoft.com/en-us/odata/concepts/
                queryoptions-overview.

        Returns:
            Sequence[Step]: The list of steps that match the query.
        """
        query_request = QueryStepsRequest(odata_query=odata_query)
        query_response = self._get_data_store_client().query_steps(query_request)
        return [Step.from_protobuf(step) for step in query_response.steps]

    def _get_data_store_client(self) -> DataStoreServiceClient:
        if self._closed:
            raise RuntimeError(self._DATA_STORE_CLIENT_CLOSED_ERROR)

        if self._data_store_client is None:
            with self._data_store_client_lock:
                if self._data_store_client is None:
                    self._data_store_client = self._instantiate_data_store_client()
        return self._data_store_client

    def _instantiate_data_store_client(self) -> DataStoreServiceClient:
        return DataStoreServiceClient(
            discovery_client=self._discovery_client,
            grpc_channel=self._grpc_channel,
            grpc_channel_pool=self._grpc_channel_pool,
        )

    def _get_moniker_client(self, service_location: str) -> MonikerClient:
        if self._closed:
            raise RuntimeError(self._DATA_STORE_CLIENT_CLOSED_ERROR)

        parsed_service_location = urlparse(service_location).netloc
        if parsed_service_location not in self._moniker_clients_by_service_location:
            with self._moniker_clients_lock:
                if parsed_service_location not in self._moniker_clients_by_service_location:
                    self._moniker_clients_by_service_location[parsed_service_location] = (
                        self._instantiate_moniker_client(parsed_service_location)
                    )
        return self._moniker_clients_by_service_location[parsed_service_location]

    def _instantiate_moniker_client(self, parsed_service_location: str) -> MonikerClient:
        return MonikerClient(
            service_location=parsed_service_location,
            grpc_channel_pool=self._grpc_channel_pool,
        )
