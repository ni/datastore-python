"""Acceptance tests that exercise DataStoreClient.query_steps()."""

from ni.datastore.data import DataStoreClient, Step, TestResult

from tests.acceptance._utils import append_hashed_time, create_step


def test___query_steps___filter_by_id___single_step_returned() -> None:
    with DataStoreClient() as data_store_client:
        step_id = create_step(data_store_client, "query steps filter by id")

        # Publish a measurement so that our single step gets published.
        measurement_name = "query filter by id measurement"
        data_store_client.publish_measurement(
            measurement_name=measurement_name,
            value=123.45,
            step_id=step_id,
        )

        # Query steps based on id.
        queried_steps = data_store_client.query_steps(odata_query=f"$filter=id eq {step_id}")

        # We should get one step back.
        assert len(queried_steps) == 1
        first_step = queried_steps[0]
        assert first_step is not None
        assert first_step.step_name == "query steps filter by id step"


def test___query_steps___filter_by_name___correct_steps_returned() -> None:
    with DataStoreClient() as data_store_client:
        description = "query steps filter by name"
        test_result_name = f"{description} test result"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create multiple similarly named steps and published a measurement for each.
        step_name_base = append_hashed_time(description)
        for index in range(0, 3):
            step_name = f"{step_name_base} {index}"
            step = Step(step_name=step_name, test_result_id=test_result_id)
            step_id = data_store_client.create_step(step)
            data_store_client.publish_measurement(
                measurement_name="some measurement",
                value=123,
                step_id=step_id,
            )

        # Create and publish one more step/measurement that doesn't match the naming pattern.
        step = Step(step_name="some other step name", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        data_store_client.publish_measurement(
            measurement_name="some measurement",
            value=123,
            step_id=step_id,
        )

        # Query steps based on name.
        queried_steps = data_store_client.query_steps(
            odata_query=f"$filter=contains(Name,'{step_name_base}')"
        )

        # We should get three steps back.
        assert len(queried_steps) == 3
        for queried_step in queried_steps:
            assert queried_step is not None
