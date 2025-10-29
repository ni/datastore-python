"""Metadata store client for publishing and reading metadata."""

from __future__ import annotations

import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from threading import Lock
from types import TracebackType
from typing import TYPE_CHECKING

from grpc import Channel
from ni.datastore.metadata._types._alias import Alias
from ni.datastore.metadata._types._extension_schema import ExtensionSchema
from ni.datastore.metadata._types._hardware_item import HardwareItem
from ni.datastore.metadata._types._operator import Operator
from ni.datastore.metadata._types._software_item import SoftwareItem
from ni.datastore.metadata._types._test import Test
from ni.datastore.metadata._types._test_adapter import TestAdapter
from ni.datastore.metadata._types._test_description import TestDescription
from ni.datastore.metadata._types._test_station import TestStation
from ni.datastore.metadata._types._uut import Uut
from ni.datastore.metadata._types._uut_instance import UutInstance
from ni.measurementlink.discovery.v1.client import DiscoveryClient
from ni.measurements.metadata.v1.client import (
    MetadataStoreClient as MetadataStoreServiceClient,
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
from ni_grpc_extensions.channelpool import GrpcChannelPool

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

_logger = logging.getLogger(__name__)


class MetadataStoreClient:
    """Metadata store client for publishing and reading metadata."""

    __slots__ = (
        "_closed",
        "_discovery_client",
        "_grpc_channel",
        "_grpc_channel_pool",
        "_metadata_store_client",
        "_metadata_store_client_lock",
    )

    _METADATA_STORE_CLIENT_CLOSED_ERROR = "This MetadataStoreClient has been closed. Create a new MetadataStoreClient for further interaction with the metadata store."

    _closed: bool
    _discovery_client: DiscoveryClient | None
    _grpc_channel: Channel | None
    _grpc_channel_pool: GrpcChannelPool | None
    _metadata_store_client: MetadataStoreServiceClient | None
    _metadata_store_client_lock: Lock

    def __init__(
        self,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel: Channel | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
    ) -> None:
        """Initialize the MetadataStoreClient.

        Args:
            discovery_client: An optional discovery client (recommended).

            grpc_channel: An optional metadata store gRPC channel. Providing this channel
                will bypass discovery service resolution of the metadata store.

            grpc_channel_pool: An optional gRPC channel pool (recommended).
        """
        self._discovery_client = discovery_client
        self._grpc_channel = grpc_channel
        self._grpc_channel_pool = grpc_channel_pool

        self._metadata_store_client = None
        self._metadata_store_client_lock = Lock()

        self._closed = False

    def __enter__(self) -> Self:
        """Enter the runtime context of the metadata store client."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the runtime context of the metadata store client."""
        self.close()

    def close(self) -> None:
        """Close the metadata store client and clean up resources that it owns."""
        self._closed = True

        with self._metadata_store_client_lock:
            if self._metadata_store_client is not None:
                self._metadata_store_client.close()
                self._metadata_store_client = None

    def create_uut_instance(self, uut_instance: UutInstance) -> str:
        """Create a new UUT instance in the metadata store.

        Args:
            uut_instance: The metadata of the UUT instance to be created.

        Returns:
            str: The identifier of the created UUT instance.
        """
        create_request = CreateUutInstanceRequest(uut_instance=uut_instance.to_protobuf())
        create_response = self._get_metadata_store_client().create_uut_instance(create_request)
        return create_response.uut_instance_id

    def get_uut_instance(self, uut_instance_id: str) -> UutInstance:
        """Get the UUT instance associated with the given identifier.

        Args:
            uut_instance_id: The identifier of the desired UUT instance.

        Returns:
            UutInstance: The metadata of the requested UUT instance.
        """
        get_request = GetUutInstanceRequest(uut_instance_id=uut_instance_id)
        get_response = self._get_metadata_store_client().get_uut_instance(get_request)
        return UutInstance.from_protobuf(get_response.uut_instance)

    def query_uut_instances(self, odata_query: str = "") -> Sequence[UutInstance]:
        """Perform an OData query on UUT instances.

        Args:
            odata_query: An OData query string. Example: "$filter=name eq
                'Value'". $expand is not supported.

        Returns:
            Sequence[UutInstance]: The list of UUT instances that match the
                query.
        """
        query_request = QueryUutInstancesRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_uut_instances(query_request)
        return [
            UutInstance.from_protobuf(uut_instance) for uut_instance in query_response.uut_instances
        ]

    def create_uut(self, uut: Uut) -> str:
        """Create a new UUT in the metadata store.

        Args:
            uut: The metadata of the UUT to be created.

        Returns:
            str: The identifier of the created UUT.
        """
        create_request = CreateUutRequest(uut=uut.to_protobuf())
        create_response = self._get_metadata_store_client().create_uut(create_request)
        return create_response.uut_id

    def get_uut(self, uut_id: str) -> Uut:
        """Get the UUT associated with the given identifier.

        Args:
            uut_id: The identifier of the desired UUT.

        Returns:
            Uut: The metadata of the requested UUT.
        """
        get_request = GetUutRequest(uut_id=uut_id)
        get_response = self._get_metadata_store_client().get_uut(get_request)
        return Uut.from_protobuf(get_response.uut)

    def query_uuts(self, odata_query: str = "") -> Sequence[Uut]:
        """Perform an OData query on UUTs.

        Args:
            odata_query: An OData query string. Example: "$filter=name eq
                'Value'". $expand is not supported.

        Returns:
            Sequence[Uut]: The list of UUTs that match the query.
        """
        query_request = QueryUutsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_uuts(query_request)
        return [Uut.from_protobuf(uut) for uut in query_response.uuts]

    def create_operator(self, operator: Operator) -> str:
        """Create a new operator in the metadata store.

        Args:
            operator: The metadata of the operator to be created.

        Returns:
            str: The identifier of the created operator.
        """
        create_request = CreateOperatorRequest(operator=operator.to_protobuf())
        create_response = self._get_metadata_store_client().create_operator(create_request)
        return create_response.operator_id

    def get_operator(self, operator_id: str) -> Operator:
        """Get the operator associated with the given identifier.

        Args:
            operator_id: The identifier of the desired operator.

        Returns:
            Operator: The metadata of the requested operator.
        """
        get_request = GetOperatorRequest(operator_id=operator_id)
        get_response = self._get_metadata_store_client().get_operator(get_request)
        return Operator.from_protobuf(get_response.operator)

    def query_operators(self, odata_query: str = "") -> Sequence[Operator]:
        """Perform an OData query on operators.

        Args:
            odata_query: An OData query string. Example: "$filter=name eq
                'Value'". $expand is not supported.

        Returns:
            Sequence[Operator]: The list of operators that match the query.
        """
        query_request = QueryOperatorsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_operators(query_request)
        return [Operator.from_protobuf(operator) for operator in query_response.operators]

    def create_test_description(self, test_description: TestDescription) -> str:
        """Create a test description in the metadata store.

        Args:
            test_description: The metadata of the test description to be created.

        Returns:
            str: The identifier of the created test description.
        """
        create_request = CreateTestDescriptionRequest(
            test_description=test_description.to_protobuf()
        )
        create_response = self._get_metadata_store_client().create_test_description(create_request)
        return create_response.test_description_id

    def get_test_description(self, test_description_id: str) -> TestDescription:
        """Get a test description from the metadata store.

        Args:
            test_description_id: The identifier of the desired test description.

        Returns:
            TestDescription: The metadata of the requested test description.
        """
        get_request = GetTestDescriptionRequest(test_description_id=test_description_id)
        get_response = self._get_metadata_store_client().get_test_description(get_request)
        return TestDescription.from_protobuf(get_response.test_description)

    def query_test_descriptions(self, odata_query: str = "") -> Sequence[TestDescription]:
        """Query test descriptions from the metadata store.

        Args:
            odata_query: An OData query string. Example: "$filter=name eq
                'Value'". $expand is not supported.

        Returns:
            Sequence[TestDescription]: The list of test descriptions that match
                the query.
        """
        query_request = QueryTestDescriptionsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_test_descriptions(query_request)
        return [
            TestDescription.from_protobuf(test_description)
            for test_description in query_response.test_descriptions
        ]

    def create_test(self, test: Test) -> str:
        """Create a test in the metadata store.

        Args:
            test: The metadata of the test to be created.

        Returns:
            str: The identifier of the created test.
        """
        create_request = CreateTestRequest(test=test.to_protobuf())
        create_response = self._get_metadata_store_client().create_test(create_request)
        return create_response.test_id

    def get_test(self, test_id: str) -> Test:
        """Get a test from the metadata store.

        Args:
            test_id: The identifier of the desired test.

        Returns:
            Test: The metadata of the requested test.
        """
        get_request = GetTestRequest(test_id=test_id)
        get_response = self._get_metadata_store_client().get_test(get_request)
        return Test.from_protobuf(get_response.test)

    def query_tests(self, odata_query: str = "") -> Sequence[Test]:
        """Query tests from the metadata store."""
        query_request = QueryTestsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_tests(query_request)
        return [Test.from_protobuf(test) for test in query_response.tests]

    def create_test_station(self, test_station: TestStation) -> str:
        """Create a test station in the metadata store.

        Args:
            test_station: The metadata of the test station to be created.

        Returns:
            str: The identifier of the created test station.
        """
        create_request = CreateTestStationRequest(test_station=test_station.to_protobuf())
        create_response = self._get_metadata_store_client().create_test_station(create_request)
        return create_response.test_station_id

    def get_test_station(self, test_station_id: str) -> TestStation:
        """Get a test station from the metadata store.

        Args:
            test_station_id: The identifier of the desired test station.

        Returns:
            TestStation: The metadata of the requested test station.
        """
        get_request = GetTestStationRequest(test_station_id=test_station_id)
        get_response = self._get_metadata_store_client().get_test_station(get_request)
        return TestStation.from_protobuf(get_response.test_station)

    def query_test_stations(self, odata_query: str = "") -> Sequence[TestStation]:
        """Query test stations from the metadata store."""
        query_request = QueryTestStationsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_test_stations(query_request)
        return [
            TestStation.from_protobuf(test_station) for test_station in query_response.test_stations
        ]

    def create_hardware_item(self, hardware_item: HardwareItem) -> str:
        """Create a hardware item in the metadata store.

        Args:
            hardware_item: The metadata of the hardware item to be created.

        Returns:
            str: The identifier of the created hardware item.
        """
        create_request = CreateHardwareItemRequest(hardware_item=hardware_item.to_protobuf())
        create_response = self._get_metadata_store_client().create_hardware_item(create_request)
        return create_response.hardware_item_id

    def get_hardware_item(self, hardware_item_id: str) -> HardwareItem:
        """Get a hardware item from the metadata store.

        Args:
            hardware_item_id: The identifier of the desired hardware item.

        Returns:
            HardwareItem: The metadata of the requested hardware item.
        """
        get_request = GetHardwareItemRequest(hardware_item_id=hardware_item_id)
        get_response = self._get_metadata_store_client().get_hardware_item(get_request)
        return HardwareItem.from_protobuf(get_response.hardware_item)

    def query_hardware_items(self, odata_query: str = "") -> Sequence[HardwareItem]:
        """Query hardware items from the metadata store."""
        query_request = QueryHardwareItemsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_hardware_items(query_request)
        return [
            HardwareItem.from_protobuf(hardware_item)
            for hardware_item in query_response.hardware_items
        ]

    def create_software_item(self, software_item: SoftwareItem) -> str:
        """Create a software item in the metadata store.

        Args:
            software_item: The metadata of the software item to be created.

        Returns:
            str: The identifier of the created software item.
        """
        create_request = CreateSoftwareItemRequest(software_item=software_item.to_protobuf())
        create_response = self._get_metadata_store_client().create_software_item(create_request)
        return create_response.software_item_id

    def get_software_item(self, software_item_id: str) -> SoftwareItem:
        """Get a software item from the metadata store.

        Args:
            software_item_id: The identifier of the desired software item.

        Returns:
            SoftwareItem: The metadata of the requested software item.
        """
        get_request = GetSoftwareItemRequest(software_item_id=software_item_id)
        get_response = self._get_metadata_store_client().get_software_item(get_request)
        return SoftwareItem.from_protobuf(get_response.software_item)

    def query_software_items(self, odata_query: str = "") -> Sequence[SoftwareItem]:
        """Query software items from the metadata store."""
        query_request = QuerySoftwareItemsRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_software_items(query_request)
        return [
            SoftwareItem.from_protobuf(software_item)
            for software_item in query_response.software_items
        ]

    def create_test_adapter(self, test_adapter: TestAdapter) -> str:
        """Create a test adapter in the metadata store.

        Args:
            test_adapter: The metadata of the test adapter to be created.

        Returns:
            str: The identifier of the created test adapter.
        """
        create_request = CreateTestAdapterRequest(test_adapter=test_adapter.to_protobuf())
        create_response = self._get_metadata_store_client().create_test_adapter(create_request)
        return create_response.test_adapter_id

    def get_test_adapter(self, test_adapter_id: str) -> TestAdapter:
        """Get a test adapter from the metadata store.

        Args:
            test_adapter_id: The identifier of the desired test adapter.

        Returns:
            TestAdapter: The metadata of the requested test adapter.
        """
        get_request = GetTestAdapterRequest(test_adapter_id=test_adapter_id)
        get_response = self._get_metadata_store_client().get_test_adapter(get_request)
        return TestAdapter.from_protobuf(get_response.test_adapter)

    def query_test_adapters(self, odata_query: str = "") -> Sequence[TestAdapter]:
        """Query test adapters from the metadata store."""
        query_request = QueryTestAdaptersRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_test_adapters(query_request)
        return [
            TestAdapter.from_protobuf(test_adapter) for test_adapter in query_response.test_adapters
        ]

    def register_schema_from_file(self, schema_file_path: Path | str) -> str:
        """Register a schema obtained from the specified file in the metadata store.

        Args:
            schema_file_path: The path at which the schema file is located

        Raises:
            FileNotFoundError: If the schema file does not exist.
        """
        if isinstance(schema_file_path, str):
            schema_file_path = Path(schema_file_path)

        if not schema_file_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file_path}")

        schema_contents = schema_file_path.read_text(encoding="utf-8-sig")
        return self.register_schema(schema_contents=schema_contents)

    def register_schema(self, schema_contents: str) -> str:
        """Register a schema in the metadata store.

        Once a schema has been published, it cannot be modified or removed.

        Args:
            schema_contents: The contents of the JSON or TOML schema. This
                should be a well-formed JSON or TOML schema. Validation will
                be performed, and an error will be returned if the schema is
                not valid.

        Returns:
            str: The ID of the schema.
        """
        register_request = RegisterSchemaRequest(schema=schema_contents)
        register_response = self._get_metadata_store_client().register_schema(register_request)
        return register_response.schema_id

    def list_schemas(self) -> Sequence[ExtensionSchema]:
        """List the schemas that have been previously registered.

        Returns:
            Sequence[ExtensionSchema]: The list of registered schemas.
        """
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
        """Create (register) an alias of the specified metadata.

        The specified metadata must have already been created prior to the
        alias registration. This method may be called with an already
        registered alias name in order to update the target mapped for that
        existing alias.

        Args:
            alias_name: The alias name to register.

            alias_target: The metadata instance to alias. The metadata
                instance to alias must have already been created in the
                metadata store in order to register an alias for it.

        Returns:
            Alias: The created alias containing the alias name, target type,
                and target ID.
        """
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
        """Get an alias and its target (the underlying metadata it represents).

        Args:
            alias_name: The name of the alias to retrieve.

        Returns:
            Alias: The alias containing the alias name, target type, and
                target ID of the underlying metadata.
        """
        get_request = GetAliasRequest(alias_name=alias_name)
        get_response = self._get_metadata_store_client().get_alias(get_request)
        return Alias.from_protobuf(get_response.alias)

    def delete_alias(self, alias_name: str) -> bool:
        """Remove a registered alias.

        Args:
            alias_name: The name of the alias to unregister.

        Returns:
            bool: Whether the action resulted in the specified alias becoming
                unregistered. False if the alias does not exist.
        """
        delete_request = DeleteAliasRequest(alias_name=alias_name)
        delete_response = self._get_metadata_store_client().delete_alias(delete_request)
        return delete_response.unregistered

    def query_aliases(self, odata_query: str = "") -> Sequence[Alias]:
        """Perform an OData query on the registered aliases.

        Args:
            odata_query: An OData query string. Example: "$filter=name eq
                'Value'". $expand is not supported.

        Returns:
            Sequence[Alias]: The list of aliases that match the query.
        """
        query_request = QueryAliasesRequest(odata_query=odata_query)
        query_response = self._get_metadata_store_client().query_aliases(query_request)
        return [Alias.from_protobuf(alias) for alias in query_response.aliases]

    def _get_metadata_store_client(self) -> MetadataStoreServiceClient:
        if self._closed:
            raise RuntimeError(self._METADATA_STORE_CLIENT_CLOSED_ERROR)

        if self._metadata_store_client is None:
            with self._metadata_store_client_lock:
                if self._metadata_store_client is None:
                    self._metadata_store_client = self._instantiate_metadata_store_client()
        return self._metadata_store_client

    def _instantiate_metadata_store_client(self) -> MetadataStoreServiceClient:
        return MetadataStoreServiceClient(
            discovery_client=self._discovery_client,
            grpc_channel=self._grpc_channel,
            grpc_channel_pool=self._grpc_channel_pool,
        )
