"""Contains tests to validate the datastore client publish condition functionality."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock

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
    mocked_datastore_client: Mock,
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


def test___publish_condition_batch___calls_datastoreclient(
    client: Client,
    mocked_datastore_client: Mock,
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
