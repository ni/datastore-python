"""Acceptance tests that exercise DataStoreClient.query_test_results()."""

from ni.datastore.data import DataStoreClient

from tests.acceptance._utils import append_hashed_time, create_test_result


def test___query_test_results___filter_by_id___single_test_result_returned() -> None:
    with DataStoreClient() as data_store_client:
        description = "query test result filter by id"
        test_result_id = create_test_result(data_store_client, description)

        # Query test results based on id.
        queried_test_results = data_store_client.query_test_results(
            odata_query=f"$filter=id eq {test_result_id}"
        )

        # We should get one test result back.
        assert len(queried_test_results) == 1
        first_test_result = queried_test_results[0]
        assert first_test_result is not None
        assert first_test_result.test_result_name == f"{description} test result"


def test___query_steps___filter_by_name___correct_steps_returned() -> None:
    with DataStoreClient() as data_store_client:
        description = "query test results filter by name"

        # Create multiple similarly named test results.
        test_result_name_base = append_hashed_time(description)
        for index in range(0, 3):
            test_result_name = f"{test_result_name_base} {index}"
            _ = create_test_result(data_store_client, test_result_name)

        # Create one more test result that doesn't match the naming pattern.
        _ = create_test_result(data_store_client, "some other test result name")

        # Query test results based on name.
        queried_test_results = data_store_client.query_test_results(
            odata_query=f"$filter=contains(Name,'{test_result_name_base}')"
        )

        # We should get three test results back.
        assert len(queried_test_results) == 3
        for queried_test_result in queried_test_results:
            assert queried_test_result is not None
