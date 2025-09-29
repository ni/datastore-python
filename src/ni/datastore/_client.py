"""Datastore client for publishing and reading data."""

from __future__ import annotations

import datetime as std_datetime
import logging
from collections.abc import Iterable
from threading import Lock
from typing import Type, TypeVar, cast, overload
from urllib.parse import urlparse

import hightime as ht
from grpc import Channel
from ni.datamonikers.v1.client import MonikerClient
from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.datastore._types._alias import Alias
from ni.datastore._types._extension_schema import ExtensionSchema
from ni.datastore._types._hardware_item import HardwareItem
from ni.datastore._types._operator import Operator
from ni.datastore._types._published_condition import PublishedCondition
from ni.datastore._types._published_measurement import PublishedMeasurement
from ni.datastore._types._software_item import SoftwareItem
from ni.datastore._types._step import Step
from ni.datastore._types._test import Test
from ni.datastore._types._test_adapter import TestAdapter
from ni.datastore._types._test_description import TestDescription
from ni.datastore._types._test_result import TestResult
from ni.datastore._types._test_station import TestStation
from ni.datastore._types._uut import Uut
from ni.datastore._types._uut_instance import UutInstance
from ni.datastore.grpc_conversion import (
    populate_publish_condition_batch_request_values,
    populate_publish_condition_request_value,
    populate_publish_measurement_batch_request_values,
    populate_publish_measurement_request_value,
    unpack_and_convert_from_protobuf_any,
)
from ni.measurementlink.discovery.v1.client import DiscoveryClient
from ni.measurements.data.v1.client import DataStoreClient
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
from ni.measurements.metadata.v1.client import MetadataStoreClient
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
    hightime_datetime_to_protobuf,
)
from ni.protobuf.types.precision_timestamp_pb2 import PrecisionTimestamp
from ni_grpc_extensions.channelpool import GrpcChannelPool

TRead = TypeVar("TRead")

_logger = logging.getLogger(__name__)


