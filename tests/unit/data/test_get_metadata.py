"""Contains tests to validate the get_* methods in the data store."""

from __future__ import annotations

import datetime as std_datetime
from typing import cast
from unittest.mock import NonCallableMock

from hightime import datetime
from ni.datastore.data import (
    DataStoreClient,
    Step,
    TestResult,
)
from ni.measurements.data.v1.data_store_pb2 import (
    Step as StepProto,
    TestResult as TestResultProto,
)
from ni.measurements.data.v1.data_store_service_pb2 import (
    GetStepRequest,
    GetStepResponse,
    GetTestResultRequest,
    GetTestResultResponse,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_to_protobuf,
)


def test___get_step___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    start_time = datetime.now(tz=std_datetime.timezone.utc)
    end_time = datetime.now(tz=std_datetime.timezone.utc)
    step = StepProto(
        id="step_id",
        parent_step_id="parent_step_id",
        test_result_id="test_result",
        test_id="test_id",
        name="step_name",
        step_type="step_type",
        notes="step_notes",
        start_date_time=hightime_datetime_to_protobuf(start_time),
        end_date_time=hightime_datetime_to_protobuf(end_time),
    )
    mocked_data_store_service_client.get_step.return_value = GetStepResponse(step=step)

    result = data_store_client.get_step(step_id="request_id")

    args, __ = mocked_data_store_service_client.get_step.call_args
    request = cast(GetStepRequest, args[0])
    assert request.step_id == "request_id"
    assert result == Step.from_protobuf(step)


def test___get_test_result___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    start_time = datetime.now(tz=std_datetime.timezone.utc)
    end_time = datetime.now(tz=std_datetime.timezone.utc)
    test_result = TestResultProto(
        id="test_result_id",
        uut_instance_id="uut_instance_id",
        operator_id="operator_id",
        test_station_id="test_station_id",
        test_description_id="test_description_id",
        software_item_ids=[],
        hardware_item_ids=[],
        test_adapter_ids=[],
        name="test_result_name",
        start_date_time=hightime_datetime_to_protobuf(start_time),
        end_date_time=hightime_datetime_to_protobuf(end_time),
    )
    expected_response = GetTestResultResponse(test_result=test_result)
    mocked_data_store_service_client.get_test_result.return_value = expected_response

    result = data_store_client.get_test_result(test_result_id="request_id")

    args, __ = mocked_data_store_service_client.get_test_result.call_args
    request = cast(GetTestResultRequest, args[0])
    assert request.test_result_id == "request_id"
    assert result == TestResult.from_protobuf(test_result)
