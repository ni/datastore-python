"""Contains tests to validate the create_* methods for the metadata store."""

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
from ni.measurements.metadata.v1.metadata_store_service_pb2 import (
    CreateHardwareItemRequest,
    CreateHardwareItemResponse,
    CreateOperatorRequest,
    CreateOperatorResponse,
    CreateSoftwareItemRequest,
    CreateSoftwareItemResponse,
    CreateTestAdapterRequest,
    CreateTestAdapterResponse,
    CreateTestDescriptionRequest,
    CreateTestDescriptionResponse,
    CreateTestRequest,
    CreateTestResponse,
    CreateTestStationRequest,
    CreateTestStationResponse,
    CreateUutInstanceRequest,
    CreateUutInstanceResponse,
    CreateUutRequest,
    CreateUutResponse,
)


def test___create_uut_instance___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    uut_instance = UutInstance(
        uut_id="uut_id",
        serial_number="serial_number",
        manufacture_date="manufacture_date",
        firmware_version="firmware_version",
        hardware_version="hardware_version",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateUutInstanceResponse(uut_instance_id="response_id")
    mocked_metadata_store_service_client.create_uut_instance.return_value = expected_response

    result = metadata_store_client.create_uut_instance(uut_instance)

    args, __ = mocked_metadata_store_service_client.create_uut_instance.call_args
    request = cast(CreateUutInstanceRequest, args[0])
    assert request.uut_instance == uut_instance.to_protobuf()
    assert result == "response_id"


def test___create_uut___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    uut = Uut(
        model_name="model_name",
        family="family",
        manufacturers=None,
        part_number="part_number",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateUutResponse(uut_id="response_id")
    mocked_metadata_store_service_client.create_uut.return_value = expected_response

    result = metadata_store_client.create_uut(uut)

    args, __ = mocked_metadata_store_service_client.create_uut.call_args
    request = cast(CreateUutRequest, args[0])
    assert request.uut == uut.to_protobuf()
    assert result == "response_id"


def test___create_operator___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    operator = Operator(
        operator_name="operator_name",
        role="role",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateOperatorResponse(operator_id="response_id")
    mocked_metadata_store_service_client.create_operator.return_value = expected_response

    result = metadata_store_client.create_operator(operator)

    args, __ = mocked_metadata_store_service_client.create_operator.call_args
    request = cast(CreateOperatorRequest, args[0])
    assert request.operator == operator.to_protobuf()
    assert result == "response_id"


def test___create_test_description___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test_description = TestDescription(
        uut_id="uut_id",
        test_description_name="test_description_name",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateTestDescriptionResponse(test_description_id="response_id")
    mocked_metadata_store_service_client.create_test_description.return_value = expected_response

    result = metadata_store_client.create_test_description(test_description)

    args, __ = mocked_metadata_store_service_client.create_test_description.call_args
    request = cast(CreateTestDescriptionRequest, args[0])
    assert request.test_description == test_description.to_protobuf()
    assert result == "response_id"


def test___create_test___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test = Test(
        test_name="test_name",
        description="description",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateTestResponse(test_id="response_id")
    mocked_metadata_store_service_client.create_test.return_value = expected_response

    result = metadata_store_client.create_test(test)

    args, __ = mocked_metadata_store_service_client.create_test.call_args
    request = cast(CreateTestRequest, args[0])
    assert request.test == test.to_protobuf()
    assert result == "response_id"


def test___create_test_station___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test_station = TestStation(
        test_station_name="test_station_name",
        asset_identifier="asset_identifier",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateTestStationResponse(test_station_id="response_id")
    mocked_metadata_store_service_client.create_test_station.return_value = expected_response

    result = metadata_store_client.create_test_station(test_station)

    args, __ = mocked_metadata_store_service_client.create_test_station.call_args
    request = cast(CreateTestStationRequest, args[0])
    assert request.test_station == test_station.to_protobuf()
    assert result == "response_id"


def test___create_hardware_item___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    hardware_item = HardwareItem(
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
    expected_response = CreateHardwareItemResponse(hardware_item_id="response_id")
    mocked_metadata_store_service_client.create_hardware_item.return_value = expected_response

    result = metadata_store_client.create_hardware_item(hardware_item)

    args, __ = mocked_metadata_store_service_client.create_hardware_item.call_args
    request = cast(CreateHardwareItemRequest, args[0])
    assert request.hardware_item == hardware_item.to_protobuf()
    assert result == "response_id"


def test___create_software_item___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    software_item = SoftwareItem(
        product="product",
        version="version",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateSoftwareItemResponse(software_item_id="response_id")
    mocked_metadata_store_service_client.create_software_item.return_value = expected_response

    result = metadata_store_client.create_software_item(software_item)

    args, __ = mocked_metadata_store_service_client.create_software_item.call_args
    request = cast(CreateSoftwareItemRequest, args[0])
    assert request.software_item == software_item.to_protobuf()
    assert result == "response_id"


def test___create_test_adapter___calls_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    test_adapter = TestAdapter(
        test_adapter_name="test_adapter_name",
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
    expected_response = CreateTestAdapterResponse(test_adapter_id="response_id")
    mocked_metadata_store_service_client.create_test_adapter.return_value = expected_response

    result = metadata_store_client.create_test_adapter(test_adapter)

    args, __ = mocked_metadata_store_service_client.create_test_adapter.call_args
    request = cast(CreateTestAdapterRequest, args[0])
    assert request.test_adapter == test_adapter.to_protobuf()
    assert result == "response_id"
