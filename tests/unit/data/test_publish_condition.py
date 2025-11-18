"""Contains tests to validate the data store client publish condition functionality."""

from __future__ import annotations

from typing import cast
from unittest.mock import NonCallableMock

import pytest
from ni.datastore.data import DataStoreClient
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionBatchResponse,
    PublishConditionRequest,
    PublishConditionResponse,
)
from nitypes.vector import Vector


def test___publish_condition___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    expected_response = PublishConditionResponse(condition_id="response_id")
    mocked_data_store_service_client.publish_condition.return_value = expected_response

    condition_id = data_store_client.publish_condition(
        name="TestCondition",
        condition_type="ConditionType",
        value=123,
        step_id="MyStep",
    )

    args, __ = mocked_data_store_service_client.publish_condition.call_args
    request = cast(PublishConditionRequest, args[0])
    assert condition_id == "response_id"
    assert request.step_id == "MyStep"
    assert request.name == "TestCondition"
    assert request.condition_type == "ConditionType"
    assert request.scalar.sint32_value == 123


def test___none___publish_condition___raises_type_error(
    data_store_client: DataStoreClient,
) -> None:
    with pytest.raises(TypeError) as exc:
        _ = data_store_client.publish_condition(
            name="TestCondition",
            condition_type="ConditionType",
            value=None,
            step_id="MyStep",
        )

    assert exc.value.args[0].startswith("Unsupported condition value type")


def test___vector___publish_condition_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    expected_response = PublishConditionBatchResponse(condition_id="response_id")
    mocked_data_store_service_client.publish_condition_batch.return_value = expected_response

    condition_id = data_store_client.publish_condition_batch(
        name="TestCondition",
        condition_type="ConditionType",
        values=Vector(values=["one", "two", "three"], units="fake_units"),
        step_id="MyStep",
    )

    args, __ = mocked_data_store_service_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert condition_id == "response_id"
    assert request.step_id == "MyStep"
    assert request.name == "TestCondition"
    assert request.condition_type == "ConditionType"
    assert list(request.scalar_values.string_array.values) == ["one", "two", "three"]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "fake_units"


def test___int_list___publish_condition_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    expected_response = PublishConditionBatchResponse(condition_id="response_id")
    mocked_data_store_service_client.publish_condition_batch.return_value = expected_response

    condition_id = data_store_client.publish_condition_batch(
        name="TestCondition",
        condition_type="ConditionType",
        values=[1, 2, 3],
        step_id="MyStep",
    )

    args, __ = mocked_data_store_service_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert condition_id == "response_id"
    assert list(request.scalar_values.sint32_array.values) == [1, 2, 3]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___float_list___publish_condition_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    expected_response = PublishConditionBatchResponse(condition_id="response_id")
    mocked_data_store_service_client.publish_condition_batch.return_value = expected_response

    condition_id = data_store_client.publish_condition_batch(
        name="TestCondition",
        condition_type="ConditionType",
        values=[1.0, 2.0, 3.0],
        step_id="MyStep",
    )

    args, __ = mocked_data_store_service_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert condition_id == "response_id"
    assert list(request.scalar_values.double_array.values) == [1.0, 2.0, 3.0]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___bool_list___publish_condition_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    expected_response = PublishConditionBatchResponse(condition_id="response_id")
    mocked_data_store_service_client.publish_condition_batch.return_value = expected_response

    condition_id = data_store_client.publish_condition_batch(
        name="TestCondition",
        condition_type="ConditionType",
        values=[True, False, True],
        step_id="MyStep",
    )

    args, __ = mocked_data_store_service_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert condition_id == "response_id"
    assert list(request.scalar_values.bool_array.values) == [True, False, True]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___string_list___publish_condition_batch___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    expected_response = PublishConditionBatchResponse(condition_id="response_id")
    mocked_data_store_service_client.publish_condition_batch.return_value = expected_response

    condition_id = data_store_client.publish_condition_batch(
        name="TestCondition",
        condition_type="ConditionType",
        values=["one", "two", "three"],
        step_id="MyStep",
    )

    args, __ = mocked_data_store_service_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert condition_id == "response_id"
    assert list(request.scalar_values.string_array.values) == ["one", "two", "three"]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___unsupported_list___publish_condition_batch___raises_type_error(
    data_store_client: DataStoreClient,
) -> None:
    with pytest.raises(TypeError) as exc:
        _ = data_store_client.publish_condition_batch(
            name="TestCondition",
            condition_type="ConditionType",
            values=[[1, 2, 3], [4, 5, 6]],  # List of lists will error during vector creation.
            step_id="MyStep",
        )

    assert exc.value.args[0].startswith("Unsupported iterable:")


def test___empty_list___publish_condition_batch___raises_value_error(
    data_store_client: DataStoreClient,
) -> None:
    with pytest.raises(ValueError) as exc:
        _ = data_store_client.publish_condition_batch(
            name="TestCondition",
            condition_type="ConditionType",
            values=[],
            step_id="MyStep",
        )

    assert exc.value.args[0].startswith("Cannot publish an empty Iterable.")


def test___none___publish_condition_batch___raises_type_error(
    data_store_client: DataStoreClient,
) -> None:
    with pytest.raises(TypeError) as exc:
        _ = data_store_client.publish_condition_batch(
            name="TestCondition",
            condition_type="ConditionType",
            values=None,
            step_id="MyStep",
        )

    assert exc.value.args[0].startswith("Unsupported condition values type")
