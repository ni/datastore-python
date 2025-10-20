"""Acceptance tests that publish various batch condition values then read the data back."""

from ni.datastore.data import (
    DataStoreClient,
    Step,
    TestResult,
)
from nitypes.vector import Vector


def test___publish_batch_float_condition___read_data_returns_vector() -> None:
    expected_value = [1.0, 2.0, 3.0]
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "float condition batch")
        published_condition = data_store_client.publish_condition_batch(
            condition_name="python float condition batch",
            type="Upper Limits",
            values=expected_value,
            step_id=step_id,
        )

        # A batch published float will be read back as a Vector.
        vector = data_store_client.read_data(published_condition, expected_type=Vector)
        assert vector._values == expected_value
        assert vector.units == ""


def test___publish_batch_integer_condition___read_data_returns_vector() -> None:
    expected_value = [5, 6, 7, 8]
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "integer condition batch")
        published_condition = data_store_client.publish_condition_batch(
            condition_name="python integer condition batch",
            type="Lower Limits",
            values=expected_value,
            step_id=step_id,
        )

        # A batch published integer will be read back as a Vector.
        vector = data_store_client.read_data(published_condition, expected_type=Vector)
        assert vector._values == expected_value
        assert vector.units == ""


def test___publish_batch_bool_condition___read_data_returns_vector() -> None:
    expected_value = [True, False, True]
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "bool condition batch")
        published_condition = data_store_client.publish_condition_batch(
            condition_name="python bool condition batch",
            type="Flags",
            values=expected_value,
            step_id=step_id,
        )

        # A batch published bool will be read back as a Vector.
        vector = data_store_client.read_data(published_condition, expected_type=Vector)
        assert vector._values == expected_value
        assert vector.units == ""


def test___publish_batch_str_condition___read_data_returns_vector() -> None:
    expected_value = ["one", "two", "three"]
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "str condition batch")
        published_condition = data_store_client.publish_condition_batch(
            condition_name="python str condition batch",
            type="Environments",
            values=expected_value,
            step_id=step_id,
        )

        # A published str will be read back as a Vector.
        vector = data_store_client.read_data(published_condition, expected_type=Vector)
        assert vector._values == expected_value
        assert vector.units == ""


def test___publish_batch_vector_condition___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "scalar condition batch")
        expected_vector = Vector(values=[25, 50, 75], units="Amps")
        published_condition = data_store_client.publish_condition_batch(
            condition_name="python vector condition batch",
            type="Upper Limit",
            values=expected_vector,
            step_id=step_id,
        )

        # A batch published Vector will be read back as a Vector.
        vector = data_store_client.read_data(published_condition, expected_type=Vector)
        assert vector == expected_vector


def _create_step(data_store_client: DataStoreClient, datatype_string: str) -> str:
    test_result_name = f"python publish {datatype_string} acceptance test"
    test_result = TestResult(test_result_name=test_result_name)
    test_result_id = data_store_client.create_test_result(test_result)

    # Publish the waveform data
    step = Step(step_name=f"Initial step: {datatype_string}", test_result_id=test_result_id)
    step_id = data_store_client.create_step(step)
    return step_id
