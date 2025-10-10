"""Contains tests related to closing the DataStoreClient."""

from __future__ import annotations

import pytest
from ni.datastore.data import DataStoreClient


def test___exit_data_store_client_context___call_method___raises_error() -> None:
    with DataStoreClient() as data_store_client:
        pass

    with pytest.raises(RuntimeError) as exc:
        data_store_client.query_measurements()

    assert exc.value.args[0] == DataStoreClient._DATA_STORE_CLIENT_CLOSED_ERROR


def test___close_data_store_client___call_method___raises_error() -> None:
    data_store_client = DataStoreClient()
    data_store_client.close()

    with pytest.raises(RuntimeError) as exc:
        data_store_client.query_measurements()

    assert exc.value.args[0] == DataStoreClient._DATA_STORE_CLIENT_CLOSED_ERROR
