"""Tests for the V2 data store Python types."""

from __future__ import annotations

import datetime as std_datetime
from typing import Any

import pytest
from google.protobuf import json_format
from hightime import datetime, timedelta
from ni.measurements.data.v2 import data_store_pb2
from ni.protobuf.types.precision_duration_conversion import hightime_timedelta_to_protobuf
from ni.protobuf.types.precision_timestamp_conversion import hightime_datetime_to_protobuf
from nitypes.scalar import Scalar
from nitypes.vector import Vector

from ni.datastore.data.v2 import (
    Condition,
    ErrorInformation,
    JsonValue,
    Measurement,
    Outcome,
    Status,
    Step,
    TestResult,
)
from ni.datastore.metadata import (
    HardwareItem,
    Operator,
    SoftwareItem,
    Test,
    TestAdapter,
    TestDescription,
    TestStation,
    Uut,
    UutInstance,
)

UTC = std_datetime.timezone.utc
START = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
END = datetime(2026, 1, 2, 3, 4, 15, tzinfo=UTC)
DURATION = timedelta(seconds=10)


def test___test_result___round_trips_through_protobuf() -> None:
    test_result = TestResult(
        "Power test",
        id="test-result-id",
        uut_instance_id="uut-instance-id",
        uut_id="uut-id",
        operator_id="operator-id",
        test_station_id="station-id",
        test_description_id="description-id",
        software_item_ids=["sw"],
        hardware_item_ids=["hw"],
        test_adapter_ids=["ta"],
        start_date_time=START,
        end_date_time=END,
        duration=DURATION,
        outcome=Outcome.PASSED,
        status=Status.DONE,
        link="https://example.com/run",
        keywords=["smoke"],
        extension={"lot": "A1", "nested": {"ok": True}},
        error_information=ErrorInformation(error_code=-1, message="boom", source="e2e"),
    )

    proto = test_result.to_protobuf()

    assert proto.name == "Power test"
    assert proto.uut_id == "uut-id"
    assert list(proto.software_item_ids) == ["sw"]
    assert proto.start_date_time == hightime_datetime_to_protobuf(START)
    assert proto.duration == hightime_timedelta_to_protobuf(DURATION)
    assert proto.outcome == data_store_pb2.OUTCOME_PASSED
    assert proto.status == data_store_pb2.STATUS_DONE
    assert list(proto.keywords) == ["smoke"]
    assert json_format.MessageToDict(proto.extension) == {"lot": "A1", "nested": {"ok": True}}
    assert proto.error_information.message == "boom"
    assert TestResult.from_protobuf(proto) == test_result


def test___test_result___unset_optional_fields_read_as_none() -> None:
    test_result = TestResult.from_protobuf(data_store_pb2.TestResult(id="id", name="name"))

    assert test_result.start_date_time is None
    assert test_result.end_date_time is None
    assert test_result.duration is None
    assert test_result.error_information is None
    assert test_result.extension == {}
    assert test_result.outcome == Outcome.UNSPECIFIED


def test___step___round_trips_through_protobuf_including_conditions() -> None:
    step = Step(
        "Measure voltage",
        id="step-id",
        parent_step_id="parent-id",
        test_result_id="test-result-id",
        test_id="test-id",
        step_type="Measurement",
        notes="first",
        start_date_time=START,
        end_date_time=END,
        duration=DURATION,
        outcome=Outcome.FAILED,
        status=Status.DONE,
        link="https://example.com/step",
        keywords=["k"],
        extension={"inputs": {"v": 1}},
        conditions=[Condition("temperature", 25.0, condition_type="Environment", units="C")],
    )

    proto = step.to_protobuf()

    assert proto.parent_step_id == "parent-id"
    assert proto.step_type == "Measurement"
    assert proto.conditions[0].value.scalar.double_value == 25.0
    assert Step.from_protobuf(proto) == step


