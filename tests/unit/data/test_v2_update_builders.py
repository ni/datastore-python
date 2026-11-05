"""Tests for the V2 update builders."""

from __future__ import annotations

import datetime as std_datetime

import pytest
from hightime import datetime, timedelta
from ni.measurements.data.v2 import data_store_pb2
from ni.protobuf.types.precision_duration_conversion import hightime_timedelta_to_protobuf
from ni.protobuf.types.precision_timestamp_conversion import hightime_datetime_to_protobuf

from ni.datastore.data.v2 import (
    ErrorInformation,
    Measurement,
    MeasurementUpdateBuilder,
    Outcome,
    Status,
    Step,
    StepUpdateBuilder,
    TestResult,
    TestResultUpdateBuilder,
)
from ni.datastore.metadata import Operator, Test, Uut

TIMESTAMP = datetime(2026, 5, 6, 7, 8, 9, tzinfo=std_datetime.timezone.utc)


def test___step_builder___build_update___sets_values_and_selects_fields_in_call_order() -> None:
    request = (
        StepUpdateBuilder("step-id")
        .with_outcome(Outcome.PASSED)
        .with_notes("Verified")
        .with_status(Status.DONE)
        .build_update()
    )

    assert request.step.id == "step-id"
    assert request.step.outcome == data_store_pb2.OUTCOME_PASSED
    assert request.step.notes == "Verified"
    assert request.step.status == data_store_pb2.STATUS_DONE
    assert list(request.update_mask.paths) == ["outcome", "notes", "status"]


def test___test_result_builder___all_fields___converts_values() -> None:
    request = (
        TestResultUpdateBuilder("tr-id")
        .with_start_date_time(TIMESTAMP)
        .with_end_date_time(TIMESTAMP)
        .with_duration(timedelta(seconds=3))
        .with_status(Status.DONE)
        .with_outcome(Outcome.FAILED)
        .with_error_information(ErrorInformation(error_code=2, message="boom"))
        .with_extension({"retest": True})
        .with_link("https://example.com")
        .with_keywords(["smoke"])
        .with_uut_instance_id("uut-instance-id")
        .with_uut_id("uut-id")
        .with_operator_id("operator-id")
        .with_test_station_id("station-id")
        .with_test_description_id("description-id")
        .build_update()
    )

    test_result = request.test_result
    assert test_result.start_date_time == hightime_datetime_to_protobuf(TIMESTAMP)
    assert test_result.end_date_time == hightime_datetime_to_protobuf(TIMESTAMP)
    assert test_result.duration == hightime_timedelta_to_protobuf(timedelta(seconds=3))
    assert test_result.status == data_store_pb2.STATUS_DONE
    assert test_result.outcome == data_store_pb2.OUTCOME_FAILED
    assert test_result.error_information.message == "boom"
    assert test_result.extension["retest"] is True
    assert test_result.link == "https://example.com"
    assert list(test_result.keywords) == ["smoke"]
    assert test_result.uut_instance_id == "uut-instance-id"
    assert test_result.uut_id == "uut-id"
    assert test_result.operator_id == "operator-id"
    assert test_result.test_station_id == "station-id"
    assert test_result.test_description_id == "description-id"
    assert len(request.update_mask.paths) == 14


def test___measurement_builder___build_update___sets_values_and_selects_fields() -> None:
    request = (
        MeasurementUpdateBuilder("m-id")
        .with_notes("Rechecked")
        .with_outcome(Outcome.PASSED)
        .with_extension({"probe": "10x"})
        .build_update()
    )

    assert request.measurement.id == "m-id"
    assert request.measurement.notes == "Rechecked"
    assert request.measurement.outcome == data_store_pb2.OUTCOME_PASSED
    assert request.measurement.extension["probe"] == "10x"
    assert list(request.update_mask.paths) == ["notes", "outcome", "extension"]


def test___builder___none___selects_field_with_empty_value() -> None:
    request = StepUpdateBuilder("step-id").with_link(None).with_notes(None).build_update()

    assert request.step.link == ""
    assert request.step.notes == ""
    assert list(request.update_mask.paths) == ["link", "notes"]


def test___builder___same_field_twice___last_value_wins() -> None:
    request = StepUpdateBuilder("step-id").with_notes("first").with_notes("second").build_update()

    assert request.step.notes == "second"
    assert list(request.update_mask.paths) == ["notes"]


def test___test_result_builder___id_after_inline___discards_inline() -> None:
    request = (
        TestResultUpdateBuilder("tr-id")
        .with_operator(Operator(name="Ada"))
        .with_operator_id("operator-id")
        .build_update()
    )

    assert request.test_result.operator_id == "operator-id"
    assert not request.test_result.HasField("operator")
    assert list(request.update_mask.paths) == ["operator_id"]


def test___test_result_builder___inline_after_id___discards_id() -> None:
    request = (
        TestResultUpdateBuilder("tr-id")
        .with_uut_id("uut-id")
        .with_uut(Uut(model_name="model"))
        .build_update()
    )

    assert request.test_result.uut_id == ""
    assert request.test_result.uut.model_name == "model"
    assert list(request.update_mask.paths) == ["uut"]


def test___step_builder___inline_test___sends_test_and_discards_id() -> None:
    request = (
        StepUpdateBuilder("step-id")
        .with_test_id("test-id")
        .with_test(Test(name="t"))
        .build_update()
    )

    assert request.step.test_id == ""
    assert request.step.test.name == "t"
    assert list(request.update_mask.paths) == ["test"]


def test___test_result_builder___from_resource___uses_resource_id() -> None:
    request = (
        TestResultUpdateBuilder(TestResult(name="t", id="tr-id"))
        .with_outcome(Outcome.PASSED)
        .build_update()
    )

    assert request.test_result.id == "tr-id"


def test___step_builder___from_resource___uses_resource_id() -> None:
    request = StepUpdateBuilder(Step(name="s", id="step-id")).with_notes("n").build_update()

    assert request.step.id == "step-id"


def test___measurement_builder___from_resource___uses_resource_id() -> None:
    request = MeasurementUpdateBuilder(Measurement(id="m-id")).with_notes("n").build_update()

    assert request.measurement.id == "m-id"


@pytest.mark.parametrize("target", ["", "   ", Step(name="unsaved")])
def test___builder___blank_id___raises_value_error(target: Step | str) -> None:
    with pytest.raises(ValueError, match="ID must not be empty"):
        StepUpdateBuilder(target)


def test___builder___no_fields_selected___build_update_raises_value_error() -> None:
    with pytest.raises(ValueError, match="At least one field"):
        MeasurementUpdateBuilder("m-id").build_update()


def test___builder___single_string_keywords___raises_type_error() -> None:
    with pytest.raises(TypeError, match="keywords must be a list"):
        StepUpdateBuilder("step-id").with_keywords("smoke")


def test___builder___input_changed_after_with___request_uses_original_value() -> None:
    extension = {"probe": "10x"}
    keywords = ["smoke"]
    builder = StepUpdateBuilder("step-id").with_extension(extension).with_keywords(keywords)

    extension["probe"] = "1x"
    keywords.append("regression")
    request = builder.build_update()

    assert request.step.extension["probe"] == "10x"
    assert list(request.step.keywords) == ["smoke"]
