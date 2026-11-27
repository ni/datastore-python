"""Helpers for V2 Data Store acceptance tests."""

from ni.datastore.data.v2 import DataStoreClient, Step


def create_test_result_and_step(data_store_client: DataStoreClient, description: str) -> Step:
    """Create a test result and an initial step for the given acceptance case."""
    test_result = data_store_client.create_test_result(f"{description} test result")
    return data_store_client.create_step(f"{description} step", test_result_id=test_result.id)
