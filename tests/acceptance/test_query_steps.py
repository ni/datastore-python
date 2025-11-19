"""Acceptance tests that exercise DataStoreClient.query_steps()."""

from ni.datastore.data import DataStoreClient, Step, TestResult
from utilities import DataStoreContext

from tests.acceptance._utils import append_hashed_time, create_test_result_and_step


def test___query_steps___filter_by_id___single_step_returned() -> None:
    with DataStoreContext(), DataStoreClient() as data_store_client:
        step_id = create_test_result_and_step(data_store_client, "query steps filter by id")

        # Query steps based on id.
        queried_steps = data_store_client.query_steps(odata_query=f"$filter=id eq {step_id}")

        # We should get one step back.
        assert len(queried_steps) == 1
        first_step = queried_steps[0]
        assert first_step is not None
        assert first_step.name == "query steps filter by id step"


def test___query_steps___filter_by_name___correct_steps_returned() -> None:
    with DataStoreContext(), DataStoreClient() as data_store_client:
        description = "query steps filter by name"
        test_result_name = f"{description} test result"
        test_result = TestResult(name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create multiple similarly named steps and published a measurement for each.
        step_name_base = append_hashed_time(description)
        for index in range(0, 3):
            step_name = f"{step_name_base} {index}"
            step = Step(name=step_name, test_result_id=test_result_id)
            _ = data_store_client.create_step(step)

        # Create and publish one more step/measurement that doesn't match the naming pattern.
        step = Step(name="some other step name", test_result_id=test_result_id)
        _ = data_store_client.create_step(step)

        # Query steps based on name.
        queried_steps = data_store_client.query_steps(
            odata_query=f"$filter=contains(Name,'{step_name_base}')"
        )

        # We should get three steps back.
        assert len(queried_steps) == 3
        for queried_step in queried_steps:
            assert queried_step is not None
