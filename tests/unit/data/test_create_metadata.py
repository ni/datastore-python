"""Contains tests to validate the create_* methods for the data store."""

from __future__ import annotations

import datetime as std_datetime
from typing import cast
from unittest.mock import NonCallableMock

import hightime as ht
from ni.datastore.data import (
    DataStoreClient,
    Step,
    TestResult,
)
from ni.datastore.data._types._outcome import Outcome
from ni.measurements.data.v1.data_store_service_pb2 import (
    CreateStepRequest,
    CreateStepResponse,
    CreateTestResultRequest,
    CreateTestResultResponse,
)
from ni.protobuf.types.precision_timestamp_conversion import hightime_datetime_to_protobuf


def test___create_step___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    step = Step(
        id="step_id",
        parent_step_id="parent_step_id",
        test_result_id="test_result",
        test_id="test_id",
        name="step_name",
        step_type="step_type",
        notes="step_notes",
    )
    expected_response = CreateStepResponse(step_id="response_id")
    mocked_data_store_service_client.create_step.return_value = expected_response

    result = data_store_client.create_step(step)

    args, __ = mocked_data_store_service_client.create_step.call_args
    request = cast(CreateStepRequest, args[0])
    assert request.step == step.to_protobuf()
    assert result == "response_id"


def test___create_test_result___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    test_result = TestResult(
        id="test_result_id",
        uut_instance_id="uut_instance_id",
        operator_id="operator_id",
        test_station_id="test_station_id",
        test_description_id="test_description_id",
        software_item_ids=[],
        hardware_item_ids=[],
        test_adapter_ids=[],
        name="test_result_name",
    )
    expected_response = CreateTestResultResponse(test_result_id="response_id")
    mocked_data_store_service_client.create_test_result.return_value = expected_response

    result = data_store_client.create_test_result(test_result)

    args, __ = mocked_data_store_service_client.create_test_result.call_args
    request = cast(CreateTestResultRequest, args[0])
    assert request.test_result == test_result.to_protobuf()
    assert result == "response_id"


def test___test_result_to_protobuf___naive_datetime___converts_to_utc() -> None:
    naive_start = ht.datetime(2024, 6, 15, 10, 30, 0)
    naive_end = ht.datetime(2024, 6, 15, 11, 0, 0)
    test_result = TestResult(
        name="test",
        start_date_time=naive_start,
        end_date_time=naive_end,
        outcome=Outcome.PASSED,
    )

    proto = test_result.to_protobuf()

    expected_start = hightime_datetime_to_protobuf(
        naive_start.astimezone(std_datetime.timezone.utc)
    )
    expected_end = hightime_datetime_to_protobuf(naive_end.astimezone(std_datetime.timezone.utc))
    assert proto.start_date_time == expected_start
    assert proto.end_date_time == expected_end


def test___test_result_to_protobuf___utc_datetime___preserved() -> None:
    utc_start = ht.datetime(2024, 6, 15, 10, 30, 0, tzinfo=std_datetime.timezone.utc)
    utc_end = ht.datetime(2024, 6, 15, 11, 0, 0, tzinfo=std_datetime.timezone.utc)
    test_result = TestResult(
        name="test",
        start_date_time=utc_start,
        end_date_time=utc_end,
        outcome=Outcome.PASSED,
    )

    proto = test_result.to_protobuf()

    expected_start = hightime_datetime_to_protobuf(utc_start)
    expected_end = hightime_datetime_to_protobuf(utc_end)
    assert proto.start_date_time == expected_start
    assert proto.end_date_time == expected_end


def test___step_to_protobuf___naive_datetime___converts_to_utc() -> None:
    naive_start = ht.datetime(2024, 6, 15, 10, 30, 0)
    naive_end = ht.datetime(2024, 6, 15, 11, 0, 0)
    step = Step(
        name="step",
        start_date_time=naive_start,
        end_date_time=naive_end,
    )

    proto = step.to_protobuf()

    expected_start = hightime_datetime_to_protobuf(
        naive_start.astimezone(std_datetime.timezone.utc)
    )
    expected_end = hightime_datetime_to_protobuf(naive_end.astimezone(std_datetime.timezone.utc))
    assert proto.start_date_time == expected_start
    assert proto.end_date_time == expected_end


def test___step_to_protobuf___utc_datetime___preserved() -> None:
    utc_start = ht.datetime(2024, 6, 15, 10, 30, 0, tzinfo=std_datetime.timezone.utc)
    utc_end = ht.datetime(2024, 6, 15, 11, 0, 0, tzinfo=std_datetime.timezone.utc)
    step = Step(
        name="step",
        start_date_time=utc_start,
        end_date_time=utc_end,
    )

    proto = step.to_protobuf()

    expected_start = hightime_datetime_to_protobuf(utc_start)
    expected_end = hightime_datetime_to_protobuf(utc_end)
    assert proto.start_date_time == expected_start
    assert proto.end_date_time == expected_end
