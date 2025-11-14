"""Contains tests to validate the get_* methods in the metadata store."""

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
    GetHardwareItemRequest,
    GetHardwareItemResponse,
    GetOperatorRequest,
    GetOperatorResponse,
    GetSoftwareItemRequest,
    GetSoftwareItemResponse,
    GetTestAdapterRequest,
    GetTestAdapterResponse,
    GetTestDescriptionRequest,
    GetTestDescriptionResponse,
    GetTestRequest,
    GetTestResponse,
    GetTestStationRequest,
    GetTestStationResponse,
    GetUutInstanceRequest,
    GetUutInstanceResponse,
    GetUutRequest,
    GetUutResponse,
)


def test___get_uut_instance___calls_metadata_store_service_client(
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
        extension=None,
        schema_id="schema_id",
    )
    expected_response = GetUutInstanceResponse(uut_instance=uut_instance)
    mocked_metadata_store_service_client.get_uut_instance.return_value = expected_response

    result = metadata_store_client.get_uut_instance(uut_instance_id="request_id")

    args, __ = mocked_metadata_store_service_client.get_uut_instance.call_args
    request = cast(GetUutInstanceRequest, args[0])
    assert request.uut_instance_id == "request_id"
    assert result == UutInstance.from_protobuf(uut_instance)


def test___get_uut___calls_metadata_store_service_client(
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
        extension=None,
        schema_id="schema_id",
    )
    expected_response = GetUutResponse(uut=uut)
    mocked_metadata_store_service_client.get_uut.return_value = expected_response

    result = metadata_store_client.get_uut(uut_id="request_id")

    args, __ = mocked_metadata_store_service_client.get_uut.call_args
    request = cast(GetUutRequest, args[0])
    assert request.uut_id == "request_id"
    assert result == Uut.from_protobuf(uut)


def test___get_operator___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    operator = OperatorProto(
        id="operator_id",
        name="name",
        role="role",
        link="link",
        extension=None,
        schema_id="schema_id",
    )
    expected_response = GetOperatorResponse(operator=operator)
    mocked_metadata_store_service_client.get_operator.return_value = expected_response

    result = metadata_store_client.get_operator(operator_id="request_id")

    args, __ = mocked_metadata_store_service_client.get_operator.call_args
    request = cast(GetOperatorRequest, args[0])
    assert request.operator_id == "request_id"
    assert result == Operator.from_protobuf(operator)


def test___get_test_description___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test_description = TestDescriptionProto(
        id="test_description_id",
        uut_id="uut_id",
        name="name",
        link="link",
        extension=None,
        schema_id="schema_id",
    )
    expected_response = GetTestDescriptionResponse(test_description=test_description)
    mocked_metadata_store_service_client.get_test_description.return_value = expected_response

    result = metadata_store_client.get_test_description(test_description_id="request_id")

    args, __ = mocked_metadata_store_service_client.get_test_description.call_args
    request = cast(GetTestDescriptionRequest, args[0])
    assert request.test_description_id == "request_id"
    assert result == TestDescription.from_protobuf(test_description)


def test___get_test___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test = TestProto(
        id="test_id",
        name="name",
        description="description",
        extension=None,
        schema_id="schema_id",
    )
    expected_response = GetTestResponse(test=test)
    mocked_metadata_store_service_client.get_test.return_value = expected_response

    result = metadata_store_client.get_test(test_id="request_id")

    args, __ = mocked_metadata_store_service_client.get_test.call_args
    request = cast(GetTestRequest, args[0])
    assert request.test_id == "request_id"
    assert result == Test.from_protobuf(test)


def test___get_test_station___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test_station = TestStationProto(
        id="test_station_id",
        name="name",
        asset_identifier="asset_identifier",
        link="link",
        extension=None,
        schema_id="schema_id",
    )
    expected_response = GetTestStationResponse(test_station=test_station)
    mocked_metadata_store_service_client.get_test_station.return_value = expected_response

    result = metadata_store_client.get_test_station(test_station_id="request_id")

    args, __ = mocked_metadata_store_service_client.get_test_station.call_args
    request = cast(GetTestStationRequest, args[0])
    assert request.test_station_id == "request_id"
    assert result == TestStation.from_protobuf(test_station)


def test___get_hardware_item___calls_metadata_store_service_client(
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
        extension=None,
        schema_id="schema_id",
    )
    expected_response = GetHardwareItemResponse(hardware_item=hardware_item)
    mocked_metadata_store_service_client.get_hardware_item.return_value = expected_response

    result = metadata_store_client.get_hardware_item(hardware_item_id="request_id")

    args, __ = mocked_metadata_store_service_client.get_hardware_item.call_args
    request = cast(GetHardwareItemRequest, args[0])
    assert request.hardware_item_id == "request_id"
    assert result == HardwareItem.from_protobuf(hardware_item)


def test___get_software_item___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    software_item = SoftwareItemProto(
        id="software_item_id",
        product="product",
        version="version",
        link="link",
        extension=None,
        schema_id="schema_id",
    )
    expected_response = GetSoftwareItemResponse(software_item=software_item)
    mocked_metadata_store_service_client.get_software_item.return_value = expected_response

    result = metadata_store_client.get_software_item(software_item_id="request_id")

    args, __ = mocked_metadata_store_service_client.get_software_item.call_args
    request = cast(GetSoftwareItemRequest, args[0])
    assert request.software_item_id == "request_id"
    assert result == SoftwareItem.from_protobuf(software_item)


def test___get_test_adapter___calls_metadata_store_service_client(
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
        extension=None,
        schema_id="schema_id",
    )
    expected_response = GetTestAdapterResponse(test_adapter=test_adapter)
    mocked_metadata_store_service_client.get_test_adapter.return_value = expected_response

    result = metadata_store_client.get_test_adapter(test_adapter_id="request_id")

    args, __ = mocked_metadata_store_service_client.get_test_adapter.call_args
    request = cast(GetTestAdapterRequest, args[0])
    assert request.test_adapter_id == "request_id"
    assert result == TestAdapter.from_protobuf(test_adapter)
