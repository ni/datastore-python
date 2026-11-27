"""Acceptance tests for V2 batch creation and resource mutations."""

from utilities import DataStoreContext

from ni.datastore.data.v2 import DataStoreClient, Step, TestResult
from tests.acceptance._utils import append_hashed_time


def test___batch_create_test_results___returns_created_resources(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 batch test results")
    expected_names = [f"{description} {index}" for index in range(2)]

    with DataStoreClient() as data_store_client:
        test_results = data_store_client.batch_create_test_results(
            [TestResult(name=name) for name in expected_names]
        )

    assert [test_result.name for test_result in test_results] == expected_names
    assert all(test_result.id for test_result in test_results)
    assert len({test_result.id for test_result in test_results}) == len(expected_names)


def test___batch_create_steps___returns_created_resources(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 batch steps")
    expected_names = [f"{description} {index}" for index in range(2)]

    with DataStoreClient() as data_store_client:
        test_result = data_store_client.create_test_result(f"{description} test result")
        steps = data_store_client.batch_create_steps(
            [Step(name=name, test_result_id=test_result.id) for name in expected_names]
        )

    assert [step.name for step in steps] == expected_names
    assert all(step.id for step in steps)
    assert len({step.id for step in steps}) == len(expected_names)


def test___resource_mutations___updates_then_deletes_created_resources(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 resource mutations")

    with DataStoreClient() as data_store_client:
        test_result = data_store_client.create_test_result(f"{description} test result")
        step = data_store_client.create_step(f"{description} step", test_result_id=test_result.id)
        measurement = data_store_client.create_measurement(
            f"{description} measurement", 1.0, step.id
        )

        updated_test_result = data_store_client.update_test_result(
            test_result.id, link=f"https://example.test/{description.replace(' ', '-')}"
        )
        updated_step = data_store_client.update_step(step.id, notes="Updated by acceptance test")
        updated_measurement = data_store_client.update_measurement(
            measurement.id, notes="Updated by acceptance test"
        )

        assert updated_test_result.link == f"https://example.test/{description.replace(' ', '-')}"
        assert updated_step.notes == "Updated by acceptance test"
        assert updated_measurement.notes == "Updated by acceptance test"

        data_store_client.delete_measurement(measurement)
        assert not data_store_client.query_measurements(f"$filter=id eq {measurement.id}")

        data_store_client.delete_step(step)
        assert not data_store_client.query_steps(f"$filter=id eq {step.id}")

        data_store_client.delete_test_result(test_result)
        assert not data_store_client.query_test_results(f"$filter=id eq {test_result.id}")


def test___batch_resource_mutations___updates_and_deletes_created_resources(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 batch resource mutations")
    link_prefix = description.replace(" ", "-")

    with DataStoreClient() as data_store_client:
        test_results = [
            data_store_client.create_test_result(f"{description} test result {index}")
            for index in range(2)
        ]
        steps = [
            data_store_client.create_step(
                f"{description} step {index}", test_result_id=test_result.id
            )
            for index, test_result in enumerate(test_results)
        ]
        measurements = [
            data_store_client.create_measurement(
                f"{description} measurement {index}", float(index), step.id
            )
            for index, step in enumerate(steps)
        ]

        updated_test_results = data_store_client.batch_update_test_results(
            {
                test_result.id: {"link": f"https://example.test/{link_prefix}-{index}"}
                for index, test_result in enumerate(test_results)
            }
        )
        updated_steps = data_store_client.batch_update_steps(
            {step.id: {"notes": f"Updated step {index}"} for index, step in enumerate(steps)}
        )
        updated_measurements = data_store_client.batch_update_measurements(
            {
                measurement.id: {"notes": f"Updated measurement {index}"}
                for index, measurement in enumerate(measurements)
            }
        )

        assert [test_result.link for test_result in updated_test_results] == [
            f"https://example.test/{link_prefix}-{index}" for index in range(2)
        ]
        assert [step.notes for step in updated_steps] == ["Updated step 0", "Updated step 1"]
        assert [measurement.notes for measurement in updated_measurements] == [
            "Updated measurement 0",
            "Updated measurement 1",
        ]

        data_store_client.batch_delete_measurements(measurements)
        data_store_client.batch_delete_steps(steps)
        data_store_client.batch_delete_test_results(test_results)

        for measurement in measurements:
            assert not data_store_client.query_measurements(f"$filter=id eq {measurement.id}")
        for step in steps:
            assert not data_store_client.query_steps(f"$filter=id eq {step.id}")
        for test_result in test_results:
            assert not data_store_client.query_test_results(f"$filter=id eq {test_result.id}")
