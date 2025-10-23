"""Acceptance test utility functions."""

import datetime as dt

from ni.datastore.data import (
    DataStoreClient,
    Step,
    TestResult,
)


def create_test_result_and_step(data_store_client: DataStoreClient, description: str) -> str:
    """Create a single step within a single test result and return the step_id."""
    test_result_name = f"{description} test result"
    test_result = TestResult(test_result_name=test_result_name)
    test_result_id = data_store_client.create_test_result(test_result)

    step = Step(step_name=f"{description} step", test_result_id=test_result_id)
    step_id = data_store_client.create_step(step)
    return step_id


def append_hashed_time(base_string: str) -> str:
    """Append the hash of the current time to a given string."""
    current_time = dt.datetime.now()
    time_hash = hash(current_time)
    return f"{base_string}-{time_hash}"
