"""Contains tests to validate the datastore client publish condition functionality."""

from __future__ import annotations

from typing import cast
from unittest.mock import NonCallableMock

import pytest
from ni.datastore import Client
from ni.measurements.data.v1.data_store_pb2 import PublishedCondition
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionBatchResponse,
    PublishConditionRequest,
    PublishConditionResponse,
)
from nitypes.vector import Vector


def test___publish_condition___calls_datastoreclient(
    client: Client,
    mocked_datastore_client: NonCallableMock,
) -> None:
    published_condition = PublishedCondition(published_condition_id="response_id")
    expected_response = PublishConditionResponse(published_condition=published_condition)
    mocked_datastore_client.publish_condition.return_value = expected_response

    result = client.publish_condition(
        condition_name="TestCondition",
        type="ConditionType",
        value=123,
        step_id="MyStep",
    )

    args, __ = mocked_datastore_client.publish_condition.call_args
    request = cast(PublishConditionRequest, args[0])
    assert result.published_condition_id == "response_id"
    assert request.step_id == "MyStep"
    assert request.condition_name == "TestCondition"
    assert request.type == "ConditionType"
    assert request.scalar.sint32_value == 123


def test___vector___publish_condition_batch___calls_datastoreclient(
    client: Client,
    mocked_datastore_client: NonCallableMock,
) -> None:
    published_condition = PublishedCondition(published_condition_id="response_id")
    expected_response = PublishConditionBatchResponse(published_condition=published_condition)
    mocked_datastore_client.publish_condition_batch.return_value = expected_response

    result = client.publish_condition_batch(
        condition_name="TestCondition",
        type="ConditionType",
        values=Vector(values=["one", "two", "three"], units="fake_units"),
        step_id="MyStep",
    )

    args, __ = mocked_datastore_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert result.published_condition_id == "response_id"
    assert request.step_id == "MyStep"
    assert request.condition_name == "TestCondition"
    assert request.type == "ConditionType"
    assert list(request.scalar_values.string_array.values) == ["one", "two", "three"]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "fake_units"


def test___int_list___publish_condition_batch___calls_datastoreclient(
    client: Client,
    mocked_datastore_client: NonCallableMock,
) -> None:
    published_condition = PublishedCondition(published_condition_id="response_id")
    expected_response = PublishConditionBatchResponse(published_condition=published_condition)
    mocked_datastore_client.publish_condition_batch.return_value = expected_response

    result = client.publish_condition_batch(
        condition_name="TestCondition",
        type="ConditionType",
        values=[1, 2, 3],
        step_id="MyStep",
    )

    args, __ = mocked_datastore_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert result.published_condition_id == "response_id"
    assert list(request.scalar_values.sint32_array.values) == [1, 2, 3]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___float_list___publish_condition_batch___calls_datastoreclient(
    client: Client,
    mocked_datastore_client: NonCallableMock,
) -> None:
    published_condition = PublishedCondition(published_condition_id="response_id")
    expected_response = PublishConditionBatchResponse(published_condition=published_condition)
    mocked_datastore_client.publish_condition_batch.return_value = expected_response

    result = client.publish_condition_batch(
        condition_name="TestCondition",
        type="ConditionType",
        values=[1.0, 2.0, 3.0],
        step_id="MyStep",
    )

    args, __ = mocked_datastore_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert result.published_condition_id == "response_id"
    assert list(request.scalar_values.double_array.values) == [1.0, 2.0, 3.0]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___bool_list___publish_condition_batch___calls_datastoreclient(
    client: Client,
    mocked_datastore_client: NonCallableMock,
) -> None:
    published_condition = PublishedCondition(published_condition_id="response_id")
    expected_response = PublishConditionBatchResponse(published_condition=published_condition)
    mocked_datastore_client.publish_condition_batch.return_value = expected_response

    result = client.publish_condition_batch(
        condition_name="TestCondition",
        type="ConditionType",
        values=[True, False, True],
        step_id="MyStep",
    )

    args, __ = mocked_datastore_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert result.published_condition_id == "response_id"
    assert list(request.scalar_values.bool_array.values) == [True, False, True]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___string_list___publish_condition_batch___calls_datastoreclient(
    client: Client,
    mocked_datastore_client: NonCallableMock,
) -> None:
    published_condition = PublishedCondition(published_condition_id="response_id")
    expected_response = PublishConditionBatchResponse(published_condition=published_condition)
    mocked_datastore_client.publish_condition_batch.return_value = expected_response

    result = client.publish_condition_batch(
        condition_name="TestCondition",
        type="ConditionType",
        values=["one", "two", "three"],
        step_id="MyStep",
    )

    args, __ = mocked_datastore_client.publish_condition_batch.call_args
    request = cast(PublishConditionBatchRequest, args[0])
    assert result.published_condition_id == "response_id"
    assert list(request.scalar_values.string_array.values) == ["one", "two", "three"]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == ""


def test___unsupported_list___publish_condition_batch___raises_type_error(
    client: Client,
) -> None:
    with pytest.raises(TypeError) as exc:
        _ = client.publish_condition_batch(
            condition_name="TestCondition",
            type="ConditionType",
            values=[[1, 2, 3], [4, 5, 6]],  # List of lists will error during vector creation.
            step_id="MyStep",
        )

    assert exc.value.args[0].startswith("Unsupported iterable:")


def test___empty_list___publish_condition_batch___raises_value_error(
    client: Client,
) -> None:
    with pytest.raises(ValueError) as exc:
        _ = client.publish_condition_batch(
            condition_name="TestCondition",
            type="ConditionType",
            values=[],
            step_id="MyStep",
        )

    assert exc.value.args[0].startswith("Cannot publish an empty Iterable.")
