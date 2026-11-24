"""Fixtures for acceptance tests that require a V2 Data Store service."""

from typing import Generator

import pytest
from utilities import DataStoreContext


@pytest.fixture(scope="module")
def acceptance_test_context() -> Generator[DataStoreContext, None, None]:
    """Set up isolated discovery and storage settings for the V2 service tests."""
    with DataStoreContext() as data_store_context:
        yield data_store_context
