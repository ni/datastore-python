"""Datastore client for publishing and reading data."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import timezone
from threading import Lock
from typing import Type, TypeVar, overload
from urllib.parse import urlparse

import numpy as np
from google.protobuf.any_pb2 import Any
from ni.datamonikers.v1.client import MonikerClient
from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.measurements.data.v1.client import DataStoreClient
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    PublishedCondition,
    PublishedMeasurement,
    Step,
    TestResult,
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
from ni.measurements.metadata.v1.client import MetadataStoreClient
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    Alias,
    ExtensionSchema,
    HardwareItem,
    Operator,
    SoftwareItem,
    Test,
    TestAdapter,
    TestDescription,
    TestStation,
    Uut,
    UutInstance,
)
from ni.measurements.metadata.v1.metadata_store_service_pb2 import (
    CreateAliasRequest,
    CreateHardwareItemRequest,
    CreateOperatorRequest,
    CreateSoftwareItemRequest,
    CreateTestAdapterRequest,
    CreateTestDescriptionRequest,
    CreateTestRequest,
    CreateTestStationRequest,
    CreateUutInstanceRequest,
    CreateUutRequest,
    DeleteAliasRequest,
    GetAliasRequest,
    GetHardwareItemRequest,
    GetOperatorRequest,
    GetSoftwareItemRequest,
    GetTestAdapterRequest,
    GetTestDescriptionRequest,
    GetTestRequest,
    GetTestStationRequest,
    GetUutInstanceRequest,
    GetUutRequest,
    ListSchemasRequest,
    QueryAliasesRequest,
    QueryHardwareItemsRequest,
    QueryOperatorsRequest,
    QuerySoftwareItemsRequest,
    QueryTestAdaptersRequest,
    QueryTestDescriptionsRequest,
    QueryTestsRequest,
    QueryTestStationsRequest,
    QueryUutInstancesRequest,
    QueryUutsRequest,
    RegisterSchemaRequest,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    bintime_datetime_to_protobuf,
)
from ni.protobuf.types.precision_timestamp_pb2 import PrecisionTimestamp
from ni.protobuf.types.scalar_conversion import scalar_to_protobuf
from ni.protobuf.types.vector_conversion import vector_from_protobuf, vector_to_protobuf
from ni.protobuf.types.vector_pb2 import Vector as VectorProto
from ni.protobuf.types.waveform_conversion import (
    digital_waveform_from_protobuf,
    digital_waveform_to_protobuf,
    float64_analog_waveform_from_protobuf,
    float64_analog_waveform_to_protobuf,
    float64_complex_waveform_from_protobuf,
    float64_complex_waveform_to_protobuf,
    float64_spectrum_from_protobuf,
    float64_spectrum_to_protobuf,
    int16_analog_waveform_from_protobuf,
    int16_analog_waveform_to_protobuf,
    int16_complex_waveform_from_protobuf,
    int16_complex_waveform_to_protobuf,
)
from ni.protobuf.types.waveform_pb2 import (
    DigitalWaveform as DigitalWaveformProto,
    DoubleAnalogWaveform,
    DoubleComplexWaveform,
    DoubleSpectrum,
    I16AnalogWaveform,
    I16ComplexWaveform,
)
from ni.protobuf.types.xydata_pb2 import DoubleXYData
from nitypes.bintime import DateTime
from nitypes.complex import ComplexInt32Base
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum

TRead = TypeVar("TRead")

_logger = logging.getLogger(__name__)


class Client:
    """Datastore client for publishing and reading data."""

    __slots__ = (
        "_data_store_client",
        "_metadata_store_client",
        "_moniker_clients_by_service_location",
        "_moniker_clients_lock",
    )

    _data_store_client: DataStoreClient
    _metadata_store_client: MetadataStoreClient
    _moniker_clients_by_service_location: dict[str, MonikerClient]
    _moniker_clients_lock: Lock

    def __init__(
        self,
        data_store_client: DataStoreClient | None = None,
        metadata_store_client: MetadataStoreClient | None = None,
        moniker_clients_by_service_location: dict[str, MonikerClient] | None = None,
    ) -> None:
        """Initialize the Client."""
        self._data_store_client = data_store_client or DataStoreClient()
        self._metadata_store_client = metadata_store_client or MetadataStoreClient()
        self._moniker_clients_by_service_location = moniker_clients_by_service_location or {}
        self._moniker_clients_lock = Lock()

    def publish_condition(
        self,
        condition_name: str,
        type: str,
        value: object,
        step_id: str,
    ) -> PublishedCondition:
        """Publish a condition value to the data store."""
        publish_request = PublishConditionRequest(
            condition_name=condition_name,
            type=type,
            step_id=step_id,
        )
        self._populate_publish_condition_request_value(publish_request, value)
        publish_response = self._data_store_client.publish_condition(publish_request)
        return publish_response.published_condition

    def publish_condition_batch(
        self, condition_name: str, type: str, values: object, step_id: str
    ) -> PublishedCondition:
        """Publish a batch of N values for a condition to the data store."""
        publish_request = PublishConditionBatchRequest(
            condition_name=condition_name,
            type=type,
            step_id=step_id,
        )
        self._populate_publish_condition_batch_request_values(publish_request, values)
        publish_response = self._data_store_client.publish_condition_batch(publish_request)
        return publish_response.published_condition

    def publish_measurement(
        self,
        measurement_name: str,
        value: object,  # More strongly typed Union[bool, AnalogWaveform] can be used if needed
        step_id: str,
        timestamp: DateTime | None = None,
        outcome: Outcome.ValueType = Outcome.OUTCOME_UNSPECIFIED,
        error_information: ErrorInformation | None = None,
        hardware_item_ids: Iterable[str] = tuple(),
        test_adapter_ids: Iterable[str] = tuple(),
        software_item_ids: Iterable[str] = tuple(),
        notes: str = "",
    ) -> PublishedMeasurement:
        """Publish a measurement value to the data store."""
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
        self._populate_publish_measurement_request_value(publish_request, value)
        publish_request.timestamp.CopyFrom(
            self._get_publish_measurement_timestamp(publish_request, timestamp)
        )
        publish_response = self._data_store_client.publish_measurement(publish_request)
        return publish_response.published_measurement

    def publish_measurement_batch(
        self,
        measurement_name: str,
        values: object,
        step_id: str,
        timestamps: Iterable[DateTime] = tuple(),
        outcomes: Iterable[Outcome.ValueType] = tuple(),
        error_information: Iterable[ErrorInformation] = tuple(),
        hardware_item_ids: Iterable[str] = tuple(),
        test_adapter_ids: Iterable[str] = tuple(),
        software_item_ids: Iterable[str] = tuple(),
    ) -> Iterable[PublishedMeasurement]:
        """Publish a batch of N values of a measurement to the data store."""
        publish_request = PublishMeasurementBatchRequest(
            measurement_name=measurement_name,
            step_id=step_id,
            timestamp=[bintime_datetime_to_protobuf(ts) for ts in timestamps],
            outcome=outcomes,
            error_information=list(error_information),
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
            software_item_ids=software_item_ids,
        )
        self._populate_publish_measurement_batch_request_values(publish_request, values)
        publish_response = self._data_store_client.publish_measurement_batch(publish_request)
        return publish_response.published_measurements

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
        """Read data published to the data store."""
        if isinstance(moniker_source, Moniker):
            moniker = moniker_source
        elif isinstance(moniker_source, PublishedMeasurement):
            moniker = moniker_source.moniker
        elif isinstance(moniker_source, PublishedCondition):
            moniker = moniker_source.moniker

        moniker_client = self._get_moniker_client(moniker.service_location)
        read_result = moniker_client.read_from_moniker(moniker)

        unpacked_data = self._unpack_data(read_result.value)
        converted_data = self._convert_from_protobuf(unpacked_data)
        if expected_type is not None and not isinstance(converted_data, expected_type):
            raise TypeError(f"Expected type {expected_type}, got {type(converted_data)}")
        return converted_data

    def create_step(self, step: Step) -> str:
        """Create a step in the datastore."""
        create_request = CreateStepRequest(step=step)
        create_response = self._data_store_client.create_step(create_request)
        return create_response.step_id

    def get_step(self, step_id: str) -> Step:
        """Get a step from the data store."""
        get_request = GetStepRequest(step_id=step_id)
        get_response = self._data_store_client.get_step(get_request)
        return get_response.step

    def create_test_result(self, test_result: TestResult) -> str:
        """Create a test result in the data store."""
        create_request = CreateTestResultRequest(test_result=test_result)
        create_response = self._data_store_client.create_test_result(create_request)
        return create_response.test_result_id

    def get_test_result(self, test_result_id: str) -> TestResult:
        """Get a test result from the data store."""
        get_request = GetTestResultRequest(test_result_id=test_result_id)
        get_response = self._data_store_client.get_test_result(get_request)
        return get_response.test_result

    def query_conditions(self, odata_query: str) -> Iterable[PublishedCondition]:
        """Query conditions from the data store."""
        query_request = QueryConditionsRequest(odata_query=odata_query)
        query_response = self._data_store_client.query_conditions(query_request)
        return query_response.published_conditions

    def query_measurements(self, odata_query: str) -> Iterable[PublishedMeasurement]:
        """Query measurements from the data store."""
        query_request = QueryMeasurementsRequest(odata_query=odata_query)
        query_response = self._data_store_client.query_measurements(query_request)
        return query_response.published_measurements

    def query_steps(self, odata_query: str) -> Iterable[Step]:
        """Query steps from the data store."""
        query_request = QueryStepsRequest(odata_query=odata_query)
        query_response = self._data_store_client.query_steps(query_request)
        return query_response.steps

    def create_uut_instance(self, uut_instance: UutInstance) -> str:
        """Create a UUT instance in the metadata store."""
        create_request = CreateUutInstanceRequest(uut_instance=uut_instance)
        create_response = self._metadata_store_client.create_uut_instance(create_request)
        return create_response.uut_instance_id

    def get_uut_instance(self, uut_instance_id: str) -> UutInstance:
        """Get a UUT instance from the metadata store."""
        get_request = GetUutInstanceRequest(uut_instance_id=uut_instance_id)
        get_response = self._metadata_store_client.get_uut_instance(get_request)
        return get_response.uut_instance

    def query_uut_instances(self, odata_query: str) -> Iterable[UutInstance]:
        """Query UUT instances from the metadata store."""
        query_request = QueryUutInstancesRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_uut_instances(query_request)
        return query_response.uut_instances

    def create_uut(self, uut: Uut) -> str:
        """Create a UUT in the metadata store."""
        create_request = CreateUutRequest(uut=uut)
        create_response = self._metadata_store_client.create_uut(create_request)
        return create_response.uut_id

    def get_uut(self, uut_id: str) -> Uut:
        """Get a UUT from the metadata store."""
        get_request = GetUutRequest(uut_id=uut_id)
        get_response = self._metadata_store_client.get_uut(get_request)
        return get_response.uut

    def query_uuts(self, odata_query: str) -> Iterable[Uut]:
        """Query UUTs from the metadata store."""
        query_request = QueryUutsRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_uuts(query_request)
        return query_response.uuts

    def create_operator(self, operator: Operator) -> str:
        """Create an operator in the metadata store."""
        create_request = CreateOperatorRequest(operator=operator)
        create_response = self._metadata_store_client.create_operator(create_request)
        return create_response.operator_id

    def get_operator(self, operator_id: str) -> Operator:
        """Get an operator from the metadata store."""
        get_request = GetOperatorRequest(operator_id=operator_id)
        get_response = self._metadata_store_client.get_operator(get_request)
        return get_response.operator

    def query_operators(self, odata_query: str) -> Iterable[Operator]:
        """Query operators from the metadata store."""
        query_request = QueryOperatorsRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_operators(query_request)
        return query_response.operators

    def create_test_description(self, test_description: TestDescription) -> str:
        """Create a test description in the metadata store."""
        create_request = CreateTestDescriptionRequest(test_description=test_description)
        create_response = self._metadata_store_client.create_test_description(create_request)
        return create_response.test_description_id

    def get_test_description(self, test_description_id: str) -> TestDescription:
        """Get a test description from the metadata store."""
        get_request = GetTestDescriptionRequest(test_description_id=test_description_id)
        get_response = self._metadata_store_client.get_test_description(get_request)
        return get_response.test_description

    def query_test_descriptions(self, odata_query: str) -> Iterable[TestDescription]:
        """Query test descriptions from the metadata store."""
        query_request = QueryTestDescriptionsRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_test_descriptions(query_request)
        return query_response.test_descriptions

    def create_test(self, test: Test) -> str:
        """Create a test in the metadata store."""
        create_request = CreateTestRequest(test=test)
        create_response = self._metadata_store_client.create_test(create_request)
        return create_response.test_id

    def get_test(self, test_id: str) -> Test:
        """Get a test from the metadata store."""
        get_request = GetTestRequest(test_id=test_id)
        get_response = self._metadata_store_client.get_test(get_request)
        return get_response.test

    def query_tests(self, odata_query: str) -> Iterable[Test]:
        """Query tests from the metadata store."""
        query_request = QueryTestsRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_tests(query_request)
        return query_response.tests

    def create_test_station(self, test_station: TestStation) -> str:
        """Create a test station in the metadata store."""
        create_request = CreateTestStationRequest(test_station=test_station)
        create_response = self._metadata_store_client.create_test_station(create_request)
        return create_response.test_station_id

    def get_test_station(self, test_station_id: str) -> TestStation:
        """Get a test station from the metadata store."""
        get_request = GetTestStationRequest(test_station_id=test_station_id)
        get_response = self._metadata_store_client.get_test_station(get_request)
        return get_response.test_station

    def query_test_stations(self, odata_query: str) -> Iterable[TestStation]:
        """Query test stations from the metadata store."""
        query_request = QueryTestStationsRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_test_stations(query_request)
        return query_response.test_stations

    def create_hardware_item(self, hardware_item: HardwareItem) -> str:
        """Create a hardware item in the metadata store."""
        create_request = CreateHardwareItemRequest(hardware_item=hardware_item)
        create_response = self._metadata_store_client.create_hardware_item(create_request)
        return create_response.hardware_item_id

    def get_hardware_item(self, hardware_item_id: str) -> HardwareItem:
        """Get a hardware item from the metadata store."""
        get_request = GetHardwareItemRequest(hardware_item_id=hardware_item_id)
        get_response = self._metadata_store_client.get_hardware_item(get_request)
        return get_response.hardware_item

    def query_hardware_items(self, odata_query: str) -> Iterable[HardwareItem]:
        """Query hardware items from the metadata store."""
        query_request = QueryHardwareItemsRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_hardware_items(query_request)
        return query_response.hardware_items

    def create_software_item(self, software_item: SoftwareItem) -> str:
        """Create a software item in the metadata store."""
        create_request = CreateSoftwareItemRequest(software_item=software_item)
        create_response = self._metadata_store_client.create_software_item(create_request)
        return create_response.software_item_id

    def get_software_item(self, software_item_id: str) -> SoftwareItem:
        """Get a software item from the metadata store."""
        get_request = GetSoftwareItemRequest(software_item_id=software_item_id)
        get_response = self._metadata_store_client.get_software_item(get_request)
        return get_response.software_item

    def query_software_items(self, odata_query: str) -> Iterable[SoftwareItem]:
        """Query software items from the metadata store."""
        query_request = QuerySoftwareItemsRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_software_items(query_request)
        return query_response.software_items

    def create_test_adapter(self, test_adapter: TestAdapter) -> str:
        """Create a test adapter in the metadata store."""
        create_request = CreateTestAdapterRequest(test_adapter=test_adapter)
        create_response = self._metadata_store_client.create_test_adapter(create_request)
        return create_response.test_adapter_id

    def get_test_adapter(self, test_adapter_id: str) -> TestAdapter:
        """Get a test adapter from the metadata store."""
        get_request = GetTestAdapterRequest(test_adapter_id=test_adapter_id)
        get_response = self._metadata_store_client.get_test_adapter(get_request)
        return get_response.test_adapter

    def query_test_adapters(self, odata_query: str) -> Iterable[TestAdapter]:
        """Query test adapters from the metadata store."""
        query_request = QueryTestAdaptersRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_test_adapters(query_request)
        return query_response.test_adapters

    # TODO: Also support providing a file path?
    def register_schema(self, schema: str) -> str:
        """Register a schema in the metadata store."""
        register_request = RegisterSchemaRequest(schema=schema)
        register_response = self._metadata_store_client.register_schema(register_request)
        return register_response.schema_id

    def list_schemas(self) -> Iterable[ExtensionSchema]:
        """List all schemas in the metadata store."""
        list_request = ListSchemasRequest()
        list_response = self._metadata_store_client.list_schemas(list_request)
        return list_response.schemas

    def create_alias(
        self,
        alias_name: str,
        alias_target: (
            UutInstance
            | Uut
            | HardwareItem
            | SoftwareItem
            | Operator
            | TestDescription
            | Test
            | TestAdapter
            | TestStation
        ),
    ) -> Alias:
        """Create an alias in the metadata store."""
        create_request = CreateAliasRequest(alias_name=alias_name)
        if isinstance(alias_target, UutInstance):
            create_request.uut_instance.CopyFrom(alias_target)
        elif isinstance(alias_target, Uut):
            create_request.uut.CopyFrom(alias_target)
        elif isinstance(alias_target, HardwareItem):
            create_request.hardware_item.CopyFrom(alias_target)
        elif isinstance(alias_target, SoftwareItem):
            create_request.software_item.CopyFrom(alias_target)
        elif isinstance(alias_target, Operator):
            create_request.operator.CopyFrom(alias_target)
        elif isinstance(alias_target, TestDescription):
            create_request.test_description.CopyFrom(alias_target)
        elif isinstance(alias_target, Test):
            create_request.test.CopyFrom(alias_target)
        elif isinstance(alias_target, TestAdapter):
            create_request.test_adapter.CopyFrom(alias_target)
        elif isinstance(alias_target, TestStation):
            create_request.test_station.CopyFrom(alias_target)
        response = self._metadata_store_client.create_alias(create_request)
        return response.alias

    def get_alias(self, alias_name: str) -> Alias:
        """Get an alias from the metadata store."""
        get_request = GetAliasRequest(alias_name=alias_name)
        get_response = self._metadata_store_client.get_alias(get_request)
        return get_response.alias

    def delete_alias(self, alias_name: str) -> bool:
        """Delete an alias from the metadata store."""
        delete_request = DeleteAliasRequest(alias_name=alias_name)
        delete_response = self._metadata_store_client.delete_alias(delete_request)
        return delete_response.unregistered

    def query_aliases(self, odata_query: str) -> Iterable[Alias]:
        """Query aliases from the metadata store."""
        query_request = QueryAliasesRequest(odata_query=odata_query)
        query_response = self._metadata_store_client.query_aliases(query_request)
        return query_response.aliases

    def _get_moniker_client(self, service_location: str) -> MonikerClient:
        parsed_service_location = urlparse(service_location).netloc
        with self._moniker_clients_lock:
            if parsed_service_location not in self._moniker_clients_by_service_location:
                self._moniker_clients_by_service_location[parsed_service_location] = MonikerClient(
                    service_location=parsed_service_location
                )
            return self._moniker_clients_by_service_location[parsed_service_location]

    @staticmethod
    def _get_publish_measurement_timestamp(
        publish_request: PublishMeasurementRequest, client_provided_timestamp: DateTime | None
    ) -> PrecisionTimestamp:
        no_client_timestamp_provided = client_provided_timestamp is None
        if no_client_timestamp_provided:
            publish_time = bintime_datetime_to_protobuf(DateTime.now(timezone.utc))
        else:
            publish_time = bintime_datetime_to_protobuf(client_provided_timestamp)

        waveform_t0: PrecisionTimestamp | None = None
        value_case = publish_request.WhichOneof("value")
        if value_case == "double_analog_waveform":
            waveform_t0 = publish_request.double_analog_waveform.t0
        elif value_case == "i16_analog_waveform":
            waveform_t0 = publish_request.i16_analog_waveform.t0
        elif value_case == "double_complex_waveform":
            waveform_t0 = publish_request.double_complex_waveform.t0
        elif value_case == "i16_complex_waveform":
            waveform_t0 = publish_request.i16_complex_waveform.t0
        elif value_case == "digital_waveform":
            waveform_t0 = publish_request.digital_waveform.t0

        # If an initialized waveform t0 value is present
        if waveform_t0 is not None and waveform_t0 != PrecisionTimestamp():
            if no_client_timestamp_provided:
                # If the client did not provide a timestamp, use the waveform t0 value
                publish_time = waveform_t0
            elif publish_time != waveform_t0:
                raise ValueError(
                    "The provided timestamp does not match the waveform t0. Please provide a matching timestamp or "
                    "omit the timestamp to use the waveform t0."
                )
        return publish_time

    # TODO: We may wish to separate out some of the conversion code below.
    @staticmethod
    def _populate_publish_condition_request_value(
        publish_request: PublishConditionRequest, value: object
    ) -> None:
        # TODO: Determine whether we wish to support primitive types such as float
        # TODO: or require wrapping in a Scalar.
        if isinstance(value, bool):
            publish_request.scalar.bool_value = value
        elif isinstance(value, int):
            publish_request.scalar.sint32_value = value
        elif isinstance(value, float):
            publish_request.scalar.double_value = value
        elif isinstance(value, str):
            publish_request.scalar.string_value = value
        elif isinstance(value, Scalar):
            publish_request.scalar.CopyFrom(scalar_to_protobuf(value))
        else:
            raise TypeError(
                f"Unsupported condition value type: {type(value)}. Please consult the documentation."
            )

    @staticmethod
    def _populate_publish_condition_batch_request_values(
        publish_request: PublishConditionBatchRequest, values: object
    ) -> None:
        # TODO: Determine whether we wish to support primitive types such as a list of float
        if isinstance(values, Vector):
            publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))
        else:
            raise TypeError(
                f"Unsupported condition values type: {type(values)}. Please consult the documentation."
            )

    @staticmethod
    def _populate_publish_measurement_request_value(
        publish_request: PublishMeasurementRequest, value: object
    ) -> None:
        # TODO: Determine whether we wish to support primitive types such as float
        # TODO: or require wrapping in a Scalar.
        if isinstance(value, bool):
            publish_request.scalar.bool_value = value
        elif isinstance(value, int):
            publish_request.scalar.sint32_value = value
        elif isinstance(value, float):
            publish_request.scalar.double_value = value
        elif isinstance(value, str):
            publish_request.scalar.string_value = value
        elif isinstance(value, Scalar):
            publish_request.scalar.CopyFrom(scalar_to_protobuf(value))
        elif isinstance(value, Vector):
            publish_request.vector.CopyFrom(vector_to_protobuf(value))
        elif isinstance(value, AnalogWaveform):
            if value.dtype == np.float64:
                publish_request.double_analog_waveform.CopyFrom(
                    float64_analog_waveform_to_protobuf(value)
                )
            elif value.dtype == np.int16:
                publish_request.i16_analog_waveform.CopyFrom(
                    int16_analog_waveform_to_protobuf(value)
                )
            else:
                raise TypeError(f"Unsupported AnalogWaveform dtype: {value.dtype}")
        elif isinstance(value, ComplexWaveform):
            if value.dtype == np.complex128:
                publish_request.double_complex_waveform.CopyFrom(
                    float64_complex_waveform_to_protobuf(value)
                )
            elif value.dtype == ComplexInt32Base:
                publish_request.i16_complex_waveform.CopyFrom(
                    int16_complex_waveform_to_protobuf(value)
                )
            else:
                raise TypeError(f"Unsupported ComplexWaveform dtype: {value.dtype}")
        elif isinstance(value, Spectrum):
            if value.dtype == np.float64:
                publish_request.double_spectrum.CopyFrom(float64_spectrum_to_protobuf(value))
            else:
                raise TypeError(f"Unsupported Spectrum dtype: {value.dtype}")
        elif isinstance(value, DigitalWaveform):
            publish_request.digital_waveform.CopyFrom(digital_waveform_to_protobuf(value))
        else:
            raise TypeError(
                f"Unsupported measurement value type: {type(value)}. Please consult the documentation."
            )
        # TODO: Implement conversion from proper XYData type

    @staticmethod
    def _populate_publish_measurement_batch_request_values(
        publish_request: PublishMeasurementBatchRequest, values: object
    ) -> None:
        # TODO: Determine whether we wish to support primitive types such as a list of float
        if isinstance(values, Vector):
            publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))
        else:
            raise TypeError(
                f"Unsupported measurement values type: {type(values)}. Please consult the documentation."
            )

    @staticmethod
    def _unpack_data(read_value: Any) -> object:
        data_type_url = read_value.type_url

        data_type_prefix = "type.googleapis.com/"
        if data_type_url == data_type_prefix + DoubleAnalogWaveform.DESCRIPTOR.full_name:
            double_analog_waveform = DoubleAnalogWaveform()
            read_value.Unpack(double_analog_waveform)
            return double_analog_waveform
        elif data_type_url == data_type_prefix + I16AnalogWaveform.DESCRIPTOR.full_name:
            i16_analog_waveform = I16AnalogWaveform()
            read_value.Unpack(i16_analog_waveform)
            return i16_analog_waveform
        elif data_type_url == data_type_prefix + DoubleComplexWaveform.DESCRIPTOR.full_name:
            double_complex_waveform = DoubleComplexWaveform()
            read_value.Unpack(double_complex_waveform)
            return double_complex_waveform
        elif data_type_url == data_type_prefix + I16ComplexWaveform.DESCRIPTOR.full_name:
            i16_complex_waveform = I16ComplexWaveform()
            read_value.Unpack(i16_complex_waveform)
            return i16_complex_waveform
        elif data_type_url == data_type_prefix + DoubleSpectrum.DESCRIPTOR.full_name:
            spectrum = DoubleSpectrum()
            read_value.Unpack(spectrum)
            return spectrum
        elif data_type_url == data_type_prefix + DigitalWaveformProto.DESCRIPTOR.full_name:
            digital_waveform = DigitalWaveformProto()
            read_value.Unpack(digital_waveform)
            return digital_waveform
        elif data_type_url == data_type_prefix + DoubleXYData.DESCRIPTOR.full_name:
            xydata = DoubleXYData()
            read_value.Unpack(xydata)
            return xydata
        elif data_type_url == data_type_prefix + VectorProto.DESCRIPTOR.full_name:
            vector = VectorProto()
            read_value.Unpack(vector)
            return vector

        else:
            raise TypeError(f"Unsupported data type URL: {data_type_url}")

    @staticmethod
    def _convert_from_protobuf(unpacked_data: object) -> object:
        if isinstance(unpacked_data, DoubleAnalogWaveform):
            return float64_analog_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, I16AnalogWaveform):
            return int16_analog_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, DoubleComplexWaveform):
            return float64_complex_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, I16ComplexWaveform):
            return int16_complex_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, DoubleSpectrum):
            return float64_spectrum_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, DigitalWaveformProto):
            return digital_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, DoubleXYData):
            _logger.warning(
                "DoubleXYData conversion is not yet implemented. Returning the raw protobuf object."
            )
            return unpacked_data  # TODO: Implement conversion to proper XYData type
        elif isinstance(unpacked_data, VectorProto):
            return vector_from_protobuf(unpacked_data)
        else:
            raise TypeError(f"Unsupported unpacked data type: {type(unpacked_data)}")
