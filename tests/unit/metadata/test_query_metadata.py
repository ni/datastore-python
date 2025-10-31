"""Contains tests to validate the query_* methods in the metadata store."""

from __future__ import annotations

from typing import cast
from unittest.mock import NonCallableMock

from ni.datastore.metadata import (
    MetadataStoreClient,
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
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    HardwareItem as HardwareItemProto,
    Operator as OperatorProto,
    SoftwareItem as SoftwareItemProto,
    Test as TestProto,
    TestAdapter as TestAdapterProto,
    TestDescription as TestDescriptionProto,
    TestStation as TestStationProto,
    Uut as UutProto,
    UutInstance as UutInstanceProto,
)
from ni.measurements.metadata.v1.metadata_store_service_pb2 import (
    QueryHardwareItemsRequest,
    QueryHardwareItemsResponse,
    QueryOperatorsRequest,
    QueryOperatorsResponse,
    QuerySoftwareItemsRequest,
    QuerySoftwareItemsResponse,
    QueryTestDescriptionsRequest,
    QueryTestDescriptionsResponse,
    QueryTestAdaptersRequest,
    QueryTestAdaptersResponse,
    QueryTestsRequest,
    QueryTestsResponse,
    QueryTestStationsRequest,
    QueryTestStationsResponse,
    QueryUutInstancesRequest,
    QueryUutInstancesResponse,
    QueryUutsRequest,
    QueryUutsResponse,
)


def test___query_uut_instances___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    uut_instance = UutInstanceProto(
        id="uut_instance_id",
        uut_id="uut_id",
        serial_number="serial_number",
        manufacture_date="manufacture_date",
        firmware_version="firmware_version",
        hardware_version="hardware_version",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QueryUutInstancesResponse(uut_instances=[uut_instance])
    mocked_metadata_store_service_client.query_uut_instances.return_value = expected_response

    result = metadata_store_client.query_uut_instances(odata_query="request_query")

    args, __ = mocked_metadata_store_service_client.query_uut_instances.call_args
    request = cast(QueryUutInstancesRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [UutInstance.from_protobuf(uut_instance)]


def test___query_uuts___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    uut = UutProto(
        id="uut_id",
        model_name="model_name",
        family="family",
        manufacturers=None,
        part_number="part_number",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QueryUutsResponse(uuts=[uut])
    mocked_metadata_store_service_client.query_uuts.return_value = expected_response

    result = metadata_store_client.query_uuts(odata_query="request_query")

    args, __ = mocked_metadata_store_service_client.query_uuts.call_args
    request = cast(QueryUutsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [Uut.from_protobuf(uut)]


def test___query_operators___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    operator = OperatorProto(
        id="operator_id",
        name="operator_name",
        role="role",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QueryOperatorsResponse(operators=[operator])
    mocked_metadata_store_service_client.query_operators.return_value = expected_response

    result = metadata_store_client.query_operators(odata_query="request_query")

    args, __ = mocked_metadata_store_service_client.query_operators.call_args
    request = cast(QueryOperatorsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [Operator.from_protobuf(operator)]


def test___query_test_descriptions___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test_description = TestDescriptionProto(
        id="test_description_id",
        uut_id="uut_id",
        name="test_description_name",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QueryTestDescriptionsResponse(test_descriptions=[test_description])
    mocked_metadata_store_service_client.query_test_descriptions.return_value = expected_response

    result = metadata_store_client.query_test_descriptions(odata_query="request_query")

    args, __ = mocked_metadata_store_service_client.query_test_descriptions.call_args
    request = cast(QueryTestDescriptionsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [TestDescription.from_protobuf(test_description)]


def test___query_tests___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test = TestProto(
        id="test_id",
        name="test_name",
        description="description",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QueryTestsResponse(tests=[test])
    mocked_metadata_store_service_client.query_tests.return_value = expected_response

    result = metadata_store_client.query_tests(odata_query="request_query")

    args, __ = mocked_metadata_store_service_client.query_tests.call_args
    request = cast(QueryTestsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [Test.from_protobuf(test)]


def test___query_test_stations___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test_station = TestStationProto(
        id="test_station_id",
        name="test_station_name",
        asset_identifier="asset_identifier",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QueryTestStationsResponse(test_stations=[test_station])
    mocked_metadata_store_service_client.query_test_stations.return_value = expected_response

    result = metadata_store_client.query_test_stations(odata_query="request_query")

    args, __ = mocked_metadata_store_service_client.query_test_stations.call_args
    request = cast(QueryTestStationsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [TestStation.from_protobuf(test_station)]


def test___query_hardware_items___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    hardware_item = HardwareItemProto(
        id="hardware_item_id",
        manufacturer="manufacturer",
        model="model",
        serial_number="serial_number",
        part_number="part_number",
        asset_identifier="asset_identifier",
        calibration_due_date="calibration_due_date",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QueryHardwareItemsResponse(hardware_items=[hardware_item])
    mocked_metadata_store_service_client.query_hardware_items.return_value = expected_response

    result = metadata_store_client.query_hardware_items(odata_query="request_query")

    args, __ = mocked_metadata_store_service_client.query_hardware_items.call_args
    request = cast(QueryHardwareItemsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [HardwareItem.from_protobuf(hardware_item)]


def test___query_software_items___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    software_item = SoftwareItemProto(
        id="software_item_id",
        product="product",
        version="version",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QuerySoftwareItemsResponse(software_items=[software_item])
    mocked_metadata_store_service_client.query_software_items.return_value = expected_response

    result = metadata_store_client.query_software_items(odata_query="request_query")

    args, __ = mocked_metadata_store_service_client.query_software_items.call_args
    request = cast(QuerySoftwareItemsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [SoftwareItem.from_protobuf(software_item)]


def test___query_test_adapters___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test_adapter = TestAdapterProto(
        id="test_adapter_id",
        name="test_adapter_name",
        manufacturer="manufacturer",
        model="model",
        serial_number="serial_number",
        part_number="part_number",
        asset_identifier="asset_identifier",
        calibration_due_date="calibration_due_date",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QueryTestAdaptersResponse(test_adapters=[test_adapter])
    mocked_metadata_store_service_client.query_test_adapters.return_value = expected_response

    result = metadata_store_client.query_test_adapters(odata_query="request_query")

    args, __ = mocked_metadata_store_service_client.query_test_adapters.call_args
    request = cast(QueryTestAdaptersRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [TestAdapter.from_protobuf(test_adapter)]
