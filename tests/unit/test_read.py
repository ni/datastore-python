"""Contains tests to validate the datastore client read functionality."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock

from google.protobuf.any_pb2 import Any as gpAny
from ni.datamonikers.v1.data_moniker_pb2 import Moniker, ReadFromMonikerResult
from ni.datastore.client import Client
from ni.protobuf.types.waveform_pb2 import DoubleAnalogWaveform
from nitypes.waveform import AnalogWaveform


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
