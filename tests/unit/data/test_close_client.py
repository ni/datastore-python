"""Contains tests related to closing the DataStoreClient."""

from __future__ import annotations

from unittest.mock import NonCallableMock

import pytest
from google.protobuf.any_pb2 import Any as gpAny
from ni.datamonikers.v1.data_moniker_pb2 import ReadFromMonikerResult
from ni.datastore.data import DataStoreClient, Moniker
from ni.protobuf.types import waveform_pb2


def test___exit_data_store_client_context___calls_close_on_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    data_store_client.query_measurements()

    with data_store_client:
        pass

    mocked_data_store_service_client.close.assert_called_once()


def test___exit_data_store_client_context___calls_close_on_moniker_client(
    data_store_client: DataStoreClient,
    mocked_moniker_client: NonCallableMock,
) -> None:

    mocked_moniker_client.read_from_moniker.return_value = _create_read_from_moniker_result()
    data_store_client.read_data(Moniker(service_location="http://localhost:50051"))

    with data_store_client:
        pass

    mocked_moniker_client.close.assert_called_once()


def test___close_data_store_client___calls_close_on_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    data_store_client.query_measurements()

    data_store_client.close()

    mocked_data_store_service_client.close.assert_called_once()


def test___close_data_store_client___calls_close_on_moniker_client(
    data_store_client: DataStoreClient,
    mocked_moniker_client: NonCallableMock,
) -> None:
    mocked_moniker_client.read_from_moniker.return_value = _create_read_from_moniker_result()
    data_store_client.read_data(Moniker(service_location="http://localhost:50051"))

    data_store_client.close()

    mocked_moniker_client.close.assert_called_once()


def test___exit_data_store_client_context___call_method___raises_error(
    data_store_client: DataStoreClient,
) -> None:
    with data_store_client:
        pass

    with pytest.raises(RuntimeError) as exc:
        data_store_client.query_measurements()

    assert exc.value.args[0] == DataStoreClient._DATA_STORE_CLIENT_CLOSED_ERROR


def test___close_data_store_client___call_method___raises_error(
    data_store_client: DataStoreClient,
) -> None:
    data_store_client.close()

    with pytest.raises(RuntimeError) as exc:
        data_store_client.query_measurements()

    assert exc.value.args[0] == DataStoreClient._DATA_STORE_CLIENT_CLOSED_ERROR


def _create_read_from_moniker_result() -> ReadFromMonikerResult:
    read_result = ReadFromMonikerResult()
    value_to_read = gpAny()
    value_to_read.Pack(waveform_pb2.DoubleAnalogWaveform(y_data=[1.0, 2.0, 3.0]))
    read_result.value.CopyFrom(value_to_read)
    return read_result
