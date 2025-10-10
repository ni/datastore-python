"""Contains tests related to closing the MetadataStoreClient."""

from __future__ import annotations

from unittest.mock import NonCallableMock

import pytest
from ni.datastore.metadata import MetadataStoreClient


def test___exit_metadata_store_client_context___calls_close_on_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    metadata_store_client.query_operators()

    with metadata_store_client:
        pass

    mocked_metadata_store_service_client.close.assert_called_once()


def test___close_metadata_store_client___calls_close_on_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
) -> None:
    metadata_store_client.query_operators()

    metadata_store_client.close()

    mocked_metadata_store_service_client.close.assert_called_once()


def test___exit_metadata_store_client_context___call_method___raises_error() -> None:
    with MetadataStoreClient() as metadata_store_client:
        pass

    with pytest.raises(RuntimeError) as exc:
        metadata_store_client.query_operators()

    assert exc.value.args[0] == MetadataStoreClient._METADATA_STORE_CLIENT_CLOSED_ERROR


def test___close_metadata_store_client___call_method___raises_error() -> None:
    metadata_store_client = MetadataStoreClient()
    metadata_store_client.close()

    with pytest.raises(RuntimeError) as exc:
        metadata_store_client.query_operators()

    assert exc.value.args[0] == MetadataStoreClient._METADATA_STORE_CLIENT_CLOSED_ERROR
