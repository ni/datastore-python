"""Contains tests to validate the query_* methods in datastore and metadatastore."""

from __future__ import annotations

import datetime as std_datetime
from typing import cast
from unittest.mock import Mock

from hightime import datetime
from ni.datastore import Client
from ni.datastore.data import Step
from ni.measurements.data.v1.data_store_pb2 import Step as StepProto
from ni.measurements.data.v1.data_store_service_pb2 import (
    QueryStepsRequest,
    QueryStepsResponse,
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
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_to_protobuf,
)


def test___query_steps___calls_datastoreclient(
    mocked_datastore_client: Mock,
) -> None:
    client = Client(data_store_client=mocked_datastore_client)
    start_time = datetime.now(tz=std_datetime.timezone.utc)
    end_time = datetime.now(tz=std_datetime.timezone.utc)
    step = StepProto(
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
    mocked_datastore_client.query_steps.return_value = QueryStepsResponse(steps=[step])

    result = client.query_steps(odata_query="request_query")

    args, __ = mocked_datastore_client.query_steps.call_args
    request = cast(QueryStepsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [Step.from_protobuf(step)]


def test___query_uut_instances___calls_metadatastoreclient(
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
    expected_response = QueryUutInstancesResponse(uut_instances=[uut_instance])
    mocked_metadatastore_client.query_uut_instances.return_value = expected_response

    result = client.query_uut_instances(odata_query="request_query")

    args, __ = mocked_metadatastore_client.query_uut_instances.call_args
    request = cast(QueryUutInstancesRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [uut_instance]


def test___query_uuts___calls_metadatastoreclient(
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
    expected_response = QueryUutsResponse(uuts=[uut])
    mocked_metadatastore_client.query_uuts.return_value = expected_response

    result = client.query_uuts(odata_query="request_query")

    args, __ = mocked_metadatastore_client.query_uuts.call_args
    request = cast(QueryUutsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [uut]


def test___query_operators___calls_metadatastoreclient(
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
    expected_response = QueryOperatorsResponse(operators=[operator])
    mocked_metadatastore_client.query_operators.return_value = expected_response

    result = client.query_operators(odata_query="request_query")

    args, __ = mocked_metadatastore_client.query_operators.call_args
    request = cast(QueryOperatorsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [operator]


def test___query_test_descriptions___calls_metadatastoreclient(
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
    expected_response = QueryTestDescriptionsResponse(test_descriptions=[test_description])
    mocked_metadatastore_client.query_test_descriptions.return_value = expected_response

    result = client.query_test_descriptions(odata_query="request_query")

    args, __ = mocked_metadatastore_client.query_test_descriptions.call_args
    request = cast(QueryTestDescriptionsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [test_description]


def test___query_tests___calls_metadatastoreclient(
    mocked_metadatastore_client: Mock,
) -> None:
    client = Client(metadata_store_client=mocked_metadatastore_client)
    test = Test(
        test_name="test_name",
        description="description",
        extensions=None,
        schema_id="schema_id",
    )
    expected_response = QueryTestsResponse(tests=[test])
    mocked_metadatastore_client.query_tests.return_value = expected_response

    result = client.query_tests(odata_query="request_query")

    args, __ = mocked_metadatastore_client.query_tests.call_args
    request = cast(QueryTestsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [test]


def test___query_test_stations___calls_metadatastoreclient(
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
    expected_response = QueryTestStationsResponse(test_stations=[test_station])
    mocked_metadatastore_client.query_test_stations.return_value = expected_response

    result = client.query_test_stations(odata_query="request_query")

    args, __ = mocked_metadatastore_client.query_test_stations.call_args
    request = cast(QueryTestStationsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [test_station]


def test___query_hardware_items___calls_metadatastoreclient(
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
    expected_response = QueryHardwareItemsResponse(hardware_items=[hardware_item])
    mocked_metadatastore_client.query_hardware_items.return_value = expected_response

    result = client.query_hardware_items(odata_query="request_query")

    args, __ = mocked_metadatastore_client.query_hardware_items.call_args
    request = cast(QueryHardwareItemsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [hardware_item]


def test___query_software_items___calls_metadatastoreclient(
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
    expected_response = QuerySoftwareItemsResponse(software_items=[software_item])
    mocked_metadatastore_client.query_software_items.return_value = expected_response

    result = client.query_software_items(odata_query="request_query")

    args, __ = mocked_metadatastore_client.query_software_items.call_args
    request = cast(QuerySoftwareItemsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [software_item]


def test___query_test_adapters___calls_metadatastoreclient(
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
    expected_response = QueryTestAdaptersResponse(test_adapters=[test_adapter])
    mocked_metadatastore_client.query_test_adapters.return_value = expected_response

    result = client.query_test_adapters(odata_query="request_query")

    args, __ = mocked_metadatastore_client.query_test_adapters.call_args
    request = cast(QueryTestAdaptersRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [test_adapter]
