"""Acceptance tests for publishing, reading, and querying with Data Store V2."""

from nitypes.scalar import Scalar
from utilities import DataStoreContext

from ni.datastore.data.v2 import (
    Condition,
    DataStoreClient,
    MeasurementField,
    Outcome,
    StepField,
    Status,
)
from tests.acceptance._utils import append_hashed_time


def test___publish_and_read_measurement___returns_v2_fields_and_value(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 publish and read")

    with DataStoreClient() as data_store_client:
        test_result = data_store_client.create_test_result(
            f"{description} test result", status=Status.RUNNING
        )
        step = data_store_client.create_step(
            f"{description} parent step",
            test_result_id=test_result.id,
            conditions=[
                Condition("Ambient Temperature", 23.0, condition_type="Environment", units="degC")
            ],
        )
        data_store_client.create_step(
            f"{description} child step",
            test_result_id=test_result.id,
            parent_step_id=step.id,
        )
        measurement = data_store_client.create_measurement(
            f"{description} measurement",
            Scalar(5.2, "V"),
            step.id,
            outcome=Outcome.PASSED,
            keywords=["acceptance"],
        )

        queried_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=Id eq {measurement.id}",
            read_fields=[MeasurementField.KEYWORDS],
        )
        assert len(queried_measurements) == 1
        queried_measurement = queried_measurements[0]
        assert queried_measurement.keywords == ["acceptance"]
        assert data_store_client.read_measurement_value(measurement.id, Scalar) == Scalar(5.2, "V")

        queried_step = data_store_client.get_step(
            step.id, read_fields=[StepField.CONDITIONS, StepField.HAS_CHILDREN]
        )
        assert queried_step.has_children is True
        assert queried_step.conditions[0].name == "Ambient Temperature"


def test___query_measurements___uses_page_token_to_return_all_matches(
    acceptance_test_context: DataStoreContext,
) -> None:
    name_prefix = append_hashed_time("v2 pagination measurement")

    with DataStoreClient() as data_store_client:
        test_result = data_store_client.create_test_result(f"{name_prefix} test result")
        step = data_store_client.create_step(f"{name_prefix} step", test_result_id=test_result.id)
        measurements = [
            data_store_client.create_measurement(
                f"{name_prefix} {index}", Scalar(float(index), "V"), step.id
            )
            for index in range(3)
        ]
        expected_ids = {measurement.id for measurement in measurements}
        odata_query = f"$filter=contains(Name,'{name_prefix}')"

        page = data_store_client.query_measurements(odata_query, page_size=1)
        queried_ids: list[str] = []
        seen_tokens = set()

        while True:
            assert len(page) <= 1
            queried_ids.extend(measurement.id for measurement in page)
            if not page.next_page_token:
                break

            assert page.next_page_token not in seen_tokens
            seen_tokens.add(page.next_page_token)
            page = data_store_client.query_measurements(
                odata_query, page_size=1, page_token=page.next_page_token
            )

        assert set(queried_ids) == expected_ids
        assert len(queried_ids) == len(expected_ids)
        assert len(seen_tokens) == len(expected_ids) - 1
