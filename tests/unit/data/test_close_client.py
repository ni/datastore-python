"""Contains tests related to closing the DataStoreClient."""

from __future__ import annotations

from unittest.mock import NonCallableMock

import pytest
from ni.datastore.data import DataStoreClient


def test___exit_data_store_client_context___calls_close_on_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    data_store_client.query_measurements()

    with data_store_client:
        pass

    mocked_data_store_service_client.close.assert_called_once()


def test___close_data_store_client___calls_close_on_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    data_store_client.query_measurements()

    data_store_client.close()

    mocked_data_store_service_client.close.assert_called_once()


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
