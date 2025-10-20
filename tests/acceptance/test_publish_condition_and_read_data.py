"""Acceptance tests that publish various condition values then read the data back."""

from ni.datastore.data import (
    DataStoreClient,
    PublishedCondition,
    Step,
    TestResult,
)
from nitypes.scalar import Scalar
from nitypes.vector import Vector


def test___publish_float_condition___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "float condition")
        published_condition = data_store_client.publish_condition(
            condition_name="python float condition",
            type="float",
            value=123.45,
            step_id=step_id,
        )

        found_condition = _get_first_condition(
            data_store_client, published_condition.published_condition_id
        )

        # A published float will be read back as a Vector.
        vector = data_store_client.read_data(found_condition, expected_type=Vector)
        assert vector[0] == 123.45
        assert vector.units == ""


def test___publish_integer_condition___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "integer condition")
        published_condition = data_store_client.publish_condition(
            condition_name="python integer condition",
            type="integer",
            value=123,
            step_id=step_id,
        )

        found_condition = _get_first_condition(
            data_store_client, published_condition.published_condition_id
        )

        # A published integer will be read back as a Vector.
        vector = data_store_client.read_data(found_condition, expected_type=Vector)
        assert vector[0] == 123
        assert vector.units == ""


def test___publish_bool_condition___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "bool condition")
        published_condition = data_store_client.publish_condition(
            condition_name="python bool condition",
            type="bool",
            value=True,
            step_id=step_id,
        )

        found_condition = _get_first_condition(
            data_store_client, published_condition.published_condition_id
        )

        # A published bool will be read back as a Vector.
        vector = data_store_client.read_data(found_condition, expected_type=Vector)
        assert vector[0] is True
        assert vector.units == ""


def test___publish_str_condition___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "str condition")
        published_condition = data_store_client.publish_condition(
            condition_name="python str condition",
            type="str",
            value="condition value",
            step_id=step_id,
        )

        found_condition = _get_first_condition(
            data_store_client, published_condition.published_condition_id
        )

        # A published str will be read back as a Vector.
        vector = data_store_client.read_data(found_condition, expected_type=Vector)
        assert vector[0] == "condition value"
        assert vector.units == ""


def test___publish_scalar_condition___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        step_id = _create_step(data_store_client, "scalar condition")
        expected_scalar = Scalar(value=25, units="Volts")
        published_condition = data_store_client.publish_condition(
            condition_name="python scalar condition",
            type="Scalar",
            value=expected_scalar,
            step_id=step_id,
        )

        found_condition = _get_first_condition(
            data_store_client, published_condition.published_condition_id
        )

        # A published Scalar will be read back as a Vector.
        vector = data_store_client.read_data(found_condition, expected_type=Vector)
        assert vector[0] == expected_scalar.value
        assert vector.units == expected_scalar.units


def _create_step(data_store_client: DataStoreClient, datatype_string: str) -> str:
    test_result_name = f"python publish {datatype_string} acceptance test"
    test_result = TestResult(test_result_name=test_result_name)
    test_result_id = data_store_client.create_test_result(test_result)

    # Publish the waveform data
    step = Step(step_name=f"Initial step: {datatype_string}", test_result_id=test_result_id)
    step_id = data_store_client.create_step(step)
    return step_id


def _get_first_condition(
    data_store_client: DataStoreClient, published_condition_id: str
) -> PublishedCondition:
    # Query for the condition id
    published_conditions = data_store_client.query_conditions(
        odata_query=f"$filter=id eq {published_condition_id}"
    )
    found_measurement = next(iter(published_conditions), None)
    assert found_measurement is not None
    return found_measurement
