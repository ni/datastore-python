"""Contains test fixtures used by the unit tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import NonCallableMock

import pytest
from ni.datastore import Client
from pytest_mock import MockerFixture


@pytest.fixture
def client(
    mocked_datastore_client: NonCallableMock,
    mocked_metadatastore_client: NonCallableMock,
    mocked_moniker_client: NonCallableMock,
    mocker: MockerFixture,
) -> Client:
    """Returns the pytest fixture for the client."""
    mocker.patch.object(Client, "_get_data_store_client", return_value=mocked_datastore_client)
    mocker.patch.object(
        Client, "_get_metadata_store_client", return_value=mocked_metadatastore_client
    )
    mocker.patch.object(Client, "_get_moniker_client", return_value=mocked_moniker_client)
    return Client()


@pytest.fixture
def mocked_datastore_client(mocker: MockerFixture) -> Any:
    """Returns the pytest fixture for a mocked datastore client."""
    mock_datastore_client = mocker.patch(
        "ni.measurements.data.v1.client.DataStoreClient", autospec=True
    )
    mock_datastore_instance = mock_datastore_client.return_value
    return mock_datastore_instance


@pytest.fixture
def mocked_metadatastore_client(mocker: MockerFixture) -> Any:
    """Returns the pytest fixture for a mocked metadatastore client."""
    mock_metadatastore_client = mocker.patch(
        "ni.measurements.metadata.v1.client.MetadataStoreClient", autospec=True
    )
    mock_metadatastore_instance = mock_metadatastore_client.return_value
    return mock_metadatastore_instance


@pytest.fixture
def mocked_moniker_client(mocker: MockerFixture) -> Any:
    """Returns the pytest fixture for a mocked moniker client."""
    mock_moniker_client = mocker.patch("ni.datamonikers.v1.client.MonikerClient", autospec=True)
    mock_moniker_instance = mock_moniker_client.return_value
    return mock_moniker_instance


@pytest.fixture(scope="module")
def schemas_directory(test_assets_directory: Path) -> Path:
    """Returns the test assets directory containing schemas."""
    return test_assets_directory / "unit" / "schemas"


@pytest.fixture(scope="module")
def test_assets_directory() -> Path:
    """Returns the test assets directory."""
    return Path(__file__).parent.parent / "assets"
