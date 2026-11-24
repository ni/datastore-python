"""Acceptance tests for paginating V2 resource queries."""

from utilities import DataStoreContext

from ni.datastore.data.v2 import DataStoreClient
from tests.acceptance._utils import append_hashed_time


def test___query_steps___follows_page_tokens_until_all_matches_are_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    name_prefix = append_hashed_time("v2 pagination step")

    with DataStoreClient() as data_store_client:
        test_result = data_store_client.create_test_result(f"{name_prefix} test result")
        steps = [
            data_store_client.create_step(f"{name_prefix} {index}", test_result_id=test_result.id)
            for index in range(3)
        ]
        expected_ids = {step.id for step in steps}
        odata_query = f"$filter=contains(Name,'{name_prefix}')"
        page = data_store_client.query_steps(odata_query, page_size=1)
        queried_ids: list[str] = []
        seen_tokens = set()

        while True:
            assert len(page) <= 1
            queried_ids.extend(step.id for step in page)
            if not page.next_page_token:
                break

            assert page.next_page_token not in seen_tokens
            seen_tokens.add(page.next_page_token)
            page = data_store_client.query_steps(
                odata_query, page_size=1, page_token=page.next_page_token
            )

    assert set(queried_ids) == expected_ids
    assert len(queried_ids) == len(expected_ids)


def test___query_test_results___follows_page_tokens_until_all_matches_are_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    name_prefix = append_hashed_time("v2 pagination test result")

    with DataStoreClient() as data_store_client:
        test_results = [
            data_store_client.create_test_result(f"{name_prefix} {index}") for index in range(3)
        ]
        expected_ids = {test_result.id for test_result in test_results}
        odata_query = f"$filter=contains(Name,'{name_prefix}')"
        page = data_store_client.query_test_results(odata_query, page_size=1)
        queried_ids: list[str] = []
        seen_tokens = set()

        while True:
            queried_ids.extend(test_result.id for test_result in page)
            if not page.next_page_token:
                break

            assert page.next_page_token not in seen_tokens
            seen_tokens.add(page.next_page_token)
            page = data_store_client.query_test_results(
                odata_query, page_size=1, page_token=page.next_page_token
            )

    assert set(queried_ids) == expected_ids
    assert len(queried_ids) == len(expected_ids)
