"""Acceptance tests that publish various batch measurement values then reads the data back."""

from ni.datastore.data import (
    DataStoreClient,
    Step,
    TestResult,
)
from nitypes.vector import Vector


def test___publish_float___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python batch publish float acceptance test"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Publish the waveform data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurements = data_store_client.publish_measurement_batch(
            measurement_name="python batch publish float",
            values=[1.0, 2.0, 3.0, 4.0],
            step_id=step_id,
        )
        published_measurement = next(iter(published_measurements), None)
        assert published_measurement is not None

        # Query for the measurement id and read/validate data
        queried_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(queried_measurements), None)
        assert found_measurement is not None

        # A published batch floats will be read back as a Vector.
        vector = data_store_client.read_data(found_measurement, expected_type=Vector)
        assert vector._values == [1.0, 2.0, 3.0, 4.0]
        assert vector.units == ""


def test___publish_batch_vector___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish scalar acceptance test"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create a Vector data to publish
        expected_vector = Vector(values=[1, 2, 3], units="Volts")

        # Batch publish the vector
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurements = data_store_client.publish_measurement_batch(
            measurement_name="python publish scalar",
            values=expected_vector,
            step_id=step_id,
        )
        published_measurement = next(iter(published_measurements), None)
        assert published_measurement is not None

        # Query for the measurement id and read/validate data
        queried_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(queried_measurements), None)
        assert found_measurement is not None

        # A batch published Vector will be read back as a Vector.
        vector = data_store_client.read_data(found_measurement, expected_type=Vector)
        assert vector == expected_vector