def test___measurement___reads_metadata_and_conditions_from_protobuf() -> None:
    proto = data_store_pb2.Measurement(
        id="measurement-id",
        test_result_id="test-result-id",
        step_id="step-id",
        name="voltage",
        value_type="Scalar",
        units="V",
        notes="note",
        outcome=data_store_pb2.OUTCOME_PASSED,
        software_item_ids=["sw"],
        comparison_type="GELE",
        start_date_time=hightime_datetime_to_protobuf(START),
        conditions=[
            data_store_pb2.Condition(name="temperature", value=data_store_pb2.ConditionValue())
        ],
    )
    proto.conditions[0].value.scalar.double_value = 25.0
    proto.value.scalar.double_value = 5.0

    measurement = Measurement.from_protobuf(proto)

    assert (measurement.id, measurement.name, measurement.units) == (
        "measurement-id",
        "voltage",
        "V",
    )
    assert (measurement.value_type, measurement.comparison_type) == ("Scalar", "GELE")
    assert measurement.outcome == Outcome.PASSED
    assert measurement.start_date_time == START
    assert list(measurement.software_item_ids) == ["sw"]
    assert measurement.conditions == [Condition("temperature", 25.0)]


def test___measurement___to_protobuf_does_not_send_value_or_output_fields() -> None:
    measurement = Measurement(
        id="measurement-id", name="voltage", step_id="step-id", value_type="x"
    )

    proto = measurement.to_protobuf()

    assert proto.id == "measurement-id"
    assert not proto.HasField("value")
    assert proto.value_type == ""
    assert len(proto.conditions) == 0


@pytest.mark.parametrize(
    ("value", "field", "expected"),
    [
        (5.5, "double_value", 5.5),
        (7, "sint32_value", 7),
        (True, "bool_value", True),
        ("high", "string_value", "high"),
    ],
)
def test___condition___converts_scalar_values(value: object, field: str, expected: object) -> None:
    proto = Condition("cond", value).to_protobuf()

    assert getattr(proto.value.scalar, field) == expected
    assert Condition.from_protobuf(proto).value == expected


def test___condition___uses_scalar_units_when_units_not_given() -> None:
    proto = Condition("voltage", Scalar(3.3, "V")).to_protobuf()

    assert proto.units == "V"
    assert proto.value.scalar.double_value == 3.3


def test___condition___converts_json_mapping() -> None:
    proto = Condition("config", {"mode": "fast"}).to_protobuf()

    assert proto.value.WhichOneof("value") == "json_value"
    assert Condition.from_protobuf(proto).value == {"mode": "fast"}


def test___condition___rejects_unsupported_value() -> None:
    with pytest.raises(TypeError):
        Condition("bad", [1, 2]).to_protobuf()


def test___error_information___round_trips_through_protobuf() -> None:
    error = ErrorInformation(error_code=3, message="m", source="s")

    assert ErrorInformation.from_protobuf(error.to_protobuf()) == error


@pytest.mark.parametrize("enum_type", [Outcome, Status])
def test___enums___reject_unknown_protobuf_values(enum_type: type[Outcome] | type[Status]) -> None:
    with pytest.raises(ValueError):
        enum_type.from_protobuf(999)  # type: ignore[arg-type]


def test___measurement___round_trips_value_limits_and_metadata() -> None:
    measurement = Measurement(
        name="voltage",
        step_id="step-id",
        value=Scalar(5.0, "V"),
        upper_limit=5.5,
        lower_limit=Vector([4.5, 4.6]),
        schema_id="schema",
        software_items=[SoftwareItem(product="p", version="1")],
        hardware_items=[HardwareItem(manufacturer="m", model="x", serial_number="1")],
        test_adapters=[TestAdapter(name="adapter")],
    )

    proto = measurement.to_protobuf()

    assert proto.value.scalar.double_value == 5.0
    assert proto.upper_limit.scalar.double_value == 5.5
    assert proto.units == "V"
    assert proto.schema_id == "schema"
    assert proto.software_items[0].product == "p"
    round_tripped = Measurement.from_protobuf(proto)
    assert round_tripped.units == "V"
    assert round_tripped.value == Scalar(5.0, "V")
    assert round_tripped.upper_limit == Scalar(5.5)
    assert round_tripped.lower_limit == Vector([4.5, 4.6])
    assert round_tripped.software_items == measurement.software_items


