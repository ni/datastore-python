"""Contains test fixtures used by the data store and metadata store acceptance tests."""

from typing import Generator

import pytest
from utilities import DataStoreContext


@pytest.fixture(scope="module")
def acceptance_test_context() -> Generator[DataStoreContext, None, None]:
    """Returns the pytest fixture for launching the data store in a testing context."""
    with DataStoreContext() as data_store_context:
        yield data_store_context
