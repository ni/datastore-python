"""Contains tests to validate the datastore client functionality."""

from __future__ import annotations

import datetime as dt
import unittest.mock
from typing import Any
from unittest.mock import Mock

import pytest
from ni.datastore.client import Client
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    PublishedMeasurement,
)
from ni.measurements.data.v1.data_store_service_pb2 import PublishMeasurementResponse
from nitypes.bintime import DateTime
from pytest_mock import MockerFixture


@pytest.mark.parametrize("value", [True, False])
def test__publish_measurement_data__calls_datastoreclient(
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


@pytest.fixture
def mocked_datastore_client(mocker: MockerFixture) -> Any:
    mock_datastore_client = mocker.patch(
        "ni.measurements.data.v1.client.DataStoreClient", autospec=True
    )
    # Set up the mock's publish method
    mock_datastore_instance = mock_datastore_client.return_value
    return mock_datastore_instance
