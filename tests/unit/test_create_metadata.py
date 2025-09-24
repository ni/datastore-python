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
