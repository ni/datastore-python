"""Contains tests to validate the datastore client functionality."""
from __future__ import annotations

import pytest

from nitypes.bintime import DateTime
from ni.datastore.client import Client
from ni.measurements.data.v1.data_store_pb2 import Outcome, ErrorInformation


def test__datastore_client() -> None:
    assert True

# Not Implemented in client.py
# @pytest.mark.parametrize("value", [True, False])
# def test_publish_and_read_bool(value: bool):
#     client = Client()
#     step_id = client.create_step(
#         "Test Step",
#         "Type A",
#         "This is a test step.",
#         start_time=DateTime.now(),
#         end_time=DateTime.now(),
#     )
#     published_measurement = client.publish_measurement_data(
#         step_id,
#         "test_bool_publish",
#         "Notes on measurement",
#         DateTime.now(),
#         value,
#         Outcome(),
#         ErrorInformation(),
#         [],
#         [],
#         [])
#     print(f"Published boolean value {value}, stored data value: {published_measurement}")
#     read_value = client.read_measurement_data(published_measurement.moniker)
#     print(f"Read boolean value: {read_value}")
#     assert read_value == value, f"Expected {value}, got {read_value}"
