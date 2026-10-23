"""Tests for the V2 data store client."""

from __future__ import annotations

import datetime as std_datetime
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
    Measurement,
    Outcome,
    Status,
    Step,
    TestResult,
)

UTC = std_datetime.timezone.utc
TIMESTAMP = datetime(2026, 5, 6, 7, 8, 9, tzinfo=UTC)


@pytest.fixture
def service_client(mocker: MockerFixture) -> Any:
    service_client = Mock()
    service_client.update_test_result.return_value = data_store_pb2.TestResult()
    service_client.update_step.return_value = data_store_pb2.Step()
    service_client.update_measurement.return_value = data_store_pb2.Measurement()
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


def test___create_test_result___sends_model_and_returns_id(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_test_result.return_value = data_store_pb2.TestResult(id="tr-id")
    test_result = TestResult(
        "Power test",
        uut_instance_id="uut-instance-id",
        software_item_ids=["sw"],
        start_date_time=TIMESTAMP,
        duration=timedelta(seconds=2),
        outcome=Outcome.PASSED,
        keywords=["smoke"],
    )

    test_result_id = client.create_test_result(test_result)

    request = _sent(service_client.create_test_result)
    assert isinstance(request, data_store_service_pb2.CreateTestResultRequest)
    assert request.test_result == test_result.to_protobuf()
    assert test_result_id == "tr-id"


def test___create_step___sends_model_with_conditions_and_returns_id(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_step.return_value = data_store_pb2.Step(id="step-id")
    step = Step(
        "Measure voltage",
        test_result_id="tr-id",
        status=Status.RUNNING,
        conditions=[Condition("temperature", 25.0)],
    )

    step_id = client.create_step(step)

    request = _sent(service_client.create_step)
    assert isinstance(request, data_store_service_pb2.CreateStepRequest)
    assert request.step == step.to_protobuf()
    assert request.step.conditions[0].value.scalar.double_value == 25.0
    assert step_id == "step-id"


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


def test___add_condition___rejects_unsupported_value_before_rpc(
    client: DataStoreClient, service_client: Any
) -> None:
    with pytest.raises(TypeError):
        client.add_condition("step-id", Condition("config", [1, 2]))

    service_client.add_condition.assert_not_called()


def test___create_measurement___converts_value_and_metadata(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.create_measurement.return_value = data_store_pb2.Measurement(id="m-id")

    measurement_id = client.create_measurement(
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
    assert measurement_id == "m-id"
    assert (request.measurement.name, request.measurement.step_id) == ("voltage", "step-id")
    assert request.measurement.units == "V"
    assert request.measurement.value.scalar.double_value == 5.2
    assert request.measurement.start_date_time == hightime_datetime_to_protobuf(TIMESTAMP)
    assert request.measurement.duration == hightime_timedelta_to_protobuf(timedelta(milliseconds=5))
    assert request.measurement.outcome == data_store_pb2.OUTCOME_PASSED
    assert request.measurement.error_information.message == "m"
    assert list(request.measurement.software_item_ids) == ["sw"]


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


def test___create_measurement___rejects_unsupported_value_before_rpc(
    client: DataStoreClient, service_client: Any
) -> None:
    with pytest.raises(TypeError, match="Unsupported measurement value type"):
        client.create_measurement("measurement", object(), "step-id")

    service_client.create_measurement.assert_not_called()


# ---------------------------------------------------------------- read value


def test___read_measurement_value___requests_value_of_measurement_id(
    client: DataStoreClient, service_client: Any
) -> None:
    value = data_store_pb2.MeasurementValue()
    value.scalar.bool_value = True
    _read_response(service_client, value)

    read_value = client.read_measurement_value(Measurement(id="m-id"))

    request = _sent(service_client.read_measurement_values)
    assert request.measurement_id == "m-id"
    assert list(request.read_mask.paths) == ["value"]
    assert read_value is True


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

    assert client.read_measurement_value(Measurement(id="m-id")) == {"enabled": True}


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

    results = client.query_test_results("$filter=Name eq 'Power test'", read_fields=["name"])

    request = _sent(service_client.query_test_results)
    assert request.odata_query == "$filter=Name eq 'Power test'"
    assert list(request.read_mask.paths) == ["name"]
    assert results == [TestResult("Power test", id="tr-id")]


def test___query_steps___returns_models(client: DataStoreClient, service_client: Any) -> None:
    service_client.query_steps.return_value = data_store_service_pb2.QueryStepsResponse(
        steps=[data_store_pb2.Step(id="step-id", name="s")]
    )

    steps = client.query_steps("$filter=Name eq 's'")

    assert _sent(service_client.query_steps).odata_query == "$filter=Name eq 's'"
    assert steps == [Step("s", id="step-id")]


def test___query_measurements___returns_models(
    client: DataStoreClient, service_client: Any
) -> None:
    service_client.query_measurements.return_value = (
        data_store_service_pb2.QueryMeasurementsResponse(
            measurements=[data_store_pb2.Measurement(id="m-id", name="voltage")]
        )
    )

    measurements = client.query_measurements("$filter=Name eq 'voltage'")

    assert _sent(service_client.query_measurements).odata_query == "$filter=Name eq 'voltage'"
    assert measurements == [Measurement(id="m-id", name="voltage")]


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
    service_client.update_measurement.return_value = data_store_pb2.Measurement(id="m-id")

    client.update_measurement(
        "m-id",
        error_information=ErrorInformation(error_code=2, message="boom"),
        extension={"retest": True},
    )

    request = _sent(service_client.update_measurement)
    assert request.measurement.error_information.message == "boom"
    assert request.measurement.extension["retest"] is True
    assert list(request.update_mask.paths) == ["error_information", "extension"]


@pytest.mark.parametrize("field", ["start_date_time", "end_date_time"])
def test___update_measurement___converts_timestamp(
    client: DataStoreClient, service_client: Any, field: str
) -> None:
    client.update_measurement("m-id", **{field: TIMESTAMP})

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
    getattr(client, method)("resource-id", duration=timedelta(seconds=3))

    request = _sent(getattr(service_client, method))
    assert getattr(request, resource_field).duration == hightime_timedelta_to_protobuf(
        timedelta(seconds=3)
    )
    assert list(request.update_mask.paths) == ["duration"]


def test___update___none_clears_field(client: DataStoreClient, service_client: Any) -> None:
    client.update_test_result("tr-id", link=None)

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
