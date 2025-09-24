"""Contains test fixtures used by the unit tests."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mocked_datastore_client(mocker: MockerFixture) -> Any:
    """Returns the pytest fixture for a mocked datastore client."""
    mock_datastore_client = mocker.patch(
        "ni.measurements.data.v1.client.DataStoreClient", autospec=True
    )
    # Set up the mock's publish method
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
    # Set up the mock's publish method
    mock_moniker_instance = mock_moniker_client.return_value
    return mock_moniker_instance
