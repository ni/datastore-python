"""Contains tests to validate the create_* methods for datastore and metadatastore."""

from __future__ import annotations

import datetime as std_datetime
from typing import cast
from unittest.mock import Mock

from hightime import datetime
from ni.datastore.client import Client
from ni.measurements.data.v1.data_store_pb2 import (
    Step,
    TestResult,
)
from ni.measurements.data.v1.data_store_service_pb2 import (
    CreateStepRequest,
    CreateStepResponse,
    CreateTestResultRequest,
    CreateTestResultResponse,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
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
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_to_protobuf,
)


def test___create_step___calls_datastoreclient(
    mocked_datastore_client: Mock,
) -> None:
    client = Client(data_store_client=mocked_datastore_client)
    start_time = datetime.now(tz=std_datetime.timezone.utc)
    end_time = datetime.now(tz=std_datetime.timezone.utc)
    step = Step(
        step_id="step_id",
        parent_step_id="parent_step_id",
        test_result_id="test_result",
        test_id="test_id",
        step_name="step_name",
        step_type="step_type",
        notes="step_notes",
        start_date_time=hightime_datetime_to_protobuf(start_time),
        end_date_time=hightime_datetime_to_protobuf(end_time),
    )
    expected_response = CreateStepResponse(step_id="response_id")
    mocked_datastore_client.create_step.return_value = expected_response

    result = client.create_step(step)

    args, __ = mocked_datastore_client.create_step.call_args
    request = cast(CreateStepRequest, args[0])
    assert request.step == step
    assert result == "response_id"


def test___create_test_result___calls_datastoreclient(
    mocked_datastore_client: Mock,
) -> None:
    client = Client(data_store_client=mocked_datastore_client)
    start_time = datetime.now(tz=std_datetime.timezone.utc)
    end_time = datetime.now(tz=std_datetime.timezone.utc)
    test_result = TestResult(
        test_result_id="test_result_id",
        uut_instance_id="uut_instance_id",
        operator_id="operator_id",
        test_station_id="test_station_id",
        test_description_id="test_description_id",
        software_item_ids=[],
        hardware_item_ids=[],
        test_adapter_ids=[],
        test_result_name="test_result_name",
        start_date_time=hightime_datetime_to_protobuf(start_time),
        end_date_time=hightime_datetime_to_protobuf(end_time),
    )
    expected_response = CreateTestResultResponse(test_result_id="response_id")
    mocked_datastore_client.create_test_result.return_value = expected_response

    result = client.create_test_result(test_result)

    args, __ = mocked_datastore_client.create_test_result.call_args
    request = cast(CreateTestResultRequest, args[0])
    assert request.test_result == test_result
    assert result == "response_id"


def test___create_uut_instance___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
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
    mocked_metadatastore_client.create_uut_instance.return_value = expected_response

    result = client.create_uut_instance(uut_instance)

    args, __ = mocked_metadatastore_client.create_uut_instance.call_args
    request = cast(CreateUutInstanceRequest, args[0])

    # Now assert on its fields
    assert request.uut_instance == uut_instance
    assert result == "response_id"


def test___create_uut___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
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
    mocked_metadatastore_client.create_uut.return_value = expected_response

    result = client.create_uut(uut)

    args, __ = mocked_metadatastore_client.create_uut.call_args
    request = cast(CreateUutRequest, args[0])

    # Now assert on its fields
    assert request.uut == uut
    assert result == "response_id"


def test___create_operator___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
    operator = Operator(
        operator_name="operator_name",
        role="role",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateOperatorResponse(operator_id="response_id")
    mocked_metadatastore_client.create_operator.return_value = expected_response

    result = client.create_operator(operator)

    args, __ = mocked_metadatastore_client.create_operator.call_args
    request = cast(CreateOperatorRequest, args[0])
    assert request.operator == operator
    assert result == "response_id"


def test___create_test_description___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
    test_description = TestDescription(
        uut_id="uut_id",
        test_description_name="test_description_name",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateTestDescriptionResponse(test_description_id="response_id")
    mocked_metadatastore_client.create_test_description.return_value = expected_response

    result = client.create_test_description(test_description)

    args, __ = mocked_metadatastore_client.create_test_description.call_args
    request = cast(CreateTestDescriptionRequest, args[0])
    assert request.test_description == test_description
    assert result == "response_id"


def test___create_test___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
    test = Test(
        test_name="test_name",
        description="description",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateTestResponse(test_id="response_id")
    mocked_metadatastore_client.create_test.return_value = expected_response

    result = client.create_test(test)

    args, __ = mocked_metadatastore_client.create_test.call_args
    request = cast(CreateTestRequest, args[0])
    assert request.test == test
    assert result == "response_id"


def test___create_test_station___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
    test_station = TestStation(
        test_station_name="test_station_name",
        asset_identifier="asset_identifier",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateTestStationResponse(test_station_id="response_id")
    mocked_metadatastore_client.create_test_station.return_value = expected_response

    result = client.create_test_station(test_station)

    args, __ = mocked_metadatastore_client.create_test_station.call_args
    request = cast(CreateTestStationRequest, args[0])
    assert request.test_station == test_station
    assert result == "response_id"


def test___create_hardware_item___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
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
    mocked_metadatastore_client.create_hardware_item.return_value = expected_response

    result = client.create_hardware_item(hardware_item)

    args, __ = mocked_metadatastore_client.create_hardware_item.call_args
    request = cast(CreateHardwareItemRequest, args[0])
    assert request.hardware_item == hardware_item
    assert result == "response_id"


def test___create_software_item___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
    software_item = SoftwareItem(
        product="product",
        version="version",
        link="link",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = CreateSoftwareItemResponse(software_item_id="response_id")
    mocked_metadatastore_client.create_software_item.return_value = expected_response

    result = client.create_software_item(software_item)

    args, __ = mocked_metadatastore_client.create_software_item.call_args
    request = cast(CreateSoftwareItemRequest, args[0])
    assert request.software_item == software_item
    assert result == "response_id"


def test___create_test_adapter___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
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
    mocked_metadatastore_client.create_test_adapter.return_value = expected_response

    result = client.create_test_adapter(test_adapter)

    args, __ = mocked_metadatastore_client.create_test_adapter.call_args
    request = cast(CreateTestAdapterRequest, args[0])
    assert request.test_adapter == test_adapter
    assert result == "response_id"
