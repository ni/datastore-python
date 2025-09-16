"""Contains tests to validate the datastore client functionality."""

from __future__ import annotations

import datetime as dt
import unittest.mock
from typing import Any, cast
from unittest.mock import Mock

import pytest
from ni.datamonikers.v1.data_moniker_pb2 import Moniker, ReadFromMonikerResult
from ni.datastore.client import Client
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    PublishedMeasurement,
)
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishMeasurementRequest,
    PublishMeasurementResponse
)
from ni.protobuf.types.waveform_conversion import float64_analog_waveform_to_protobuf
from ni.protobuf.types.waveform_pb2 import DoubleAnalogWaveform
from ni.protobuf.types.vector_pb2 import Vector
from nitypes.waveform import AnalogWaveform
from nitypes.bintime import DateTime
from pytest_mock import MockerFixture


@pytest.mark.parametrize("value", [True, False])
def test__publish_boolean_data__calls_datastoreclient(
    mocked_datastore_client: Mock, value: bool
) -> None:
    timestamp = DateTime.now(tz=dt.timezone.utc)
    published_measurement = PublishedMeasurement()
    publish_measurement_response = PublishMeasurementResponse(
        published_measurement=published_measurement
    )
    mocked_datastore_client.publish_measurement.return_value = publish_measurement_response
    client = Client(data_store_client=mocked_datastore_client)
    # Now, when client.publish_measurement_data calls foo.MyClass().publish(), it will use the mock
    client.publish_measurement_data(
        "step_id",
        "name",
        "notes",
        timestamp,
        value,
        Outcome.OUTCOME_PASSED,
        ErrorInformation(),
        [],
        [],
        [],
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


def test__publish_analog_waveform_data__calls_datastoreclient(
    mocked_datastore_client: Mock
) -> None:
    timestamp = DateTime.now(tz=dt.timezone.utc)
    published_measurement = PublishedMeasurement()
    publish_measurement_response = PublishMeasurementResponse(
        published_measurement=published_measurement
    )
    mocked_datastore_client.publish_measurement.return_value = publish_measurement_response
    waveform_values = [1.0, 2.0, 3.0]
    analog_waveform = AnalogWaveform.from_array_1d(waveform_values, dtype=float)
    expected_protobuf_waveform = DoubleAnalogWaveform()
    expected_protobuf_waveform.CopyFrom(float64_analog_waveform_to_protobuf(analog_waveform))
    client = Client(data_store_client=mocked_datastore_client)
    # Now, when client.publish_measurement_data calls foo.MyClass().publish(), it will use the mock
    client.publish_measurement_data(
        "step_id",
        "name",
        "notes",
        timestamp,
        analog_waveform,
        Outcome.OUTCOME_PASSED,
        ErrorInformation(),
        [],
        [],
        [],
    )
    args, __ = mocked_datastore_client.publish_measurement.call_args
    request = cast(PublishMeasurementRequest, args[0])  # The PublishMeasurementRequest object

    # Now assert on its fields
    assert request.step_id == "step_id"
    assert request.measurement_name == "name"
    assert request.notes == "notes"
    assert request.timestamp == unittest.mock.ANY
    assert request.double_analog_waveform == expected_protobuf_waveform
    assert request.outcome == Outcome.OUTCOME_PASSED
    assert request.error_information == ErrorInformation()
    assert request.hardware_item_ids == []
    assert request.software_item_ids == []
    assert request.test_adapter_ids == []


def test__read_boolean_data__calls_monikerclient(
    mocked_moniker_client: Mock
) -> None:
    client = Client(moniker_client=mocked_moniker_client)
    moniker = Moniker()
    moniker.data_instance = 12
    moniker.data_source = "ABCD123"
    moniker.service_location = "localhost:50051"
    client.read_measurement_data(moniker, type[Vector])
    mocked_moniker_client.read_from_moniker.return_value = ReadFromMonikerResult()

    args, __ = mocked_moniker_client.read_from_moniker.call_args
    requested_moniker = cast(Moniker, args[0])

    assert requested_moniker.service_location == moniker.service_location
    assert requested_moniker.data_instance == moniker.data_instance
    assert requested_moniker.data_source == moniker.data_source


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
    mock_moniker_client = mocker.patch(
        "ni.datamonikers.v1.client.MonikerClient", autospec=True
    )
    # Set up the mock's publish method
    mock_moniker_instance = mock_moniker_client.return_value
    return mock_moniker_instance
