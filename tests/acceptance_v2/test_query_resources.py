"""Acceptance tests for filtering V2 measurements, steps, and test results."""

from nitypes.scalar import Scalar
from utilities import DataStoreContext

from ni.datastore.data.v2 import (
    DataStoreClient,
    MeasurementField,
    StepField,
    TestResultField,
)
from tests.acceptance._utils import append_hashed_time
from tests.acceptance_v2._utils import create_test_result_and_step


def test___query_measurements___filter_by_id___single_measurement_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 query measurement by id")

    with DataStoreClient() as data_store_client:
        step = create_test_result_and_step(data_store_client, description)
        measurement = data_store_client.create_measurement(
            "query filter by id measurement", 123.45, step.id
        )
        queried_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {measurement.id}",
            read_fields=[MeasurementField.ID, MeasurementField.NAME],
        )
        assert len(queried_measurements) == 1
        found_measurement = queried_measurements[0]
        value = data_store_client.read_measurement_value(found_measurement.id, Scalar)

    assert found_measurement.name == "query filter by id measurement"
    assert value == Scalar(123.45)


def test___query_measurements___filter_by_name___correct_measurements_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 query measurement by name")
    name_base = f"{description} measurement"

    with DataStoreClient() as data_store_client:
        step = create_test_result_and_step(data_store_client, description)
        expected_names = {f"{name_base} {index}" for index in range(3)}
        for index, name in enumerate(sorted(expected_names)):
            data_store_client.create_measurement(name, index, step.id)
        data_store_client.create_measurement("some other measurement", 123, step.id)

        queried_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=contains(Name,'{name_base}')",
            read_fields=[MeasurementField.ID, MeasurementField.NAME],
        )
        found_names = {measurement.name for measurement in queried_measurements}
        values_by_name = {
            measurement.name: data_store_client.read_measurement_value(measurement.id, Scalar).value
            for measurement in queried_measurements
        }

    assert found_names == expected_names
    assert values_by_name == {f"{name_base} {index}": index for index in range(3)}


def test___query_steps___filter_by_id___single_step_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 query step by id")

    with DataStoreClient() as data_store_client:
        step = create_test_result_and_step(data_store_client, description)
        queried_steps = data_store_client.query_steps(
            odata_query=f"$filter=id eq {step.id}", read_fields=[StepField.NAME]
        )

    assert len(queried_steps) == 1
    assert queried_steps[0].name == f"{description} step"


def test___query_steps___filter_by_name___correct_steps_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 query steps by name")
    name_base = f"{description} step"

    with DataStoreClient() as data_store_client:
        test_result = data_store_client.create_test_result(f"{description} test result")
        expected_names = {f"{name_base} {index}" for index in range(3)}
        for name in sorted(expected_names):
            data_store_client.create_step(name, test_result_id=test_result.id)
        data_store_client.create_step("some other step name", test_result_id=test_result.id)

        queried_steps = data_store_client.query_steps(
            odata_query=f"$filter=contains(Name,'{name_base}')",
            read_fields=[StepField.NAME],
        )
        found_names = {step.name for step in queried_steps}

    assert found_names == expected_names


def test___query_test_results___filter_by_id___single_test_result_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 query test result by id")

    with DataStoreClient() as data_store_client:
        test_result = data_store_client.create_test_result(f"{description} test result")
        queried_test_results = data_store_client.query_test_results(
            odata_query=f"$filter=id eq {test_result.id}",
            read_fields=[TestResultField.NAME],
        )

    assert len(queried_test_results) == 1
    assert queried_test_results[0].name == f"{description} test result"


def test___query_test_results___filter_by_name___correct_test_results_returned(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 query test results by name")
    name_base = f"{description} test result"

    with DataStoreClient() as data_store_client:
        expected_names = {f"{name_base} {index}" for index in range(3)}
        for name in sorted(expected_names):
            data_store_client.create_test_result(name)
        data_store_client.create_test_result("some other test result name")

        queried_test_results = data_store_client.query_test_results(
            odata_query=f"$filter=contains(Name,'{name_base}')",
            read_fields=[TestResultField.NAME],
        )
        found_names = {test_result.name for test_result in queried_test_results}

    assert found_names == expected_names
