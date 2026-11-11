"""Tests for the V2 data store client."""

from __future__ import annotations

import datetime as std_datetime
import uuid
from collections.abc import Callable
from typing import Any
from unittest.mock import Mock

import numpy as np
import pytest
from hightime import datetime, timedelta
from ni.measurements.data.v2 import data_store_pb2, data_store_service_pb2
from ni.protobuf.types.precision_duration_conversion import hightime_timedelta_to_protobuf
from ni.protobuf.types.precision_timestamp_conversion import hightime_datetime_to_protobuf
from ni.protobuf.types.vector_conversion import vector_to_protobuf
from ni.protobuf.types.waveform_pb2 import DoubleAnalogWaveform
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, Timing
from pytest_mock import MockerFixture

from ni.datastore.data.v2 import (
    Condition,
    DataStoreClient,
    ErrorInformation,
    JsonValue,
    Measurement,
    MeasurementField,
    MeasurementUpdateBuilder,
    MeasurementUpdateFields,
    MeasurementValueField,
    Outcome,
    QueryResults,
    Status,
    Step,
    StepField,
    StepUpdateBuilder,
    TestResult,
    TestResultField,
    TestResultUpdateBuilder,
)

UTC = std_datetime.timezone.utc
TIMESTAMP = datetime(2026, 5, 6, 7, 8, 9, tzinfo=UTC)


@pytest.fixture
def service_client(mocker: MockerFixture) -> Any:
    service_client = Mock()
    # Default responses for tests that check only the request. Tests that check
    # the returned model set their own response.
    service_client.update_test_result.return_value = data_store_pb2.TestResult()
    service_client.update_step.return_value = data_store_pb2.Step()
    service_client.update_measurement.return_value = data_store_pb2.Measurement()
    service_client.create_measurement.return_value = data_store_pb2.Measurement()
    service_client.remove_test_result_metadata.return_value = (
        data_store_service_pb2.RemoveTestResultMetadataResponse()
    )
    mocker.patch(
        "ni.datastore.data.v2._data_store_client.DataStoreServiceClient",
        return_value=service_client,
    )
    return service_client


@pytest.fixture
def client(service_client: Any) -> DataStoreClient:
    return DataStoreClient()


def _sent(service_method: Mock) -> Any:
    return service_method.call_args.args[0]


def _read_response(service_client: Any, value: data_store_pb2.MeasurementValue) -> None:
    service_client.read_measurement_values.return_value = (
        data_store_service_pb2.ReadMeasurementValuesResponse(value=value)
    )


# ---------------------------------------------------------------- create


