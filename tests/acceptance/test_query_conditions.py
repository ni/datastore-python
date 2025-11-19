"""Acceptance tests that exercise DataStoreClient.query_conditions()."""

from ni.datastore.data import DataStoreClient
from nitypes.vector import Vector
from utilities import DataStoreContext

from tests.acceptance._utils import append_hashed_time, create_test_result_and_step


def test___query_conditions___filter_by_id___single_condition_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    with DataStoreClient() as data_store_client:
        step_id = create_test_result_and_step(data_store_client, "query condition filter by id")

        # Publish a single condition
        condition_name = "query filter by id condition"
        published_condition_id = data_store_client.publish_condition(
            name=condition_name,
            condition_type="Upper Limit",
            value=123.45,
            step_id=step_id,
        )

        # Query conditions based on id.
        queried_conditions = data_store_client.query_conditions(
            odata_query=f"$filter=id eq {published_condition_id}"
        )

        #  We should get one condition back.
        assert len(queried_conditions) == 1
        first_condition = queried_conditions[0]
        assert first_condition is not None
        assert first_condition.name == condition_name

        # Check the value of the queried condition.
        vector = data_store_client.read_data(first_condition, expected_type=Vector)
        assert len(vector) == 1
        assert vector[0] == 123.45
        assert vector.units == ""


def test___query_conditions___filter_by_name___correct_conditions_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    with DataStoreClient() as data_store_client:
        step_id = create_test_result_and_step(data_store_client, "query condition filter by name")

        # Publish several similarly named conditions. These names should be unique for each
        # run of this test to prevent previous results from causing the test to fail.
        condition_name_base = append_hashed_time("query filter by name condition")
        for index in range(0, 3):
            condition_name = f"{condition_name_base} {index}"
            data_store_client.publish_condition(
                name=condition_name,
                condition_type="Condition Type",
                value=index,
                step_id=step_id,
            )

        # Publish one differently named condition to adequately test filtering.
        data_store_client.publish_condition(
            name="some other condition",
            condition_type="Condition Type",
            value=123,
            step_id=step_id,
        )

        # Query conditions based on name.
        queried_conditions = data_store_client.query_conditions(
            odata_query=f"$filter=contains(Name,'{condition_name_base}')"
        )

        # We should get three conditions back.
        assert len(queried_conditions) == 3

        # Check the value of each queried condition.
        for condition in queried_conditions:
            assert condition is not None
            vector = data_store_client.read_data(condition, expected_type=Vector)
            assert condition.name == f"{condition_name_base} {vector[0]}"
            assert vector.units == ""
