"""Contains tests to validate the get_* methods in datastore and metadatastore."""

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
    GetStepRequest,
    GetStepResponse,
    GetTestResultRequest,
    GetTestResultResponse,
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
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_to_protobuf,
)


def test___get_step___calls_datastoreclient(
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
    mocked_datastore_client.get_step.return_value = GetStepResponse(step=step)

    result = client.get_step(step_id="request_id")

    args, __ = mocked_datastore_client.get_step.call_args
    request = cast(GetStepRequest, args[0])
    assert request.step_id == "request_id"
    assert result == step


def test___get_test_result___calls_datastoreclient(
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
    expected_response = GetTestResultResponse(test_result=test_result)
    mocked_datastore_client.get_test_result.return_value = expected_response

    result = client.get_test_result(test_result_id="request_id")

    args, __ = mocked_datastore_client.get_test_result.call_args
    request = cast(GetTestResultRequest, args[0])
    assert request.test_result_id == "request_id"
    assert result == test_result


def test___get_uut_instance___calls_metadatastoreclient(
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

    expected_response = GetUutInstanceResponse(uut_instance=uut_instance)
    mocked_metadatastore_client.get_uut_instance.return_value = expected_response
    result = client.get_uut_instance(uut_instance_id="request_id")

    args, __ = mocked_metadatastore_client.get_uut_instance.call_args
    request = cast(GetUutInstanceRequest, args[0])

    # Now assert on its fields
    assert request.uut_instance_id == "request_id"
    assert result == uut_instance


def test___get_uut___calls_metadatastoreclient(
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

    expected_response = GetUutResponse(uut=uut)
    mocked_metadatastore_client.get_uut.return_value = expected_response
    result = client.get_uut(uut_id="request_id")

    args, __ = mocked_metadatastore_client.get_uut.call_args
    request = cast(GetUutRequest, args[0])

    # Now assert on its fields
    assert request.uut_id == "request_id"
    assert result == uut


def test___get_operator___calls_metadatastoreclient(
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

    expected_response = GetOperatorResponse(operator=operator)
    mocked_metadatastore_client.get_operator.return_value = expected_response
    result = client.get_operator(operator_id="request_id")

    args, __ = mocked_metadatastore_client.get_operator.call_args
    request = cast(GetOperatorRequest, args[0])

    # Now assert on its fields
    assert request.operator_id == "request_id"
    assert result == operator


def test___get_test_description___calls_metadatastoreclient(
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

    expected_response = GetTestDescriptionResponse(test_description=test_description)
    mocked_metadatastore_client.get_test_description.return_value = expected_response
    result = client.get_test_description(test_description_id="request_id")

    args, __ = mocked_metadatastore_client.get_test_description.call_args
    request = cast(GetTestDescriptionRequest, args[0])

    # Now assert on its fields
    assert request.test_description_id == "request_id"
    assert result == test_description


def test___get_test___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
    test = Test(
        test_name="test_name",
        description="description",
        extensions=None,
        schema_id="schema_id",
    )

    expected_response = GetTestResponse(test=test)
    mocked_metadatastore_client.get_test.return_value = expected_response
    result = client.get_test(test_id="request_id")

    args, __ = mocked_metadatastore_client.get_test.call_args
    request = cast(GetTestRequest, args[0])

    # Now assert on its fields
    assert request.test_id == "request_id"
    assert result == test


def test___get_test_station___calls_metadatastoreclient(
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

    expected_response = GetTestStationResponse(test_station=test_station)
    mocked_metadatastore_client.get_test_station.return_value = expected_response
    result = client.get_test_station(test_station_id="request_id")

    args, __ = mocked_metadatastore_client.get_test_station.call_args
    request = cast(GetTestStationRequest, args[0])

    # Now assert on its fields
    assert request.test_station_id == "request_id"
    assert result == test_station


def test___get_hardware_item___calls_metadatastoreclient(
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

    expected_response = GetHardwareItemResponse(hardware_item=hardware_item)
    mocked_metadatastore_client.get_hardware_item.return_value = expected_response
    result = client.get_hardware_item(hardware_item_id="request_id")

    args, __ = mocked_metadatastore_client.get_hardware_item.call_args
    request = cast(GetHardwareItemRequest, args[0])

    # Now assert on its fields
    assert request.hardware_item_id == "request_id"
    assert result == hardware_item


def test___get_software_item___calls_metadatastoreclient(
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

    expected_response = GetSoftwareItemResponse(software_item=software_item)
    mocked_metadatastore_client.get_software_item.return_value = expected_response
    result = client.get_software_item(software_item_id="request_id")

    args, __ = mocked_metadatastore_client.get_software_item.call_args
    request = cast(GetSoftwareItemRequest, args[0])

    # Now assert on its fields
    assert request.software_item_id == "request_id"
    assert result == software_item


def test___get_test_adapter___calls_metadatastoreclient(
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

    expected_response = GetTestAdapterResponse(test_adapter=test_adapter)
    mocked_metadatastore_client.get_test_adapter.return_value = expected_response
    result = client.get_test_adapter(test_adapter_id="request_id")

    args, __ = mocked_metadatastore_client.get_test_adapter.call_args
    request = cast(GetTestAdapterRequest, args[0])

    # Now assert on its fields
    assert request.test_adapter_id == "request_id"
    assert result == test_adapter