def test___create_test_result___sends_model_and_returns_created_test_result(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_test_result.return_value = data_store_pb2.TestResult(
        id="tr-id", name="Power test"
    )
    test_result = TestResult(
        "Power test",
        uut_instance_id="uut-instance-id",
        software_item_ids=["sw"],
        start_date_time=TIMESTAMP,
        duration=timedelta(seconds=2),
        outcome=Outcome.PASSED,
        keywords=["smoke"],
    )

    created = client.create_test_result(test_result)

    request = _sent(service_client.create_test_result)
    assert isinstance(request, data_store_service_pb2.CreateTestResultRequest)
    assert request.test_result == test_result.to_protobuf()
    assert created == TestResult("Power test", id="tr-id")


def test___create_step___sends_model_with_conditions_and_returns_created_step(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_step.return_value = data_store_pb2.Step(
        id="step-id", name="Measure voltage"
    )
    step = Step(
        "Measure voltage",
        test_result_id="tr-id",
        status=Status.RUNNING,
        conditions=[Condition("temperature", 25.0)],
    )

    created = client.create_step(step)

    request = _sent(service_client.create_step)
    assert isinstance(request, data_store_service_pb2.CreateStepRequest)
    assert request.step == step.to_protobuf()
    assert request.step.conditions[0].value.scalar.double_value == 25.0
    assert created == Step("Measure voltage", id="step-id")


def test___create_test_result___name_and_fields___sends_same_request_as_model(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_test_result.return_value = data_store_pb2.TestResult(id="tr-id")

    created = client.create_test_result(
        "Power test", operator_id="operator-id", outcome=Outcome.PASSED, keywords=["smoke"]
    )

    expected = TestResult(
        "Power test", operator_id="operator-id", outcome=Outcome.PASSED, keywords=["smoke"]
    )
    assert _sent(service_client.create_test_result).test_result == expected.to_protobuf()
    assert created.id == "tr-id"


def test___create_step___name_and_fields___sends_same_request_as_model(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_step.return_value = data_store_pb2.Step(id="step-id")

    created = client.create_step(
        "Measure voltage", test_result_id="tr-id", conditions=[Condition("temperature", 25.0)]
    )

    expected = Step(
        "Measure voltage", test_result_id="tr-id", conditions=[Condition("temperature", 25.0)]
    )
    assert _sent(service_client.create_step).step == expected.to_protobuf()
    assert created.id == "step-id"


def test___create_measurement___model___sends_same_request_as_fields(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_measurement.return_value = data_store_pb2.Measurement(id="m-id")
    measurement = Measurement(
        name="voltage", value=Scalar(5.0, "V"), step_id="step-id", outcome=Outcome.PASSED
    )

    created = client.create_measurement(measurement)

    from_fields = client.create_measurement(
        "voltage", Scalar(5.0, "V"), "step-id", outcome=Outcome.PASSED
    )
    first, second = [call.args[0] for call in service_client.create_measurement.call_args_list]
    assert first.measurement == measurement.to_protobuf()
    assert first == second
    assert created.id == from_fields.id == "m-id"


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(
            lambda client: client.create_test_result(TestResult("t"), link="x"),
            id="create_test_result",
        ),
        pytest.param(lambda client: client.create_step(Step("s"), notes="x"), id="create_step"),
        pytest.param(
            lambda client: client.create_measurement(Measurement(name="v"), 1.0),
            id="create_measurement_positional",
        ),
        pytest.param(
            lambda client: client.create_measurement(Measurement(name="v"), units="V"),
            id="create_measurement_keyword",
        ),
    ],
)
def test___create___model_with_fields___raises_type_error_before_rpc(
    client: DataStoreClient, service_client: Any, call: Callable[[DataStoreClient], object]
) -> None:
    with pytest.raises(TypeError, match="not both"):
        call(client)

    assert service_client.method_calls == []


def test___add_condition___sends_condition_and_returns_step(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.add_condition.return_value = data_store_service_pb2.AddConditionResponse(
        step=data_store_pb2.Step(id="step-id", name="Measure voltage")
    )
    condition = Condition("supply-voltage", Scalar(5.0, "V"), condition_type="Nominal")

    step = client.add_condition("step-id", condition)

    request = _sent(service_client.add_condition)
    assert request.step_id == "step-id"
    assert request.condition == condition.to_protobuf()
    assert request.condition.units == "V"
    assert step == Step("Measure voltage", id="step-id")


def test___add_condition___name_value_and_fields___sends_same_request_as_model(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.add_condition.return_value = data_store_service_pb2.AddConditionResponse()

    client.add_condition("step-id", "supply-voltage", 5.0, condition_type="Nominal", units="V")

    expected = Condition("supply-voltage", 5.0, condition_type="Nominal", units="V")
    request = _sent(service_client.add_condition)
    assert request.step_id == "step-id"
    assert request.condition == expected.to_protobuf()


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(
            lambda client: client.add_condition("step-id", Condition("c", 1.0), units="V"),
            id="keyword_field",
        ),
        pytest.param(
            lambda client: client.add_condition("step-id", Condition("c", 1.0), 2.0),
            id="positional_value",
        ),
    ],
)
def test___add_condition___condition_with_fields___raises_type_error_before_rpc(
    client: DataStoreClient, service_client: Any, call: Callable[[DataStoreClient], object]
) -> None:
    with pytest.raises(TypeError, match="not both"):
        call(client)

    assert service_client.method_calls == []


def test___add_condition___name_without_value___raises_type_error_before_rpc(
    client: DataStoreClient, service_client: Any
) -> None:
    # Typed as Any to bypass the type checker, which already rejects a missing value, and
    # test the runtime check.
    add_condition: Any = client.add_condition

    with pytest.raises(TypeError, match="value"):
        add_condition("step-id", "supply-voltage")

    assert service_client.method_calls == []


def test___add_condition___rejects_unsupported_value_before_rpc(
    client: DataStoreClient, service_client: Any
) -> None:
    with pytest.raises(TypeError):
        client.add_condition("step-id", Condition("config", [1, 2]))

    service_client.add_condition.assert_not_called()


def test___create_measurement___converts_value_and_metadata(
    client: DataStoreClient, service_client: Any
) -> None:
    response = data_store_pb2.Measurement(id="m-id", name="voltage", step_id="step-id", units="V")
    response.value.scalar.double_value = 5.2
    service_client.create_measurement.return_value = response

    created = client.create_measurement(
        "voltage",
        5.2,
        "step-id",
        units="V",
        start_date_time=TIMESTAMP,
        duration=timedelta(milliseconds=5),
        outcome=Outcome.PASSED,
        error_information=ErrorInformation(error_code=1, message="m", source="s"),
        software_item_ids=["sw"],
    )

    request = _sent(service_client.create_measurement)
    assert isinstance(request, data_store_service_pb2.CreateMeasurementRequest)
    assert created == Measurement(
        id="m-id", name="voltage", step_id="step-id", units="V", value=Scalar(5.2)
    )
    assert (request.measurement.name, request.measurement.step_id) == ("voltage", "step-id")
    assert request.measurement.units == "V"
    assert request.measurement.value.scalar.double_value == 5.2
    assert request.measurement.start_date_time == hightime_datetime_to_protobuf(TIMESTAMP)
    assert request.measurement.duration == hightime_timedelta_to_protobuf(timedelta(milliseconds=5))
    assert request.measurement.outcome == data_store_pb2.OUTCOME_PASSED
    assert request.measurement.error_information.message == "m"
    assert list(request.measurement.software_item_ids) == ["sw"]


def test___create_measurement___uses_scalar_units_when_units_not_given(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_measurement.return_value = data_store_pb2.Measurement(id="m-id")

    client.create_measurement("voltage", Scalar(5.2, "V"), "step-id")

    assert _sent(service_client.create_measurement).measurement.units == "V"


def test___create_measurement___keeps_given_units_for_scalar_value(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_measurement.return_value = data_store_pb2.Measurement(id="m-id")

    client.create_measurement("voltage", Scalar(5.2, "V"), "step-id", units="mV")

    assert _sent(service_client.create_measurement).measurement.units == "mV"


def test___create_measurement___accepts_inline_metadata_objects(
    client: DataStoreClient, service_client: Any
) -> None:
    from ni.datastore.metadata import HardwareItem, SoftwareItem, TestAdapter

    software = SoftwareItem(product="p", version="1")
    hardware = HardwareItem(manufacturer="m", model="x", serial_number="1")
    adapter = TestAdapter(name="adapter")

    client.create_measurement(
        "voltage",
        5.0,
        "step-id",
        software_items=[software],
        hardware_items=[hardware],
        test_adapters=[adapter],
    )

    measurement = _sent(service_client.create_measurement).measurement
    assert list(measurement.software_items) == [software.to_protobuf()]
    assert list(measurement.hardware_items) == [hardware.to_protobuf()]
    assert list(measurement.test_adapters) == [adapter.to_protobuf()]


def test___create_measurement___converts_mapping_to_json_value(
    client: DataStoreClient, service_client: Any
) -> None:
    client.create_measurement("configuration", {"enabled": True}, "step-id")

    value = _sent(service_client.create_measurement).measurement.value
    assert value.WhichOneof("value") == "json_value"
    assert value.json_value.value.fields["enabled"].bool_value is True


def test___create_measurement___converts_analog_waveform(
    client: DataStoreClient, service_client: Any
) -> None:
    waveform = AnalogWaveform(
        sample_count=2,
        raw_data=np.array([1.0, 2.0], dtype=np.float64),
        timing=Timing.create_with_regular_interval(timedelta(seconds=1), TIMESTAMP),
    )

    client.create_measurement("signal", waveform, "step-id")

    value = _sent(service_client.create_measurement).measurement.value
    assert value.WhichOneof("value") == "double_analog_waveform"
    assert list(value.double_analog_waveform.y_data) == [1.0, 2.0]
    assert value.double_analog_waveform.dt == 1.0


def test___create_measurement___rejects_unsupported_value_before_rpc(
    client: DataStoreClient, service_client: Any
) -> None:
    # Typed as Any to bypass the type checker, which already rejects this value, and test
    # the runtime check that protects callers who do not use a type checker.
    unsupported_value: Any = object()

    with pytest.raises(TypeError, match="Unsupported measurement value type"):
        client.create_measurement("measurement", unsupported_value, "step-id")

    service_client.create_measurement.assert_not_called()


# ---------------------------------------------------------------- read value


@pytest.mark.parametrize(
    "read_source",
    [
        pytest.param(Measurement(id="m-id"), id="measurement"),
        pytest.param("m-id", id="measurement_id"),
    ],
)
def test___read_measurement_value___requests_value_of_measurement_id(
    client: DataStoreClient, service_client: Any, read_source: Measurement | str
) -> None:
    value = data_store_pb2.MeasurementValue()
    value.scalar.bool_value = True
    _read_response(service_client, value)

    read_value = client.read_measurement_value(read_source)

    request = _sent(service_client.read_measurement_values)
    assert request.measurement_id == "m-id"
    assert list(request.read_mask.paths) == ["value"]
    assert read_value == Scalar(True)


def test___read_measurement_value___returns_scalar_without_units(
    client: DataStoreClient, service_client: Any
) -> None:
    value = data_store_pb2.MeasurementValue()
    value.scalar.double_value = 5.2
    _read_response(service_client, value)

    read_value = client.read_measurement_value(Measurement(id="m-id"), Scalar)

    assert (read_value.value, read_value.units) == (5.2, "")


def test___read_measurement_value___preserves_scalar_units(
    client: DataStoreClient, service_client: Any
) -> None:
    value = data_store_pb2.MeasurementValue()
    value.scalar.double_value = 5.2
    value.scalar.attributes["NI_UnitDescription"].string_value = "V"
    _read_response(service_client, value)

    read_value = client.read_measurement_value(Measurement(id="m-id"), Scalar)

    assert (read_value.value, read_value.units) == (5.2, "V")


def test___read_measurement_value___converts_vector(
    client: DataStoreClient, service_client: Any
) -> None:
    value = data_store_pb2.MeasurementValue()
    value.vector.CopyFrom(vector_to_protobuf(Vector([1.0, 2.0])))
    _read_response(service_client, value)

    read_value = client.read_measurement_value(Measurement(id="m-id"), Vector)

    assert list(read_value) == [1.0, 2.0]


def test___read_measurement_value___converts_json(
    client: DataStoreClient, service_client: Any
) -> None:
    value = data_store_pb2.MeasurementValue()
    value.json_value.value.update({"enabled": True})
    _read_response(service_client, value)

    read_value = client.read_measurement_value(Measurement(id="m-id"))

    assert read_value == {"enabled": True}


def test___read_measurement_value___converts_analog_waveform(
    client: DataStoreClient, service_client: Any
) -> None:
    _read_response(
        service_client,
        data_store_pb2.MeasurementValue(double_analog_waveform=DoubleAnalogWaveform(y_data=[1.0])),
    )

    read_value = client.read_measurement_value(Measurement(id="m-id"), AnalogWaveform)

    assert list(read_value.scaled_data) == [1.0]


def test___read_measurement_value___wrong_expected_type___raises(
    client: DataStoreClient, service_client: Any
) -> None:
    value = data_store_pb2.MeasurementValue()
    value.scalar.double_value = 1.0
    _read_response(service_client, value)

    with pytest.raises(TypeError, match="Expected type"):
        client.read_measurement_value(Measurement(id="m-id"), Vector)


# ---------------------------------------------------------------- get / query


def test___get_test_result___returns_model_with_python_values(
    client: DataStoreClient, service_client: Any
) -> None:
    proto = data_store_pb2.TestResult(
        id="tr-id",
        name="Power test",
        start_date_time=hightime_datetime_to_protobuf(TIMESTAMP),
        outcome=data_store_pb2.OUTCOME_PASSED,
    )
    proto.extension.update({"lot": "A1"})
    service_client.get_test_result.return_value = proto

    test_result = client.get_test_result("tr-id", read_fields=["name", "extension"])

    request = _sent(service_client.get_test_result)
    assert request.test_result_id == "tr-id"
    assert list(request.read_mask.paths) == ["name", "extension"]
    assert isinstance(test_result, TestResult)
    assert test_result.start_date_time == TIMESTAMP
    assert test_result.outcome == Outcome.PASSED
    assert test_result.extension == {"lot": "A1"}


def test___get_step___omits_empty_read_mask(client: DataStoreClient, service_client: Any) -> None:
    service_client.get_step.return_value = data_store_pb2.Step(id="step-id", name="s")

    step = client.get_step("step-id")

    assert not _sent(service_client.get_step).HasField("read_mask")
    assert step == Step("s", id="step-id")


def test___get_measurement___returns_model(client: DataStoreClient, service_client: Any) -> None:
    service_client.get_measurement.return_value = data_store_pb2.Measurement(
        id="m-id", name="voltage", units="V"
    )

    measurement = client.get_measurement("m-id")

    assert _sent(service_client.get_measurement).measurement_id == "m-id"
    assert measurement == Measurement(id="m-id", name="voltage", units="V")


def test___get_measurement___propagates_transport_error(
    client: DataStoreClient, service_client: Any
) -> None:
    transport_error = RuntimeError("service unavailable")
    service_client.get_measurement.side_effect = transport_error

    with pytest.raises(RuntimeError) as error:
        client.get_measurement("m-id")

    assert error.value is transport_error


def test___query_test_results___returns_models(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.query_test_results.return_value = (
        data_store_service_pb2.QueryTestResultsResponse(
            test_results=[data_store_pb2.TestResult(id="tr-id", name="Power test")]
        )
    )
    odata_query = "$filter=Name eq 'Power test'"

    results = client.query_test_results(odata_query, read_fields=["name"])

    request = _sent(service_client.query_test_results)
    assert request.odata_query == odata_query
    assert list(request.read_mask.paths) == ["name"]
    assert results == [TestResult("Power test", id="tr-id")]


def test___query_steps___returns_models(client: DataStoreClient, service_client: Any) -> None:
    service_client.query_steps.return_value = data_store_service_pb2.QueryStepsResponse(
        steps=[data_store_pb2.Step(id="step-id", name="s")]
    )
    odata_query = "$filter=Name eq 's'"

    steps = client.query_steps(odata_query)

    assert _sent(service_client.query_steps).odata_query == odata_query
    assert steps == [Step("s", id="step-id")]


def test___query_measurements___returns_models(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.query_measurements.return_value = (
        data_store_service_pb2.QueryMeasurementsResponse(
            measurements=[data_store_pb2.Measurement(id="m-id", name="voltage")]
        )
    )
    odata_query = "$filter=Name eq 'voltage'"

    measurements = client.query_measurements(odata_query)

    assert _sent(service_client.query_measurements).odata_query == odata_query
    assert measurements == [Measurement(id="m-id", name="voltage")]


@pytest.mark.parametrize(
    ("method", "response_type"),
    [
        ("query_test_results", "QueryTestResultsResponse"),
        ("query_steps", "QueryStepsResponse"),
        ("query_measurements", "QueryMeasurementsResponse"),
    ],
)
def test___query___returns_next_link(
    client: DataStoreClient,
    service_client: Any,
    method: str,
    response_type: str,
) -> None:
    getattr(service_client, method).return_value = getattr(data_store_service_pb2, response_type)(
        next_link="https://next"
    )

    results = getattr(client, method)()

    assert isinstance(results, QueryResults)
    assert (list(results), results.next_link) == ([], "https://next")


def test___query___next_link_is_empty_on_last_page(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.query_steps.return_value = data_store_service_pb2.QueryStepsResponse()

    results = client.query_steps()

    assert results.next_link == ""


def test___json_value_measurement___sends_and_reads_attributes(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_measurement.return_value = data_store_pb2.Measurement(id="m-id")
    value = JsonValue({"serial": "SN-1"}, attributes={"source": "dmm", "rev": 2})

    client.create_measurement("config", value, "step-id")

    sent = _sent(service_client.create_measurement).measurement.value
    _read_response(service_client, sent)
    read_value = client.read_measurement_value(Measurement(id="m-id"))

    assert read_value == value


# ---------------------------------------------------------------- update


def test___update_test_result___builds_mask_and_returns_model(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.update_test_result.return_value = data_store_pb2.TestResult(
        id="tr-id", name="t", link="https://example.com", outcome=data_store_pb2.OUTCOME_FAILED
    )

    updated = client.update_test_result(
        "tr-id", link="https://example.com", outcome=Outcome.FAILED, uut_id="uut-id"
    )

    request = _sent(service_client.update_test_result)
    assert request.test_result.id == "tr-id"
    assert request.test_result.link == "https://example.com"
    assert request.test_result.outcome == data_store_pb2.OUTCOME_FAILED
    assert request.test_result.uut_id == "uut-id"
    assert list(request.update_mask.paths) == ["link", "outcome", "uut_id"]
    assert updated.outcome == Outcome.FAILED


def test___update_step___builds_mask_and_returns_model(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.update_step.return_value = data_store_pb2.Step(id="step-id", notes="done")

    updated = client.update_step("step-id", notes="done", status=Status.DONE)

    request = _sent(service_client.update_step)
    assert request.step.notes == "done"
    assert request.step.status == data_store_pb2.STATUS_DONE
    assert list(request.update_mask.paths) == ["notes", "status"]
    assert updated.notes == "done"


def test___update_measurement___converts_error_information_and_extension(
    client: DataStoreClient, service_client: Any
) -> None:
    client.update_measurement(
        "m-id",
        error_information=ErrorInformation(error_code=2, message="boom"),
        extension={"retest": True},
    )

    request = _sent(service_client.update_measurement)
    assert request.measurement.error_information.message == "boom"
    assert request.measurement.extension["retest"] is True
    assert list(request.update_mask.paths) == ["error_information", "extension"]


@pytest.mark.parametrize("fields", [{"start_date_time": TIMESTAMP}, {"end_date_time": TIMESTAMP}])
def test___update_measurement___converts_timestamp(
    client: DataStoreClient, service_client: Any, fields: MeasurementUpdateFields
) -> None:
    client.update_measurement("m-id", **fields)

    [field] = fields
    request = _sent(service_client.update_measurement)
    assert getattr(request.measurement, field) == hightime_datetime_to_protobuf(TIMESTAMP)
    assert list(request.update_mask.paths) == [field]


@pytest.mark.parametrize(
    ("method", "resource_field"),
    [("update_test_result", "test_result"), ("update_step", "step")],
)
def test___update___replaces_keywords(
    client: DataStoreClient, service_client: Any, method: str, resource_field: str
) -> None:
    getattr(client, method)("resource-id", keywords=["b", "c"])

    request = _sent(getattr(service_client, method))
    assert list(getattr(request, resource_field).keywords) == ["b", "c"]
    assert list(request.update_mask.paths) == ["keywords"]


@pytest.mark.parametrize(
    ("method", "resource_field"),
    [
        ("update_test_result", "test_result"),
        ("update_step", "step"),
        ("update_measurement", "measurement"),
    ],
)
def test___update___converts_duration(
    client: DataStoreClient, service_client: Any, method: str, resource_field: str
) -> None:
    duration = timedelta(seconds=3)

    getattr(client, method)("resource-id", duration=duration)

    request = _sent(getattr(service_client, method))
    assert getattr(request, resource_field).duration == hightime_timedelta_to_protobuf(duration)
    assert list(request.update_mask.paths) == ["duration"]


def test___update___none_sends_field_in_mask_with_empty_value(
    client: DataStoreClient, service_client: Any
) -> None:
    client.update_test_result("tr-id", link=None)

    # The service clears a field that is in the update mask but has an empty value.
    request = _sent(service_client.update_test_result)
    assert request.test_result.link == ""
    assert list(request.update_mask.paths) == ["link"]


def test___update___rejects_empty_update_before_rpc(
    client: DataStoreClient, service_client: Any
) -> None:
    with pytest.raises(ValueError, match="At least one field"):
        client.update_measurement("m-id")

    service_client.update_measurement.assert_not_called()


@pytest.mark.parametrize(
    ("method", "field"),
    [
        ("update_test_result", "name"),
        ("update_step", "step_type"),
        ("update_measurement", "units"),
    ],
)
def test___update___rejects_immutable_field_before_rpc(
    client: DataStoreClient, service_client: Any, method: str, field: str
) -> None:
    with pytest.raises(ValueError, match=f"Fields cannot be updated: {field}"):
        getattr(client, method)("resource-id", **{field: "x"})

    getattr(service_client, method).assert_not_called()


def test___update_step___builder___sends_builder_request(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.update_step.return_value = data_store_pb2.Step(id="step-id", notes="ok")

    updated = client.update_step(StepUpdateBuilder("step-id").with_notes("ok"))

    request = _sent(service_client.update_step)
    assert request.step.id == "step-id"
    assert request.step.notes == "ok"
    assert list(request.update_mask.paths) == ["notes"]
    assert updated.notes == "ok"


@pytest.mark.parametrize(
    ("method", "builder"),
    [
        ("update_test_result", TestResultUpdateBuilder("tr-id").with_link("x")),
        ("update_step", StepUpdateBuilder("step-id").with_notes("x")),
        ("update_measurement", MeasurementUpdateBuilder("m-id").with_notes("x")),
    ],
)
def test___update___builder_with_keyword_fields___raises_type_error(
    client: DataStoreClient, service_client: Any, method: str, builder: object
) -> None:
    with pytest.raises(TypeError, match="builder"):
        getattr(client, method)(builder, outcome=Outcome.PASSED)

    getattr(service_client, method).assert_not_called()


def test___update_step___resource_with_keyword_fields___updates_only_given_fields(
    client: DataStoreClient, service_client: Any
) -> None:
    step = Step(name="s", id="step-id", notes="old", link="https://example.com")

    client.update_step(step, outcome=Outcome.PASSED)

    request = _sent(service_client.update_step)
    assert request.step.id == "step-id"
    assert request.step.notes == ""
    assert list(request.update_mask.paths) == ["outcome"]


def test___update_test_result___resource_only___selects_every_supported_field(
    client: DataStoreClient, service_client: Any
) -> None:
    test_result = TestResult(
        name="ignored",
        id="tr-id",
        operator_id="operator-id",
        link="https://example.com",
        outcome=Outcome.PASSED,
        schema_id="ignored-schema",
        software_item_ids=["sw-id"],
    )

    client.update_test_result(test_result)

    request = _sent(service_client.update_test_result)
    assert list(request.update_mask.paths) == [
        "uut_instance_id",
        "operator_id",
        "test_station_id",
        "test_description_id",
        "start_date_time",
        "end_date_time",
        "outcome",
        "status",
        "error_information",
        "link",
        "extension",
        "uut_instance",
        "operator",
        "test_station",
        "test_description",
    ]
    sent = request.test_result
    assert sent.id == "tr-id"
    assert sent.operator_id == "operator-id"
    assert sent.link == "https://example.com"
    assert sent.outcome == data_store_pb2.OUTCOME_PASSED
    assert not sent.HasField("extension")
    # Immutable and dedicated-RPC fields are not sent.
    assert sent.name == ""
    assert sent.schema_id == ""
    assert list(sent.software_item_ids) == []


def test___update_test_result___resource_only_with_stage_2_values___selects_them(
    client: DataStoreClient, service_client: Any
) -> None:
    test_result = TestResult(
        name="t", id="tr-id", uut_id="uut-id", keywords=["smoke"], duration=timedelta(seconds=1)
    )

    client.update_test_result(test_result)

    paths = list(_sent(service_client.update_test_result).update_mask.paths)
    assert {"uut_id", "keywords", "duration"} <= set(paths)
    assert "uut" not in paths


def test___update_step___resource_only_with_id_and_inline___sends_id_only(
    client: DataStoreClient, service_client: Any
) -> None:
    from ni.datastore.metadata import Test

    step = Step(name="s", id="step-id", test_id="test-id", test=Test(name="expanded"))

    client.update_step(step)

    request = _sent(service_client.update_step)
    assert request.step.test_id == "test-id"
    assert not request.step.HasField("test")
    assert {"test_id", "test"} <= set(request.update_mask.paths)


def test___update_measurement___resource_only___does_not_send_value(
    client: DataStoreClient, service_client: Any
) -> None:
    measurement = Measurement(
        id="m-id", name="v", value=Vector([1.0, 2.0]), notes="checked", outcome=Outcome.PASSED
    )

    client.update_measurement(measurement)

    request = _sent(service_client.update_measurement)
    assert list(request.update_mask.paths) == [
        "notes",
        "start_date_time",
        "end_date_time",
        "outcome",
        "error_information",
        "extension",
    ]
    assert request.measurement.notes == "checked"
    assert not request.measurement.HasField("value")


def test___batch_update_steps___builders_and_resources___sends_each_request(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.batch_update_steps.return_value = (
        data_store_service_pb2.BatchUpdateStepsResponse()
    )

    client.batch_update_steps(
        [StepUpdateBuilder("a").with_notes("n"), Step(name="b", id="b", notes="m")]
    )

    first, second = _sent(service_client.batch_update_steps).requests
    assert first.step.id == "a"
    assert list(first.update_mask.paths) == ["notes"]
    assert second.step.id == "b"
    assert second.step.notes == "m"
    assert "notes" in second.update_mask.paths


@pytest.mark.parametrize(
    ("method", "updates"),
    [
        ("batch_update_test_results", [TestResultUpdateBuilder("a").with_link("x")]),
        ("batch_update_measurements", [MeasurementUpdateBuilder("a").with_notes("x")]),
    ],
)
def test___batch_update___builders___sends_builder_requests(
    client: DataStoreClient, service_client: Any, method: str, updates: list[Any]
) -> None:
    client_method = getattr(service_client, method)
    client_method.return_value = Mock(test_results=[], measurements=[])

    getattr(client, method)(updates)

    [request] = _sent(client_method).requests
    assert len(request.update_mask.paths) == 1


def test___batch_update___empty_iterable___raises_value_error(
    client: DataStoreClient, service_client: Any
) -> None:
    with pytest.raises(ValueError, match="At least one update"):
        client.batch_update_steps([])

    service_client.batch_update_steps.assert_not_called()


# ---------------------------------------------------------------- delete


@pytest.mark.parametrize("force", [False, True])
def test___delete_test_result___sends_id_and_force(
    client: DataStoreClient, service_client: Any, force: bool
) -> None:
    client.delete_test_result("tr-id", force=force)

    assert _sent(service_client.delete_test_result) == (
        data_store_service_pb2.DeleteTestResultRequest(test_result_id="tr-id", force=force)
    )


@pytest.mark.parametrize("force", [False, True])
def test___delete_step___sends_id_and_force(
    client: DataStoreClient, service_client: Any, force: bool
) -> None:
    client.delete_step("step-id", force=force)

    assert _sent(service_client.delete_step) == data_store_service_pb2.DeleteStepRequest(
        step_id="step-id", force=force
    )


def test___delete_measurement___sends_id(client: DataStoreClient, service_client: Any) -> None:
    client.delete_measurement("m-id")

    assert _sent(service_client.delete_measurement) == (
        data_store_service_pb2.DeleteMeasurementRequest(measurement_id="m-id")
    )


def test___delete___defaults_to_no_force(client: DataStoreClient, service_client: Any) -> None:
    client.delete_test_result("tr-id")
    client.delete_step("step-id")

    assert _sent(service_client.delete_test_result).force is False
    assert _sent(service_client.delete_step).force is False


def test___delete___resources___sends_their_ids(
    client: DataStoreClient, service_client: Any
) -> None:
    client.delete_test_result(TestResult("t", id="tr-id"), force=True)
    client.delete_step(Step("s", id="step-id"))
    client.delete_measurement(Measurement(id="m-id"))

    assert _sent(service_client.delete_test_result).test_result_id == "tr-id"
    assert _sent(service_client.delete_test_result).force is True
    assert _sent(service_client.delete_step).step_id == "step-id"
    assert _sent(service_client.delete_measurement).measurement_id == "m-id"


def test___batch_delete___resources_and_ids___sends_ids_in_order(
    client: DataStoreClient, service_client: Any
) -> None:
    client.batch_delete_test_results([TestResult("t", id="a"), "b"], force=[True, False])
    client.batch_delete_steps([Step("s", id="c"), "d"])
    client.batch_delete_measurements(["e", Measurement(id="f")])

    test_results = _sent(service_client.batch_delete_test_results).requests
    assert [(r.test_result_id, r.force) for r in test_results] == [("a", True), ("b", False)]
    assert [r.step_id for r in _sent(service_client.batch_delete_steps).requests] == ["c", "d"]
    measurements = _sent(service_client.batch_delete_measurements).requests
    assert [r.measurement_id for r in measurements] == ["e", "f"]


# ---------------------------------------------------------------- conditions and metadata links


def test___remove_test_result_metadata___sends_request_without_checking_measurements(
    client: DataStoreClient, service_client: Any
) -> None:
    client.remove_test_result_metadata(
        "tr-id", software_item_ids=["sw"], hardware_item_ids=["hw"], test_adapter_ids=["ta"]
    )

    service_client.query_measurements.assert_not_called()
    assert _sent(service_client.remove_test_result_metadata) == (
        data_store_service_pb2.RemoveTestResultMetadataRequest(
            test_result_id="tr-id",
            software_item_ids=["sw"],
            hardware_item_ids=["hw"],
            test_adapter_ids=["ta"],
        )
    )


def test___remove_condition___sends_name_and_returns_step(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.remove_condition.return_value = data_store_service_pb2.RemoveConditionResponse(
        step=data_store_pb2.Step(id="step-id")
    )

    step = client.remove_condition("step-id", "temperature")

    assert _sent(service_client.remove_condition) == data_store_service_pb2.RemoveConditionRequest(
        step_id="step-id", condition_name="temperature"
    )
    assert step.id == "step-id"


@pytest.mark.parametrize(
    ("method", "id_field", "response_type", "response_field"),
    [
        (
            "add_test_result_metadata",
            "test_result_id",
            "AddTestResultMetadataResponse",
            "test_result",
        ),
        (
            "remove_test_result_metadata",
            "test_result_id",
            "RemoveTestResultMetadataResponse",
            "test_result",
        ),
        (
            "add_measurement_metadata",
            "measurement_id",
            "AddMeasurementMetadataResponse",
            "measurement",
        ),
        (
            "remove_measurement_metadata",
            "measurement_id",
            "RemoveMeasurementMetadataResponse",
            "measurement",
        ),
    ],
)
def test___metadata_link_methods___send_ids_and_return_model(
    client: DataStoreClient,
    service_client: Any,
    method: str,
    id_field: str,
    response_type: str,
    response_field: str,
) -> None:
    response = getattr(data_store_service_pb2, response_type)()
    getattr(response, response_field).id = "resource-id"
    getattr(service_client, method).return_value = response

    result = getattr(client, method)(
        "resource-id", software_item_ids=["sw"], hardware_item_ids=["hw"], test_adapter_ids=["ta"]
    )

    request = _sent(getattr(service_client, method))
    assert getattr(request, id_field) == "resource-id"
    assert list(request.software_item_ids) == ["sw"]
    assert list(request.hardware_item_ids) == ["hw"]
    assert list(request.test_adapter_ids) == ["ta"]
    assert result.id == "resource-id"


# ---------------------------------------------------------------- limits and value reads


def test___create_measurement___sends_limits_and_extra_fields(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_measurement.return_value = data_store_pb2.Measurement(id="m-id")

    client.create_measurement(
        "voltage",
        5.0,
        "step-id",
        upper_limit=5.5,
        lower_limit=Vector([4.5, 4.6]),
        comparison_type="GELE",
        extension={"lot": "A1"},
        schema_id="schema",
    )

    sent = _sent(service_client.create_measurement).measurement
    assert sent.value.scalar.double_value == 5.0
    assert sent.upper_limit.scalar.double_value == 5.5
    assert sent.lower_limit.vector == vector_to_protobuf(Vector([4.5, 4.6]))
    assert (sent.comparison_type, sent.schema_id) == ("GELE", "schema")
    assert sent.extension["lot"] == "A1"


def test___create_measurement___omits_limits_when_not_given(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_measurement.return_value = data_store_pb2.Measurement(id="m-id")

    client.create_measurement("voltage", 5.0, "step-id")

    sent = _sent(service_client.create_measurement).measurement
    assert not sent.HasField("upper_limit")
    assert not sent.HasField("lower_limit")


@pytest.mark.parametrize(
    "read_source",
    [
        pytest.param(Measurement(id="m-id"), id="measurement"),
        pytest.param("m-id", id="measurement_id"),
    ],
)
def test___read_measurement_values___returns_value_and_limits(
    client: DataStoreClient, service_client: Any, read_source: Measurement | str
) -> None:
    response = data_store_service_pb2.ReadMeasurementValuesResponse()
    response.value.scalar.double_value = 5.0
    response.upper_limit.scalar.double_value = 5.5
    service_client.read_measurement_values.return_value = response

    result = client.read_measurement_values(read_source)

    assert _sent(service_client.read_measurement_values) == (
        data_store_service_pb2.ReadMeasurementValuesRequest(measurement_id="m-id")
    )
    assert (result.id, result.value, result.upper_limit, result.lower_limit) == (
        "m-id",
        Scalar(5.0),
        Scalar(5.5),
        None,
    )


def test___read_measurement_values___sends_read_fields(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.read_measurement_values.return_value = (
        data_store_service_pb2.ReadMeasurementValuesResponse()
    )

    client.read_measurement_values(
        Measurement(id="m-id"), read_fields=[MeasurementValueField.UPPER_LIMIT]
    )

    assert list(_sent(service_client.read_measurement_values).read_mask.paths) == ["upper_limit"]


def test___get_test_result___sends_read_field_enums_as_field_names(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.get_test_result.return_value = data_store_pb2.TestResult(id="tr-id")

    client.get_test_result("tr-id", read_fields=[TestResultField.NAME, TestResultField.OUTCOME])

    assert list(_sent(service_client.get_test_result).read_mask.paths) == ["name", "outcome"]


def test___get_step___sends_read_field_enums_as_field_names(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.get_step.return_value = data_store_pb2.Step(id="step-id")

    client.get_step(
        "step-id", read_fields=[StepField.NAME, StepField.CONDITIONS, StepField.HAS_CHILDREN]
    )

    assert list(_sent(service_client.get_step).read_mask.paths) == [
        "name",
        "conditions",
        "has_children",
    ]


def test___query_measurements___accepts_read_field_enums_and_plain_names(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.query_measurements.return_value = (
        data_store_service_pb2.QueryMeasurementsResponse()
    )

    client.query_measurements(read_fields=[MeasurementField.NAME, "conditions"])

    assert list(_sent(service_client.query_measurements).read_mask.paths) == [
        "name",
        "conditions",
    ]


# ---------------------------------------------------------------- batch create


def test___batch_create_test_results___sends_models_and_returns_created_test_results(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.batch_create_test_results.return_value = (
        data_store_service_pb2.BatchCreateTestResultsResponse(
            test_results=[
                data_store_pb2.TestResult(id="a", name="tr-1"),
                data_store_pb2.TestResult(id="b", name="tr-2"),
            ]
        )
    )
    nested = TestResult("tr-1", steps=[Step("s", measurements=[Measurement(name="m", value=1.0)])])

    created = client.batch_create_test_results([nested, TestResult("tr-2")])

    requests = _sent(service_client.batch_create_test_results).requests
    assert [r.test_result.name for r in requests] == ["tr-1", "tr-2"]
    assert requests[0].test_result.steps[0].measurements[0].value.scalar.double_value == 1.0
    assert created == [TestResult("tr-1", id="a"), TestResult("tr-2", id="b")]


def test___batch_create_steps___sends_models_and_returns_created_steps(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.batch_create_steps.return_value = (
        data_store_service_pb2.BatchCreateStepsResponse(
            steps=[data_store_pb2.Step(id="a", name="parent")]
        )
    )

    created = client.batch_create_steps([Step("parent", children=[Step("child")])])

    [request] = _sent(service_client.batch_create_steps).requests
    assert request.step.children[0].name == "child"
    assert created == [Step("parent", id="a")]


def test___batch_create_measurements___sends_values_and_returns_created_measurements(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.batch_create_measurements.return_value = (
        data_store_service_pb2.BatchCreateMeasurementsResponse(
            measurements=[
                data_store_pb2.Measurement(id="a", name="m1"),
                data_store_pb2.Measurement(id="b", name="m2"),
            ]
        )
    )

    created = client.batch_create_measurements(
        [
            Measurement(name="m1", step_id="s1", value=1.0, upper_limit=2.0),
            Measurement(name="m2", step_id="s2", value="PASS"),
        ]
    )

    requests = _sent(service_client.batch_create_measurements).requests
    assert requests[0].measurement.upper_limit.scalar.double_value == 2.0
    assert requests[1].measurement.value.scalar.string_value == "PASS"
    assert created == [Measurement(id="a", name="m1"), Measurement(id="b", name="m2")]


# ---------------------------------------------------------------- batch update


@pytest.mark.parametrize(
    ("method", "response_type", "response_field", "resource_field", "proto_type"),
    [
        (
            "batch_update_test_results",
            "BatchUpdateTestResultsResponse",
            "test_results",
            "test_result",
            data_store_pb2.TestResult,
        ),
        ("batch_update_steps", "BatchUpdateStepsResponse", "steps", "step", data_store_pb2.Step),
        (
            "batch_update_measurements",
            "BatchUpdateMeasurementsResponse",
            "measurements",
            "measurement",
            data_store_pb2.Measurement,
        ),
    ],
)
def test___batch_update___sends_per_item_masks_and_returns_models(
    client: DataStoreClient,
    service_client: Any,
    method: str,
    response_type: str,
    response_field: str,
    resource_field: str,
    proto_type: Any,
) -> None:
    response = getattr(data_store_service_pb2, response_type)(
        **{response_field: [proto_type(id="a"), proto_type(id="b")]}
    )
    getattr(service_client, method).return_value = response

    results = getattr(client, method)(
        {"a": {"outcome": Outcome.PASSED}, "b": {"extension": {"x": 1}, "outcome": None}}
    )

    first, second = _sent(getattr(service_client, method)).requests
    assert getattr(first, resource_field).id == "a"
    assert list(first.update_mask.paths) == ["outcome"]
    assert getattr(first, resource_field).outcome == data_store_pb2.OUTCOME_PASSED
    assert getattr(second, resource_field).id == "b"
    assert list(second.update_mask.paths) == ["extension", "outcome"]
    assert [r.id for r in results] == ["a", "b"]


@pytest.mark.parametrize(
    "method", ["batch_update_test_results", "batch_update_steps", "batch_update_measurements"]
)
def test___batch_update___rejects_empty_or_invalid_before_rpc(
    client: DataStoreClient, service_client: Any, method: str
) -> None:
    with pytest.raises(ValueError, match="At least one update"):
        getattr(client, method)({})
    with pytest.raises(ValueError, match="At least one field"):
        getattr(client, method)({"a": {}})
    with pytest.raises(ValueError, match="Fields cannot be updated: name"):
        getattr(client, method)({"a": {"name": "x"}})

    getattr(service_client, method).assert_not_called()


def test___update_test_result___accepts_metadata_models(
    client: DataStoreClient, service_client: Any
) -> None:
    from ni.datastore.metadata import Operator, Uut

    client.update_test_result(
        "tr-id", operator=Operator(name="Ada", role="Engineer"), uut=Uut(model_name="model")
    )

    sent = _sent(service_client.update_test_result)
    assert sent.test_result.operator.name == "Ada"
    assert sent.test_result.uut.model_name == "model"
    assert list(sent.update_mask.paths) == ["operator", "uut"]


def test___batch_update_test_results___accepts_inline_uut(
    client: DataStoreClient, service_client: Any
) -> None:
    from ni.datastore.metadata import Uut

    service_client.batch_update_test_results.return_value = (
        data_store_service_pb2.BatchUpdateTestResultsResponse()
    )

    client.batch_update_test_results({"tr-id": {"uut": Uut(model_name="model")}})

    request = _sent(service_client.batch_update_test_results).requests[0]
    assert request.test_result.uut.model_name == "model"
    assert list(request.update_mask.paths) == ["uut"]


# ---------------------------------------------------------------- batch delete


def test___batch_delete_test_results___applies_single_force_to_all(
    client: DataStoreClient, service_client: Any
) -> None:
    client.batch_delete_test_results(["a", "b"], force=True)

    requests = _sent(service_client.batch_delete_test_results).requests
    assert [(r.test_result_id, r.force) for r in requests] == [("a", True), ("b", True)]


def test___batch_delete_steps___accepts_per_item_force(
    client: DataStoreClient, service_client: Any
) -> None:
    client.batch_delete_steps(["a", "b"], force=[True, False])

    requests = _sent(service_client.batch_delete_steps).requests
    assert [(r.step_id, r.force) for r in requests] == [("a", True), ("b", False)]


def test___batch_delete___rejects_mismatched_force_count(
    client: DataStoreClient, service_client: Any
) -> None:
    with pytest.raises(ValueError, match="Expected 2 force flags"):
        client.batch_delete_steps(["a", "b"], force=[True])

    service_client.batch_delete_steps.assert_not_called()


def test___batch_delete_measurements___sends_ids(
    client: DataStoreClient, service_client: Any
) -> None:
    client.batch_delete_measurements(["a", "b"])

    requests = _sent(service_client.batch_delete_measurements).requests
    assert [r.measurement_id for r in requests] == ["a", "b"]


# ---------------------------------------------------------------- string list arguments


@pytest.mark.parametrize(
    ("argument", "call"),
    [
        pytest.param(
            "keywords",
            lambda client: client.update_test_result("tr-id", keywords="smoke"),
            id="update_test_result",
        ),
        pytest.param(
            "keywords",
            lambda client: client.update_step("step-id", keywords="smoke"),
            id="update_step",
        ),
        pytest.param(
            "keywords",
            lambda client: client.batch_update_test_results({"tr-id": {"keywords": "smoke"}}),
            id="batch_update_test_results",
        ),
        pytest.param(
            "keywords",
            lambda client: client.batch_update_steps({"step-id": {"keywords": "smoke"}}),
            id="batch_update_steps",
        ),
        pytest.param(
            "software_item_ids",
            lambda client: client.create_measurement("v", 1.0, "step-id", software_item_ids="sw"),
            id="create_measurement",
        ),
        pytest.param(
            "software_item_ids",
            lambda client: client.add_test_result_metadata("tr-id", software_item_ids="sw"),
            id="add_test_result_metadata",
        ),
        pytest.param(
            "hardware_item_ids",
            lambda client: client.remove_test_result_metadata("tr-id", hardware_item_ids="hw"),
            id="remove_test_result_metadata",
        ),
        pytest.param(
            "test_adapter_ids",
            lambda client: client.add_measurement_metadata("m-id", test_adapter_ids="ta"),
            id="add_measurement_metadata",
        ),
        pytest.param(
            "software_item_ids",
            lambda client: client.remove_measurement_metadata("m-id", software_item_ids="sw"),
            id="remove_measurement_metadata",
        ),
        pytest.param(
            "read_fields",
            lambda client: client.get_test_result("tr-id", read_fields="name"),
            id="get_test_result",
        ),
        pytest.param(
            "read_fields",
            lambda client: client.get_step("step-id", read_fields="name"),
            id="get_step",
        ),
        pytest.param(
            "read_fields",
            lambda client: client.get_measurement("m-id", read_fields="name"),
            id="get_measurement",
        ),
        pytest.param(
            "read_fields",
            lambda client: client.query_test_results(read_fields="name"),
            id="query_test_results",
        ),
        pytest.param(
            "read_fields",
            lambda client: client.query_steps(read_fields="name"),
            id="query_steps",
        ),
        pytest.param(
            "read_fields",
            lambda client: client.query_measurements(read_fields="name"),
            id="query_measurements",
        ),
        pytest.param(
            "read_fields",
            lambda client: client.read_measurement_values(
                Measurement(id="m-id"), read_fields=MeasurementValueField.VALUE
            ),
            id="read_measurement_values",
        ),
        pytest.param(
            "test_results",
            lambda client: client.batch_delete_test_results("tr-id"),
            id="batch_delete_test_results",
        ),
        pytest.param(
            "steps",
            lambda client: client.batch_delete_steps("step-id"),
            id="batch_delete_steps",
        ),
        pytest.param(
            "measurements",
            lambda client: client.batch_delete_measurements("m-id"),
            id="batch_delete_measurements",
        ),
    ],
)
def test___string_list_argument___single_string___raises_before_rpc(
    client: DataStoreClient,
    service_client: Any,
    argument: str,
    call: Callable[[DataStoreClient], object],
) -> None:
    with pytest.raises(TypeError, match=f"^{argument} must be"):
        call(client)

    assert service_client.method_calls == []


# ---------------------------------------------------------------- UUID IDs

ID = uuid.UUID("3f2b8c1e-5a7d-4e2b-9c1f-2d4e6a8b0c3d")
ID_TEXT = str(ID)


def test___get_methods___uuid___send_string_ids(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.get_test_result.return_value = data_store_pb2.TestResult()
    service_client.get_step.return_value = data_store_pb2.Step()
    service_client.get_measurement.return_value = data_store_pb2.Measurement()

    client.get_test_result(ID)
    client.get_step(ID)
    client.get_measurement(ID)

    assert _sent(service_client.get_test_result).test_result_id == ID_TEXT
    assert _sent(service_client.get_step).step_id == ID_TEXT
    assert _sent(service_client.get_measurement).measurement_id == ID_TEXT


def test___read_measurement_value___uuid___sends_string_id(
    client: DataStoreClient, service_client: Any
) -> None:
    client.create_measurement("v", 1.0, "step-id")
    _read_response(service_client, _sent(service_client.create_measurement).measurement.value)

    client.read_measurement_value(ID)
    assert _sent(service_client.read_measurement_values).measurement_id == ID_TEXT
    client.read_measurement_values(uuid.UUID(int=1))
    assert _sent(service_client.read_measurement_values).measurement_id == str(uuid.UUID(int=1))


def test___create_measurement___uuid_ids___sends_string_ids(
    client: DataStoreClient, service_client: Any
) -> None:
    client.create_measurement("v", 1.0, ID, software_item_ids=[ID])

    sent = _sent(service_client.create_measurement).measurement
    assert sent.step_id == ID_TEXT
    assert list(sent.software_item_ids) == [ID_TEXT]


def test___create_step___uuid_fields___sends_string_ids(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_step.return_value = data_store_pb2.Step()

    client.create_step("s", test_result_id=ID, test_id=ID)

    sent = _sent(service_client.create_step).step
    assert (sent.test_result_id, sent.test_id) == (ID_TEXT, ID_TEXT)


def test___conditions___uuid_step_id___sends_string_id(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.add_condition.return_value = data_store_service_pb2.AddConditionResponse()
    service_client.remove_condition.return_value = data_store_service_pb2.RemoveConditionResponse()

    client.add_condition(ID, Condition("c", 1.0))
    client.remove_condition(ID, "c")

    assert _sent(service_client.add_condition).step_id == ID_TEXT
    assert _sent(service_client.remove_condition).step_id == ID_TEXT


def test___update___uuid_target_and_id_fields___sends_string_ids(
    client: DataStoreClient, service_client: Any
) -> None:
    client.update_test_result(ID, operator_id=ID)
    client.update_step(StepUpdateBuilder(ID).with_test_id(ID))

    test_result = _sent(service_client.update_test_result).test_result
    assert (test_result.id, test_result.operator_id) == (ID_TEXT, ID_TEXT)
    step = _sent(service_client.update_step).step
    assert (step.id, step.test_id) == (ID_TEXT, ID_TEXT)


def test___batch_update___uuid_keys___sends_string_ids(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.batch_update_measurements.return_value = (
        data_store_service_pb2.BatchUpdateMeasurementsResponse()
    )

    client.batch_update_measurements({ID: {"notes": "n"}})

    assert _sent(service_client.batch_update_measurements).requests[0].measurement.id == ID_TEXT


def test___metadata_links___uuid_ids___sends_string_ids(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.add_test_result_metadata.return_value = (
        data_store_service_pb2.AddTestResultMetadataResponse()
    )
    service_client.add_measurement_metadata.return_value = (
        data_store_service_pb2.AddMeasurementMetadataResponse()
    )

    client.add_test_result_metadata(ID, software_item_ids=[ID], test_adapter_ids=["alias"])
    client.add_measurement_metadata(ID, hardware_item_ids=[ID])

    test_result_request = _sent(service_client.add_test_result_metadata)
    assert test_result_request.test_result_id == ID_TEXT
    assert list(test_result_request.software_item_ids) == [ID_TEXT]
    assert list(test_result_request.test_adapter_ids) == ["alias"]
    measurement_request = _sent(service_client.add_measurement_metadata)
    assert measurement_request.measurement_id == ID_TEXT
    assert list(measurement_request.hardware_item_ids) == [ID_TEXT]


def test___deletes___uuid_ids___send_string_ids(
    client: DataStoreClient, service_client: Any
) -> None:
    client.delete_test_result(ID)
    client.delete_step(ID)
    client.delete_measurement(ID)
    client.batch_delete_steps([ID, "b"])

    assert _sent(service_client.delete_test_result).test_result_id == ID_TEXT
    assert _sent(service_client.delete_step).step_id == ID_TEXT
    assert _sent(service_client.delete_measurement).measurement_id == ID_TEXT
    assert [r.step_id for r in _sent(service_client.batch_delete_steps).requests] == [
        ID_TEXT,
        "b",
    ]


def test___id_list___single_uuid___raises_type_error_before_rpc(
    client: DataStoreClient, service_client: Any
) -> None:
    # Typed as Any to bypass the type checker, which already rejects a single ID, and test
    # the runtime check.
    single_id: Any = ID

    with pytest.raises(TypeError, match="^steps must be"):
        client.batch_delete_steps(single_id)
    with pytest.raises(TypeError, match="^software_item_ids must be"):
        client.add_test_result_metadata("tr-id", software_item_ids=single_id)

    assert service_client.method_calls == []


# ---------------------------------------------------------------- lifecycle


def test___init___forwards_connection_options(mocker: MockerFixture) -> None:
    service_client_class = mocker.patch(
        "ni.datastore.data.v2._data_store_client.DataStoreServiceClient"
    )
    discovery_client, grpc_channel, grpc_channel_pool = Mock(), Mock(), Mock()

    DataStoreClient(
        discovery_client=discovery_client,
        grpc_channel=grpc_channel,
        grpc_channel_pool=grpc_channel_pool,
    )

    service_client_class.assert_called_once_with(
        discovery_client=discovery_client,
        grpc_channel=grpc_channel,
        grpc_channel_pool=grpc_channel_pool,
    )


def test___close___closes_underlying_client(client: DataStoreClient, service_client: Any) -> None:
    client.close()

    service_client.close.assert_called_once_with()


def test___context_manager___closes_underlying_client(service_client: Any) -> None:
    with DataStoreClient():
        pass

    service_client.close.assert_called_once_with()


def test___closed_client___raises_without_calling_service(
    client: DataStoreClient, service_client: Any
) -> None:
    client.close()

    with pytest.raises(RuntimeError, match="closed"):
        client.get_measurement("m-id")

    service_client.get_measurement.assert_not_called()
