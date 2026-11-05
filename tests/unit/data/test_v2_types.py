"""Tests for the V2 data store Python types."""

from __future__ import annotations

import datetime as std_datetime
import inspect
import uuid
from collections.abc import Callable
from enum import Enum
from typing import Any

import pytest
from google.protobuf import json_format
from hightime import datetime, timedelta
from ni.measurements.data.v2 import data_store_pb2, data_store_service_pb2
from ni.protobuf.types.precision_duration_conversion import hightime_timedelta_to_protobuf
from ni.protobuf.types.precision_timestamp_conversion import hightime_datetime_to_protobuf
from nitypes.scalar import Scalar
from nitypes.vector import Vector

from ni.datastore.data.v2 import (
    Condition,
    ErrorInformation,
    JsonValue,
    Measurement,
    MeasurementField,
    MeasurementValueField,
    Outcome,
    Status,
    Step,
    StepCreateFields,
    StepField,
    StepUpdateFields,
    TestResult,
    TestResultCreateFields,
    TestResultField,
    TestResultUpdateFields,
)
from ni.datastore.data.v2._update_conversion import (
    STEP_UPDATE_FIELDS,
    TEST_RESULT_UPDATE_FIELDS,
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


def test___test_result___unset_optional_fields_read_as_default() -> None:
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
    assert measurement.conditions == (Condition("temperature", 25.0),)


def test___measurement___conditions_are_read_only() -> None:
    condition = Condition("temperature", 25.0)
    measurement = Measurement(conditions=[condition])

    assert isinstance(measurement.conditions, tuple)
    with pytest.raises(AttributeError):
        getattr(measurement.conditions, "append")(Condition("humidity", 50.0))
    with pytest.raises(AttributeError):
        getattr(measurement.conditions, "pop")(0)


def test___measurement___accepts_but_does_not_send_output_fields() -> None:
    condition = Condition("temperature", 25.0)
    measurement = Measurement(
        id="measurement-id",
        name="voltage",
        step_id="step-id",
        value_type="x",
        conditions=[condition],
    )

    proto = measurement.to_protobuf()

    assert proto.id == "measurement-id"
    assert measurement.value_type == "x"
    assert measurement.conditions == (condition,)
    assert proto.value_type == ""
    assert len(proto.conditions) == 0


def test___measurement___to_protobuf_omits_unset_value() -> None:
    measurement = Measurement(name="voltage", step_id="step-id")

    proto = measurement.to_protobuf()

    assert not proto.HasField("value")
    assert not proto.HasField("upper_limit")
    assert not proto.HasField("lower_limit")


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


@pytest.mark.parametrize("model", ["condition", "measurement"])
def test___scalar_value_on_construction___sets_units(model: str) -> None:
    value = Scalar(3.4, "V")
    item = Condition("Vcc", value) if model == "condition" else Measurement(name="Vcc", value=value)

    assert item.units == "V"


@pytest.mark.parametrize("model", ["condition", "measurement"])
def test___scalar_value_with_given_units___keeps_given_units(model: str) -> None:
    value = Scalar(3.4, "V")
    item = (
        Condition("Vcc", value, units="mV")
        if model == "condition"
        else Measurement(name="Vcc", value=value, units="mV")
    )

    assert item.units == "mV"


@pytest.mark.parametrize("model", ["condition", "measurement"])
def test___scalar_value_set_later___sets_empty_units(model: str) -> None:
    item = Condition("Vcc", 3.4) if model == "condition" else Measurement(name="Vcc", value=3.4)

    item.value = Scalar(3.4, "V")

    assert item.units == "V"


@pytest.mark.parametrize("model", ["condition", "measurement"])
def test___scalar_value_set_later___keeps_existing_units(model: str) -> None:
    item = (
        Condition("Vcc", 3.4, units="mV")
        if model == "condition"
        else Measurement(name="Vcc", value=3.4, units="mV")
    )

    item.value = Scalar(3.4, "V")

    assert item.units == "mV"


def test___condition___scalar_with_only_units_reads_as_plain_value() -> None:
    proto = Condition("voltage", Scalar(3.3, "V")).to_protobuf()

    condition = Condition.from_protobuf(proto)

    assert condition.value == 3.3
    assert not isinstance(condition.value, Scalar)
    assert condition.units == "V"


def test___condition___scalar_extended_properties_round_trip() -> None:
    proto = Condition(
        "supply", Scalar(1.25, "V", extended_properties={"custom": "source"})
    ).to_protobuf()

    condition = Condition.from_protobuf(proto)

    assert isinstance(condition.value, Scalar)
    assert condition.value.value == 1.25
    assert condition.value.extended_properties["custom"] == "source"
    assert condition.units == "V"


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


@pytest.mark.parametrize(
    ("field_type", "message_type"),
    [
        (TestResultField, data_store_pb2.TestResult),
        (StepField, data_store_pb2.Step),
        (MeasurementField, data_store_pb2.Measurement),
        (MeasurementValueField, data_store_service_pb2.ReadMeasurementValuesResponse),
    ],
)
def test___read_field_enums___match_protobuf_fields(
    field_type: type[Enum], message_type: Any
) -> None:
    field_names = sorted(field.value for field in field_type)

    assert field_names == sorted(field.name for field in message_type.DESCRIPTOR.fields)


@pytest.mark.parametrize(
    ("argument", "create_model"),
    [
        pytest.param(
            "keywords", lambda: TestResult("t", keywords="smoke"), id="test_result_keywords"
        ),
        pytest.param(
            "software_item_ids",
            lambda: TestResult("t", software_item_ids="sw"),
            id="test_result_software_item_ids",
        ),
        pytest.param(
            "hardware_item_ids",
            lambda: TestResult("t", hardware_item_ids="hw"),
            id="test_result_hardware_item_ids",
        ),
        pytest.param(
            "test_adapter_ids",
            lambda: TestResult("t", test_adapter_ids="ta"),
            id="test_result_test_adapter_ids",
        ),
        pytest.param("keywords", lambda: Step("s", keywords="smoke"), id="step_keywords"),
        pytest.param("path", lambda: Step("s", path="root"), id="step_path"),
        pytest.param("path_ids", lambda: Step("s", path_ids="root-id"), id="step_path_ids"),
        pytest.param(
            "software_item_ids",
            lambda: Measurement(software_item_ids="sw"),
            id="measurement_software_item_ids",
        ),
        pytest.param(
            "hardware_item_ids",
            lambda: Measurement(hardware_item_ids="hw"),
            id="measurement_hardware_item_ids",
        ),
        pytest.param(
            "test_adapter_ids",
            lambda: Measurement(test_adapter_ids="ta"),
            id="measurement_test_adapter_ids",
        ),
    ],
)
def test___models___single_string_for_string_list___raises_type_error(
    argument: str, create_model: Callable[[], object]
) -> None:
    with pytest.raises(TypeError, match=f"^{argument} must be"):
        create_model()


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


def test___measurement___plain_value_equals_scalar() -> None:
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


_OUTPUT_ONLY_INIT_PARAMETERS = {"id", "created_at", "updated_at", "created_by", "updated_by"}


@pytest.mark.parametrize(
    ("model", "create_fields", "excluded"),
    [
        (TestResult, TestResultCreateFields, {"name"}),
        (Step, StepCreateFields, {"name", "path", "path_ids"}),
    ],
)
def test___create_fields___match_model_constructor(
    model: type, create_fields: type, excluded: set[str]
) -> None:
    parameters = set(inspect.signature(model).parameters)

    expected = parameters - excluded - _OUTPUT_ONLY_INIT_PARAMETERS
    assert set(create_fields.__annotations__) == expected


@pytest.mark.parametrize(
    ("update_fields", "allowed"),
    [
        (TestResultUpdateFields, TEST_RESULT_UPDATE_FIELDS),
        (StepUpdateFields, STEP_UPDATE_FIELDS),
    ],
)
def test___update_fields___match_updatable_fields(
    update_fields: type, allowed: frozenset[str]
) -> None:
    assert set(update_fields.__annotations__) == allowed


_UUID = uuid.UUID("3f2b8c1e-5a7d-4e2b-9c1f-2d4e6a8b0c3d")


def test___test_result___uuid_ids___stored_as_strings() -> None:
    test_result = TestResult(
        "t",
        id=_UUID,
        uut_instance_id=_UUID,
        uut_id=_UUID,
        operator_id=_UUID,
        test_station_id=_UUID,
        test_description_id=_UUID,
        software_item_ids=[_UUID, "alias"],
        hardware_item_ids=[_UUID],
        test_adapter_ids=[_UUID],
    )

    proto = test_result.to_protobuf()
    assert test_result.id == str(_UUID)
    assert test_result.operator_id == str(_UUID)
    assert list(test_result.software_item_ids) == [str(_UUID), "alias"]
    assert proto.uut_instance_id == proto.test_description_id == str(_UUID)
    assert list(proto.hardware_item_ids) == list(proto.test_adapter_ids) == [str(_UUID)]


def test___step___uuid_ids___stored_as_strings() -> None:
    step = Step("s", id=_UUID, parent_step_id=_UUID, test_result_id=_UUID, test_id=_UUID)

    assert (step.id, step.parent_step_id, step.test_result_id, step.test_id) == (str(_UUID),) * 4


def test___measurement___uuid_ids___stored_as_strings() -> None:
    measurement = Measurement(
        id=_UUID,
        test_result_id=_UUID,
        step_id=_UUID,
        software_item_ids=[_UUID],
        hardware_item_ids=[_UUID],
        test_adapter_ids=[_UUID],
    )

    assert (measurement.id, measurement.test_result_id, measurement.step_id) == (str(_UUID),) * 3
    assert list(measurement.to_protobuf().software_item_ids) == [str(_UUID)]


def test___model___single_uuid_for_id_list___raises_type_error() -> None:
    with pytest.raises(TypeError, match="^software_item_ids must be"):
        TestResult("t", software_item_ids=_UUID)  # type: ignore[arg-type]
