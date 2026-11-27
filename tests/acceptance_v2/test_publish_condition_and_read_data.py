"""Acceptance tests for adding and reading V2 step conditions."""

import pytest
from nitypes.scalar import Scalar
from utilities import DataStoreContext

from ni.datastore.data.v2 import Condition, DataStoreClient, StepField
from tests.acceptance._utils import append_hashed_time
from tests.acceptance_v2._utils import create_test_result_and_step


@pytest.mark.parametrize(
    ("value", "expected_value", "expected_units", "condition_type"),
    [
        pytest.param(123.45, 123.45, "", "Upper Limit", id="float"),
        pytest.param(123, 123, "", "Lower Limit", id="integer"),
        pytest.param(True, True, "", "Flag", id="bool"),
        pytest.param("condition value", "condition value", "", "Environment", id="string"),
        pytest.param(Scalar(25, "Volts"), 25, "Volts", "Lower Limit", id="scalar-with-units"),
    ],
)
def test___add_condition___read_condition_value_returns_expected_scalar(
    acceptance_test_context: DataStoreContext,
    value: object,
    expected_value: object,
    expected_units: str,
    condition_type: str,
) -> None:
    description = append_hashed_time("v2 condition value")

    with DataStoreClient() as data_store_client:
        step = create_test_result_and_step(data_store_client, description)
        data_store_client.add_condition(
            step.id,
            "Python condition",
            value,
            condition_type=condition_type,
        )

        read_step = data_store_client.get_step(step.id, read_fields=[StepField.CONDITIONS])

    assert len(read_step.conditions) == 1
    condition = read_step.conditions[0]
    assert condition.name == "Python condition"
    assert condition.condition_type == condition_type
    assert condition.value == expected_value
    assert condition.units == expected_units


def test___add_condition___replaces_same_name_and_remove_clears_condition(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 condition replacement")

    with DataStoreClient() as data_store_client:
        step = create_test_result_and_step(data_store_client, description)
        data_store_client.add_condition(step.id, Condition("Supply Voltage", 3.3, units="V"))
        replaced_step = data_store_client.add_condition(
            step.id,
            Condition("Supply Voltage", 5.0, condition_type="Measured", units="V"),
        )
        assert len(replaced_step.conditions) == 1
        assert replaced_step.conditions[0].value == 5.0
        assert replaced_step.conditions[0].condition_type == "Measured"

        removed_step = data_store_client.remove_condition(step.id, "Supply Voltage")

    assert removed_step.conditions == []


def test___add_condition___reads_json_mapping_value(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 json condition")
    expected_value = {"ambient": {"temperature": 23.0, "units": "degC"}}

    with DataStoreClient() as data_store_client:
        step = create_test_result_and_step(data_store_client, description)
        data_store_client.add_condition(
            step.id,
            Condition("Environment", expected_value, condition_type="Setup"),
        )
        read_step = data_store_client.get_step(step.id, read_fields=[StepField.CONDITIONS])

    assert len(read_step.conditions) == 1
    assert read_step.conditions[0].value == expected_value