class Client:
    """Datastore client for publishing and reading data."""

    __slots__ = (
        "_discovery_client",
        "_grpc_channel",
        "_grpc_channel_pool",
        "_data_store_client",
        "_data_store_client_lock",
        "_metadata_store_client",
        "_metadata_store_client_lock",
        "_moniker_clients_by_service_location",
        "_moniker_clients_lock",
    )

    _discovery_client: DiscoveryClient | None
    _grpc_channel: Channel | None
    _grpc_channel_pool: GrpcChannelPool | None
    _data_store_client: DataStoreClient | None
    _metadata_store_client: MetadataStoreClient | None
    _moniker_clients_by_service_location: dict[str, MonikerClient]
    _data_store_client_lock: Lock
    _metadata_store_client_lock: Lock
    _moniker_clients_lock: Lock

    def __init__(
        self,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel: Channel | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
    ) -> None:
        """Initialize the Client.

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
        self._metadata_store_client = None
        self._moniker_clients_by_service_location = {}

        self._data_store_client_lock = Lock()
        self._metadata_store_client_lock = Lock()
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
        populate_publish_condition_request_value(publish_request, value)
        publish_response = self._get_data_store_client().publish_condition(publish_request)
        return PublishedCondition.from_protobuf(publish_response.published_condition)

    def publish_condition_batch(
        self, condition_name: str, type: str, values: object, step_id: str
    ) -> PublishedCondition:
        """Publish a batch of N values for a condition to the data store."""
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
        populate_publish_measurement_request_value(publish_request, value)
        publish_request.timestamp.CopyFrom(
            self._get_publish_measurement_timestamp(publish_request, timestamp)
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
    ) -> Iterable[PublishedMeasurement]:
        """Publish a batch of N values of a measurement to the data store."""
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
        """Read data published to the data store."""
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
        """Create a step in the datastore."""
        create_request = CreateStepRequest(step=step.to_protobuf())
        create_response = self._get_data_store_client().create_step(create_request)
        return create_response.step_id

    def get_step(self, step_id: str) -> Step:
        """Get a step from the data store."""
        get_request = GetStepRequest(step_id=step_id)
        get_response = self._get_data_store_client().get_step(get_request)
        return Step.from_protobuf(get_response.step)

    def create_test_result(self, test_result: TestResult) -> str:
        """Create a test result in the data store."""
        create_request = CreateTestResultRequest(test_result=test_result.to_protobuf())
        create_response = self._get_data_store_client().create_test_result(create_request)
        return create_response.test_result_id

    def get_test_result(self, test_result_id: str) -> TestResult:
        """Get a test result from the data store."""
        get_request = GetTestResultRequest(test_result_id=test_result_id)
        get_response = self._get_data_store_client().get_test_result(get_request)
        return TestResult.from_protobuf(get_response.test_result)

    def query_conditions(self, odata_query: str) -> Iterable[PublishedCondition]:
        """Query conditions from the data store."""
        query_request = QueryConditionsRequest(odata_query=odata_query)
        query_response = self._get_data_store_client().query_conditions(query_request)
        return [
            PublishedCondition.from_protobuf(published_condition)
            for published_condition in query_response.published_conditions
        ]

    def query_measurements(self, odata_query: str) -> Iterable[PublishedMeasurement]:
        """Query measurements from the data store."""
        query_request = QueryMeasurementsRequest(odata_query=odata_query)
        query_response = self._get_data_store_client().query_measurements(query_request)
        return [
            PublishedMeasurement.from_protobuf(published_measurement)
            for published_measurement in query_response.published_measurements
        ]

    def query_steps(self, odata_query: str) -> Iterable[Step]:
        """Query steps from the data store."""
        query_request = QueryStepsRequest(odata_query=odata_query)
        query_response = self._get_data_store_client().query_steps(query_request)
        return [Step.from_protobuf(step) for step in query_response.steps]

    def create_uut_instance(self, uut_instance: UutInstance) -> str:
        """Create a UUT instance in the metadata store."""
        create_request = CreateUutInstanceRequest(uut_instance=uut_instance.to_protobuf())
        create_response = self._get_metadata_store_client().create_uut_instance(create_request)
        return create_response.uut_instance_id

    def get_uut_instance(self, uut_instance_id: str) -> UutInstance:
        """Get a UUT instance from the metadata store."""
        get_request = GetUutInstanceRequest(uut_instance_id=uut_instance_id)
        get_response = self._get_metadata_store_client().get_uut_instance(get_request)
        return UutInstance.from_protobuf(get_response.uut_instance)

    def query_uut_instances(self, odata_query: str) -> Iterable[UutInstance]:
        """Query UUT instances from the metadata store."""
        query_request = QueryUutInstancesRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_uut_instances(query_request)
        return [
            UutInstance.from_protobuf(uut_instance) for uut_instance in query_response.uut_instances
        ]

    def create_uut(self, uut: Uut) -> str:
        """Create a UUT in the metadata store."""
        create_request = CreateUutRequest(uut=uut.to_protobuf())
        create_response = self._get_metadata_store_client().create_uut(create_request)
        return create_response.uut_id

    def get_uut(self, uut_id: str) -> Uut:
        """Get a UUT from the metadata store."""
        get_request = GetUutRequest(uut_id=uut_id)
        get_response = self._get_metadata_store_client().get_uut(get_request)
        return Uut.from_protobuf(get_response.uut)

    def query_uuts(self, odata_query: str) -> Iterable[Uut]:
        """Query UUTs from the metadata store."""
        query_request = QueryUutsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_uuts(query_request)
        return [Uut.from_protobuf(uut) for uut in query_response.uuts]

    def create_operator(self, operator: Operator) -> str:
        """Create an operator in the metadata store."""
        create_request = CreateOperatorRequest(operator=operator.to_protobuf())
        create_response = self._get_metadata_store_client().create_operator(create_request)
        return create_response.operator_id

    def get_operator(self, operator_id: str) -> Operator:
        """Get an operator from the metadata store."""
        get_request = GetOperatorRequest(operator_id=operator_id)
        get_response = self._get_metadata_store_client().get_operator(get_request)
        return Operator.from_protobuf(get_response.operator)

    def query_operators(self, odata_query: str) -> Iterable[Operator]:
        """Query operators from the metadata store."""
        query_request = QueryOperatorsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_operators(query_request)
        return [Operator.from_protobuf(operator) for operator in query_response.operators]

    def create_test_description(self, test_description: TestDescription) -> str:
        """Create a test description in the metadata store."""
        create_request = CreateTestDescriptionRequest(
            test_description=test_description.to_protobuf()
        )
        create_response = self._get_metadata_store_client().create_test_description(create_request)
        return create_response.test_description_id

    def get_test_description(self, test_description_id: str) -> TestDescription:
        """Get a test description from the metadata store."""
        get_request = GetTestDescriptionRequest(test_description_id=test_description_id)
        get_response = self._get_metadata_store_client().get_test_description(get_request)
        return TestDescription.from_protobuf(get_response.test_description)

    def query_test_descriptions(self, odata_query: str) -> Iterable[TestDescription]:
        """Query test descriptions from the metadata store."""
        query_request = QueryTestDescriptionsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_test_descriptions(query_request)
        return [
            TestDescription.from_protobuf(test_description)
            for test_description in query_response.test_descriptions
        ]

    def create_test(self, test: Test) -> str:
        """Create a test in the metadata store."""
        create_request = CreateTestRequest(test=test.to_protobuf())
        create_response = self._get_metadata_store_client().create_test(create_request)
        return create_response.test_id

    def get_test(self, test_id: str) -> Test:
        """Get a test from the metadata store."""
        get_request = GetTestRequest(test_id=test_id)
        get_response = self._get_metadata_store_client().get_test(get_request)
        return Test.from_protobuf(get_response.test)

    def query_tests(self, odata_query: str) -> Iterable[Test]:
        """Query tests from the metadata store."""
        query_request = QueryTestsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_tests(query_request)
        return [Test.from_protobuf(test) for test in query_response.tests]

    def create_test_station(self, test_station: TestStation) -> str:
        """Create a test station in the metadata store."""
        create_request = CreateTestStationRequest(test_station=test_station.to_protobuf())
        create_response = self._get_metadata_store_client().create_test_station(create_request)
        return create_response.test_station_id

    def get_test_station(self, test_station_id: str) -> TestStation:
        """Get a test station from the metadata store."""
        get_request = GetTestStationRequest(test_station_id=test_station_id)
        get_response = self._get_metadata_store_client().get_test_station(get_request)
        return TestStation.from_protobuf(get_response.test_station)

    def query_test_stations(self, odata_query: str) -> Iterable[TestStation]:
        """Query test stations from the metadata store."""
        query_request = QueryTestStationsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_test_stations(query_request)
        return [
            TestStation.from_protobuf(test_station) for test_station in query_response.test_stations
        ]

    def create_hardware_item(self, hardware_item: HardwareItem) -> str:
        """Create a hardware item in the metadata store."""
        create_request = CreateHardwareItemRequest(hardware_item=hardware_item.to_protobuf())
        create_response = self._get_metadata_store_client().create_hardware_item(create_request)
        return create_response.hardware_item_id

    def get_hardware_item(self, hardware_item_id: str) -> HardwareItem:
        """Get a hardware item from the metadata store."""
        get_request = GetHardwareItemRequest(hardware_item_id=hardware_item_id)
        get_response = self._get_metadata_store_client().get_hardware_item(get_request)
        return HardwareItem.from_protobuf(get_response.hardware_item)

    def query_hardware_items(self, odata_query: str) -> Iterable[HardwareItem]:
        """Query hardware items from the metadata store."""
        query_request = QueryHardwareItemsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_hardware_items(query_request)
        return [
            HardwareItem.from_protobuf(hardware_item)
            for hardware_item in query_response.hardware_items
        ]

    def create_software_item(self, software_item: SoftwareItem) -> str:
        """Create a software item in the metadata store."""
        create_request = CreateSoftwareItemRequest(software_item=software_item.to_protobuf())
        create_response = self._get_metadata_store_client().create_software_item(create_request)
        return create_response.software_item_id

    def get_software_item(self, software_item_id: str) -> SoftwareItem:
        """Get a software item from the metadata store."""
        get_request = GetSoftwareItemRequest(software_item_id=software_item_id)
        get_response = self._get_metadata_store_client().get_software_item(get_request)
        return SoftwareItem.from_protobuf(get_response.software_item)

    def query_software_items(self, odata_query: str) -> Iterable[SoftwareItem]:
        """Query software items from the metadata store."""
        query_request = QuerySoftwareItemsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_software_items(query_request)
        return [
            SoftwareItem.from_protobuf(software_item)
            for software_item in query_response.software_items
        ]

    def create_test_adapter(self, test_adapter: TestAdapter) -> str:
        """Create a test adapter in the metadata store."""
        create_request = CreateTestAdapterRequest(test_adapter=test_adapter.to_protobuf())
        create_response = self._get_metadata_store_client().create_test_adapter(create_request)
        return create_response.test_adapter_id

    def get_test_adapter(self, test_adapter_id: str) -> TestAdapter:
        """Get a test adapter from the metadata store."""
        get_request = GetTestAdapterRequest(test_adapter_id=test_adapter_id)
        get_response = self._get_metadata_store_client().get_test_adapter(get_request)
        return TestAdapter.from_protobuf(get_response.test_adapter)

    def query_test_adapters(self, odata_query: str) -> Iterable[TestAdapter]:
        """Query test adapters from the metadata store."""
        query_request = QueryTestAdaptersRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_test_adapters(query_request)
        return [
            TestAdapter.from_protobuf(test_adapter) for test_adapter in query_response.test_adapters
        ]

    # TODO: Also support providing a file path?
    def register_schema(self, schema: str) -> str:
        """Register a schema in the metadata store."""
        register_request = RegisterSchemaRequest(schema=schema)
        register_response = self._get_metadata_store_client().register_schema(register_request)
        return register_response.schema_id

    def list_schemas(self) -> Iterable[ExtensionSchema]:
        """List all schemas in the metadata store."""
        list_request = ListSchemasRequest()
        list_response = self._get_metadata_store_client().list_schemas(list_request)
        return [ExtensionSchema.from_protobuf(schema) for schema in list_response.schemas]

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
            create_request.uut_instance.CopyFrom(alias_target.to_protobuf())
        elif isinstance(alias_target, Uut):
            create_request.uut.CopyFrom(alias_target.to_protobuf())
        elif isinstance(alias_target, HardwareItem):
            create_request.hardware_item.CopyFrom(alias_target.to_protobuf())
        elif isinstance(alias_target, SoftwareItem):
            create_request.software_item.CopyFrom(alias_target.to_protobuf())
        elif isinstance(alias_target, Operator):
            create_request.operator.CopyFrom(alias_target.to_protobuf())
        elif isinstance(alias_target, TestDescription):
            create_request.test_description.CopyFrom(alias_target.to_protobuf())
        elif isinstance(alias_target, Test):
            create_request.test.CopyFrom(alias_target.to_protobuf())
        elif isinstance(alias_target, TestAdapter):
            create_request.test_adapter.CopyFrom(alias_target.to_protobuf())
        elif isinstance(alias_target, TestStation):
            create_request.test_station.CopyFrom(alias_target.to_protobuf())
        response = self._get_metadata_store_client().create_alias(create_request)
        return Alias.from_protobuf(response.alias)

    def get_alias(self, alias_name: str) -> Alias:
        """Get an alias from the metadata store."""
        get_request = GetAliasRequest(alias_name=alias_name)
        get_response = self._get_metadata_store_client().get_alias(get_request)
        return Alias.from_protobuf(get_response.alias)

    def delete_alias(self, alias_name: str) -> bool:
        """Delete an alias from the metadata store."""
        delete_request = DeleteAliasRequest(alias_name=alias_name)
        delete_response = self._get_metadata_store_client().delete_alias(delete_request)
        return delete_response.unregistered

    def query_aliases(self, odata_query: str) -> Iterable[Alias]:
        """Query aliases from the metadata store."""
        query_request = QueryAliasesRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_aliases(query_request)
        return [Alias.from_protobuf(alias) for alias in query_response.aliases]

    def _get_data_store_client(self) -> DataStoreClient:
        if self._data_store_client is None:
            with self._data_store_client_lock:
                if self._data_store_client is None:
                    self._data_store_client = DataStoreClient(
                        discovery_client=self._discovery_client,
                        grpc_channel=self._grpc_channel,
                        grpc_channel_pool=self._grpc_channel_pool,
                    )
        return self._data_store_client

    def _get_metadata_store_client(self) -> MetadataStoreClient:
        if self._metadata_store_client is None:
            with self._metadata_store_client_lock:
                if self._metadata_store_client is None:
                    self._metadata_store_client = MetadataStoreClient(
                        discovery_client=self._discovery_client,
                        grpc_channel=self._grpc_channel,
                        grpc_channel_pool=self._grpc_channel_pool,
                    )
        return self._metadata_store_client

    def _get_moniker_client(self, service_location: str) -> MonikerClient:
        parsed_service_location = urlparse(service_location).netloc
        if parsed_service_location not in self._moniker_clients_by_service_location:
            with self._moniker_clients_lock:
                if parsed_service_location not in self._moniker_clients_by_service_location:
                    self._moniker_clients_by_service_location[parsed_service_location] = (
                        MonikerClient(
                            service_location=parsed_service_location,
                            grpc_channel_pool=self._grpc_channel_pool,
                        )
                    )
        return self._moniker_clients_by_service_location[parsed_service_location]

    @staticmethod
    def _get_publish_measurement_timestamp(
        publish_request: PublishMeasurementRequest, client_provided_timestamp: ht.datetime | None
    ) -> PrecisionTimestamp:
        no_client_timestamp_provided = client_provided_timestamp is None
        if no_client_timestamp_provided:
            publish_time = hightime_datetime_to_protobuf(ht.datetime.now(std_datetime.timezone.utc))
        else:
            publish_time = hightime_datetime_to_protobuf(
                cast(ht.datetime, client_provided_timestamp)
            )

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
