"""Contains tests to validate the datastore client functionality."""

from __future__ import annotations

import datetime as std_datetime
import unittest.mock
from typing import Any, cast
from unittest.mock import Mock

import numpy as np
import pytest
from google.protobuf.any_pb2 import Any as gpAny
from hightime import datetime
from ni.datamonikers.v1.data_moniker_pb2 import Moniker, ReadFromMonikerResult
from ni.datastore.client import Client
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    Step,
    TestResult,
)
from ni.measurements.data.v1.data_store_service_pb2 import (
    CreateStepRequest,
    CreateStepResponse,
    CreateTestResultRequest,
    CreateTestResultResponse,
    GetStepRequest,
    GetStepResponse,
    GetTestResultRequest,
    GetTestResultResponse,
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_to_protobuf,
)
from ni.protobuf.types.waveform_conversion import float64_analog_waveform_to_protobuf
from ni.protobuf.types.waveform_pb2 import DoubleAnalogWaveform
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, Timing
from pytest_mock import MockerFixture


@pytest.mark.parametrize("value", [True, False])
def test___publish_boolean_data___calls_datastoreclient(
    mocked_datastore_client: Mock, value: bool
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    client = Client(data_store_client=mocked_datastore_client)
    client.publish_measurement(
        "name",
        value,
        "step_id",
        timestamp,
        Outcome.OUTCOME_PASSED,
        ErrorInformation(),
        [],
        [],
        [],
        "notes",
    )
    args, __ = mocked_datastore_client.publish_measurement.call_args
    request = args[0]  # The PublishMeasurementRequest object

    # Now assert on its fields
    assert request.step_id == "step_id"
    assert request.measurement_name == "name"
    assert request.notes == "notes"
    assert request.timestamp == unittest.mock.ANY
    assert request.scalar.bool_value == value
    assert request.outcome == Outcome.OUTCOME_PASSED
    assert request.error_information == ErrorInformation()
    assert request.hardware_item_ids == []
    assert request.software_item_ids == []
    assert request.test_adapter_ids == []


def test___publish_analog_waveform_data___calls_datastoreclient(
    mocked_datastore_client: Mock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    waveform_values = [1.0, 2.0, 3.0]
    analog_waveform = AnalogWaveform(
        sample_count=len(waveform_values),
        raw_data=np.array(waveform_values, dtype=np.float64),
        timing=Timing.create_with_regular_interval(std_datetime.timedelta(seconds=1), timestamp),
    )

    expected_protobuf_waveform = DoubleAnalogWaveform()
    expected_protobuf_waveform.CopyFrom(float64_analog_waveform_to_protobuf(analog_waveform))
    client = Client(data_store_client=mocked_datastore_client)
    # Now, when client.publish_measurement calls foo.MyClass().publish(), it will use the mock
    client.publish_measurement(
        "name",
        analog_waveform,
        "step_id",
        timestamp,
        Outcome.OUTCOME_PASSED,
        ErrorInformation(),
        [],
        [],
        [],
        "notes",
    )
    args, __ = mocked_datastore_client.publish_measurement.call_args
    request = cast(PublishMeasurementRequest, args[0])  # The PublishMeasurementRequest object

    # Now assert on its fields
    assert request.step_id == "step_id"
    assert request.measurement_name == "name"
    assert request.notes == "notes"
    assert request.timestamp == hightime_datetime_to_protobuf(timestamp)
    assert request.double_analog_waveform == expected_protobuf_waveform
    assert request.outcome == Outcome.OUTCOME_PASSED
    assert request.error_information == ErrorInformation()
    assert request.hardware_item_ids == []
    assert request.software_item_ids == []
    assert request.test_adapter_ids == []


def test___publish_analog_waveform_data_without_timestamp_parameter___uses_waveform_t0(
    mocked_datastore_client: Mock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    waveform_values = [1.0, 2.0, 3.0]
    analog_waveform = AnalogWaveform(
        sample_count=len(waveform_values),
        raw_data=np.array(waveform_values, dtype=np.float64),
        timing=Timing.create_with_regular_interval(std_datetime.timedelta(seconds=1), timestamp),
    )
    client = Client(data_store_client=mocked_datastore_client)

    client.publish_measurement("name", analog_waveform, "step_id")

    args, __ = mocked_datastore_client.publish_measurement.call_args
    request = cast(PublishMeasurementRequest, args[0])  # The PublishMeasurementRequest object
    assert request.timestamp == hightime_datetime_to_protobuf(timestamp)


def test___publish_analog_waveform_data_without_t0___uses_timestamp_parameter(
    mocked_datastore_client: Mock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    analog_waveform = AnalogWaveform.from_array_1d([1.0, 2.0, 3.0], dtype=float)
    client = Client(data_store_client=mocked_datastore_client)

    client.publish_measurement("name", analog_waveform, "step_id", timestamp)

    args, __ = mocked_datastore_client.publish_measurement.call_args
    request = cast(PublishMeasurementRequest, args[0])  # The PublishMeasurementRequest object
    assert request.timestamp == hightime_datetime_to_protobuf(timestamp)


def test___publish_analog_waveform_data_with_mismatched_timestamp_parameter___raises_error(
    mocked_datastore_client: Mock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    waveform_values = [1.0, 2.0, 3.0]
    analog_waveform = AnalogWaveform(
        sample_count=len(waveform_values),
        raw_data=np.array(waveform_values, dtype=np.float64),
        timing=Timing.create_with_regular_interval(std_datetime.timedelta(seconds=1), timestamp),
    )
    client = Client(data_store_client=mocked_datastore_client)

    mismatched_timestamp = timestamp + std_datetime.timedelta(seconds=1)
    with pytest.raises(ValueError):
        client.publish_measurement("name", analog_waveform, "step_id", mismatched_timestamp)


def test___publish_measurement_batch___calls_datastoreclient(
    mocked_datastore_client: Mock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    client = Client(data_store_client=mocked_datastore_client)
    client.publish_measurement_batch(
        measurement_name="name",
        values=Vector(values=[1.0, 2.0, 3.0], units="BatchUnits"),
        step_id="step_id",
        timestamps=[timestamp],
        outcomes=[Outcome.OUTCOME_PASSED],
        error_information=[ErrorInformation()],
        hardware_item_ids=[],
        test_adapter_ids=[],
        software_item_ids=[],
    )

    args, __ = mocked_datastore_client.publish_measurement_batch.call_args
    request = cast(PublishMeasurementBatchRequest, args[0])

    # Now assert on its fields
    assert request.step_id == "step_id"
    assert request.measurement_name == "name"
    assert request.timestamp == [hightime_datetime_to_protobuf(timestamp)]
    assert request.scalar_values.double_array.values == [1.0, 2.0, 3.0]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "BatchUnits"
    assert request.outcome == [Outcome.OUTCOME_PASSED]
    assert request.error_information == [ErrorInformation()]
    assert request.hardware_item_ids == []
    assert request.software_item_ids == []
    assert request.test_adapter_ids == []


def test___publish_condition___calls_datastoreclient(
    mocked_datastore_client: Mock,
) -> None:
    client = Client(data_store_client=mocked_datastore_client)
    _ = client.publish_condition(
        condition_name="TestCondition",
        type="ConditionType",
        value=123,
        step_id="MyStep",
    )

    args, __ = mocked_datastore_client.publish_condition.call_args
    request = cast(PublishConditionRequest, args[0])

    # Now assert on its fields
    assert request.step_id == "MyStep"
    assert request.condition_name == "TestCondition"
    assert request.type == "ConditionType"
    assert request.scalar.sint32_value == 123


def test___publish_condition_batch___calls_datastoreclient(
    mocked_datastore_client: Mock,
) -> None:
    client = Client(data_store_client=mocked_datastore_client)
    _ = client.publish_condition_batch(
        condition_name="TestCondition",
        type="ConditionType",
        values=Vector(values=["one", "two", "three"], units="fake_units"),
        step_id="MyStep",
    )

    args, __ = mocked_datastore_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])

    # Now assert on its fields
    assert request.step_id == "MyStep"
    assert request.condition_name == "TestCondition"
    assert request.type == "ConditionType"
    assert list(request.scalar_values.string_array.values) == ["one", "two", "three"]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "fake_units"


def test___read_data___calls_monikerclient(mocked_moniker_client: Mock) -> None:
    client = Client(moniker_clients_by_service_location={"localhost:50051": mocked_moniker_client})
    moniker = Moniker()
    moniker.data_instance = 12
    moniker.data_source = "ABCD123"
    moniker.service_location = "http://localhost:50051"
    result = ReadFromMonikerResult()
    value_to_read = gpAny()
    value_to_read.Pack(DoubleAnalogWaveform())
    result.value.CopyFrom(value_to_read)
    mocked_moniker_client.read_from_moniker.return_value = result

    client.read_data(moniker, AnalogWaveform)

    args, __ = mocked_moniker_client.read_from_moniker.call_args
    requested_moniker = cast(Moniker, args[0])
    assert requested_moniker.service_location == moniker.service_location
    assert requested_moniker.data_instance == moniker.data_instance
    assert requested_moniker.data_source == moniker.data_source


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

    # Now assert on its fields
    assert request.step == step
    assert result == "response_id"


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

    # Now assert on its fields
    assert request.step_id == "request_id"
    assert result == step


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

    # Now assert on its fields
    assert request.test_result == test_result
    assert result == "response_id"


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

    # Now assert on its fields
    assert request.test_result_id == "request_id"
    assert result == test_result


@pytest.fixture
def mocked_datastore_client(mocker: MockerFixture) -> Any:
    mock_datastore_client = mocker.patch(
        "ni.measurements.data.v1.client.DataStoreClient", autospec=True
    )
    # Set up the mock's publish method
    mock_datastore_instance = mock_datastore_client.return_value
    return mock_datastore_instance


@pytest.fixture
def mocked_moniker_client(mocker: MockerFixture) -> Any:
    mock_moniker_client = mocker.patch("ni.datamonikers.v1.client.MonikerClient", autospec=True)
    # Set up the mock's publish method
    mock_moniker_instance = mock_moniker_client.return_value
    return mock_moniker_instance
