"""Contains test fixtures used by the data store unit tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import NonCallableMock

import pytest
from ni.datastore.data import DataStoreClient
from pytest_mock import MockerFixture


@pytest.fixture
def data_store_client(
    mocked_data_store_service_client: NonCallableMock,
    mocked_moniker_client: NonCallableMock,
    mocker: MockerFixture,
) -> DataStoreClient:
    """Returns the pytest fixture for the data store client."""
    mocker.patch.object(
        DataStoreClient, "_get_data_store_client", return_value=mocked_data_store_service_client
    )
    mocker.patch.object(DataStoreClient, "_get_moniker_client", return_value=mocked_moniker_client)
    return DataStoreClient()


@pytest.fixture
def mocked_data_store_service_client(mocker: MockerFixture) -> Any:
    """Returns the pytest fixture for a mocked data store service client."""
    mock_datastore_client = mocker.patch(
        "ni.measurements.data.v1.client.DataStoreClient", autospec=True
    )
    mock_datastore_instance = mock_datastore_client.return_value
    return mock_datastore_instance


@pytest.fixture
def mocked_moniker_client(mocker: MockerFixture) -> Any:
    """Returns the pytest fixture for a mocked moniker client."""
    mock_moniker_client = mocker.patch("ni.datamonikers.v1.client.MonikerClient", autospec=True)
    mock_moniker_instance = mock_moniker_client.return_value
    return mock_moniker_instance
