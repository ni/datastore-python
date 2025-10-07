"""Contains tests to validate the data store client publish functionality."""

from __future__ import annotations

import datetime as std_datetime
import unittest.mock
from typing import cast
from unittest.mock import NonCallableMock

import numpy as np
import pytest
from hightime import datetime, timedelta
from ni.datastore.data import DataStoreClient
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    PublishedMeasurement,
)
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishMeasurementBatchRequest,
    PublishMeasurementBatchResponse,
    PublishMeasurementRequest,
    PublishMeasurementResponse,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_to_protobuf,
)
from ni.protobuf.types.waveform_conversion import float64_analog_waveform_to_protobuf
from ni.protobuf.types.waveform_pb2 import DoubleAnalogWaveform
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, Timing


@pytest.mark.parametrize("value", [True, False])
def test___publish_boolean_data___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
    value: bool,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    published_measurement = PublishedMeasurement(published_measurement_id="response_id")
    expected_response = PublishMeasurementResponse(published_measurement=published_measurement)
    mocked_data_store_service_client.publish_measurement.return_value = expected_response

    result = data_store_client.publish_measurement(
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

    args, __ = mocked_data_store_service_client.publish_measurement.call_args
    request = args[0]  # The PublishMeasurementRequest object
    assert result.published_measurement_id == "response_id"
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


def test___publish_analog_waveform_data___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    waveform_values = [1.0, 2.0, 3.0]
    analog_waveform = AnalogWaveform(
        sample_count=len(waveform_values),
        raw_data=np.array(waveform_values, dtype=np.float64),
        timing=Timing.create_with_regular_interval(timedelta(seconds=1), timestamp),
    )
    expected_protobuf_waveform = DoubleAnalogWaveform()
    expected_protobuf_waveform.CopyFrom(float64_analog_waveform_to_protobuf(analog_waveform))
    published_measurement = PublishedMeasurement(published_measurement_id="response_id")
    expected_response = PublishMeasurementResponse(published_measurement=published_measurement)
    mocked_data_store_service_client.publish_measurement.return_value = expected_response

    # Now, when client.publish_measurement calls foo.MyClass().publish(), it will use the mock
    result = data_store_client.publish_measurement(
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

    args, __ = mocked_data_store_service_client.publish_measurement.call_args
    request = cast(PublishMeasurementRequest, args[0])  # The PublishMeasurementRequest object
    assert result.published_measurement_id == "response_id"
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
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    waveform_values = [1.0, 2.0, 3.0]
    analog_waveform = AnalogWaveform(
        sample_count=len(waveform_values),
        raw_data=np.array(waveform_values, dtype=np.float64),
        timing=Timing.create_with_regular_interval(timedelta(seconds=1), timestamp),
    )
    published_measurement = PublishedMeasurement(published_measurement_id="response_id")
    publish_measurement_response = PublishMeasurementResponse(
        published_measurement=published_measurement
    )
    mocked_data_store_service_client.publish_measurement.return_value = publish_measurement_response

    result = data_store_client.publish_measurement("name", analog_waveform, "step_id")

    args, __ = mocked_data_store_service_client.publish_measurement.call_args
    request = cast(PublishMeasurementRequest, args[0])  # The PublishMeasurementRequest object
    assert result.published_measurement_id == "response_id"
    assert request.timestamp == hightime_datetime_to_protobuf(timestamp)


def test___publish_analog_waveform_data_without_t0___uses_timestamp_parameter(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    analog_waveform = AnalogWaveform.from_array_1d([1.0, 2.0, 3.0], dtype=float)
    published_measurement = PublishedMeasurement(published_measurement_id="response_id")
    publish_measurement_response = PublishMeasurementResponse(
        published_measurement=published_measurement
    )
    mocked_data_store_service_client.publish_measurement.return_value = publish_measurement_response

    result = data_store_client.publish_measurement("name", analog_waveform, "step_id", timestamp)

    args, __ = mocked_data_store_service_client.publish_measurement.call_args
    request = cast(PublishMeasurementRequest, args[0])  # The PublishMeasurementRequest object
    assert result.published_measurement_id == "response_id"
    assert request.timestamp == hightime_datetime_to_protobuf(timestamp)


def test___publish_analog_waveform_data_with_mismatched_timestamp_parameter___raises_error(
    data_store_client: DataStoreClient,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    waveform_values = [1.0, 2.0, 3.0]
    analog_waveform = AnalogWaveform(
        sample_count=len(waveform_values),
        raw_data=np.array(waveform_values, dtype=np.float64),
        timing=Timing.create_with_regular_interval(timedelta(seconds=1), timestamp),
    )
    mismatched_timestamp = timestamp + timedelta(seconds=1)

    with pytest.raises(ValueError):
        data_store_client.publish_measurement(
            "name", analog_waveform, "step_id", mismatched_timestamp
        )


def test___none___publish_measurement___raises_type_error(
    data_store_client: DataStoreClient,
) -> None:
    with pytest.raises(TypeError) as exc:
        _ = data_store_client.publish_measurement(
            measurement_name="name",
            value=None,
            step_id="step_id",
        )

    assert exc.value.args[0].startswith("Unsupported measurement value type")


def test___vector___publish_measurement_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    published_measurement = PublishedMeasurement(published_measurement_id="response_id")
    expected_response = PublishMeasurementBatchResponse(
        published_measurements=[published_measurement]
    )
    mocked_data_store_service_client.publish_measurement_batch.return_value = expected_response

    response = data_store_client.publish_measurement_batch(
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

    args, __ = mocked_data_store_service_client.publish_measurement_batch.call_args
    request = cast(PublishMeasurementBatchRequest, args[0])
    assert next(iter(response)).published_measurement_id == "response_id"
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


def test___int_list___publish_measurement_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    published_measurement = PublishedMeasurement(published_measurement_id="response_id")
    expected_response = PublishMeasurementBatchResponse(
        published_measurements=[published_measurement]
    )
    mocked_data_store_service_client.publish_measurement_batch.return_value = expected_response

    response = data_store_client.publish_measurement_batch(
        measurement_name="name",
        values=[1, 2, 3],
        step_id="step_id",
        timestamps=[timestamp],
        outcomes=[Outcome.OUTCOME_PASSED],
        error_information=[ErrorInformation()],
        hardware_item_ids=[],
        test_adapter_ids=[],
        software_item_ids=[],
    )

    args, __ = mocked_data_store_service_client.publish_measurement_batch.call_args
    request = cast(PublishMeasurementBatchRequest, args[0])
    assert next(iter(response)).published_measurement_id == "response_id"
    assert request.step_id == "step_id"
    assert request.measurement_name == "name"
    assert request.timestamp == [hightime_datetime_to_protobuf(timestamp)]
    assert request.scalar_values.sint32_array.values == [1, 2, 3]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___float_list___publish_measurement_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    published_measurement = PublishedMeasurement(published_measurement_id="response_id")
    expected_response = PublishMeasurementBatchResponse(
        published_measurements=[published_measurement]
    )
    mocked_data_store_service_client.publish_measurement_batch.return_value = expected_response

    response = data_store_client.publish_measurement_batch(
        measurement_name="name",
        values=[1.0, 2.0, 3.0],
        step_id="step_id",
        timestamps=[timestamp],
        outcomes=[Outcome.OUTCOME_PASSED],
        error_information=[ErrorInformation()],
        hardware_item_ids=[],
        test_adapter_ids=[],
        software_item_ids=[],
    )

    args, __ = mocked_data_store_service_client.publish_measurement_batch.call_args
    request = cast(PublishMeasurementBatchRequest, args[0])
    assert next(iter(response)).published_measurement_id == "response_id"
    assert request.step_id == "step_id"
    assert request.measurement_name == "name"
    assert request.timestamp == [hightime_datetime_to_protobuf(timestamp)]
    assert request.scalar_values.double_array.values == [1.0, 2.0, 3.0]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___bool_list___publish_measurement_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    published_measurement = PublishedMeasurement(published_measurement_id="response_id")
    expected_response = PublishMeasurementBatchResponse(
        published_measurements=[published_measurement]
    )
    mocked_data_store_service_client.publish_measurement_batch.return_value = expected_response

    response = data_store_client.publish_measurement_batch(
        measurement_name="name",
        values=[True, False, True],
        step_id="step_id",
        timestamps=[timestamp],
        outcomes=[Outcome.OUTCOME_PASSED],
        error_information=[ErrorInformation()],
        hardware_item_ids=[],
        test_adapter_ids=[],
        software_item_ids=[],
    )

    args, __ = mocked_data_store_service_client.publish_measurement_batch.call_args
    request = cast(PublishMeasurementBatchRequest, args[0])
    assert next(iter(response)).published_measurement_id == "response_id"
    assert request.step_id == "step_id"
    assert request.measurement_name == "name"
    assert request.timestamp == [hightime_datetime_to_protobuf(timestamp)]
    assert request.scalar_values.bool_array.values == [True, False, True]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___str_list___publish_measurement_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    timestamp = datetime.now(tz=std_datetime.timezone.utc)
    published_measurement = PublishedMeasurement(published_measurement_id="response_id")
    expected_response = PublishMeasurementBatchResponse(
        published_measurements=[published_measurement]
    )
    mocked_data_store_service_client.publish_measurement_batch.return_value = expected_response

    response = data_store_client.publish_measurement_batch(
        measurement_name="name",
        values=["one", "two", "three"],
        step_id="step_id",
        timestamps=[timestamp],
        outcomes=[Outcome.OUTCOME_PASSED],
        error_information=[ErrorInformation()],
        hardware_item_ids=[],
        test_adapter_ids=[],
        software_item_ids=[],
    )

    args, __ = mocked_data_store_service_client.publish_measurement_batch.call_args
    request = cast(PublishMeasurementBatchRequest, args[0])
    assert next(iter(response)).published_measurement_id == "response_id"
    assert request.step_id == "step_id"
    assert request.measurement_name == "name"
    assert request.timestamp == [hightime_datetime_to_protobuf(timestamp)]
    assert request.scalar_values.string_array.values == ["one", "two", "three"]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___unsupported_list___publish_measurement_batch___raises_type_error(
    data_store_client: DataStoreClient,
) -> None:
    with pytest.raises(TypeError) as exc:
        _ = data_store_client.publish_measurement_batch(
            measurement_name="name",
            values=[[1, 2, 3], [4, 5, 6]],  # List of lists will error during vector creation.
            step_id="step_id",
        )

    assert exc.value.args[0].startswith("Unsupported iterable:")


def test___empty_list___publish_measurement_batch___raises_type_error(
    data_store_client: DataStoreClient,
) -> None:
    with pytest.raises(ValueError) as exc:
        _ = data_store_client.publish_measurement_batch(
            measurement_name="name",
            values=[],
            step_id="step_id",
        )

    assert exc.value.args[0].startswith("Cannot publish an empty Iterable.")


def test___none___publish_measurement_batch___raises_type_error(
    data_store_client: DataStoreClient,
) -> None:
    with pytest.raises(TypeError) as exc:
        _ = data_store_client.publish_measurement_batch(
            measurement_name="name",
            values=None,
            step_id="step_id",
        )

    assert exc.value.args[0].startswith("Unsupported measurement values type")
