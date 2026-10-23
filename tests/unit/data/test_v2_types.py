"""Tests for the V2 data store Python types."""

from __future__ import annotations

import datetime as std_datetime

import pytest
from google.protobuf import json_format
from hightime import datetime, timedelta
from ni.measurements.data.v2 import data_store_pb2
from ni.protobuf.types.precision_duration_conversion import hightime_timedelta_to_protobuf
from ni.protobuf.types.precision_timestamp_conversion import hightime_datetime_to_protobuf
from nitypes.scalar import Scalar

from ni.datastore.data.v2 import (
    Condition,
    ErrorInformation,
    Measurement,
    Outcome,
    Status,
    Step,
    TestResult,
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
