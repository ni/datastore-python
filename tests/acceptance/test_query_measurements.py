"""Acceptance tests that exercise DataStoreClient.query_measurements()."""

from ni.datastore.data import DataStoreClient
from nitypes.vector import Vector
from utilities import DataStoreContext

from tests.acceptance._utils import append_hashed_time, create_test_result_and_step


def test___query_measurements___filter_by_id___single_measurement_returned() -> None:
    with DataStoreContext(), DataStoreClient() as data_store_client:
        step_id = create_test_result_and_step(data_store_client, "query measurement filter by id")

        # Publish a single measurement.
        measurement_name = "query filter by id measurement"
        published_measurement_id = data_store_client.publish_measurement(
            name=measurement_name,
            value=123.45,
            step_id=step_id,
        )

        # Query measurements based on id.
        queried_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement_id}"
        )

        # We should get one measurement back.
        assert len(queried_measurements) == 1
        first_measurement = queried_measurements[0]
        assert first_measurement is not None
        assert first_measurement.name == measurement_name

        # Check the value of the queried measurement.
        vector = data_store_client.read_data(first_measurement, expected_type=Vector)
        assert vector[0] == 123.45
        assert vector.units == ""


def test___query_measurements___filter_by_name___correct_measurements_returned() -> None:
    with DataStoreContext(), DataStoreClient() as data_store_client:
        step_id = create_test_result_and_step(data_store_client, "query measurement filter by name")

        # Publish several similarly named measurements. These names should be unique for each
        # run of this test to prevent previous results from causing the test to fail.
        measurement_name_base = append_hashed_time("query filter by name measurement")
        for index in range(0, 3):
            measurement_name = f"{measurement_name_base} {index}"
            data_store_client.publish_measurement(
                name=measurement_name,
                value=index,
                step_id=step_id,
            )

        # Publish one differently named measurement to adequately test filtering.
        data_store_client.publish_measurement(
            name="some other measurement",
            value=123,
            step_id=step_id,
        )

        # Query measurements based on name.
        queried_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=contains(Name,'{measurement_name_base}')"
        )

        # We should get three measurements back.
        assert len(queried_measurements) == 3

        # Check the value of each queried measurement.
        for measurement in queried_measurements:
            assert measurement is not None
            vector = data_store_client.read_data(measurement, expected_type=Vector)
            assert measurement.name == f"{measurement_name_base} {vector[0]}"
            assert vector.units == ""
