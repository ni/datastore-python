"""Contains test fixtures used by the metadata store unit tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import NonCallableMock

import pytest
from ni.datastore.metadata import MetadataStoreClient
from pytest_mock import MockerFixture


@pytest.fixture
def metadata_store_client(
    mocked_metadata_store_service_client: NonCallableMock,
    mocker: MockerFixture,
) -> MetadataStoreClient:
    """Returns the pytest fixture for the metadata store client."""
    mocker.patch.object(
        MetadataStoreClient,
        "_get_metadata_store_client",
        return_value=mocked_metadata_store_service_client,
    )
    return MetadataStoreClient()


@pytest.fixture
def mocked_metadata_store_service_client(mocker: MockerFixture) -> Any:
    """Returns the pytest fixture for a mocked metadata store service client."""
    mock_metadatastore_client = mocker.patch(
        "ni.measurements.metadata.v1.client.MetadataStoreClient", autospec=True
    )
    mock_metadatastore_instance = mock_metadatastore_client.return_value
    return mock_metadatastore_instance


@pytest.fixture(scope="module")
def schemas_directory(test_assets_directory: Path) -> Path:
    """Returns the test assets directory containing schemas."""
    return test_assets_directory / "unit" / "metadata" / "schemas"


@pytest.fixture(scope="module")
def test_assets_directory() -> Path:
    """Returns the test assets directory."""
    return Path(__file__).parent.parent.parent / "assets"