def test___measurement___moniker_or_missing_value_reads_as_none() -> None:
    proto = data_store_pb2.Measurement(id="m")
    proto.value.data_moniker.data_instance = 1

    measurement = Measurement.from_protobuf(proto)

    assert (measurement.value, measurement.upper_limit, measurement.lower_limit) == (
        None,
        None,
        None,
    )


def test___test_result___round_trips_metadata_objects_and_nested_steps() -> None:
    test_result = TestResult(
        "Power test",
        uut_instance=UutInstance(uut_id="uut", serial_number="sn"),
        uut=Uut(model_name="model"),
        operator=Operator(name="Ada", role="Engineer"),
        test_station=TestStation(name="station"),
        test_description=TestDescription(uut_id="uut", name="desc"),
        software_items=[SoftwareItem(product="p", version="1")],
        schema_id="schema",
        steps=[
            Step(
                "parent",
                test=Test(name="t"),
                schema_id="step-schema",
                measurements=[Measurement(name="m", value=1.0)],
                children=[Step("child")],
            )
        ],
    )

    proto = test_result.to_protobuf()

    assert proto.operator.name == "Ada"
    assert proto.steps[0].children[0].name == "child"
    assert proto.steps[0].measurements[0].value.scalar.double_value == 1.0
    assert proto.steps[0].test.name == "t"
    assert TestResult.from_protobuf(proto) == test_result


def test___measurement___plain_value_equals_scalar_read_back() -> None:
    assert Measurement(value=1.0, upper_limit=2) == Measurement(
        value=Scalar(1.0), upper_limit=Scalar(2)
    )
    assert Measurement(value=1.0) != Measurement(value=Scalar(1.0, "V"))


def test___test_result___unset_metadata_objects_read_as_none() -> None:
    test_result = TestResult.from_protobuf(data_store_pb2.TestResult(name="n"))

    assert (test_result.operator, test_result.uut_instance, test_result.uut) == (None, None, None)
    assert test_result.steps == []


def test___json_value___round_trips_attributes_and_schema() -> None:
    value = JsonValue(
        {"a": 1, "nested": {"ok": True}},
        attributes={"flag": True, "count": 3, "ratio": 0.5, "name": "x"},
        schema_id="schema",
    )

    proto = value.to_protobuf()

    assert proto.attributes["count"].integer_value == 3
    assert proto.attributes["flag"].bool_value is True
    assert proto.schema_id == "schema"
    assert JsonValue.from_protobuf(proto) == value


def test___json_value___rejects_unsupported_attribute() -> None:
    with pytest.raises(TypeError):
        JsonValue({}, attributes={"bad": [1]}).to_protobuf()  # type: ignore[dict-item]


def test___condition___json_value_with_attributes_round_trips() -> None:
    condition = Condition("config", JsonValue({"mode": "fast"}, attributes={"source": "fixture"}))

    assert Condition.from_protobuf(condition.to_protobuf()) == condition


def test___condition___plain_json_reads_as_dict() -> None:
    proto = Condition("config", {"mode": "fast"}).to_protobuf()

    assert Condition.from_protobuf(proto).value == {"mode": "fast"}


@pytest.mark.parametrize(
    ("proto_type", "model_type"),
    [
        (data_store_pb2.TestResult, TestResult),
        (data_store_pb2.Step, Step),
        (data_store_pb2.Measurement, Measurement),
        (data_store_pb2.Condition, Condition),
        (data_store_pb2.ErrorInformation, ErrorInformation),
        (data_store_pb2.JsonValue, JsonValue),
    ],
)
def test___models___expose_every_protobuf_field(proto_type: Any, model_type: Any) -> None:
    model_fields = {slot.lstrip("_") for slot in model_type.__slots__}

    missing = [f.name for f in proto_type.DESCRIPTOR.fields if f.name not in model_fields]

    assert missing == []


def test___client___wraps_every_low_level_method() -> None:
    from ni.measurements.data.v2.client import DataStoreClient as LowLevelClient

    from ni.datastore.data.v2 import DataStoreClient

    low_level_methods = {
        name
        for name in dir(LowLevelClient)
        if not name.startswith("_") and callable(getattr(LowLevelClient, name))
    }

    assert sorted(low_level_methods - set(dir(DataStoreClient))) == []
