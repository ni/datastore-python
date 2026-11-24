"""Acceptance tests for V2 measurement values and limits."""

from nitypes.scalar import Scalar
from utilities import DataStoreContext

from ni.datastore.data.v2 import DataStoreClient, MeasurementValueField
from tests.acceptance._utils import append_hashed_time
from tests.acceptance_v2._utils import create_step


def test___read_measurement_values___returns_value_and_limits(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 measurement limits")
    expected_value = Scalar(5.2, "V")
    expected_lower_limit = Scalar(0.0, "V")
    expected_upper_limit = Scalar(10.0, "V")

    with DataStoreClient() as data_store_client:
        step = create_step(data_store_client, description)
        measurement = data_store_client.create_measurement(
            description,
            expected_value,
            step.id,
            lower_limit=expected_lower_limit,
            upper_limit=expected_upper_limit,
        )
        read_measurement = data_store_client.read_measurement_values(
            measurement.id,
            read_fields=[
                MeasurementValueField.VALUE,
                MeasurementValueField.LOWER_LIMIT,
                MeasurementValueField.UPPER_LIMIT,
            ],
        )

    assert read_measurement.value == expected_value
    assert read_measurement.lower_limit == expected_lower_limit
    assert read_measurement.upper_limit == expected_upper_limit
